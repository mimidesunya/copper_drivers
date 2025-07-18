# -*- coding: utf-8 -*-
"""
$Id: session.py 935 2013-05-31 06:46:26Z miyabe $
"""

import sys
import select
from ctip2 import *
from builder import *
from results import *

class IllegalStateError(Exception):
    """関数の呼び出し順が不適切な場合に発生する例外です。
    """
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)

class Session:
    def __init__(self, io, options = {}):
        """セッションのコンストラクタです。
         セッションの作成は通常DriverManager.phpのcti_get_sessionで行うため、
         ユーザーがコンストラクタを直接呼び出す必要はありません。
        
         io: ソケット
         options: 接続オプション
        """
        self.state = None
        self.io = None
        self.reset();
        self.io = io
        self.encoding = (options.has_key('encoding') and options['encoding']) or 'UTF-8'
        self.user = (options.has_key('user') and options['user']) or ''
        self.password = (options.has_key('password') and options['password']) or ''
        
        cti_connect(self.io, self.encoding)
        data = "PLAIN: " + self.user + " " + self.password + "\n"
        self.io.sendall(data)
        res = readfully(io, 4)
        if res != "OK \n":
            raise IllegalStateError("Authentication failure.")

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
 
    def get_server_info(self, uri):
        """サーバー情報を返します。
    詳細は{オンラインのドキュメント}[http://sourceforge.jp/projects/copper/wiki/CTIP2.0%E3%81%AE%E3%82%B5%E3%83%BC%E3%83%90%E3%83%BC%E6%83%85%E5%A0%B1]をご覧下さい。
    
    uri: サーバー情報のURI
    
    返り値: サーバー情報のデータ文字列(XML)
        """
        req_server_info(self.io, uri)
        data = ''
        while 1:
            res = res_next(self.io)
            if res['type'] == RES_EOF:
                break
            data += res['bytes']
        return data

    def set_results(self, results):
        """変換結果の出力先を指定します。
    
    Session#transcode および Session#transcode_server の前に呼び出してください。
    この関数を呼び出さないデフォルトの状態では、出力先は標準出力( sys.__stdout__ )になります。
    
    また、デフォルトの状態では、自動的にContent-Type, Content-Lengthヘッダが送出されます。
    
    results: 出力先のResults オブジェクト
        """
        if self.state >= 2:
            raise IllegalStateError("set_results: Main content is already sent.") 
        self.results = results

    def set_output_as_file(self, file):
        """変換結果の出力先ファイル名を指定します。
    
    Session#set_results　の簡易版です。
    こちらは、１つだけ結果を出力するファイル名を直接設定することができます。
    
    file: 出力先ファイル名
        """
        self.set_results(SingleResult(FileBuilder(file)))

    def set_output_as_directory(self, dir, prefix = '', suffix = ''):
        """変換結果の出力先ディレクトリ名を指定します。
    
    Session#set_results の簡易版です。
    こちらは、複数の結果をファイルとして出力するディレクトリ名を直接設定することができます。
    ファイル名は prefix ページ番号 suffix をつなげたものです。
    
    dir: 出力先ディレクトリ名
    prefix: 出力するファイルの名前の前に付ける文字列
    suffix: 出力するファイルの名前の後に付ける文字列
        """
        self.set_results(DirectoryResults(dir, prefix, suffix))

    def set_output_as_stream(self, out):
        """変換結果の出力先リソースを指定します。
    
    Session#set_results の簡易版です。
    こちらは、１つだけの結果出力先を直接設定することができます。
    
    out: 出力先 IO オブジェクト
        """
        self.set_results(SingleResult(StreamBuilder(out)))

    def set_message_func(self, message_func):
        """エラーメッセージ受信のためのコールバック関数を設定します。
    
    Session#transcode および Session#transcode_server の前に呼び出してください。
    コールバック関数の引数は、エラーコード(int)、メッセージ(str)、付属データ(配列)です。
    
    message_func: 関数
    
    例:
        def message_func(code, message, args):
            print "%X %s" % (code, message)
        session.set_message_func(message_func)
        """
        if self.state >= 2:
            raise IllegalStateError("receive_message: Main content is already sent.")
        self.message_func = message_func

    def set_progress_func(self, progress_func):
        """進行状況受信のためのコールバック関数を設定します。
    
    Session#transcode および Session#transcode_server の前に呼び出してください。
    コールバック関数の引数は、全体のバイト数(int)、読み込み済みバイト数(int)です。
    
    progress_func: 関数
    
    例:
        def progress_func(length, read):
            print "%d %d" % (length, read)
        session.set_progress_func(progress_func)
        """
        if self.state >= 2:
            raise IllegalStateError("receive_progress: Main content is already sent.")
        self.progress_func = progress_func

    def set_resolver_func(self, resolver_func):
        """リソース解決のためのコールバック関数を設定します。
    
    Session#transcode および Session#transcode_server の前に呼び出してください。
    コールバック関数の引数は、URI(str)、リソース出力クラス( Resource )です。
    
    resolver_func: 関数
    
    URIに対応するリソースが見つかった場合、 Resource#found メソッドを呼び出してください。
    foundの呼び出しがない場合、リソースは見つからなかったものと扱われます。
    
    例:
        def resolver(uri, r):
            if os.path.exists(uri):
                out = r.found()
                try:
                    file = open(uri)
                    try:
                        out.write(file.read())
                    finally:
                        file.close()
                finally:
                    out.close()
        session.set_resolver_func(resolver)
        """
        if self.state >= 2:
            raise IllegalStateError("resolver: Main content is already sent.")
        self.resolver_func = resolver_func;
        req_client_resource(self.io, (resolver_func and 1) or 0)

    def set_continuous(self, continuous):
        """複数の結果を結合するモードを切り替えます。
    モードが有効な場合、 Session#join の呼び出しで複数の結果を結合して返します。
    
    Session#transcode およびSession#transcode_server の前に呼び出してください。
    
    continuous: 有効にするにはtrue
        """
        if self.state >= 2:
            raise IllegalStateError("set_continuous: Main content is already sent.")
        req_continuous(self.io, (continuous and 1) or 0)

    def property(self, name, value):
        """プロパティを設定します。
    
    セッションを作成した直後に呼び出してください。
    利用可能なプロパティの一覧は{資料集}[http://dl.cssj.jp/docs/copper/3.0/html/5100_io-properties.html]を参照してください。
    
    name: 名前
    value: 値
        """
        if self.state >= 2:
            raise IllegalStateError("property: Main content is already sent.")
        req_property(self.io, name, value)

    def resource(self, uri, opts = {}):
        """リソース送信処理を行います。
        Session#transcode および Session#transcode_server の前に呼び出してください。
        
        uri: 仮想URI
        opts: リソースオプション(ハッシュ型で、'mime_type', 'encoding', 'length'というキーでデータ型、文字コード、長さを設定することができます。)
        
        戻り値: リソースの出力先ストリームが返されます。
        
        例:
            out = session.resource('test.css', {'mime_type' => 'test/css'})
            try:
                file = open('data/test.css')
                try:
                    out.write(file.read())
                finally:
                    file.close()
            finally:
                out.close()
        """
        if self.state >= 2:
            raise IllegalStateError("resource: Main content is already sent.")
        mime_type = (opts.has_key('mime_type') and opts['mime_type']) or 'text/css'
        encoding = (opts.has_key('encoding') and opts['encoding']) or ''
        length = (opts.has_key('length') and opts['length']) or -1
        req_resource(self.io, uri, mime_type, encoding, length)
        return ResourceOut(self.io)

    def transcode(self, uri = '.', opts = {}):
        """変換対象の文書リソースを送信し、変換処理を行います。
        
        uri: 仮想URI
        opts: リソースオプション(ハッシュ型で、'mime_type', 'encoding', 'length'というキーでデータ型、文字コード、長さを設定することができます。)
        
        戻り値: リソースの出力先ストリームが返されます。
        
        例:
            out = session.transcode('.', {'mime_type' => 'text/html'})
            try:
                file = open('data/test.html')
                try:
                    out.write(file.read())
                finally:
                    file.close()
            finally:
                out.close()
        """
        if self.state >= 2:
            raise IllegalStateError("transcode: Main content is already sent.")
        mime_type = (opts.has_key('mime_type') and opts['mime_type']) or 'text/css'
        encoding = (opts.has_key('encoding') and opts['encoding']) or ''
        length = (opts.has_key('length') and opts['length']) or -1
        self.state = 2
        req_start_main(self.io, uri, mime_type, encoding, length)
        return MainOut(self.io, self)
    
    def transcode_server(self, uri):
        """サーバー側リソースを変換します。
    
    uri: URI
        """
        if self.state >= 2:
            raise IllegalStateError("transcode_server: Main content is already sent.")
        req_server_main(self.io, uri)
        self.state = 2
        while self.build_next():
            pass

    def abort(self, mode):
        """変換処理の中断を要求します。
    
    mode: 中断モード 0=生成済みのデータを出力して中断, 1=即時中断
        """
        if self.state >= 2:
            raise IllegalStateError("abort: The session is already closed.")
        req_abort(self.io, mode)

    def reset(self):
        """全ての状態をリセットします。
        """
        if self.state >= 3:
            raise IllegalStateError("reset: The session is already closed.")
        if self.io:
            req_reset(self.io)
        self.progress_func = None
        self.message_func = None
        self.resolver_func = None
        self.builder = None
        self.main_length = None
        self.main_read = 0
        
        def content_type(opts):
            print >> sys.__stdout__, "Content-Type: "+opts['mime_type']
        def content_length(length):
            print >> sys.__stdout__, "Content-Length: "+str(length)
            print >> sys.__stdout__
        self.results = SingleResult(StreamBuilder(sys.__stdout__, content_length), content_type)
        
        self.state = 1

    def join(self):
        """結果を結合します。
    
    先にSession#set_continuous を呼び出しておく必要があります。
        """
        if self.state >= 3:
            raise IllegalStateError("join: The session is already closed.")
        req_join(self.io)
        self.state = 2
        while self.build_next():
            pass
     
    def close(self):
        """セッションを閉じます。
        """
        if self.state >= 3:
            raise IllegalStateError("close: The session is already closed.")
        req_close(self.io);
        self.state = 3
        
    def build_next(self):
        res = res_next(self.io)
        type = res['type']
        if type == RES_START_DATA:
            if self.builder is not None:
                self.builder.finish()
                self.builder.dispose()
            self.builder = self.results.next_builder(res)
        elif type == RES_BLOCK_DATA:
            self.builder.block_write(res['block_id'], res['bytes'])
        elif type == RES_ADD_BLOCK:
            self.builder.add_block()
        elif type == RES_INSERT_BLOCK:
            self.builder.insert_block_before(res['block_id'])
        elif type == RES_CLOSE_BLOCK:
            self.builder.close_block(res['block_id'])
        elif type == RES_DATA:
            self.builder.serial_write(res['bytes'])
        elif type == RES_MESSAGE:
            if self.message_func is not None:
                self.message_func(res['code'], res['message'], res['args'])
        elif type == RES_MAIN_LENGTH:
            self.main_length = res['length']
            if self.progress_func is not None:
                self.progress_func(self.main_length, self.main_read)
        elif type == RES_MAIN_READ:
            self.main_read = res['length']
            if self.progress_func is not None:
                self.progress_func(self.main_length, self.main_read)        
        elif type == RES_RESOURCE_REQUEST:
            uri = res['uri']
            r = Resource(self.io, uri)
            if self.resolver_func is not None:
                self.resolver_func(uri, r)
            r.finish()
            if r.missing:
                req_missing_resource(self.io, uri)
        elif type == RES_ABORT:
            if self.builder is not None:
                if res['mode'] == 0:
                    self.builder.finish()
                self.builder.dispose()
                self.builder = None
            self.main_length = None
            self.main_read = 0
            self.state = 1
            return False
        elif type == RES_EOF:
            self.builder.finish()
            self.builder.dispose()
            self.builder = None
            self.main_length = None
            self.main_read = 0
            self.state = 1
            return False
        elif type == RES_NEXT:
            self.state = 1
            return False
        return True

