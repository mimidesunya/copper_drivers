# -*- coding: utf-8 -*-
"""
$Id: builder.py 932 2013-05-31 05:28:13Z miyabe $
"""

import tempfile

"""メモリ上のフラグメントの最大サイズです。

フラグメントがこの大きさを超えるとディスクに書き込みます。
"""
FRG_MEM_SIZE = 256

"""メモリ上に置かれるデータの最大サイズです。

メモリ上のデータがこのサイズを超えると、
FRG_MEM_SIZEとは無関係にディスクに書き込まれます。
"""
ON_MEMORY = 1024 * 1024

"""一時ファイルのセグメントサイズです。
"""
SEGMENT_SIZE = 8192

class Fragment:
    def __init__(self, id):
        self.pref = None
        self.next = None
        self.length = 0
        self.buffer = ''
        self.segments = None
        self.id = id

    def write(self, tempFile, onMemory, segment, bytes):
        """フラグメントにデータを書き込みます。
        
        tempFile: 一時ファイル
        onMemory: メモリ上に置かれたデータの合計サイズ
        segment: セグメント番号シーケンス
        bytes: データ
        
        戻り値: 書き込んだバイト数
        """
        l = len(bytes)
        if (self.segments == None and
        self.length + l <= FRG_MEM_SIZE and
        onMemory + l <= ON_MEMORY):
            self.buffer += bytes
            onMemory += l
        else:
            if self.buffer:
                segment, wlen = self._raf_write(tempFile, segment, self.buffer)
                onMemory -= wlen
                self.buffer = None
            segment, l = self._raf_write(tempFile, segment, bytes)
        self.length += l
        return onMemory, segment, l

    def flush(self, tempFile, out):
        """フラグメントの内容を吐き出して、フラグメントを破棄します。
        
        tempFile: 一時ファイル
        out: 出力先ストリーム( IO )
        """
        if self.segments == None:
            out.write(self.buffer)
            self.buffer = None
        else:
            segcount = len(self.segments)
            for seg in self.segments:
                tempFile.seek(seg * SEGMENT_SIZE)
                buff = tempFile.read((seg == self.segments[-1] and self.segLen) or SEGMENT_SIZE)
                out.write(buff)

    def _raf_write(self, tempFile, segment, bytes):
        """ 一時ファイルに書き込みます。
        
        tempFile: 一時ファイル
        segment: セグメント番号シーケンス
        bytes: データ
        
        戻り値: 書き込んだバイト数
        """
        if self.segments == None:
            self.segments = [segment]
            segment += 1
            self.segLen = 0
        written = 0
        while len(bytes) > 0:
            l = len(bytes)
            if self.segLen == SEGMENT_SIZE:
                self.segments.append(segment)
                segment += 1
                self.segLen = 0
            seg = self.segments[-1]
            wlen = min(l, SEGMENT_SIZE - self.segLen)
            wpos = seg * SEGMENT_SIZE + self.segLen
            tempFile.seek(wpos)
            data = bytes[0:wlen]
            bytes = bytes[wlen:]
            tempFile.write(data)
            self.segLen += wlen
            written += wlen
        return segment, written
    
class StreamBuilder:
    """ストリームに対して結果を構築するオブジェクトです。
    """
    def __init__(self, out, finish_func = None):
        """結果構築オブジェクトを作成します。
        
        out: 出力先ストリーム
        finish_func: 結果を実際に出力する前に呼び出されるコールバック関数。引数として結果のバイト数が渡されます
        
        例:
        def content_type(opts):
            print "Content-Type: "+opts['mime_type']
        def content_length(length):
            print "Content-Length: "+str(length)
            print
        results = SingleResult(StreamBuilder(sys.stdout, content_length), content_type)
        """
        self.frgs = []
        self.first = None
        self.last = None
        self.onMemory = 0
        self.length = 0
        self.segment = 0
        self.tempFile = tempfile.TemporaryFile()
        self.out = out
        self.finish_func = finish_func

    def add_block(self):
        id = len(self.frgs)
        frg = Fragment(id)
        self.frgs.append(frg)
        if self.first == None:
            self.first = frg
        else:
            self.last.next = frg
            frg.prev = self.last
        self.last = frg
    
    def insert_block_before(self, anchor_id):
        id = len(self.frgs)
        anchor = self.frgs[anchor_id]
        frg = Fragment(id)
        self.frgs.append(frg)
        frg.prev = anchor.prev
        frg.next = anchor
        anchor.prev.next = frg
        anchor.prev = frg
        if self.first.id == anchor.id:
            self.first = frg
    
    def block_write(self, id, data):
        frg = self.frgs[id]
        self.onMemory, self.segment, l = frg.write(self.tempFile, self.onMemory, self.segment, data)
        self.length += l
    
    def close_block(self, id):
        pass
    
    def serial_write(self, data):
        self.out.write(data)
    
    def finish(self):
        try:
            if self.finish_func is not None:
                self.finish_func(self.length) 
            frg = self.first
            while frg:
                frg.flush(self.tempFile, self.out)
                frg = frg.next
        finally:
            self.tempFile.close
    
    def dispose(self):
        pass

class FileBuilder(StreamBuilder):
    """ファイルに対して結果を構築するオブジェクトです。
    """
    def __init__(self, file):
        """
        結果構築オブジェクトを作成します。
        
        file: 結果ファイル
        """
        StreamBuilder.__init__(self, None)
        self.file = file

    def serial_write(self, data):
        if self.out == None:
            self.out = open(self.file, 'w')
        self.out.write(data)
 
    def finish(self):
        if self.out == None:
            self.out = open(self.file, 'w')
            StreamBuilder.finish(self)
        self.out.close()
        self.out = None
        
class NullBuilder:
    """このオブジェクトは結果を構築しません。
    """
    def add_block(self):
        pass
    
    def insert_block_before(self, anchor_id):
        pass
    
    def block_write(self, id, data):
        pass
    
    def close_block(self, id):
        pass
    
    def serial_write(self, data):
        pass
    
    def finish(self):
        pass
    
    def dispose(self):
        pass
