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

import requests


# 生成字典的时候，允许用户自定义keyword(例如domain)
class URIBruter(object):
    infoFile = os.path.join("directory","files.json")
    javaConsoleFile = os.path.join("directory","java-webconsole.json")
    '''
    URI bruteforce.
    Input:
        stype: specify the server type, support asp/aspx/php/jsp. when stype is 'None', user all server types.
    '''
    def __init__(self, stype=None, keywords=None, ext=None):
        self.stype = stype
        self.userdefinedExt = ext.split() if ext else []
        self.defaultExt = ["asp","aspx","php","jsp"]
        self.info = self._loadInfoDB()


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
                        if self.stype == "jsp":
                            result[key] += self._loadJavaConsole()
                else:
                    result[key].append(line)

        return result


    def _dictIter(self):
        '''
        返回特定类型字典的生成器
        '''
        for zdir in [""]+self.info.webzip_dir:
            for file in self.info.webzip_file:
                for ext in self.info.webzip_ext:
                    yield zdir+"/"+file+ext

    def genDict(self):
        '''
        生成特定类型的字典文件
        '''
        pass


    def bruteforce(self):
        '''
        爆破
        '''
        pass