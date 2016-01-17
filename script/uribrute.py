#!/usr/bin/env python
#coding: UTF-8

'''
Pentestdb, a database for penetration test.
Copyright (c) 2014-2015 alpha1e0
==================================================================================
URI 爆破.
爆破网站备份，配置文件备份, 后台路径以及其他敏感文件.
'''

import os
import json
import random
import time

import requests as http

from commons import Log, PenError


class URIBruter(object):
    '''
    URI bruteforce.
    Input:
        baseURL: base url
        stype: 服务器类型, 支持 asp/aspx/php/jsp. 如果为 'None', 使用所有类型.
        keywords: 指定关键字列表，关键字用于生成备份文件字典
        exts: 指定文件后缀列表，生成的字典文件会自动加入这些后缀
        notFoundPattern: 指定notFoundPattern，有时候website只返回301或200，这时候需要该字段来识别‘404’
    '''

    infoFile = os.path.join("directory","files.json")
    javaConsoleFile = os.path.join("directory","java-webconsole.json")

    def __init__(self, baseURL=None, stype=None, keywords=None, exts=None, notFoundPattern=None, safeURL=None, timeout=None, delay=None, encode="utf-8"):
        if baseURL:
            if not baseURL.startswith("http"):
                raise PenError("URIBruter, baseURL format error, not startswith 'http'.")
            self.baseURL = baseURL.rstrip("/")
        else:
            self.baseURL = baseURL
        self.stype = stype
        self.keywords = keywords.split() if keywords else []
        self.userdefinedExt = exts.split() if exts else []
        self.defaultExt = ["asp","aspx","php","jsp"]
        self.notFoundPattern = notFoundPattern
        self.safeURL = safeURL
        self.timeout = int(timeout) if timeout else 10
        self.delay = float(delay) if delay else 0
        self.encode = encode if encode else "utf-8"

        self.info = self._loadInfoDB()
        self.log = Log()


    def _genUserdefinedDict(self):
        suffixList = [u"web", u"www",u"webroot", u"wwwroot",u"backup", u"back",u"bak",u"backupdata",u"0", u"1",u"aaa", u"db", u"data", u"database", u"备份", u"网站备份"]

        result = []
        for suffix in suffixList:
            for keyword in self.keywords:
                result.append("".join([keyword,suffix]))
                result.append("-".join([keyword,suffix]))
                result.append("_".join([keyword,suffix]))

        return [unicode(x) for x in self.keywords] + result


    def _loadJavaConsole(self):
        result = []
        info = json.load(open(self.javaConsoleFile, "r"))
        for server, consoles in info.iteritems():
            for console in consoles:
                if console['type'] == "http":
                    result.append(console['url'])

        return result


    def _loadInfoDB(self):
        '''
        加载files.json数据文件，处理'<ext>'占位符，返回info字典
        '''
        result = {}
        info = json.load(open(self.infoFile, "r"))

        for key, value in info.iteritems():
            result[key] = []
            for line in value:
                if "<ext>" in line:
                    if not self.stype:
                        for ext in self.defaultExt+self.userdefinedExt:
                            result[key].append(line.replace("<ext>", ext))
                    else:
                        if self.stype in self.defaultExt:
                            result[key].append(line.replace("<ext>", self.stype))
                            for ext in self.userdefinedExt:
                                result[key].append(line.replace("<ext>", ext))
                else:
                    result[key].append(line)

        if self.keywords:
            result['webzip_file'] += self._genUserdefinedDict()

        return result


    def _dictIter(self):
        '''
        返回特定类型字典的生成器
        '''
        for zdir in [""]+self.info['webzip_dir']:
            for zfile in self.info['webzip_file']:
                for ext in self.info['webzip_ext']:
                    if zdir:
                        yield "/"+zdir+"/"+zfile+ext
                    else:
                        yield "/"+zfile+ext

        for bdir in [""]+self.info['backup_dir']:
            for bfile in self.info['backup_file']:
                for ext in self.info['backup_ext']:
                    if bdir:
                        yield "/"+bdir+"/"+bfile+ext
                    else:
                        yield "/"+bfile+ext

        for cdir in [""]+self.info['web_console_dir']:
            for cfile in self.info['web_console_file']:
                if cdir:
                    yield "/"+cdir+cfile
                else:
                    yield "/"+cfile

        if self.stype == "jsp":
            for line in self._loadJavaConsole():
                yield line

        for line in self.info['interesting_file']:
            yield "/"+line


    def genDict(self):
        '''
        生成特定类型的字典文件
        '''
        result = []
        for line in self._dictIter():
            result.append(line)

        return result


    def _safeRequest(self):
        if not self.safeURL:
            return

        url = random.choice(self.safeURL.split())
        try:
            response.get(url, timeout=self.timeout)
        except:
            pass


    def bruteforce(self):
        '''
        爆破
        '''
        if not self.baseURL:
            return False

        matchs = []
        for line in self._dictIter():
            time.sleep(self.delay)
            self._safeRequest()

            url = self.baseURL+line
            try:
                print ">>>>debug, request url", url.encode(self.encode), self.timeout, self.delay
                response = http.get(url.encode(self.encode), timeout=self.timeout)
            except:
                continue
            if response.status_code == 200:
                if self.notFoundPattern:
                    if self.notFoundPattern in response.content:
                        continue
                    if response.history:
                        if self.notFoundPattern in response.history[0].content:
                            continue
                else:
                    self.log.info("find available url '{0}'".format(url))
                    matchs.append(url)
            else:
                continue

        self.log.info("find result >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        if not matchs:
            self.log.info("find nothing")
        else:
            for line in matchs:
                self.log.info("find: '{0}'".format(line))
