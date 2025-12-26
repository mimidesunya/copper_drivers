const { get_session } = require('../src');
const fs = require('fs');
const path = require('path');

/**
 * ディレクトリに連番ファイルとして出力するサンプル
 * 使用法: node output-dir.js <URI> <HTMLファイル> <出力ディレクトリ>
 */
async function main() {
    // 使用法: node output-dir.js <HTMLファイル> <出力ディレクトリ> [URI]
    // デフォルトURI: ctip://cti.li/

    if (process.argv.length < 3) {
        console.log('Usage: node output-dir.js <HTML_FILE> [OUTPUT_DIR] [URI]');
        process.exit(1);
    }

    const htmlFile = process.argv[2];
    const outDir = process.argv[3] || 'output/dir';
    const uri = process.argv[4] || 'ctip://cti.li/';

    if (!fs.existsSync(outDir)) {
        fs.mkdirSync(outDir, { recursive: true });
    }

    const session = get_session(uri, { user: 'user', password: 'kappa' });

    try {
        // 結果の出力先をディレクトリに設定
        // page_1.pdf, page_2.pdf ... のように出力されます
        session.setOutputAsDirectory(outDir, 'page_', '.pdf');
        
        // ページごとにファイルを分ける設定
        session.setProperty('coppdf.page.separate', 'true');

        const input = session.transcode();
        fs.createReadStream(htmlFile).pipe(input);

        await session.waitForCompletion();
        console.log(`Successfully output to directory: ${outDir}`);

    } catch (err) {
        console.error('Error:', err);
    } finally {
        session.close();
    }
}

main();
