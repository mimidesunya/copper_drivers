# Copper PDF CTI Driver for Node.js

Node.jsを使ってCopper PDF 2.1以降にアクセスするための公式ドライバです。
CTIP (Copper Transaction Interlace Protocol) 2.0 に対応しています。

## 動作環境

* Node.js 14以降

## インストール

npmはGitリポジトリのサブディレクトリからの直接インストールをサポートしていないため、リポジトリをクローンしてからローカルパスを指定してインストールします。

```bash
git clone https://github.com/mimidesunya/copper_drivers.git
npm install ./copper_drivers/cti.nodejs --install-links
```

※Windows環境などでシンボリックリンクのエラーが発生する場合は、`--install-links` オプションを付与することでファイルをコピーしてインストールできます。または、以下のようにパッケージ化してからインストールしてください。

```bash
cd copper_drivers/cti.nodejs
npm pack
cd ../..
npm install ./copper_drivers/cti.nodejs/copper-cti-nodejs-1.0.0.tgz
```

または、ご自身のプロジェクトに `cti.nodejs` ディレクトリをダウンロード・コピーして使用することも可能です。

## 使い方

詳細は `examples/` ディレクトリ内のサンプルコードを参照してください。

### 基本的な変換 (ファイル出力)

```javascript
const { get_session } = require('copper-cti-nodejs');
const fs = require('fs');
const path = require('path');

async function main() {
    // Copper PDFサーバーに接続 (例: ctip://cti.li/)
    const session = get_session('ctip://cti.li/', {
        user: 'user',
        password: 'kappa'
    });

    try {
        const outFile = 'output/result.pdf';
        
        // 出力先ディレクトリがない場合は作成
        const outDir = path.dirname(outFile);
        if (!fs.existsSync(outDir)) {
            fs.mkdirSync(outDir, { recursive: true });
        }

        // 結果の出力先をファイルに指定
        session.setOutputAsFile(outFile);

        // 変換中のメッセージを表示するハンドラ
        session.setMessageFunc((code, msg, args) => {
            console.log(`Message [${code}]: ${msg}`);
        });

        // 変換開始 (ストリームへの書き込み)
        // transcode() の引数にリソースのベースパスを指定できます ('.' はカレントディレクトリ)
        const writer = session.transcode('.');
        
        // HTMLを流し込む
        writer.write('<html><body><h1>Hello, Copper PDF!</h1></body></html>');
        writer.end();

        // 変換完了を待機
        await session.waitForCompletion();
        console.log(`PDF generated successfully: ${outFile}`);

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
const fs = require('fs');

async function main() {
    const session = get_session('ctip://cti.li/', {
        user: 'user',
        password: 'kappa'
    });

    try {
        // 結果を標準出力に流す (バイナリ破壊に注意: PowerShellなどではリダイレクトに問題がある場合があります)
        session.setOutputAsStream(process.stdout);

        const writer = session.transcode('.');
        fs.createReadStream('index.html').pipe(writer);

        await session.waitForCompletion();
    } catch (err) {
        console.error(err);
    } finally {
        session.close();
    }
}

main();
```

### プロパティの設定

```javascript
session.setProperty('output.pdf.version', '1.5');
```

## ドキュメント

APIドキュメントは JSDoc 形式で記述されています。以下のコマンドで生成できます。

```bash
cd cti.nodejs
npm run doc
```

生成されたドキュメントは `docs/` ディレクトリに出力されます。 `docs/index.html` をブラウザで開いて確認してください。

## ディレクトリ構成

* `src/`: ドライバのソースコード
* `examples/`: 使用例 (ファイル出力、標準出力、ディレクトリ出力、リソース解決)
* `docs/`: 生成されたドキュメント (生成後)

## ライセンス

Apache License 2.0
