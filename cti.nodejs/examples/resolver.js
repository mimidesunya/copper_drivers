const { get_session } = require('../src');
const fs = require('fs');
const path = require('path');

/**
 * リソースリゾルバを使用するサンプル
 * HTML内の画像などをローカルから送信します
 * 使用法: node resolver.js <URI> <HTMLファイル> <出力PDFファイル>
 */
async function main() {
    // 使用法: node resolver.js <HTMLファイル> <出力PDFファイル> [URI]
    // デフォルトURI: ctip://cti.li/

    if (process.argv.length < 3) {
        console.log('Usage: node resolver.js <HTML_FILE> [OUTPUT_PDF] [URI]');
        process.exit(1);
    }

    const htmlFile = process.argv[2];
    const outFile = process.argv[3] || 'output/resolver.pdf';
    const uri = process.argv[4] || 'ctip://cti.li/';
    const baseDir = path.dirname(path.resolve(htmlFile));

    // Ensure output directory exists
    const outDir = path.dirname(outFile);
    if (!fs.existsSync(outDir)) {
        fs.mkdirSync(outDir, { recursive: true });
    }

    const session = get_session(uri, { user: 'user', password: 'kappa' });

    try {
        session.setOutputAsFile(outFile);

        // リゾルバ関数を設定
        session.setResolverFunc((uri, resource) => {
            console.log(`Server requested resource: ${uri}`);
            
            // 相対パス解決の簡易実装
            let localPath = uri;
            if (!path.isAbsolute(uri)) {
                localPath = path.join(baseDir, uri);
            }

            if (fs.existsSync(localPath)) {
                console.log(`Sending local file: ${localPath}`);
                
                // Content-Typeの簡易判定（実際にはもっと厳密に行うべき）
                let mime = 'application/octet-stream';
                if (localPath.endsWith('.css')) mime = 'text/css';
                else if (localPath.endsWith('.png')) mime = 'image/png';
                else if (localPath.endsWith('.jpg')) mime = 'image/jpeg';

                const output = resource.found({ mime_type: mime });
                fs.createReadStream(localPath).pipe(output);
                
                // ストリーム完了を待つ必要があればPromiseを返すべきだが、
                // pipeは非同期に進む。ドライバ側はResource#foundが同期的に呼ばれることを期待しているが、
                // 実際のデータ送信は非同期でOK。
            } else {
                console.warn(`Resource not found: ${localPath}`);
                // 何もしないと missing 扱いになる
            }
        });

        const input = session.transcode();
        fs.createReadStream(htmlFile).pipe(input);

        await session.waitForCompletion();
        console.log(`Created ${outFile}`);

    } catch (err) {
        console.error('Error:', err);
    } finally {
        session.close();
    }
}

main();
