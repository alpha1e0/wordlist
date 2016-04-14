#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
Pentestdb, a database for penetration test.
Copyright (c) 2014-2015 alpha1e0
'''


import sys
import argparse
import os
import glob
import re
import importlib
import inspect

from script.libs.commons import PenError
from script.libs.commons import WordList
from script.libs.commons import Log
from script.libs.commons import Output
from script.libs.cms import CMSIdentify
from script.libs.password import PasswdGenerator
from script.libs.uribrute import URIBruter
from script.libs.coder import Code
from script.libs.coder import File
from script.libs.exploit import Exploit
from script.libs.exploit import ExpModel
from script.libs.exploit import ExploitError
from script.libs.exploit import NotImplementError
from script.libs.orm import ORMError
from script.libs.orm import DBError
from script.libs.searchengine import Baidu
from script.libs.searchengine import Bing
from script.libs.searchengine import Google
from script.libs.searchengine import SearchEngineError



def handleException(func):
    def _wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PenError as error:
            Output.red(str(error))
        except ExploitError as error:
            Output.red(str(error))
        except NotImplementError as error:
            Output.red(str(error))
        except ORMError as error:
            Output.red(str(error))
        except SearchEngineError as error:
            Output.red(str(error))
        except Exception as error:
            Output.red(u"未知错误, '{0}'".format(error))

    return _wrapper



def _loadExpClass(expFile):
    '''
    根据文件加载Exploit类
    '''
    expFile = os.path.join(sys.path[0], "exploit", os.path.split(expFile)[-1])
    if not os.path.exists(expFile):
        raise ExploitError("can not find exploit file '{0}'".format(expFile))

    fileName = os.path.split(expFile)[-1]
    fileName = fileName.endswith(".pyc") and fileName[:-4] or fileName.endswith(".py") and fileName[:-3] or fileName
    expModuleName = ".".join(['exploit', fileName])

    module = importlib.import_module(expModuleName)

    for member in dir(module):
        expClass = getattr(module, member)
        if inspect.isclass(expClass):
            if issubclass(expClass, Exploit) and expClass.__name__ != 'Exploit':
                break
    else:
        raise ExploitError(u"can not find exploit defination in file '{0}'".format(expFile))

    return expClass


def _execExploit(expFile, url, args):
    '''
    执行exploit
    Input:
        expFile: exploit的文件名
        args: 命令行参数
    '''

    expClass = _loadExpClass(expFile)

    cookie = ""
    headers = dict()
    if args.cookie:
        cookie = args.cookie
    if args.referer:
        headers['Referer'] = args.referer
    if args.useragent:
        headers['User-Agent'] = args.useragent
    if args.header:
        for param in args.header.split("#"):
            paramSplited = param.strip().split("=")
            headers[paramSplited[0]] = paramSplited[1]

    elseArgs = dict()
    if args.elseargs:
        for param in args.elseargs.split("#"):
            paramSplited = param.strip().split("=")
            elseArgs[paramSplited[0]] = paramSplited[1]

    url = url.strip()
    if not url.startswith("http"):
        url = "http://" + url

    exploit = expClass(url, cookie, headers, elseArgs)
    if args.verify:
        result = exploit.execute("verify")
    elif args.attack:
        result = exploit.execute("attack")
    else:
        result = exploit.execute("verify")

    return result


def _parseExpSearchParam(param):
    '''
    搜索参数column:keyword处理
    '''
    columns = ['expName', 'os', 'webserver', 'language', 'appName']
    
    if ":" not in param:
        column = 'expName'
        keyword = param.strip().decode(sys.stdout.encoding)
    else:
        splited = param.split(":")
        column = splited[0].strip()
        keyword = splited[1].strip().decode(sys.stdout.encoding)

    if column not in columns:
        raise ExploitError("search param error, should be one of '{0}'".format(columns))

    return (column, keyword)


@handleException
def doExploit(args):
    '''
    子命令，exploit模块
    '''
    out = Output(u"Exploit验证系统", toFile=args.output)
    out.init()
    # 创建exploit信息数据库
    if args.createdb:
        try:
            ExpModel.create()
        except DBError as error:
            out.error(u"创建数据库失败，'{0}'".format(error))
        else:
            out.info(u"创建数据库成功")
        return True

    # 注册register
    if args.register:
        path = os.path.split(args.register.rstrip("\\/"))[-1]
        if ".py" in path:
            path = os.path.join(sys.path[0],"exploit",path)
        else:
            path = os.path.join(sys.path[0],path)

        if not os.path.exists(path):
            out.error(u"路径'{0}'不存在".format(path))
            return False

        if os.path.isfile(path):
            try:
                expClass = _loadExpClass(path)
            except ExploitError as error:
                out.error(u"加载'{0}'失败，'{1}'".format(path,str(error)))
                return False
            exploit = expClass()
            exploit.register()
            out.info(u"'{0}'文件中的exploit注册成功".format(path))
            return True
        else:
            files = glob.glob(os.path.join(path,"*.py"))
            for f in files:
                try:
                    expClass = _loadExpClass(f)
                    exploit = expClass()
                    exploit.register()
                except ExploitError as error:
                    continue
                else:
                    out.info(u"'{0}'文件中的exploit注册成功".format(f))
            return True

    # 更新exploit
    if args.update:
        try:
            expClass = _loadExpClass(args.update)
        except ExploitError as error:
            out.error(u"加载exploit失败，reason: {0}".format(error))
            return False
        else:
            exploit = expClass()
            exploit.update()
            out.info(u"Exploit信息更新成功")
            return True

    # 删除exploit信息条目
    if args.delete:
        expName = args.delete.strip().decode(sys.stdout.encoding).encode("utf8")
        try:
            ExpModel.delete(expName)
        except DBError as error:
            out.error(u"删除exploit信息条目失败，'{0}'".format(error))
        else:
            out.info(u"删除exploit信息条目成功")
        return True

    # 列举所有exploit
    if args.list:
        exploits = ExpModel.gets('expName','expFile')
        for exp in exploits:
            out.info(out.R(u"名称 : ") + exp.expName)
            out.info(out.R(u"文件 : ") + exp.expFile + "\n")
        return True

    # 搜索exploit
    if args.query:
        column, keyword = _parseExpSearchParam(args.query)
        if not column: return False

        exploits = ExpModel.search(column, keyword)
        if exploits:
            out.green(u"关键词 '{0}' 在 '{1}' 列中搜索结果:\n".format(keyword,column))
            for exp in exploits:
                out.info(out.R("expName: ") + exp.expName)
                out.info(out.R("expFile: ") + exp.expFile + "\n")
        else:
            out.red(u"在 '{0}' 列中未搜索到包含关键词 '{1}' 的exploit".format(column,keyword))
        return True
    
    # 显示某个exploit的详细信息
    if args.detail:
        expName = args.detail.strip().decode(sys.stdout.encoding).encode("utf8")
        exp = ExpModel.get(expName)
        out.info(str(exp))
        
    # Exploit执行
    if args.execute:
        if ".py" in args.execute:
            if not args.url:
                out.error(u"缺少参数 -u/--url")
                return False

            if args.url.startswith("@"):
                try:
                    urls = open(args.url[1:],"r").readlines()
                except IOError as error:
                    out.error(u"url文件打开失败，'{0}'".format(str(error)))
                    return False
            else:
                urls = [args.url]

            for url in urls:
                result = _execExploit(args.execute, url, args)
                out.info(result)

            return True
        else:
            if not args.url:
                out.error(u"缺少参数 -u/--url")
                return False

            if args.url.startswith("@"):
                try:
                    urls = open(args.url[1:],"r").readlines()
                except IOError as error:
                    out.error(u"url文件打开失败，原因:'{0}'".format(str(error)))
                    return False
            else:
                urls = [args.url]

            column, keyword = _parseExpSearchParam(args.execute)
            if not column: return False

            exploits = ExpModel.search(column, keyword)
            if exploits:
                for exp in exploits:
                    for url in urls:
                        result = _execExploit(exp.expFile, url, args)
                        out.info(result)
            else:
                out.red(u"在 '{0}' 列中未搜索到包含关键词 '{1}' 的exploit".format(column,keyword))
                return False

            return True

    out.close()


@handleException
def doCMSIdentify(args):
    '''
    子命令，CMS类型识别
    '''
    with Output(u"CMS识别") as out:
        if args.notfound:
            cms = CMSIdentify(args.url, notFoundPattern=args.notfound)
        else:
            cms = CMSIdentify(args.url)
        result = cms.identify()

    
        if result[1]:
            out.info(u"\n识别成功，目标站点 {0} 可能是:".format(args.url))
            out.red("{0}".format(result[0]))
        else:
            out.info(u"识别失败")



@handleException
def doGenPassword(args):
    '''
    子命令，密码生成
    '''
    pwgen = PasswdGenerator(fullname=args.fullname, nickname=args.nickname, englishname=args.englishname, \
        partnername=args.partnername, birthday=args.birthday, phone=args.phone, qq=args.qq, company=args.company, \
        domain=args.domain, oldpasswd=args.oldpasswd, keywords=args.keywords, keynumbers=args.keynumbers)
    wordlist = pwgen.generate()

    with Output(u"密码生成", args.output) as out:
        for line in wordlist:
            out.info(line)
            out.write(line)



@handleException
def doURIBrute(args):
    '''
    子命令，URI爆破
    '''
    types = args.types.split(",") if args.types else URIBruter.allowTypes
    keywords = args.keywords.split(",") if args.keywords else []
    exts = args.exts.split(",") if args.exts else []
    timeout = args.timeout if args.timeout else 10
    delay = args.delay if args.delay else 0
    size = args.size if args.size else "small"
    size = size if size in ['small','large'] else "small"

    if args.brute:
        if not args.url:
            Output.red("缺少URL参数")
            sys.exit(1)
        if args.url.startswith("@"):
            try:
                urls = open(args.url[1:],"r").readlines()
            except IOError as error:
                Output.red(u"URL文件打开失败")
                return False
        else:
            if not args.url.startswith("http"):
                url = "http://" + args.url.strip()
            else:
                url = args.url.strip()
            urls = [url]

        bruter = URIBruter(types=types, keywords=keywords, exts=exts, size=size)

        matchs = []
        for url in urls:
            matchs = matchs + bruter.bruteforce(url.strip(), args.notfound, args.safeurl, timeout, delay)   

        with Output(u"URI爆破字典生成") as out:
            if not matchs:
                out.red(u"未爆破到有效资源")
            else:
                out.red(u"爆破结果:")
                for line in matchs:
                    out.info(line)
    else:
        url = args.url if args.url else None
        bruter = URIBruter(types=types, keywords=keywords, exts=exts, size=size)
        result = bruter.genDict(url)

        with Output(u"URI爆破字典生成") as out:
            for line in result:
                out.info(line)

        if args.generate:
            with open(args.generate.strip(), 'w') as fd:
                for line in result:
                    fd.write(line + '\n')


@handleException
def doEncode(args):
    '''
    子命令，字符串编码
    '''
    code = Code(args.code)

    with Output(u"编码") as out:
        for line in code.encode(args.type, args.method):
            out.info(line.strip())


@handleException
def doDecode(args):
    '''
    子命令，字符串解码
    '''
    code = Code(args.code)
    with Output(u"解码") as out:
        for line in code.decode(args.type, args.method):
            out.info(line.strip())


@handleException
def doFileOp(args):
    '''
    子命令，文件处理
    '''
    _file = File(args.file, args.method)

    if args.detect:
        size = args.size if args.size else 2048
        result = _file.detect(size)
        with Output(u"文本文件编码推断") as out:
            out.info(u"编码：" + out.Y(str(result['encoding'])))
            out.info(u"置信度：" + out.Y(str(result['confidence']*100)[:5] + "%"))
        return True
    if args.convert:
        if not args.dtype:
            Output.red(u"\n缺少参数 --dtype")
            return False
        if not args.dfile:
            Output.red(u"\n缺少参数 -d/--dfile")
            return False
        _file.convert(args.dfile, args.dtype)
        return True
    if args.hash:
        if args.hash not in File.hashMethod:
            Output.red(u"hash类型'{0}'不支持，支持{1}".format(args.hash, "/".join(File.hashMethod)))
            return False
        else:
            result = _file.hash(args.hash)
            with Output(u"文件hash计算") as out:
                out.info(out.R(u"hash类型: ") + args.hash)
                out.info(out.R(u"结果: ") + result)
            return True
    if args.hfile:
        if not args.dfile:
            Output.red(u"\n缺少参数 -d/--dfile")
            return False
        _file.hide(args.hfile, args.dfile)
        return True
    if args.list:
        with Output(u"文件编码转换支持的类型") as out:
            out.info("\n".join(_file.convertType))
        return True



@handleException
def doGoogleHacking(args):
    keywords = args.keywords.decode(sys.stdin.encoding)
    engineName = args.engine.lower().strip() if args.engine else "baidu"
    size = args.size if args.size else 20

    if engineName == "baidu":
        engine = Baidu()
    elif engineName == "bing":
        engine = Bing()
    elif engineName == "google":
        engine = Google()
    else:
        Output.red(u"不支持 '{0}' 引擎，必须为baidu/bing/google其中之一".format(engineName))
        return False

    urlPattern = re.compile(r"^((?:http(?:s)?\://)?(?:[-0-9a-zA-Z_]+\.)+(?:[-0-9a-zA-Z_]+)(?:\:\d+)?).*")

    domainSet = set()

    try:
        outfile = open(args.output.strip(),"w") if args.output else None
    except IOError:
        Output.red(u"打开文件{0}失败".format(args.output.strip()))

    with Output("Google Hacking:") as out:
        for item in engine.search(keywords,size):
            if not args.unique:
                if outfile:
                    outfile.write(item.url+"\n")
                out.info(out.Y("{0:>6} : ".format("title")) + item.title)
                out.info(out.Y("{0:>6} : ".format("url")) + item.url + "\n")
            else:
                match = urlPattern.match(item.url)
                domain = match.groups()[0] if match else False
                if domain:
                    if domain not in domainSet:
                        domainSet.add(domain)
                        if outfile:
                            outfile.write(item.url+"\n")
                        out.info(out.Y("{0:>6} : ".format("title")) + item.title)
                        out.info(out.Y("{0:>6} : ".format("url")) + item.url + "\n")
                    else:
                        continue
                else:
                    if outfile:
                        outfile.write(item.url+"\n")
                    out.info(out.Y("{0:>6} : ".format("title")) + item.title)
                    out.info(out.Y("{0:>6} : ".format("url")) + item.url + "\n")


