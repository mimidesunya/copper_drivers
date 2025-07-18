CTI ドライバ .NET版
バージョン @version@

.NET(C#, VB.NETなど)でCopper PDF 2.1以降にアクセスするためのプログラムです。
.NET 3.5 以降が必要です。
使用方法は付属のAPIドキュメント、サンプルプログラムまたは以下オンラインマニュアルを参照してください。
http://dl.cssj.jp/docs/copper/3.0/html/3423_ctip2_dotnet.html

■ 付属物

CTI     -- ドライバのソースとサンプル・プログラム
apidoc   -- APIドキュメント
dll/3.5/CTI.dll -- .NET3.5向けDLL
dll/4.0/CTI.dll -- .NET4.0向けDLL

■ ライセンス

Copyright (c) 2011-2015 Zamasoft

Apache License Version 2.0に基づいてライセンスされます。
あなたがこのファイルを使用するためには、本ライセンスに従わなければなりません。
本ライセンスのコピーは下記の場所から入手できます。

   http://www.apache.org/licenses/LICENSE-2.0

適用される法律または書面での同意によって命じられない限り、
本ライセンスに基づいて頒布されるソフトウェアは、明示黙示を問わず、
いかなる保証も条件もなしに「現状のまま」頒布されます。
本ライセンスでの権利と制限を規定した文言については、本ライセンスを参照してください。 

Copyright (c) 2011-2015 Zamasoft

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
-- v2.0.1
2015/04/09
SSL/TLSに対応しました。
プロトコルでタイムアウトを設定できるようになりました。
以下のようにURLパラメータで、timeoutをミリ秒単位で指定できます。
ctip://hostname/?timeout=10000
Copper PDF 3.1.1 の新しい認証方式に対応しました。

-- v2.0.0
2013/02/08
.NET 3.5と4.0のDLLを添付

-- v2.0.0
2011/11/06
初回リリース