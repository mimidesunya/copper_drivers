# -*- coding: utf-8 -*-
"""
$Id: ctip2.py 926 2013-05-30 13:13:59Z miyabe $
"""

from struct import *

def readfully(io, a):
    """データをバイト数だけ確実に読み込みます。
    
    io: ソケット
    a: バイト数
    戻り値: 読み込んだ文字列
    """
    ret = ''
    while a > 0:
        b = io.recv(a)
        a -= len(b)
        ret += b
    return ret

def write_int(io, a):
    """32ビット数値をビッグインディアンで書き出します。
    
    io: ソケット
    a: 数値
    """
    io.sendall(pack('>L', a))

def write_long(io, a):
    """64ビット数値をビッグインディアンで書き出します。
    
    io: ソケット
    a: 数値
    """
    io.sendall(pack('>L', a >> 32 & 0xFFFFFFFF))
    io.sendall(pack('>L', a & 0xFFFFFFFF))

def write_byte(io, b):
    """8ビット数値を書き出します。
    
    io: ソケット
    b: 数値
    """
    io.sendall(pack('B', b))

def write_bytes(io, b):
    """バイト数を16ビットビッグインディアンで書き出した後、バイト列を書き出します。
    
    io: ソケット
    b: バイト列
    """
    io.sendall(pack('>H', len(b)))
    io.sendall(b)

def read_short(io):
    """16ビットビッグインディアン数値を読み込みます。
    
    io: ソケット
    戻り値: 数値
    """
    b = readfully(io, 2)
    a = unpack('>H', b)
    return a[0]

def read_int(io):
    """32ビットビッグインディアン数値を読み込みます。
    
    io: ソケット
    戻り値: 数値
    """
    b = readfully(io, 4)
    a = unpack('>L', b)
    return a[0]
    
def read_long(io):
    """64ビットビッグインディアン数値を読み込みます。
    
    io: ソケット
    戻り値: 数値
    """
    b = readfully(io, 4)
    h = unpack('>L', b)[0]
    b = readfully(io, 4)
    l = unpack('>L', b)[0]
    if h >> 31 != 0:
        h ^= 0xFFFFFFFF
        l ^= 0xFFFFFFFF
        b = (h << 32) | l
        b = -(b + 1)
    else:
        b = (h << 32) | l
    return b;

def read_byte(io):
    """8ビット数値を読み込みます。
    
    io: ソケット
    戻り値: 数値
    """
    b = readfully(io, 1)
    b = unpack('B', b)
    return b[0]

def read_bytes(io):
    """16ビットビッグインディアン数値を読み込み、そのバイト数だけバイト列を読み込みます。
    
    io: ソケット
    戻り値: バイト列
    """
    b = readfully(io, 2)
    a = unpack('>H', b)
    len = a[0]
    b = readfully(io, len);
    return b;

REQ_PROPERTY = 0x01
REQ_START_MAIN = 0x02
REQ_SERVER_MAIN = 0x03
REQ_CLIENT_RESOURCE = 0x04
REQ_CONTINUOUS = 0x05
REQ_DATA = 0x11
REQ_START_RESOURCE = 0x21
REQ_MISSING_RESOURCE = 0x22
REQ_EOF = 0x31
REQ_ABORT = 0x32
REQ_JOIN = 0x33
REQ_RESET = 0x41
REQ_CLOSE = 0x42
REQ_SERVER_INFO = 0x51

RES_START_DATA = 0x01
RES_BLOCK_DATA = 0x11
RES_ADD_BLOCK = 0x12
RES_INSERT_BLOCK = 0x13
RES_MESSAGE = 0x14
RES_MAIN_LENGTH = 0x15
RES_MAIN_READ = 0x16
RES_DATA = 0x17
RES_CLOSE_BLOCK = 0x18
RES_RESOURCE_REQUEST = 0x21
RES_EOF = 0x31
RES_ABORT = 0x32
RES_NEXT = 0x33
    
"""パケットの送信に使うバッファのサイズです。
"""
CTI_BUFFER_SIZE = 1024

def cti_connect(io, encoding):
    """セッションを開始します。
    
    io: ソケット
    encoding: 通信に用いるエンコーディング
    """
    io.sendall("CTIP/2.0 "+encoding+"\n")

def req_server_info(io, uri):
    """サーバー情報を要求します。
    
    io: ソケット
    uri: URI
    """
    payload = 1 + 2 + len(uri)
    write_int(io, payload)
    write_byte(io, REQ_SERVER_INFO)
    write_bytes(io, uri)

def req_client_resource(io, mode):
    """サーバーからクライアントのリソースを要求するモードを切り替えます。
    
    io: ソケット
    mode: 0=off, 1=on
    """
    payload = 2
    write_int(io, payload)
    write_byte(io, REQ_CLIENT_RESOURCE)
    write_byte(io, mode)

def req_continuous(io, mode):
    """複数の結果を結合するモードを切り替えます。
    
    io: ソケット
    mode: 0=off, 1=on
    """
    payload = 2
    write_int(io, payload)
    write_byte(io, REQ_CONTINUOUS)
    write_byte(io, mode)

def req_missing_resource(io, uri):
    """リソースの不存在を通知します。
    
    io: ソケット
    uri: URI
    """
    payload = 1 + 2 + len(uri)
    write_int(io, payload)
    write_byte(io, REQ_MISSING_RESOURCE)
    write_bytes(io, uri)

def req_reset(io):
    """状態のリセットを要求します。
    
    io: ソケット
    """
    payload = 1
    write_int(io, payload)
    write_byte(io, REQ_RESET)

