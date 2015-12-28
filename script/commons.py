#!/usr/local/env python
#coding: UTF-8

'''
Pentestdb, a database for penetration test.
Copyright (c) 2014-2015 alpha1e0
'''


import os
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
        pos = self.dbfile.find(".")
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
    critical, error, warning, info, debug, notset
    '''
    def __new__(cls, logname=None):            
        if not logname:
            log = logging.getLogger('pen')
            log.setLevel(logging.DEBUG)

            streamHD = logging.StreamHandler()
            streamHD.setLevel(logging.DEBUG)
            formatter = logging.Formatter('[%(levelname)s] %(message)s')
            streamHD.setFormatter(formatter)

            log.addHandler(streamHD)
        else:
            logFilePath = os.path.join("script","log")
            if not os.path.exists(logFilePath):
                os.mkdir(logFilePath)

            logFileName = os.path.join(logFilePath, '{0}.log'.format(logname))
            if not os.path.exists(logFileName):
                with open(logFileName,"w") as fd:
                    fd.write("{0} log start----------------\r\n".format(logname))

            log = logging.getLogger(logname)
            log.setLevel(logging.DEBUG)

            fileHD = logging.FileHandler(logFileName)
            fileHD.setLevel(logging.DEBUG)
            formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
            fileHD.setFormatter(formatter)

            log.addHandler(fileHD)

        return log