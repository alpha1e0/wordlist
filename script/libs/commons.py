#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
Pentestdb, a database for penetration test.
Copyright (c) 2014-2015 alpha1e0
'''


import os
import sys
import logging
import types
import re
import urlparse
import urllib

from lxml import etree
import thirdparty.yaml as yaml



class PenError(Exception):
    def __init__(self, errorMsg):
        self.errorMsg = errorMsg

    def __str__(self):
        #return self.errorMsg.encode(sys.stdout.encoding)
        return self.errorMsg



class DictError(PenError):
    def __str__(self):
        return str(" ".join(["Dict error", self.errorMsg]))



def exceptionHook(etype, evalue, trackback):
    if isinstance(evalue, KeyboardInterrupt):
        print "User force exit."
        exit()
    else:
        sys.__excepthook__(etype, evalue, trackback)



class WordList(object):
    def __init__(self, fileName):
        self.fileName = fileName
        try:
            self._file = open(fileName, 'r')
        except IOError:
            raise PenError("Loading wordlist file '{0}' failed".format(fileName))


    def __iter__(self):
        return self


    def next(self):
        line = self._file.readline()
        if line == '':
            self._file.close()
            raise StopIteration()
        else:
            line = line.strip()
            if not line.startswith("/**"):
                return line
            else:
                return self.next()



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



class YamlConf(object):
    def __new__(cls, path):
        try:
            _file = open(path,"r")
            result = yaml.load(_file)
        except IOError:
            raise PenError("Loading yaml file '{0}' failed, read file failed".format(path))
        except yaml.YAMLError as error:
            raise PenError("Loading yaml file '{0}' failed, yaml error, reason: '{1}'".format(path,str(error)))
        except Exception as error:
            raise PenError("Loading yaml file '{0}' failed, reason: {1}".format(path,str(error)))

        return result



class Output(object):
    '''
    Output类用于输出信息到控制台和文件
    '''
    _RED = '\033[31m'
    _BLUE = '\033[34m'
    _YELLOW = '\033[33m'
    _GREEN = '\033[32m'
    _EOF = '\033[0m'

    _WIDTH = 80
    _CHAR = "-"

    def __init__(self, title=None, tofile=None):
        self._title = title
        self._fileName = tofile
        self._file = self._openFile(tofile)


    def _openFile(self, filename):
        if filename:
            try:
                _file = open(filename, "w")
            except IOError:
                _file = None
                raise PenError("open output file '{0}' failed".format(filename))
        else:
            _file = None

        return _file


    def openFile(self, filename):
        self._fileName = filename
        self._file = self._openFile(filename)


    def init(self, title=None, tofile=None):
        if title: self._title = title
        if tofile: 
            self._fileName = tofile
            self._file = self._openFile(tofile)
        
        self.raw(self._banner())
        self.yellow(u"[{0}]".format(self._title))
        self.raw(self._CHAR * self._WIDTH)


    @classmethod
    def R(cls, msg):
        return cls._RED + msg + cls._EOF

    @classmethod
    def Y(cls, msg):
        return cls._YELLOW + msg + cls._EOF

    @classmethod
    def B(cls, msg):
        return cls._BLUE + msg + cls._EOF

    @classmethod
    def G(cls, msg):
        return cls._GREEN + msg + cls._EOF


    @classmethod
    def raw(cls, msg):
        try:
            print msg
        except UnicodeError:
            print '*'*len(msg)
    

    @classmethod
    def red(cls, msg):
        cls.raw(cls.R(msg))

    @classmethod
    def yellow(cls, msg):
        cls.raw(cls.Y(msg))

    @classmethod
    def blue(cls, msg):
        cls.raw(cls.B(msg))

    @classmethod
    def green(cls, msg):
        cls.raw(cls.G(msg))


    @classmethod
    def info(cls, msg):
        cls.raw(msg)

    @classmethod
    def error(cls, msg):
        cls.red(msg)

    @classmethod
    def warnning(cls, msg):
        cls.yellow(msg)


    def write(self, data):
        '''
        写入数据到文件
        '''
        if self._file:
            try:
                self._file.write(data)
                return True
            except IOError:
                raise PenError("write output file '{0}' failed".format(self._fileName))
        else:
            return False


    def writeLine(self, line, parser=None):
        '''
        写入一行数据到文件
        line: 待写入的数据
        parser: 处理待写入数据的回调函数
        '''
        if self._file:
            if parser and isinstance(parser, types.FunctionType):
                line = parser(line)
            try:
                self._file.write(line + "\n")
                return True
            except IOError:
                raise PenError("write output file '{0}' failed".format(self._fileName))
        else:
            return False



    def _banner(self):
        fmt = "|{0:^" + "{0}".format(self._WIDTH+7) + "}|"

        banner = "+" + self._CHAR * (self._WIDTH-2) + "+\n"
        banner = banner + fmt.format(self.Y("PentestDB.") + " Tools and Resources for Web Penetration Test.") + "\n"
        banner = banner + fmt.format(self.G("https://github.com/alpha1e0/pentestdb")) + "\n"
        banner = banner + "+" + self._CHAR * (self._WIDTH-2) + "+\n"

        return banner


    def close(self):
        self.raw(self._CHAR * self._WIDTH)
        if self._file:
            self._file.close()


    def __enter__(self):
        self.init()
        return self


    def __exit__(self, *args):
        self.close()
        


class Log(object):
    '''
    Log class, support:critical, error, warning, info, debug, notset
    input:
        logname: specify the logname
        toConsole: whether outputing to console
        tofile: whether to logging to file
    '''
    def __new__(cls, logname=None, toConsole=True, tofile="pen"):
        logname = logname if logname else "pen"

        log = logging.getLogger(logname)
        log.setLevel(logging.DEBUG)

        if toConsole:
            streamHD = logging.StreamHandler()
            streamHD.setLevel(logging.DEBUG)
            formatter = logging.Formatter('[%(asctime)s] <%(levelname)s> %(message)s' ,datefmt="%Y-%m-%d %H:%M:%S")
            streamHD.setFormatter(formatter)
            log.addHandler(streamHD)

        if tofile:
            fileName = os.path.join(sys.path[0],"script","log",'{0}.log'.format(tofile))
            try:
                if not os.path.exists(fileName):
                    with open(fileName,"w") as fd:
                        fd.write("{0} log start----------------\r\n".format(tofile))
            except IOError:
                raise PenError("Creating log file '{0}' failed".format(fileName))
            fileHD = logging.FileHandler(fileName)
            fileHD.setLevel(logging.DEBUG)
            formatter = logging.Formatter('[%(asctime)s] <%(levelname)s> %(message)s' ,datefmt="%Y-%m-%d %H:%M:%S")
            fileHD.setFormatter(formatter)
            log.addHandler(fileHD)

        return log



class URL(object):
    '''
    URL处理
    '''
    _urlPattern = re.compile(r"^((?:http(?:s)?\://)?(?:[-0-9a-zA-Z_]+\.)+(?:[-0-9a-zA-Z_]+)(?:\:\d+)?).*")

    @classmethod
    def check(cls, url):
        '''
        检查URL格式是否正确
        '''
        matchs = cls._urlPattern.match(url)
        if not matchs:
            return False
        else:
            return True


    @classmethod
    def _strUrlFromat(cls, url):
        if "://" not in url:
            url = "http://" + url

        if not cls.check(url):
            raise PenError("url format error")

        return url


    @classmethod
    def format(cls, url):
        '''
        格式化url，返回url/host/path/baseURL/params信息
        例如：http://www.aaa.com/path/index.php?a=1&b=2
            uri: http://www.aaa.com/path/index.php
            host: http://www.aaa.com
            path: /index.php
            baseURL: http://www.aaa.com/path/
            params: {'a': '1', 'b': '2'}
        '''
        url = cls._strUrlFromat(url)
        parsed = urlparse.urlparse(url)

        protocol = parsed[0]
        host = parsed[1]
        uri = parsed[0] + "://" + parsed[1] + parsed[2]
        path = parsed[2]

        if not path.endswith("/"):
            sp = path.split("/")
            baseURL = parsed[0] + "://" + parsed[1] + "/".join(sp[0:-1]) + "/"
        else:
            baseURL = uri

        params = dict()

        for param in parsed[4].split("&"):
            if not param:
                continue
            sp = param.split("=")
            try:
                params[sp[0]] = urllib.unquote(sp[1])
            except IndexError:
                params[sp[0]] = ""

        return Dict(protocol=protocol,uri=uri,host=host,path=path,baseURL=baseURL,params=params)


    @classmethod
    def getHost(cls, url):
        url = cls._strUrlFromat(url)
        parsed = urlparse.urlparse(url)

        return parsed[1]


    @classmethod
    def getURI(cls, url):
        url = cls._strUrlFromat(url)
        parsed = urlparse.urlparse(url)

        return parsed[0] + "://" + parsed[1] + parsed[2]


