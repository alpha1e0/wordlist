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
from script.libs.exploit import loadExpClass
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
            Output.red(error)
        except ExploitError as error:
            Output.red(error)
        except NotImplementError as error:
            Output.red(error)
        except ORMError as error:
            Output.red(error)
        except SearchEngineError as error:
            Output.red(error)
        except Exception as error:
            Output.red(u"未知错误, '{0}'".format(error))

    return _wrapper


@handleException
def doCMSIdentify(args):
    '''
    子命令，CMS类型识别
    '''
    if args.notfound:
        cms = CMSIdentify(args.url, notFoundPattern=args.notfound)
    else:
        cms = CMSIdentify(args.url)
    result = cms.identify()

    with Output(u"CMS识别") as out:
        if result[1]:
            out.raw(u"识别成功，目标站点 {0} 可能是 {1}".format(args.url, result[0]))
            out.red(u"详细结果：")
            for line in result[1]:
                out.raw("match path '{0}', pattern '{1}'".format(line[0], line[1]))
        else:
            out.raw(u"识别失败")


@handleException
def doGenPassword(args):
    '''
    子命令，密码生成
    '''
    pwgen = PasswdGenerator(fullname=args.fullname, nickname=args.nickname, englishname=args.englishname, \
        partnername=args.partnername, birthday=args.birthday, phone=args.phone, qq=args.qq, company=args.company, \
        domain=args.domain, oldpasswd=args.oldpasswd, keywords=args.keywords, keynumbers=args.keynumbers)
    wordlist = pwgen.generate()

    with Output(u"密码生成") as out:
        for line in wordlist:
            out.raw(line)

    if args.output:
        with open(args.output, 'w') as fd:
            for line in wordlist:
                fd.write(line + '\n')


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
    #encode = args.encode if args.encode else "utf-8"

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
                Output.red(u"URL格式错误")
                return False
            urls = [args.url]

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
                    out.raw(line)
    else:
        url = args.url if args.url else None
        bruter = URIBruter(types=types, keywords=keywords, exts=exts, size=size)
        result = bruter.genDict(url)

        with Output(u"URI爆破字典生成") as out:
            for line in result:
                out.raw(line)

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
            out.raw(line.strip())


@handleException
def doDecode(args):
    '''
    子命令，字符串解码
    '''
    code = Code(args.code)
    with Output(u"解码") as out:
        for line in code.decode(args.type, args.method):
            out.raw(line.strip())


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
            out.raw(u"编码：" + out.Y(str(result['encoding'])))
            out.raw(u"置信度：" + out.Y(str(result['confidence']*100)[:5] + "%"))
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
                out.raw(out.R(u"hash类型: ") + args.hash)
                out.raw(out.R(u"结果: ") + result)
            return True
    if args.hfile:
        if not args.dfile:
            Output.red(u"\n缺少参数 -d/--dfile")
            return False
        _file.hide(args.hfile, args.dfile)
        return True
    if args.list:
        with Output(u"文件编码转换支持的类型") as out:
            out.raw("\n".join(_file.convertType))
        return True


def execExploit(expFile, url, args):
    '''
    执行exploit
    Input:
        expFile: exploit的文件名
        args: 命令行参数
    '''
    try:
        expClass = loadExpClass(expFile)
    except ExploitError as error:
        with Output(u"Exploit操作") as out:
            out.red(u"加载exploit失败，reason: {0}".format(error))
        sys.exit(1)

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

    return (exploit.expName, result)


def parseSearchParam(param):
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
        Output.red(u"搜索参数错误，列必须为 '{0}' 中一个".format(columns))
        return (False, False)

    return (column, keyword)


