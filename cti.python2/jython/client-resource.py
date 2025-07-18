#!/usr/bin/jython
# -*- coding: utf-8 -*-
import sys
sys.path.append('cti-driver.jar');
from jp.cssj.cti2.helpers import CTIMessageHelper
from jp.cssj.cti2.helpers import CTISessionHelper
from jp.cssj.resolver.helpers import MetaSourceImpl
from jp.cssj.driver.ctip import CTIPDriver
from java.io import File
from java.net import URI
from java.lang import System
from java.util import HashMap
from org.python.core.util import FileUtil

driver = CTIPDriver()
params = HashMap()
params.put('user', 'user')
params.put('password', 'kappa')
uri = URI.create('ctip://localhost:8099/')
session = driver.getSession(uri, params)
try:
	# ファイル出力
	file = File('test.pdf')
	CTISessionHelper.setResultFile(session, file)
	
	# エラーメッセージを標準エラー出力に表示する
	mh = CTIMessageHelper.createStreamMessageHandler(System.err)
	session.setMessageHandler(mh)
	
	# サーバーへの出力を取得
	ms = MetaSourceImpl(URI.create('.'), 'text/html', 'UTF-8')
	out = FileUtil.wrap(session.transcode(ms))
	try:
		out.write('''
<html>
<body>
JythonからCopper PDFを使う。
</body>
</html>
		''')
	finally:
		# クローズを忘れないこと！
		out.close()
finally:
	# セッションの終了
	session.close()
