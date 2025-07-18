# -*- coding: utf-8 -*-
"""
$Id: results.py 932 2013-05-31 05:28:13Z miyabe $
"""

import os
from .builder import *

class SingleResult:
    """単一の結果を得るためのオブジェクトです。
    """
    def __init__(self, builder, finish_func = None):
        """結果オブジェクトを作成します。
        
        builder: Builder オブジェクト
        finish_func: 結果が出力される直前に呼び出されるコールバック関数です。引数にハッシュ型として結果に関する情報が渡されます。
        ハッシュには'uri', 'mime_type', 'encoding', 'length'というキーでそれぞれURI, MIME型, 文字コード, 結果長さが格納されます。
        ただし、'encoding', 'length'は必ずしも提供されません。
        """
        self.builder = builder
        self.finish_func = finish_func
    
    def next_builder(self, opts = {}):
        if self.builder == None:
            return NullBuilder()
        if self.finish_func is not None:
            # バイト文字列をデコードしたoptsを作成
            decoded_opts = {}
            for key, value in opts.items():
                if isinstance(value, bytes):
                    decoded_opts[key] = value.decode('utf-8')
                else:
                    decoded_opts[key] = value
            self.finish_func(decoded_opts)
        builder = self.builder
        self.builder = None
        return builder

class DirectoryResults:
    """ディレクトリに複数のファイルとして結果を得るためのオブジェクトです。
    """
    def __init__(self, dir, prefix = '', suffix = ''):
        """結果オブジェクトを作成します。
        
        dir: 出力先ディレクトリ
        prefix: 結果ファイル名の先頭に付ける文字列
        suffix: 結果ファイル名の末尾に付ける文字列
        """
        self.counter = 0;
        self.dir = dir
        self.prefix = prefix
        self.suffix = suffix

    
    def next_builder(self, opts = {}):
        self.counter += 1
        filename = self.prefix + str(self.counter) + self.suffix
        filepath = os.path.join(self.dir, filename)
        return FileBuilder(filepath)
