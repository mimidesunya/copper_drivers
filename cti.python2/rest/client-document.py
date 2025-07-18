#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2

# multipart/form-dataの出力(boundaryは適当な文字列)
boundary = '3w48588hfwfdwed2332hdiuj2d3jiuhd32'
def multipart_formdata(form_dict):
    disposition = 'Content-Disposition: form-data; name="%s"'
    lines = []
    for k, v in form_dict.iteritems():
        lines.append('--' + boundary)
        lines.append(disposition % k)
        lines.append('')
        lines.append(v)
    lines.append('--' + boundary + '--')
    lines.append('')
    value = '\r\n'.join(lines)
    return value

# 変換対象のHTML
data = '''
<html>
<body>
PythonからCopper PDFを使う。
</body>
</html>
'''

# POSTの実行
params = {'rest.user':'user',
	'rest.password':'kappa',
	'rest.main':data}

url = 'http://localhost:8097/transcode'
req = urllib2.Request(url)
req.add_header('Content-Type',
               'multipart/form-data; boundary=' + boundary)
data = multipart_formdata(params)
f = urllib2.urlopen(req, data)

# 結果表示
print f.read()
