#!/usr/bin/env python
# coding: UTF-8

'''
Pentestdb, a database for penetration test.
Copyright (c) 2014-2015 alpha1e0
========================================================
CMS 识别
'''


import os
import json
import requests as http

from commons import Log, PenError

class CMSIdentify(object):
    '''
    Identify the CMS type.
    Input:
        baseURL: base url to test.
        notFoundPattern: 指定notFoundPattern，有时候website只返回301或200，这时候需要该字段来识别‘404’
    '''

    fingerprintFile = os.path.join("directory","cms","cms_fingerprint.json")

    def __init__(self, baseURL, notFoundPattern=None):
        if not baseURL.startswith("http"):
            raise PenError("CMSIdentify, baseURL format error, not startswith 'http'.")
        self.baseURL = baseURL.rstrip("/")
        self.notFoundPattern = notFoundPattern

        self.fp = json.load(open(self.fingerprintFile, "r"))

        self.log = Log()


    def checkPath(self, path, pattern):
        url = self.baseURL + path
        try:
            response = http.get(url)
        except http.exceptions.ConnectionError as error:
            self.log.debug("check '{0}' failed, connection failed".format(url))
            return False

        #import pdb
        #pdb.set_trace()
        if response.status_code == 200:
            if self.notFoundPattern:
                if self.notFoundPattern in response.content:
                    self.log.debug("check '{0}' failed, notFoundPattern matchs.".format(url))
                    return False
                if response.history:
                    if self.notFoundPattern in response.history[0].content:
                        self.log.debug("check '{0}' failed, notFoundPattern matchs.".format(url))
                        return False
            if not pattern:
                self.log.debug("[+]: check '{0}' success, status code 200.".format(url))
                return True
            else:
                if pattern in response.content:
                    self.log.debug("[+]: check '{0}' success, status code 200, match pattern {1}.".format(url,pattern))
                    return True
                else:
                    self.log.debug("check '{0}' failed, pattern not found.".format(url))
                    return False
        else:
            self.log.debug("check '{0}' failed, status code {1}".format(url, response.status_code))
            return False


    def checkCMS(self, cmstype, cmsfp):
        matchList = []
        for line in cmsfp:
            if line['need']:
                if not self.checkPath(line['path'], line['pattern']):
                    return False
            else:
                if self.checkPath(line['path'], line['pattern']):
                    matchList.append([line['path'], line['pattern']])

        return matchList if matchList else False



    def identify(self):
        for cmstype,cmsfp in self.fp.iteritems():
            self.log.info("check {0}".format(cmstype))
            match = self.checkCMS(cmstype, cmsfp)
            if match:
                self.log.info("site {0} maybe {1}".format(self.baseURL, cmstype))
                for line in match:
                    self.log.info("match path ==> {0}, pattern ==> {1}".format(line[0], line[1]))
                break
        else:
            print "[-]: CMS identify failed!"