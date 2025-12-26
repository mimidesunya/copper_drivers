const { get_session } = require('../src');
const fs = require('fs');

/**
 * 標準出力にPDFを出力するサンプル
 * 使用法: node output-stdout.js <URI> <HTMLファイル> > output.pdf
 */
async function main() {
    // 使用法: node output-stdout.js [HTMLファイル] [URI]
    // デフォルトURI: ctip://cti.li/
    
    if (process.argv.length < 3) {
        console.error('Usage: node output-stdout.js <HTML_FILE> [URI]');
        process.exit(1);
    }

    const htmlFile = process.argv[2];
    const uri = process.argv[3] || 'ctip://cti.li/';

    // セッションの作成
    const session = get_session(uri, { user: 'user', password: 'kappa' });

    try {
        // 結果の出力先を標準出力に設定
        session.setOutputAsStream(process.stdout);

        // プログレス表示（標準エラー出力へ）
        session.setProgressFunc((total, read) => {
            console.error(`Progress: ${read}/${total !== -1 ? total : '???'}`);
        });

        // 変換開始
        console.error('Starting transcoding...');
        const input = session.transcode();
        
        // ファイルを読み込んでCopperサーバーへ送信
        fs.createReadStream(htmlFile).pipe(input);

        // 完了待機
        await session.waitForCompletion();
        console.error('Done.');

    } catch (err) {
        console.error('Error:', err.message);
    } finally {
        session.close();
    }
}

main();
