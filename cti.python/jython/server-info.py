#!/usr/bin/jython
# -*- coding: utf-8 -*-
import sys
sys.path.append('cti-driver.jar');
from jp.cssj.driver.ctip import CTIPDriver
from java.net import URI
from java.util import HashMap
from org.python.core.util import FileUtil

driver = CTIPDriver()
params = HashMap()
params.put('user', 'user')
params.put('password', 'kappa')
uri = URI.create('ctip://localhost:8099/')
session = driver.getSession(uri, params)
try:
  #バージョン情報
  uri = URI.create('http://www.cssj.jp/ns/ctip/version')
  inp = FileUtil.wrap(session.getServerInfo(uri))
  print inp.read()
  inp.close()

  #サポートする出力形式
  uri = URI.create('http://www.cssj.jp/ns/ctip/output-types')
  inp = FileUtil.wrap(session.getServerInfo(uri))
  print inp.read()
  inp.close()
  
finally:
	# セッションの終了
	session.close()
