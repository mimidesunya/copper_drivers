CTI ドライバ Ruby版
バージョン @version@

Ruby(http://www.ruby-lang.org/)を使ってCopper PDF 2.1以降にアクセスするためのプログラムです。
使用方法は付属のAPIドキュメント、サンプルプログラムまたは以下オンラインマニュアルを参照してください。
http://dl.cssj.jp/docs/copper/3.2/html/3424_ctip2_ruby.html

■ 動作環境
Ruby 1.8.7以降

■ 付属物

code     -- ドライバ本体(ソース)
apidoc   -- APIドキュメント(RDoc)
test     -- サンプル・プログラム

■ ライセンス

Copyright (c) 2013-2022 Zamasoft.

Apache License Version 2.0に基づいてライセンスされます。
あなたがこのファイルを使用するためには、本ライセンスに従わなければなりません。
本ライセンスのコピーは下記の場所から入手できます。

   http://www.apache.org/licenses/LICENSE-2.0

適用される法律または書面での同意によって命じられない限り、
本ライセンスに基づいて頒布されるソフトウェアは、明示黙示を問わず、
いかなる保証も条件もなしに「現状のまま」頒布されます。
本ライセンスでの権利と制限を規定した文言については、本ライセンスを参照してください。 

Copyright (c) 2013-2022 Zamasoft.

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
-- v2.0.0
2013/4/24
最初のリリース

-- v2.1.0
2022/1/24
Ruby 3に対応しました。
FileUtilsまたはIOのcopy_streamではなくCTI::copy_streamを使ってください。
