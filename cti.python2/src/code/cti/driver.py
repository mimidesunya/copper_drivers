# -*- coding: utf-8 -*-
"""
$Id: driver.py 926 2013-05-30 13:13:59Z miyabe $
"""

from session import Session
import re
import socket

"""ドライバクラスです。通常は直接使用する必要はありません。
代わりに get_session 関数を使用してください。
"""
class Driver:
    def get_session(self, uri, options = {}):
        """指定されたURIに接続し、セッションを返します。
        
        uri: 接続先アドレス
        options: 接続オプション
        
            返り値: Session オブジェクト
        """
        # uriの解析
        host = 'localhost'
        port = 8099
        useSSL = False
        m = re.match('^ctips:\/\/([^:\/]+):([0-9]+)\/?$', uri)
        if m:
            useSSL = True
            host = m.group(1)
            port = int(m.group(2))
        else:
            m = re.match('^ctips:\/\/([^:\/]+)\/?$', uri)
            if m:
                useSSL = True
                host = m.group(1)
            else:
                m = re.match('^ctip:\/\/([^:\/]+):([0-9]+)\/?$', uri)
                if m:
                    host = m.group(1)
                    port = int(m.group(2))
                else:
                    m = re.match('^ctip:\/\/([^:\/]+)\/?$', uri)
                    if m:
                        host = m.group(1)
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if useSSL:
            # SSLを使う場合
            import ssl
            s = ssl.wrap_socket(s)
        s.connect((host, port))
        return Session(s, options)