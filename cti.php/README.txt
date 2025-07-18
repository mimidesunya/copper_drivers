CTI ドライバ PHP版
バージョン @version@

PHP(http://www.php.net/)を使ってCopper PDF 2.1以降にアクセスするためのプログラムです。
使用方法は付属のAPIドキュメント、サンプルプログラムまたは以下オンラインマニュアルを参照してください。
http://dl.cssj.jp/docs/copper/3.0/html/3422_ctip2_php.html

■ 動作環境
PHP 5.1.6 以降

■ 付属物

code     -- ドライバ本体(ソース)
apidoc   -- APIドキュメント(PHP Documentor)
test     -- サンプル・プログラム

■ ライセンス

Copyright (c) 2011-2021 Zamasoft.

Apache License Version 2.0に基づいてライセンスされます。
あなたがこのファイルを使用するためには、本ライセンスに従わなければなりません。
本ライセンスのコピーは下記の場所から入手できます。

   http://www.apache.org/licenses/LICENSE-2.0

適用される法律または書面での同意によって命じられない限り、
本ライセンスに基づいて頒布されるソフトウェアは、明示黙示を問わず、
いかなる保証も条件もなしに「現状のまま」頒布されます。
本ライセンスでの権利と制限を規定した文言については、本ライセンスを参照してください。 

Copyright (c) 2011-2021 Zamasoft.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

■ 変更履歴
-- v2.1.4
2021/11/15
'Only variables should be passed by reference' 警告が出ないように対応しました。

-- v2.1.3
2014/08/11
Session->start_main関数のデフォルトの引数を'.'にしました。
画像を標準出力に出力すると、Cannot modify header information警告が出る問題に対応しました。

-- v2.1.2
2013/04/24
debパッケージのPHPバージョンチェックの不具合を修正。
phpDocumentorを4.1.4に更新。
コールバック関数を参照として渡してしまっている部分を値を渡すように修正。
以下の関数には、コールバック関数の関数名をリテラルとして直接渡せるようになります。
set_message_func
set_progress_func
set_resolver_func

-- v2.1.1
2011/03/16
.rpm, .deb パッケージをリリース。
PHP 5.1.6 以降に対応。
Content-Length ヘッダに不正確な値が出力される問題を修正。

-- v2.1.0
2011/03/03
Copper PDF 3 以降からサポートする、複数の文書から１つのPDFを生成する機能に対応。
TLS通信に対応。

-- v2.0.0
2010/11/02
最初のリリース
