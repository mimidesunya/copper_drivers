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
    def message_func(code, message, args):
        print("%X %s" % (code, message))
    session.set_message_func(message_func)
    
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
