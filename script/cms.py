#!/usr/bin/env python
# coding: UTF-8

'''
Pentestdb, a database for penetration test.
Copyright (c) 2014-2015 alpha1e0
========================================================
Identify CMS
'''


import os
import json
import requests as http


class CMSIdentify(object):
    '''
    Identify the CMS type.
    '''
    def __init__(self, baseURL, fingerprintFile=None):
        self.baseURL = baseURL.rstrip("/")

        self.fpfile = fingerprintFile if fingerprintFile else os.path.join("directory","cms","cms_fingerprint.json")
        self.fp = json.load(open(self.fpfile, "r"))


    def checkPath(self, path, pattern):
        url = self.baseURL + path
        try:
            response = http.get(url)
        except http.exceptions.ConnectionError as error:
            log.debug("check '{0}' failed, connection failed".format(url))
            return False

        if response.status_code == 200:
            if not pattern:
                log.debug("[+]: check '{0}' success, status code 200.".format(url))
                return True
            else:
                if pattern in response.content:
                    log.debug("[+]: check '{0}' success, status code 200, match pattern {1}.".format(url,pattern))
                    return True
                else:
                    log.debug("check '{0}' failed, status code {1}".format(url, response.status_code))
                    return False
        else:
            log.debug("check '{0}' failed, status code {1}".format(url, response.status_code))
            return False


    def checkCMS(self, cmstype, cmsfp):
        matchList = []
        for line in cmsfp:
            if line.need:
                if not checkCMS(line.path, line.pattern):
                    return False
            else:
                if checkCMS(line.path, line.pattern):
                    matchList.append([line.path, line.pattern])

        return matchList if matchList else False



    def identify(self):
        for key,value in self.fp.iteritems():
            match = self.checkCMS(key, value)
            if match:
                log.warning("site {0} maybe {1}".format(self.baseURL, key))
                for line in match:
                    log.warning("match path ==> {0}, pattern ==> {1}".format(line[0], line[1]))
        else:
            print "[-]: CMS identify failed!"