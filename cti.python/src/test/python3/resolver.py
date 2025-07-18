#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
sys.path.append('../../code/')

import os
import os.path
from cti import *
from cti.builder import *
from cti.results import *

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
    session.set_output_as_file('out/resolver.pdf')
    
    # リソースの送信
    def resolver(uri, r):
        if os.path.exists(uri):
            out = r.found()
            try:
                file = open(uri)
                try:
                    out.write(file.read())
                finally:
                    file.close()
            finally:
                out.close()
    session.set_resolver_func(resolver)
  
    # 文書の送信
    out = session.transcode('data/test.html')
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
