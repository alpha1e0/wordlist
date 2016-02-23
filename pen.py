#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
Pentestdb, a database for penetration test.
Copyright (c) 2014-2015 alpha1e0
'''


import sys
import argparse
import os
import poplib
import signal
import glob
import re

from script.commons import Database, PenError, DictError, WordList, Log, Output
from script.mail import getMailServers, checkMail
from script.cms import CMSIdentify
from script.password import PasswdGenerator
from script.uribrute import URIBruter
from script.coder import Code, File
from script.exploit import Exploit, ExpInfo, ExploitError, loadExpClass
from script.orm import DBError
from script.searchengine import Baidu, Bing, Google


reload(sys)
sys.setdefaultencoding("utf8")


#================================sub commands=====================================

def doDictParse(args):
    '''
    子命令，字典处理
    '''
    db = Database(args.database)

    if args.generate:
        db.generate(args.generate)
        with Output(u"字典处理") as out:
            out.yellow(u"字典生成成功")
    elif args.wordlist:
        db.addWordlist(args.wordlist)
        db.dump()
        with Output(u"字典处理") as out:
            out.yellow(u"字典数据库更新成功")


def doMailChecks(args):
    '''
    子命令，mail账户批量验证
    '''
    log = Log()
    mailServers = getMailServers(os.path.join(sys.path[0],"else","mail_server.json"))

    result = []
    for line in WordList(args.file):
        info = line.split()
        if len(info) < 2:
            continue
        user = info[0].strip()
        passwd = info[2].strip() if len(info)==3 else info[1].strip()

        serverStr = user.split("@")[1].strip()
        serverInfo = mailServers.get(serverStr, None)
        server = args.server if args.server else serverInfo['server']
        if not server:
            continue
        port = args.port if args.port else serverInfo.get('port',None)

        log.debug("checking '{0}' '{1}' '{2}'".format(user, passwd, server))
        if checkMail(server, user, passwd, port=port):
            log.debug("success, user is {0}, password is {1}".format(user,passwd))
            result.append((user,passwd))

    with Output(u"Mail账户验证") as out:
        if result:
            out.raw(u"以下账户通过验证:")
            for line in result:
                out.raw("{0} {1}".format(line[0],line[1]))
        else:
            out.red("验证失败")


def doMailBrute(args):
    '''
    子命令，mail账户爆破
    '''
    log = Log('mailbrute')
    mailServers = getMailServers(os.path.join(sys.path[0],"else","mail_server.json"))

    users = WordList(args.user[1:]) if args.user.startswith("@") else [args.user]
    passwords = WordList(args.passwd[1:]) if args.passwd.startswith("@") else [args.passwd]

    result = []
    for user in users:
        for password in passwords:
            server = user.split("@")[1].strip()
            server = mailServers.get(server, None)
            ssl = mailServers.get('ssl', False)
            port = server.get('port',None)
            if not server:
                continue

            log.debug("checking '{0}' '{1}' '{2}'".format(user, passwd, server['server']))
            
            if checkMail(server['server'], user, passwd, ssl=ssl, port=port):
                log.debug("success, user is {0}, password is {1}".format(user,passwd))
                result.append((user,passwd))

    with Output(u"Mail账户爆破") as out:
        if result:
            out.raw("成功爆破以下账户:")
            for line in result:
                out.raw("{0} {1}".format(line[0],line[1]))
        else:
            out.raw(u"爆破失败")


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
            out.raw("识别失败")


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


def doURIBrute(args):
    '''
    子命令，URI爆破
    '''
    if args.generate:
        bruter = URIBruter(stype=args.type, keywords=args.keywords, exts=args.ext)
        result = bruter.genDict()

        with Output(u"URI爆破字典生成") as out:
            for line in result:
                out.raw(line)

        if args.output:
            with open(args.output, 'w') as fd:
                for line in result:
                    fd.write(line + '\n')
    else:
        bruter = URIBruter(baseURL=args.url ,stype=args.type, keywords=args.keywords, exts=args.ext, \
            notFoundPattern=args.notfound, safeURL=args.safeurl, timeout=args.timeout, delay=args.delay, encode=args.encode)
        matchs = bruter.bruteforce()

        with Output(u"URI爆破字典生成") as out:
            if not matchs:
                out.red(u"未爆破到有效资源")
            else:
                for line in matchs:
                    out.raw("find alive uri '{0}'".format(line))


def doEncode(args):
    '''
    子命令，字符串编码
    '''
    code = Code(args.code)

    with Output(u"编码") as out:
        for line in code.encode(args.type, args.method):
            out.raw(line.strip())


def doDecode(args):
    '''
    子命令，字符串解码
    '''
    code = Code(args.code)
    with Output(u"解码") as out:
        for line in code.decode(args.type, args.method):
            out.raw(line.strip())


def doFileOp(args):
    '''
    子命令，文件处理
    '''
    _file = File(args.file, args.method)

    if args.detect:
        size = args.size if args.size else 2048
        result = _file.detect(size)
        with Output(u"文本文件编码推断") as out:
            out.raw(u"编码：" + out.Y(result['encoding']))
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

    headers = dict()
    if args.cookie:
        headers['Cookie'] = args.cookie
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

    exploit = expClass(url, headers, elseArgs)
    if args.verify:
        result = exploit.verify()
    elif args.attack:
        result = exploit.attack()
    else:
        result = exploit.verify()

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


def doExploit(args):
    '''
    子命令，exploit模块
    '''
    # 创建exploit信息数据库
    if args.createdb:
        try:
            ExpInfo.create()
        except DBError as error:
            with Output(u"Exploit信息管理") as out:
                out.red(u"创建数据库失败，reason: '{0}'".format(error))
        else:
            with Output(u"Exploit信息管理") as out:
                out.raw(u"创建数据库成功")
        return True

    # 注册register
    if args.register:
        path = os.path.split(args.register)[-1]
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
            ExpInfo.delete(expName)
        except DBError as error:
            with Output(u"Exploit信息管理") as out:
                out.red(u"删除exploit信息条目失败，reason: '{0}'".format(error))
        else:
            with Output(u"Exploit信息管理") as out:
                out.raw(u"删除exploit信息条目成功")
        return True

    # 列举所有exploit
    if args.list:
        exploits = ExpInfo.gets('expName','expFile')
        with Output(u"Exploit信息管理") as out:
            for exp in exploits:
                out.raw(out.R("expName: ") + exp.expName)
                out.raw(out.R("expFile: ") + exp.expFile + "\n")
        return True

    # 搜索exploit
    if args.query:
        column, keyword = parseSearchParam(args.query)
        if not column: return False

        exploits = ExpInfo.search(column, keyword)
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
        exp = ExpInfo.get(expName)
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
                        out.red("url文件打开失败，原因:'{0}'".format(str(error)))
                    return False
            else:
                urls = [args.url]

            with Output(u"Exploit执行") as out:
                for url in urls:
                    expName, result = execExploit(args.execute, url, args)
                    out.raw(out.R("Exploit: ") + expName)
                    out.raw(out.R("Target:  ") + url.strip() + "\n")
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
                        out.red("url文件打开失败，原因:'{0}'".format(str(error)))
                    return False
            else:
                urls = [args.url]

            column, keyword = parseSearchParam(args.execute)
            if not column: return False

            exploits = ExpInfo.search(column, keyword)
            with Output(u"Exploit执行") as out:
                if exploits:
                    for exp in exploits:
                        for url in urls:
                            expName, result = execExploit(exp.expFile, url, args)
                            if not expName: continue
                            out.raw(out.R("Exploit: ") + expName)
                            out.raw(out.R("Target:  ") + url.strip() + "\n")
                            out.raw(result)
                            out.raw("---------------------------------------------------------------------")
                else:
                    out.red(u"在 '{0}' 列中未搜索到包含关键词 '{1}' 的exploit".format(column,keyword))
                    return False

            return True


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
    urls = list()
    with Output("Google Hacking:") as out:
        for item in engine.search(keywords,size):
            if not args.unique:
                out.raw(out.R("Title: ") + item.title)
                out.raw(out.R("URL: ") + item.url + "\n")
                urls.append(item.url)
            else:
                match = urlPattern.match(item.url)
                domain = match.groups()[0] if match else False
                if domain:
                    if domain not in domainSet:
                        domainSet.add(domain)
                        urls.append(item.url)
                        out.raw(out.R("Title: ") + item.title)
                        out.raw(out.R("URL: ") + item.url + "\n")
                    else:
                        continue
                else:
                    urls.append(item.url)
                    out.raw(out.R("Title: ") + item.title)
                    out.raw(out.R("URL: ") + item.url + "\n")

    if args.output:
        with open(args.output.strip(),"w") as fd:
            for url in urls:
                fd.write(url + "\n")


#=====================================main================================================

def exceptionHook(etype, evalue, trackback):
    if isinstance(evalue, KeyboardInterrupt):
        print "User force exit."
        exit()
    else:
        sys.__excepthook__(etype, evalue, trackback)


if __name__ == "__main__":
    sys.excepthook = exceptionHook

    parser = argparse.ArgumentParser(description=u"渗透测试辅助工具")
    subparser = parser.add_subparsers(title=u"子命令", description=u"使用子命令")

    # cms identify
    cms = subparser.add_parser("cms", help=u"CMS 识别")
    cms.add_argument("url", help=u"指定目的URL")
    cms.add_argument("--notfound", help=u"自定义notfound页面关键字")
    cms.set_defaults(func=doCMSIdentify)

    # password generate
    passwdgen = subparser.add_parser("passwdgen", help=u"密码生成器")
    passwdgen.add_argument("--fullname", help=u"指定姓名汉语拼音全拼, 例如: 'zhang san' 'lin zhi ling'")
    passwdgen.add_argument("--nickname", help=u"指定昵称")
    passwdgen.add_argument("--englishname", help=u"指定英文名，例如: 'alice' 'tom'")
    passwdgen.add_argument("--partnername", help=u"指定爱人姓名汉语拼音全拼")
    passwdgen.add_argument("--birthday", help=u"指定生日, 格式: '2000-1-10'")
    passwdgen.add_argument("--phone", help=u"指定手机号")
    passwdgen.add_argument("--qq", help=u"指定QQ号")
    passwdgen.add_argument("--company", help=u"指定公司名")
    passwdgen.add_argument("--domain", help=u"指定域名")
    passwdgen.add_argument("--oldpasswd", help=u"指定老密码")
    passwdgen.add_argument("--keywords", help=u"指定关键字列表, 例如: 'keyword1 keyword2'")
    passwdgen.add_argument("--keynumbers", help=u"指定关键数字, 例如: '123 789'")
    passwdgen.add_argument("-o","--output", help=u"指定输出文件")
    passwdgen.set_defaults(func=doGenPassword)

    # uri bruteforce
    uribrute = subparser.add_parser("uribrute", help=u"URI爆破字典")
    uribrute.add_argument("-u", "--url", help=u"指定目的URL")
    uribrute.add_argument("--type", help=u"指定server类型，支持：asp/aspx/php/jsp")
    uribrute.add_argument("--keywords", help=u"自定义关键字，用于生成备份文件爆破字典")
    uribrute.add_argument("--ext", help=u"自定义后缀名，例如：php7")
    uribrute.add_argument("--notfound", help=u"自定义notfound页面关键字")
    uribrute.add_argument("--safeurl", help=u"自定义安全URL，用于bypass安全软件")
    uribrute.add_argument("-g","--generate", help=u"生成字典", action="store_true")
    uribrute.add_argument("--timeout", help=u"指定http请求超时事件, 默认为 10", type=int)
    uribrute.add_argument("--delay", help=u"指定http请求间隔时间, 默认无间隔", type=float)
    uribrute.add_argument("--encode", help=u"指定url非ASCII编码方式, 默认为UTF-8")
    uribrute.add_argument("-o","--output", help=u"指定输出文件")
    uribrute.set_defaults(func=doURIBrute)

    # exploit
    exploit = subparser.add_parser("exploit", help=u"exploit执行")
    # exploit 管理
    expManage = exploit.add_argument_group(u'exploit管理')
    expManage.add_argument("--createdb", action="store_true", help=u"创建exploit信息数据库")
    expManage.add_argument("--register", help=u"指定exploit目录或exploit文件注册exploit信息")
    expManage.add_argument("--update", help=u"根据exploit文件更新exploit注册信息")
    expManage.add_argument("--delete", help=u"根据exploit名字删除exploit注册信息")
    expManage.add_argument("-q", "--query", help=u"搜索exploit，参数格式column:keyword，column支持expName/os/webserver/language/appName，默认为expName")
    expManage.add_argument("-l", "--list", action="store_true", help=u"列举所有exploit")
    expManage.add_argument("--detail", help=u"根据exploit名称显示某个exploit的详细信息")
    # exploit 执行
    expExec = exploit.add_argument_group(u'exploit执行')
    expExec.add_argument("-e","--execute", help=u"exploit执行，参数格式column:keyword，column支持expName/os/webserver/language/appName，默认为expName")
    expExec.add_argument("-u", "--url", help=u"指定目标URL，使用@file指定url列表文件")
    expExec.add_argument("--verify", action="store_true", help=u"验证模式")
    expExec.add_argument("--attack", action="store_true", help=u"攻击模式")
    expExec.add_argument("--cookie", help=u"指定Cookie")
    expExec.add_argument("--useragent", help=u"指定UserAgent")
    expExec.add_argument("--referer", help=u"指定referer")
    expExec.add_argument("--header", help=u"指定其他HTTP header,例如--header 'xxx=xxxx#yyy=yyyy'")
    expExec.add_argument("--elseargs", help=u"指定其他参数,例如--elseargs 'xxx=xxxx#yyy=yyyy'")
    expManage.set_defaults(func=doExploit)

    # encode
    encode = subparser.add_parser("encode", help=u"编码工具", \
        description=u"编码工具，支持的编码种类有:{0}".format(" ".join(Code.encodeTypes)))
    encode.add_argument("code", help=u"待编码字符串，建议用引号包括")
    encode.add_argument("-t", "--type", help=u"指定编码种类")
    encode.add_argument("-m", "--method", help=u"指定非ASCII字符编码方式，例如：utf8、gbk")
    encode.set_defaults(func=doEncode)

    # decode
    decode = subparser.add_parser("decode", help=u"解码工具", \
        description=u"解码工具，支持的解码种类有: {0}，其中html不能和其他编码混合".format(" ".join(Code.decodeTypes)), \
        epilog="示例:\n  pen.py decode -m utf8 target\\x3Fid\\x3D\\xC4\\xE3\\xBA\\xC3\n  pen.py decode -t decimal '116 97 114 103 101 116 63 105 100 61 196 227 186 195'", \
        formatter_class=argparse.RawDescriptionHelpFormatter)
    decode.add_argument("code", default="hello", help=u"解码字符串，例如：ASCII、URL编码，\\xaa\\xbb、0xaa0xbb、\\uxxxx\\uyyyy、混合编码")
    decode.add_argument("-t", "--type", help=u"指定解码种类，建议用引号包括")
    decode.add_argument("-m", "--method", help=u"指定非ASCII字符解码方式，例如：utf8、gbk")
    decode.set_defaults(func=doDecode)

    # file操作
    fileop = subparser.add_parser("file", help=u"文件处理", \
        description=u"文件处理工具，支持文件编码转换、文件编码类型检测、文件hash计算、文件隐藏")
    fileop.add_argument("file", help=u"指定待处理文件")
    fileop.add_argument("--method", help=u"手工指定文件编码类型")
    fileop.add_argument("--dfile", help=u"指定目标文件")
    fileop.add_argument("-d", "--detect", action="store_true", help=u"文件编码类型检测")
    fileop.add_argument("--size", type=int, help=u"文件编码检测指定检测长度，默认为2048字节")
    fileop.add_argument("-c", "--convert", action="store_true", help=u"文件编码类型转换")
    fileop.add_argument("--dtype", help=u"文件编码转换指定目标编码类型，使用--list查看支持格式")
    fileop.add_argument("--list", action="store_true", help=u"显示编码转换支持的格式")
    fileop.add_argument("--hash", help=u"文件hash计算，支持{0}".format("/".join(File.hashMethod)))
    fileop.add_argument("--hfile", help=u"文件隐藏指定用来隐藏的图片文件")
    fileop.set_defaults(func=doFileOp)

    # google hacking功能
    gh = subparser.add_parser("gh", help=u"Google Hacking功能")
    gh.add_argument("keywords", help=u"指定搜索关键字")
    gh.add_argument("-e", "--engine", help=u"指定搜索引擎，目前支持baidu/bing/google，默认使用baidu")
    gh.add_argument("-s", "--size", type=int, help=u"指定搜索返回条目数，默认为200条")
    gh.add_argument("-o", "--output", help=u"指定输出文件，输出文件为URL列表")
    gh.add_argument("--unique", action="store_true", help=u"设置domain唯一")
    gh.set_defaults(func=doGoogleHacking)

    # dbparse, add wordlist to database and generate new wordlists
    dbparse = subparser.add_parser("db", help=u"字典数据库处理，字典导入到数据库，数据库生成字典")
    dbparse.add_argument("database", help=u"指定数据库文件")
    dbparse.add_argument("-g", "--generate", help=u"按指定的大小生成字典文件", type=int)
    dbparse.add_argument("-w", "--wordlist", help=u"将指定的字典文件导入数据库")
    dbparse.set_defaults(func=doDictParse)

    # mailcheck, check and find useful mail accounts
    mailcheck = subparser.add_parser("mailcheck", help=u"mail账户批量验证")
    mailcheck.add_argument("file", help=u"指定字典文件, 字典格式 'xx@xx.com passwd'")
    mailcheck.add_argument("-s", "--server", help=u"自定义POP3 server地址")  
    mailcheck.add_argument("-c", "--ssl", help=u"使用 ssl", action="store_true")
    mailcheck.add_argument("-p", "--port", help=u"自定义端口", type=int)
    mailcheck.set_defaults(func=doMailChecks)

    # mail bruteforce
    mailbrute = subparser.add_parser("mailbrute", help=u"mail账户爆破")
    mailbrute.add_argument("user", help=u"指定mail账户名, 使用 @file 指定账户字典文件")
    mailbrute.add_argument("passwd", help=u"指定mail账户密码, 使用 @file 指定密码字典文件")
    mailbrute.add_argument("-s","--server", help=u"自定义POP3 server地址")  
    mailbrute.add_argument("-c","--ssl", help=u"使用 ssl", action="store_true")
    mailbrute.add_argument("-p","--port", help=u"自定义端口", type=int)
    mailbrute.set_defaults(func=doMailBrute)


    args = parser.parse_args()
    args.func(args)


