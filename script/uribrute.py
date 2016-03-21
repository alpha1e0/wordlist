#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
Pentestdb, a database for penetration test.
Copyright (c) 2014-2015 alpha1e0
==================================================================================
URI 爆破.
爆破网站备份，配置文件备份, 后台路径以及其他敏感文件.
'''

import os
import sys
import json
import random
import time
import urlparse

import requests as http

from commons import Log, PenError


def getKeywordFromURL(url):
    parseResult = urlparse.urlparse(url)
    keyword = parseResult[1].split(".")[0]
    if not keyword.isdigit():
        return keyword
    else:
        return None


class URIBruter(object):
    '''
    URI bruteforce.
        allowTypes: 字典类型列表，["webbak","cfgbak","interestfile","webconsole"]
        keywords: 指定关键字列表，关键字用于生成备份文件字典
        exts: 指定文件后缀列表，生成的字典文件会自动加入这些后缀
    '''
    allowTypes = ["webbak","cfgbak","interestfile","webconsole"]

    dirInfoFile = os.path.join(sys.path[0],"directory","files.json")
    javaConsoleFile = os.path.join(sys.path[0],"directory","java-webconsole.json")

    def __init__(self, types, keywords=[], exts=[], size="small"):
        self.types = types

        self.keywords = keywords
        self.exts = exts if exts else ["php"]
        self.size = size

        self.dirInfo = self._loadDirInfo()
        self.log = Log("uribrute")


    # 根据用户指定关键字生成web_backup字典
    def _genKeywordWebbakDict(self, dirInfo=None):        
        dirInfo = dirInfo if dirInfo else self.dirInfo
        suffixList = dirInfo['web_bak_file']

        result = []
        for suffix in suffixList:
            for keyword in self.keywords:
                result.append("".join([keyword,suffix]))
                result.append("-".join([keyword,suffix]))
                result.append("_".join([keyword,suffix]))

        return [unicode(x) for x in self.keywords] + result


    def _loadJavaConsoleDict(self):
        result = []
        javaConsoleInfo = json.load(open(self.javaConsoleFile, "r"))
        for server, consoles in javaConsoleInfo.iteritems():
            for console in consoles:
                if console['type'] == "http":
                    if console['url'] != "/":
                        result.append(console['url'])

        return result


    def _loadDirInfo(self):
        '''
        加载files.json数据文件，处理'<ext>'占位符，返回dirInfo字典
        '''
        result = {}
        dirInfo = json.load(open(self.dirInfoFile, "r"))

        for key, value in dirInfo.iteritems():
            result[key] = []
            for line in value:
                if "<ext>" in line:
                    for ext in self.exts:
                        result[key].append(line.replace("<ext>", ext))
                else:
                    result[key].append(line)

        if self.keywords:
            result['web_bak_file'] += self._genKeywordWebbakDict(result)

        return result


    def _dictIter(self):
        '''
        返回特定类型字典的生成器
        '''
        if "webbak" in self.types:
            if self.size == "small":
                self.dirInfo['web_bak_dir'] = []
            for zdir in [""]+self.dirInfo['web_bak_dir']:
                for zfile in self.dirInfo['web_bak_file']:
                    for ext in self.dirInfo['web_bak_ext']:
                        if zdir:
                            yield "/"+zdir+"/"+zfile+ext
                        else:
                            yield "/"+zfile+ext

        if "cfgbak" in self.types:
            if self.size == "small":
                self.dirInfo['cfg_bak_dir'] = []
            for bdir in [""]+self.dirInfo['cfg_bak_dir']:
                for bfile in self.dirInfo['cfg_bak_file']:
                    for ext in self.dirInfo['cfg_bak_ext']:
                        if bdir:
                            yield "/"+bdir+"/"+bfile+ext
                        else:
                            yield "/"+bfile+ext

        if "webconsole" in self.types:
            for cdir in [""]+self.dirInfo['web_console_dir']:
                for cfile in self.dirInfo['web_console_file']:
                    if cdir:
                        yield "/"+cdir+cfile
                    else:
                        yield "/"+cfile

        if "interestfile" in self.types:
            for line in self.dirInfo['interest_file']:
                yield "/"+line

        if "jsp" in self.exts:
            for line in self._loadJavaConsoleDict():
                yield line




    def genDict(self):
        '''
        生成特定类型的字典文件
        '''
        result = []
        for line in self._dictIter():
            result.append(line)

        return result


    def _safeRequest(self, safeURL):
        if not safeURL:
            return

        #url = random.choice(safeURL.split())
        try:
            http.get(safeURL)
        except http.ConnectionError:
            pass


    def bruteforce(self, baseURL, notFoundPattern=None, safeURL=None, timeout=10, delay=0):
        '''
        爆破
        '''
        matchs = []
        
        for line in self._dictIter():
            time.sleep(delay)
            self._safeRequest(safeURL)

            url = baseURL + line
            try:
                self.log.debug(u"request url '{0}'".format(url))
                response = http.get(url, timeout=timeout)
            except http.ConnectionError:
                continue
            if response.status_code == 200:
                if notFoundPattern:
                    if notFoundPattern in response.content:
                        continue
                    if response.history:
                        if notFoundPattern in response.history[0].content:
                            continue
                else:
                    self.log.debug(u"find available url '{0}'".format(url))
                    matchs.append(url)
            else:
                continue

        return matchs
