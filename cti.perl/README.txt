CTI ドライバ Perl版
バージョン @version@

Perl(http://www.perl.com/)を使ってCopper PDF 2.1以降にアクセスするためのプログラムです。
使用方法は付属のAPIドキュメント、サンプルプログラムまたは以下オンラインマニュアルを参照してください。
http://dl.cssj.jp/docs/copper/3.0/html/3421_ctip2_perl.html

■ 動作環境
Perl 5.6.1 以降
File::Temp モジュール
IO::Socket::SSL （SSL接続をする場合）

■ 付属物

code     -- ドライバ本体(ソース)
apidoc   -- APIドキュメント(pod2html)
test -- サンプル・プログラム

■ ライセンス

Copyright (c) 2011-2013 Zamasoft.

Apache License Version 2.0に基づいてライセンスされます。
あなたがこのファイルを使用するためには、本ライセンスに従わなければなりません。
本ライセンスのコピーは下記の場所から入手できます。

   http://www.apache.org/licenses/LICENSE-2.0

適用される法律または書面での同意によって命じられない限り、
本ライセンスに基づいて頒布されるソフトウェアは、明示黙示を問わず、
いかなる保証も条件もなしに「現状のまま」頒布されます。
本ライセンスでの権利と制限を規定した文言については、本ライセンスを参照してください。 

Copyright (c) 2011-2012 Zamasoft.

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
-- v2.1.3
2013/04/23
RPMが正常な場所にインストールされない不具合を修正。

-- v2.1.2
2012/04/10
画像の出力時にContent-Lengthヘッダが不適切に出力されるため、
画像出力時はContent-Lengthを自動で出力しないように修正。

-- v2.1.1
2011/03/16
.rpm, .deb パッケージをリリース。
大きな数値の扱い中に警告が出る問題を修正。

-- v2.1.0
2011/03/03
Copper PDF 3 以降からサポートする、複数の文書から１つのPDFを生成する機能に対応。
TLS通信に対応。

-- v2.0.0
2010/01/11
初回リリース