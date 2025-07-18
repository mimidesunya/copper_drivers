#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
sys.path.append('../../code/')

from cti import *
from cti.builder import *
from cti.results import *

# セッションの開始
session = get_session('ctip://localhost:8099/',{
    'user'  :'user',
    'password'  :'kappa'
})
try:
    # 出力しない
    session.set_results(SingleResult(NullBuilder()))
    
    # メッセージ
    def progress_func(length, read):
        print("%s %s" % (length if length is not None else "-", read if read is not None else "-"))
    session.set_progress_func(progress_func)

    #リソースのアクセス許可
    session.property('input.include', 'https://www.w3.org/**')
      
    #文書の送信
    session.transcode_server('https://www.w3.org/TR/xslt-10/');
finally:
    session.close()
