#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
sys.path.append('../../code/')

import os
import os.path
from cti import *

# セッションの開始
session = get_session('ctip://localhost:8099/',{
    'user'  :'user',
    'password'  :'kappa'
})
try:
    # ファイル出力
    dir = 'out';
    if not os.path.exists(dir):
        os.mkdir(dir)
    session.set_output_as_file('out/server-resource.pdf')

    #リソースのアクセス許可
    session.property('input.include', 'http://copper-pdf.com/**')
      
    #文書の変換
    session.transcode_server('http://copper-pdf.com/');
finally:
    session.close()
