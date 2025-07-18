#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
sys.path.append('../../code/')

from cti import *

# セッションの開始
session = get_session('ctip://localhost:8099/',{
    'user'  :'user',
    'password'  :'kappa'
})
try:
    print(session.get_server_info('http://www.cssj.jp/ns/ctip/version'))
finally:
    session.close()
