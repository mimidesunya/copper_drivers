# -*- coding: utf-8 -*-
"""CTI driver for Python
$Id: __init__.py 926 2013-05-30 13:13:59Z miyabe $

PythonでCopper PDF 2.1以降にアクセスするためのドライバです。
以下のドキュメントを参照してください。

http://dl.cssj.jp/docs/copper/3.0/html/3425_ctip2_python.html
"""

__author__ = "MIYABE Tatsuhiko <tatsuhiko@miya.be>"
__status__ = "production"
__version__ = "2.0.0"
__date__ = "31 May 2012"

from .driver import Driver

def get_driver(uri):
    """指定されたURIに接続するためのドライバを返します。
     
    uri: 接続先アドレス
    
    返り値: Driver オブジェクト
    """
    return Driver()

def get_session(uri, options = {}):
    """指定されたURIに接続し、セッションを返します。
     
    uri: 接続先アドレス
    options: 接続オプション
    
    返り値: Session オブジェクト
    """
    return get_driver(uri).get_session(uri, options)
