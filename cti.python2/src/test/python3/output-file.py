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
    session.set_output_as_file('out/output-file.pdf')

    # リソースの送信
    out = session.resource('test.css')
    try:
        file = open('data/test.css', 'rb')
        try:
            out.write(file.read())
        finally:
            file.close()
    finally:
        out.close()
  
    # 文書の送信
    out = session.transcode()
    try:
        file = open('data/test.html', 'rb')
        try:
            out.write(file.read())
        finally:
            file.close()
    finally:
        out.close()
finally:
    session.close()