class ResourceOut:
    def __init__(self, io):
        self.closed = False
        self.io = io

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    
    def write(self, str):
        while len(str) > 0:
            data = str[0:CTI_BUFFER_SIZE]
            str = str[CTI_BUFFER_SIZE:]
            req_write(self.io, data)
    
    def close(self):
        if not self.closed:
            req_eof(self.io)
            self.closed = True

class MainOut:
    def __init__(self, io, session):
        self.io = io
        self.session = session
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    
    def write(self, s):
        while len(s) > 0:
            data = s[0:CTI_BUFFER_SIZE]
            s = s[CTI_BUFFER_SIZE:]
            packet = pack('>LB', len(data) + 1, REQ_DATA) + data
            while len(packet) > 0:
                rs, ws, xs = select.select([self.io], [self.io], [])
                if len(packet) > 0 and len(ws) > 0:
                    l = self.io.send(packet)
                    packet = packet[l:]
                if len(rs) > 0:
                    self.session.build_next()

    def close(self):
        req_eof(self.io)
        while self.session.build_next():
            pass

class Resource:
    def __init__(self, io, uri):
        self.missing = True
        self.out = None
        self.io = io
        self.uri = uri
        self.missing = True

    def missing(self):
        return self.missing

    def found(self, opts = {}):
        """サーバーから要求されたリソースが見つかった場合の処理をします。

opts: リソースオプション(ハッシュ型で、'mime_type', 'encoding', 'length'というキーでデータ型、文字コード、長さを設定することができます。)

戻り値: 出力先ストリームが返されます。

例:
Session#resolver を参照してください。
        """
        mime_type = (opts.has_key('mime_type') and opts['mime_type']) or 'text/css'
        encoding = (opts.has_key('encoding') and opts['encoding']) or ''
        length = (opts.has_key('length') and opts['length']) or -1
        req_resource(self.io, self.uri, mime_type, encoding, length)
        self.missing = False
        self.out = ResourceOut(self.io)
        return self.out

    def finish(self):
        if self.out is not None:
            self.out.close()
