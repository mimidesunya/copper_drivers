#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
sys.path.append('../../code/')

import os
import os.path
import time
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
    session.set_output_as_file('out/input-stdout.pdf')

    print("変換開始")

    # 文書の送信
    sys.stdout = session.transcode()
    try:
        print("""
<html>
  <head>
    <title>Python Test</title>
  </head>
  <body>
<h1>Hello Python</h1>
<p>只今の時刻は: %s</p>
  </body>
</html>""" % time.strftime("%Y/%m/%d %H:%M:%S"))
    finally:
        sys.stdout.close()
    
    sys.stdout = sys.__stdout__
    print("おわり")
finally:
    session.close()
