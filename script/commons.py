#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
Pentestdb, a database for penetration test.
Copyright (c) 2014-2015 alpha1e0
================================================================
Common functions.
'''


import os
import sys
import logging


class PenError(Exception):
    def __init__(self, errorMsg):
        self.errorMsg = errorMsg

    def __str__(self):
        return str(self.errorMsg)


class DictError(PenError):
    def __str__(self):
        return str(" ".join(["Dict error", self.errorMsg]))


def WordList(fileName):
    result = set()
    if os.path.exists(fileName):
        with open(fileName, "r") as fd:
            for line in fd:
                if line.strip() and not line.strip().startswith("/**"):
                    yield line.strip()


class Dict(dict):
    def __init__(self, **kwargs):
        super(Dict, self).__init__(**kwargs)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError("object dose not have attribute '{0}'".format(key))

    def __setattr__(self, key, value):
        self[key] = value


class Output(object):
    RED = '\033[31m'
    BLUE = '\033[34m'
    YELLOW = '\033[33m'
    GREEN = '\033[32m'
    EOF = '\033[0m'

    def __init__(self, title):
        self.title = title
        
    @classmethod
    def raw(cls, msg):
        print msg

    @classmethod
    def R(cls, msg):
        return cls.RED + msg + cls.EOF

    @classmethod
    def red(cls, msg):
        print cls.R(msg)

    @classmethod
    def B(cls, msg):
        return cls.BLUE + msg + cls.EOF

    @classmethod
    def blue(cls, msg):
        print cls.B(msg)

    @classmethod
    def Y(cls, msg):
        return cls.YELLOW + msg + cls.EOF

    @classmethod
    def yellow(cls, msg):
        print cls.Y(msg)

    @classmethod
    def G(cls, msg):
        return cls.GREEN + msg + cls.EOF

    @classmethod
    def green(cls, msg):
        print cls.G(msg)


    def __enter__(self):
        print self.Y(u"\n[+]: "+self.title)
        print self.R("======================================================================")
        return self

    def __exit__(self, *args):
        print self.R("======================================================================\n")


class Database(object):
    def __init__(self, dbfile):
        self.dbfile = dbfile
        self.list = []
        self._load()


    def _load(self):
        if not os.path.exists(self.dbfile):
            return
        try:
            with open(self.dbfile, "r") as fd:
                for line in fd:
                    if line:
                        splited = line.strip().split()
                        self.list.append([splited[0].strip(), int(splited[1])])
        except IOError as error:
            print "[!] load database file error, reason:", str(error)


    def dump(self):
        self.list.sort(key=lambda x: x[1], reverse=True)
        try:
            with open(self.dbfile, "w") as fd:
                for line in self.list:
                    fd.write("{0} {1}\n".format(line[0],line[1]))
        except IOError:
            raise DictError()


    def generate(self, count):
        pos = self.dbfile.rfind(".")
        prefix = self.dbfile[:pos] if pos!=-1 else self.dbfile
        wordlistFileName = prefix + "_top_" + str(count) + ".txt"

        fileLen = count if count<len(self.list) else len(self.list)
        with open(wordlistFileName, "w") as fd:
            for i in range(fileLen):
                fd.write(self.list[i][0]+"\n")


    def addWord(self, word):
        if not self.list:
            self.list.append([word, 1])
            return
        for line in self.list:
            if word == line[0]:
                line[1] += 1
                break
        else:
            self.list.append([word, 1])


    def addWordlist(self, dictFile):
        for line in WordList(dictFile):
            self.addWord(line.strip())


class Log(object):
    '''
    Log class, support:critical, error, warning, info, debug, notset
    input:
        logname: specify the logname
        toConsole: whether outputing to console
        toFile: whether to logging to file
    '''
    def __new__(cls, logname=None, toConsole=True, toFile="pen"):
        logname = logname if logname else "pen"

        #logging.basicConfig(datefmt="%Y-%m-%d %H:%M:%S")

        log = logging.getLogger(logname)
        log.setLevel(logging.DEBUG)

        if toConsole:
            streamHD = logging.StreamHandler()
            streamHD.setLevel(logging.DEBUG)
            formatter = logging.Formatter('[%(asctime)s] <%(levelname)s> %(message)s' ,datefmt="%Y-%m-%d %H:%M:%S")
            streamHD.setFormatter(formatter)
            log.addHandler(streamHD)

        if toFile:
            fileName = os.path.join(sys.path[0],"script","log",'{0}.log'.format(toFile))
            if not os.path.exists(fileName):
                try:
                    os.mkdir(os.path.join(sys.path[0],"script","log"))
                except WindowsError, OSError:
                    pass
                with open(fileName,"w") as fd:
                    fd.write("{0} log start----------------\r\n".format(toFile))
            fileHD = logging.FileHandler(fileName)
            fileHD.setLevel(logging.DEBUG)
            formatter = logging.Formatter('[%(asctime)s] <%(levelname)s> %(message)s' ,datefmt="%Y-%m-%d %H:%M:%S")
            fileHD.setFormatter(formatter)
            log.addHandler(fileHD)

        return log