@handleException
def doExploit(args):
    '''
    子命令，exploit模块
    '''
    # 创建exploit信息数据库
    if args.createdb:
        try:
            ExpModel.create()
        except DBError as error:
            with Output(u"Exploit信息管理") as out:
                out.red(u"创建数据库失败，reason: '{0}'".format(error))
        else:
            with Output(u"Exploit信息管理") as out:
                out.raw(u"创建数据库成功")
        return True

    # 注册register
    if args.register:
        path = os.path.split(args.register.rstrip("\\/"))[-1]
        if ".py" in path:
            path = os.path.join(sys.path[0],"exploit",path)
        else:
            path = os.path.join(sys.path[0],path)

        if not os.path.exists(path):
            with Output(u"Exploit信息管理") as out:
                out.red(u"路径'{0}'不存在".format(path))
            return False

        if os.path.isfile(path):
            try:
                expClass = loadExpClass(path)
            except ExploitError as error:
                with Output(u"Exploit信息管理") as out:
                    out.red(u"加载'{0}'失败，原因: {1}".format(path,str(error)))
                return False
            exploit = expClass()
            exploit.register()
            with Output(u"Exploit信息管理") as out:
                out.raw(u"'{0}'文件中的exploit注册成功".format(path))
            return True
        else:
            files = glob.glob(os.path.join(path,"*.py"))
            with Output(u"Exploit信息管理") as out:
                for f in files:
                    try:
                        expClass = loadExpClass(f)
                        exploit = expClass()
                        exploit.register()
                    except ExploitError as error:
                        continue
                    else:
                        out.raw(u"'{0}'文件中的exploit注册成功".format(f))
            return True

    # 更新exploit
    if args.update:
        try:
            expClass = loadExpClass(args.update)
        except ExploitError as error:
            with Output(u"Exploit信息管理") as out:
                out.red(u"加载exploit失败，reason: {0}".format(error))
            return False
        else:
            exploit = expClass()
            exploit.update()
            with Output(u"Exploit信息管理") as out:
                out.red(u"Exploit信息更新成功")
            return True

    # 删除exploit信息条目
    if args.delete:
        expName = args.delete.strip().decode(sys.stdout.encoding).encode("utf8")
        try:
            ExpModel.delete(expName)
        except DBError as error:
            with Output(u"Exploit信息管理") as out:
                out.red(u"删除exploit信息条目失败，reason: '{0}'".format(error))
        else:
            with Output(u"Exploit信息管理") as out:
                out.raw(u"删除exploit信息条目成功")
        return True

    # 列举所有exploit
    if args.list:
        exploits = ExpModel.gets('expName','expFile')
        with Output(u"Exploit信息管理") as out:
            for exp in exploits:
                out.raw(out.R("expName: ") + exp.expName)
                out.raw(out.R("expFile: ") + exp.expFile + "\n")
        return True

    # 搜索exploit
    if args.query:
        column, keyword = parseSearchParam(args.query)
        if not column: return False

        exploits = ExpModel.search(column, keyword)
        with Output(u"Exploit信息管理") as out:
            if exploits:
                out.green(u"关键词 '{0}' 在 '{1}' 列中搜索结果:\n".format(keyword,column))
                for exp in exploits:
                    out.raw(out.R("expName: ") + exp.expName)
                    out.raw(out.R("expFile: ") + exp.expFile + "\n")
            else:
                out.red(u"在 '{0}' 列中未搜索到包含关键词 '{1}' 的exploit".format(column,keyword))
        return True
    
    # 显示某个exploit的详细信息
    if args.detail:
        expName = args.detail.strip().decode(sys.stdout.encoding).encode("utf8")
        exp = ExpModel.get(expName)
        with Output(u"Exploit信息管理") as out:
            out.raw(str(exp))
        
    # Exploit执行
    if args.execute:
        if ".py" in args.execute:
            if not args.url:
                Output.red(u"\n缺少参数 -u/--url")
                return False

            if args.url.startswith("@"):
                try:
                    urls = open(args.url[1:],"r").readlines()
                except IOError as error:
                    with Output(u"Exploit执行") as out:
                        out.red(u"url文件打开失败，原因:'{0}'".format(str(error)))
                    return False
            else:
                urls = [args.url]

            with Output(u"Exploit执行") as out:
                for url in urls:
                    expName, result = execExploit(args.execute, url, args)
                    out.raw(out.R("Exploit: ") + expName)
                    out.raw(result)
                    out.raw("---------------------------------------------------------------------")

                return True
        else:
            if not args.url:
                Output.red(u"\n缺少参数 -u/--url")
                return False

            if args.url.startswith("@"):
                try:
                    urls = open(args.url[1:],"r").readlines()
                except IOError as error:
                    with Output(u"Exploit执行") as out:
                        out.red(u"url文件打开失败，原因:'{0}'".format(str(error)))
                    return False
            else:
                urls = [args.url]

            column, keyword = parseSearchParam(args.execute)
            if not column: return False

            exploits = ExpModel.search(column, keyword)
            with Output(u"Exploit执行") as out:
                if exploits:
                    for exp in exploits:
                        for url in urls:
                            expName, result = execExploit(exp.expFile, url, args)
                            if not expName: continue
                            out.raw(out.R("Exploit: ") + expName)
                            out.raw(result)
                            out.raw("---------------------------------------------------------------------")
                else:
                    out.red(u"在 '{0}' 列中未搜索到包含关键词 '{1}' 的exploit".format(column,keyword))
                    return False

            return True


@handleException
def doGoogleHacking(args):
    keywords = args.keywords.decode(sys.stdin.encoding)
    engineName = args.engine.lower().strip() if args.engine else "baidu"
    size = args.size if args.size else 200

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
                out.raw(out.R("Title: ") + item.title)
                out.raw(out.R("URL: ") + item.url + "\n")
            else:
                match = urlPattern.match(item.url)
                domain = match.groups()[0] if match else False
                if domain:
                    if domain not in domainSet:
                        domainSet.add(domain)
                        if outfile:
                            outfile.write(item.url+"\n")
                        out.raw(out.R("Title: ") + item.title)
                        out.raw(out.R("URL: ") + item.url + "\n")
                    else:
                        continue
                else:
                    if outfile:
                        outfile.write(item.url+"\n")
                    out.raw(out.R("Title: ") + item.title)
                    out.raw(out.R("URL: ") + item.url + "\n")


