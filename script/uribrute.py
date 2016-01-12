#!/usr/local/env python
#coding: UTF-8

'''
Pentestdb, a database for penetration test.
Copyright (c) 2014-2015 alpha1e0
==================================================================================
URI bruteforce.
bruteforce backup files, configure files, consoles and other interesting files.
'''

import os
import json

import requests as http

from commons import Log, PenError


# 生成字典的时候，允许用户自定义keyword(例如domain)
class URIBruter(object):
    '''
    URI bruteforce.
    Input:
        baseURL: base url
        stype: specify the server type, support asp/aspx/php/jsp. when stype is 'None', user all server types.
        keywords: specify the keywords, the keyword will be used to generate website backup file wordlist.
        exts: specify the userdefined extention
        notFoundPattern: specify the notFoundPattern, some website always return 200, use this
            paramte to identify '404 message'
    '''

    infoFile = os.path.join("directory","files.json")
    javaConsoleFile = os.path.join("directory","java-webconsole.json")

    def __init__(self, baseURL=None, stype=None, keywords=None, exts=None, notFoundPattern=None):
        if not baseURL.startswith("http"):
            raise PenError("URIBruter, baseURL format error, not startswith 'http'.")
        self.baseURL = baseURL.rstrip("/")
        self.stype = stype
        self.keywords = keywords.split() if keywords else []
        self.userdefinedExt = exts.split() if exts else []
        self.defaultExt = ["asp","aspx","php","jsp"]
        self.info = self._loadInfoDB()

        self.log = Log()


    def _genUserdefinedDict(self):
        suffixList = [u"web", u"www",u"webroot", u"wwwroot",u"backup", u"back",u"bak",u"tmp",u"temp",u"backupdata",u"0", u"1",u"aaa", u"db", u"data", u"database", u"备份", u"网站备份"]

        result = []
        for suffix in suffixList:
            for keyword in self.keywords:
                result.append("".join([suffix,keyword]))
                result.append("-".join([suffix,keyword]))
                result.append("_".join([suffix,keyword]))

        return [unicode(x) for x in self.keywords] + result


    def _loadJavaConsole(self):
        result = []
        info = json.load(open(self.javaConsoleFile, "r"))
        for server, consoles in info.iteritems():
            for console in consoles:
                if console.type == "http":
                    result.append(console.url)

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

        if self.

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

        if self.keywords:
            for line in self._genUserdefinedDict():
                yield line

        for bdir in [""]+self.info['backup_dir']:
            for bfile in self.info['backup_file']:
                for ext in self.info['backup_ext']:
                    if bdir:
                        yield "/"+bdir+"/"+bfile+ext
                    else:
                        yield "/"+bfile+ext

        for line in self.info['interesting_file']:
            yield line

        for cdir in [""]+self.info['web_console_dir']:
            for cfile in self.info['web_console_file']:
                if cdir:
                    yield "/"+cdir+cfile
                else:
                    yield "/"+cfile

        if self.stype == "jsp":
            for line in self._loadJavaConsole():
                yield line


    def genDict(self):
        '''
        生成特定类型的字典文件
        '''
        result = []
        for line in self._dictIter():
            result.append(line)

        return result


    def bruteforce(self):
        '''
        爆破
        '''
        if not self.baseURL:
            return False
        for line in self._dictIter():
            url = self.baseURL+line
            try:
                response = http.get(url)
            except http.exceptions.ConnectionError as error:
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
            else:
                continue
