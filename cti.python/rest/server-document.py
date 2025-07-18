#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib

url = 'http://localhost:8097/transcode'
params = urllib.urlencode({'rest.user':'user',
                           'rest.password':'kappa',
                           'input.include':'http://copper-pdf.com/**',
                           'rest.mainURI':'http://copper-pdf.com/',
                           })
f = urllib.urlopen(url, params)
print f.read()
