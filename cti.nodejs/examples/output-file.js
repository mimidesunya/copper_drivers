const { Driver, get_session } = require('../src');
const fs = require('fs');
const path = require('path');

/**
 * ファイルにPDFを出力するサンプル
 * 使用法: node output-file.js <URI> <HTMLファイル> <出力PDFファイル>
 */
async function main() {
    // 使用法: node output-file.js <HTMLファイル> <出力PDFファイル> [URI]
    // デフォルトURI: ctip://cti.li/

    if (process.argv.length < 3) {
        console.log('Usage: node output-file.js <HTML_FILE> [OUTPUT_PDF] [URI]');
        process.exit(1);
    }

    const htmlFile = process.argv[2];
    const outFile = process.argv[3] || 'output/file.pdf';
    const uri = process.argv[4] || 'ctip://cti.li/';

    // Ensure output directory exists
    const outDir = path.dirname(outFile);
    if (!fs.existsSync(outDir)) {
        fs.mkdirSync(outDir, { recursive: true });
    }

    const session = get_session(uri, { user: 'user', password: 'kappa' });

    try {
        // 結果の出力先をファイルに設定
        session.setOutputAsFile(outFile);

        // メッセージハンドラの設定
        session.setMessageFunc((code, msg, args) => {
            console.error(`Message [${code}]: ${msg}`, args);
        });

        const input = session.transcode();
        fs.createReadStream(htmlFile).pipe(input);

        await session.waitForCompletion();
        console.log(`Successfully created ${outFile}`);

    } catch (err) {
        console.error('Error:', err);
    } finally {
        session.close();
    }
}

main();
