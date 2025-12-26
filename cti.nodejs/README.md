# Copper PDF CTI Driver for Node.js

Node.jsを使ってCopper PDF 2.1以降にアクセスするための公式ドライバです。
CTIP (Copper Transaction Interlace Protocol) 2.0 に対応しています。

## 動作環境

* Node.js 14以降

## インストール

このリポジトリをクローンするか、プロジェクトに含めて使用してください。
Git経由でインストールすることも可能です。

```bash
npm install git+https://github.com/mimidesunya/copper_drivers/cti.nodejs
```

## 使い方

詳細は `examples/` ディレクトリ内のサンプルコードを参照してください。

### 基本的な変換 (ファイル出力)

```javascript
const { get_session } = require('copper-cti-nodejs'); 
// ローカルパスの場合は require('./src/index') など

async function main() {
    // Copper PDFサーバーに接続
    // 公開サーバーなどを指定できます (例: ctip://cti.li/)
    const session = get_session('ctip://localhost:8099', {
        user: 'user',        // 認証が必要な場合
        password: 'password'
    });

    try {
        // 結果の出力先をファイルに指定
        session.setOutputAsFile('output/result.pdf');

        // 変換開始 (ストリームへの書き込み)
        const input = session.transcode('.');
        input.write('<html><body><h1>Hello, Copper PDF!</h1></body></html>');
        input.end();

        // 変換完了を待機
        await session.waitForCompletion();
        console.log('PDF generated successfully.');

    } catch (err) {
        console.error('Error:', err);
    } finally {
        session.close();
    }
}

main();
```

### ストリームの使用 (標準出力など)

```javascript
const { get_session } = require('copper-cti-nodejs');

const session = get_session('ctip://localhost:8099');

// 結果を標準出力に流す (バイナリ破壊に注意: PowerShellなどではリダイレクトに問題がある場合があります)
session.setOutput(process.stdout);

const input = session.transcode('.');
fs.createReadStream('index.html').pipe(input);

await session.waitForCompletion();
session.close();
```

### プロパティの設定

```javascript
session.setProperty('cssj.page.size', 'A4');
```

## ドキュメント

APIドキュメントは JSDoc 形式で記述されています。以下のコマンドで生成できます。

```bash
npx jsdoc -c jsdoc.json
```

## ディレクトリ構成

* `src/`: ドライバのソースコード
* `examples/`: 使用例 (ファイル出力、標準出力、ディレクトリ出力、リソース解決)
* `docs/`: 生成されたドキュメント (生成後)

## ライセンス

Apache License 2.0