def req_abort(io, mode):
    """変換処理の中断を要求します。
    
    io: ソケット
    mode:  0=生成済みのデータを出力して中断, 1=即時中断
    """
    payload = 2
    write_int(io, payload)
    write_byte(io, REQ_ABORT)
    write_byte(io, mode)

def req_join(io):
    """変換結果を結合します。
    
    io: ソケット
    """
    payload = 1
    write_int(io, payload)
    write_byte(io, REQ_JOIN)

def req_eof(io):
    """終了を通知します。
    
    io: ソケット
    """
    payload = 1
    write_int(io, payload)
    write_byte(io, REQ_EOF)

def req_property(io, name, value):
    """プロパティを送ります。
    
    io: ソケット
    name: 名前
    value: 値
    """
    payload = len(name) + len(value) + 5
    write_int(io, payload)
    write_byte(io, REQ_PROPERTY)
    write_bytes(io, name)
    write_bytes(io, value)

def req_server_main(io, uri):
    """サーバー側データの変換を要求します。
    
    io: ソケット
    uri: URI
    """
    payload = len(uri) + 3
    write_int(io, payload)
    write_byte(io, REQ_SERVER_MAIN)
    write_bytes(io, uri)

def req_resource(io, uri, mime_type = 'text/css', encoding = '', length = -1):
    """リソースの開始を通知します。
    
    io: ソケット
    uri: URI
    mime_type: MIME型
    encoding: エンコーディング
    length: 長さ
    """
    payload = len(uri) + len(mime_type) + len(encoding) + 7 + 8
    write_int(io, payload)
    write_byte(io, REQ_START_RESOURCE)
    write_bytes(io, uri)
    write_bytes(io, mime_type)
    write_bytes(io, encoding)
    write_long(io, length)

def req_start_main(io, uri, mime_type = 'text/html', encoding = '', length = -1):
    """本体の開始を通知します。
    
    io: ソケット
    uri: URI
    mime_type: MIME型
    encoding: エンコーディング
    length: 長さ
    """
    payload = len(uri) + len(mime_type) + len(encoding) + 7 + 8
    write_int(io, payload)
    write_byte(io, REQ_START_MAIN)
    write_bytes(io, uri)
    write_bytes(io, mime_type)
    write_bytes(io, encoding)
    write_long(io, length)

def req_write(io, b):
    """データを送ります。
    
    io: ソケット
    b: データ
    """
    payload = len(b) + 1
    write_int(io, payload)
    write_byte(io, REQ_DATA)
    io.sendall(b)

def req_close(io):
    """通信を終了します。
    
    io: ソケット
    """
    payload = 1
    write_int(io, payload)
    write_byte(io, REQ_CLOSE)

def res_next(io):
    """次のレスポンスを取得します。
    
    結果ハッシュには次のデータが含まれます。
    
    - 'type' レスポンスタイプ
    - 'anchorId' 挿入する場所の直後のフラグメントID
    - 'level' エラーレベル
    - 'error' エラーメッセージ
    - 'id' 断片ID
    - 'progress' 処理済バイト数
    - 'bytes' データのバイト列
    
    io: ソケット
    戻り値: レスポンス
    """
    payload = read_int(io)
    type = read_byte(io)
    
    if type == RES_ADD_BLOCK or type == RES_EOF or type == RES_NEXT:
        return {'type'  :type}
    elif type == RES_START_DATA:
        uri = read_bytes(io)
        mime_type = read_bytes(io)
        encoding = read_bytes(io)
        length = read_long(io)
        return {
        'type'  :type,
        'uri'  :uri,
        'mime_type'  :mime_type,
        'encoding'  :encoding,
        'length'  :length
        }
    elif type == RES_MAIN_LENGTH or type == RES_MAIN_READ:
        length = read_long(io)
        return {
        'type'  :type,
        'length'  :length
        }
    
    elif type == RES_INSERT_BLOCK or type == RES_CLOSE_BLOCK:
        block_id = read_int(io)
        return {
        'type'  :type,
        'block_id'  :block_id
        }
    
    elif type == RES_MESSAGE:
        code = read_short(io)
        payload -= 1 + 2
        message = read_bytes(io)
        payload -= 2 + len(message)
        args = []
        while payload > 0:
            arg = read_bytes(io)
            payload -= 2 + len(arg)
            args.append(arg)
        return {
        'type'  :type,
        'code'  :code,
        'message'  :message,
        'args'  :args
        }
    
    elif type == RES_BLOCK_DATA:
        length = payload - 5
        block_id = read_int(io)
        bytes = readfully(io, length)
        return {
        'type'  :type,
        'block_id'  :block_id,
        'bytes'  :bytes,
        'length'  :length
        }
    
    elif type == RES_DATA:
        length = payload - 1
        bytes = readfully(io, length)
        return {
        'type'  :type,
        'bytes'  :bytes,
        'length'  :length
        }
    
    elif type == RES_RESOURCE_REQUEST:
        uri = read_bytes(io)
        return {
        'type'  :type,
        'uri'  :uri
        }
    
    elif type == RES_ABORT:
        mode = read_byte(io)
        code = read_short(io)
        payload -= 1 + 1 + 2
        message = read_bytes(io)
        payload -= 2 + len(message)
        args = []
        while payload > 0:
            arg = read_bytes(io)
            payload -= 2 + len(arg)
            args.append(arg)
        return {
        'type'  :type,
        'mode'  :mode,
        'code'  :code,
        'message'  :message,
        'args'  :args
        }
    
    else:
        raise IllegalStateError("Bad response type:#{type}")
