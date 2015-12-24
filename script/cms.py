#!/usr/bin/env python
# coding: UTF-8

'''
Pentestdb, a database for penetration test.
Copyright (c) 2014-2015 alpha1e0
'''


import os
import json
import requests as http


class CMSIdentify(object):
    def __init__(self, baseURL, fingerprintFile=None, verbose=False):
        self.baseURL = baseURL.rstrip("/")
        self.verbose = verbose

        self.fpfile = fingerprintFile if fingerprintFile else os.path.join("script","cms_fingerprint.json")
        self.fp = json.load(open(self.fpfile, "r"))


    def checkPath(self, path):
        url = self.baseURL + path
        try:
            response = http.get(url)
        except http.exceptions.ConnectionError as error:
            if self.verbose: print "[!]: check '{0}' failed, connection failed".format(url)
            return False

        if response.status_code == 200:
            if self.verbose: print "[+]: check '{0}' success, status code 200.".format(url)
            return True
        else:
            if self.verbose: print "[+]: check '{0}' failed, status code {1}".format(url, response.status_code)
            return False


    def checkCMS(self, cmstype, cmsfp):
        pass


    def identify(self):
        for key,value in self.fp.iteritems():
            if self.checkCMS(key, value)
        else:
            print "[-]: CMS identify failed!"