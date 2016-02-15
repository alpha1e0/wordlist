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
import inspect
import importlib

from script.commons import Database, PenError, DictError, WordList, Log, Output
from script.mail import getMailServers, checkMail
from script.cms import CMSIdentify
from script.password import PasswdGenerator
from script.uribrute import URIBruter
from script.coder import Code
from script.exploit import Exploit, ExpInfo
from script.orm import DBError


reload(sys)
sys.setdefaultencoding("utf-8")


#================================sub commands=====================================

def doDictParse(args):
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


def doGenPicShell(args):
    with open(args.pic, "rb") as fd:
        picData = fd.read()
    with open(args.shell, "rb") as fd:
        shellData = fd.read()
    with open(args.dest, "wb") as fd:
        fd.write(picData)
        fd.write(shellData)

    with Output(u"生成隐藏木马") as out:
        out.yellow(u"隐藏木马生成成功，结果\n{0}".format(args.dest))


def doMailChecks(args):
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
    if args.type in ['md5','sha']:
        if args.code.startswith("@"):
            with open(args.code[1:],"rb") as fd:
                code = Code(fd.read())
        else:
            code = Code(args.code)
    else:
        code = Code(args.code)

    with Output(u"编码") as out:
        for line in code.encode(args.type, args.method):
            out.raw(line.strip())


def doDecode(args):
    if args.detect:
        if args.code.startswith("@"):
            with open(args.code[1:],"rb") as fd:
                code = Code(fd.read(200))
        else:
            code = Code(args.code)
        result = code.detect()
        with Output(u"编码方式推断") as out:
            out.raw(u"编码：", out.Y(result['encoding']))
            out.raw(u"置信度：", out.Y(str(result['confidence']*100)[:5] + "%"))
    else:
        code = Code(args.code)
        with Output(u"解码") as out:
            for line in code.decode(args.type, args.method):
                out.raw(line.strip())


def doExploit(args):
    if args.list:
        exploits = ExpInfo.gets('expName','expFile')
        with Output(u"Exploit信息管理") as out:
            for exp in exploits:
                out.raw(exp.expFile + "\t" + exp.expName)
        return True
    # 搜索exploit
    if args.search:
        exploits = ExpInfo.gets('expName','expFile')
        result = []
        for exp in exploits:
            if args.search in exp.expName:
                result.append(exp)

        with Output(u"Exploit信息管理") as out:
            if result:
                for exp in result:
                    out.raw(exp.expName + "\t" + exp.expFile)
            else:
                out.red(u"未搜索到关键词 '{0}' 相关的内容".format(args.search))
        return True
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
    # 删除exploit信息条目
    if args.delete:
        try:
            ExpInfo.delete(args.delete.strip())
        except DBError as error:
            with Output(u"Exploit信息管理") as out:
                out.red(u"删除exploit信息条目失败，reason: '{0}'".format(error))
        else:
            with Output(u"Exploit信息管理") as out:
                out.raw(u"删除exploit信息条目成功")
        return True
    # exploit操作
    if args.expfile:
        # 通过文件名加载模块
        expfile = os.path.join(sys.path[0], "exploit", os.path.split(args.expfile)[-1])
        if not os.path.exists(expfile):
            with Output(u"Exploit执行") as out:
                out.red(u"找不到exploit，'{0}'".format(args.expfile))

        fileName = os.path.split(expfile)[-1]
        fileName = fileName.endswith(".pyc") and fileName[:-4] or fileName.endswith(".py") and fileName[:-3] or fileName
        expModuleName = ".".join(['exploit', fileName])

        module = importlib.import_module(expModuleName)

        for member in dir(module):
            expClass = getattr(module, member)
            if inspect.isclass(expClass):
                if issubclass(expClass, Exploit) and expClass.__name__ != 'Exploit':
                    break
        else:
            with Output(u"Exploit操作") as out:
                out.red(u"'{0}'中找不到exploit".format(expfile))
            return False

        if args.update:
            exploit.update()
            return True
        
        if not args.url:
            Output.red("缺少参数 -u/--url")
            return False
        url = args.url.lower().strip()
        if not url.startswith("http"):
            url = "http://" + url

        headers = dict()
        if args.cookie:
            headers['Cookie'] = args.cookie
        if args.referer:
            headers['Referer'] = args.referer
        if args.useragent:
            headers['User-Agent'] = args.useragent
        if args.header:
            for line in args.header.split("|"):
                for x in line.strip().split("="):
                    headers[x[0]] = x[1]

        ext = dict()
        if args.ext:
            for line in args.ext.split("|"):
                for x in line.strip().split("="):
                    ext[x[0]] = x[1]

        exploit = expClass(url, headers, ext)
        if args.verify:
            result = exploit.verify()
        elif args.attack:
            result = exploit.attack()
        else:
            result = exploit.attack()
        with Output(u"Exploit执行") as out:
            out.raw(result)
        
    else:
        Output.red("缺少参数 -e/--expfile")


#=====================================main================================================

def signalHandler(signum, frame):
    print "[+]: User exit."
    exit()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signalHandler)

    parser = argparse.ArgumentParser(description=u"渗透测试辅助小工具")
    subparser = parser.add_subparsers(title=u"子命令", description=u"使用子命令")

    # dbparse, add wordlist to database and generate new wordlists
    dbparse = subparser.add_parser("db", help=u"字典数据库处理，字典导入到数据库，数据库生成字典")
    dbparse.add_argument("database", help=u"指定数据库文件")
    dbparse.add_argument("-g", "--generate", help=u"按指定的大小生成字典文件", type=int)
    dbparse.add_argument("-w", "--wordlist", help=u"将指定的字典文件导入数据库")
    dbparse.set_defaults(func=doDictParse)

    # picshell, generate a picture webshell
    picshell = subparser.add_parser("picshell", help=u"生成图片webshell")
    picshell.add_argument("pic", help=u"指定承载webshell的图片文件")
    picshell.add_argument("shell", help=u"指定webshell文件")
    picshell.add_argument("dest", help="指定输出文件")
    picshell.set_defaults(func=doGenPicShell)

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

    # encode
    encode = subparser.add_parser("encode", help=u"编码工具", \
        description=u"编码工具，支持的编码种类有:{0}".format(" ".join(Code.encodeTypes)))
    encode.add_argument("code", help=u"待编码字符串，建议用引号包括")
    encode.add_argument("-t", "--type", help=u"指定编码种类，md5/sha@file使用指定文件")
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
    decode.add_argument("-d", "--detect", help=u"非ASCII字符编码检测，使用@file指定文件", action="store_true")
    decode.set_defaults(func=doDecode)

    # exploit
    exploit = subparser.add_parser("exploit", help=u"执行exploit")
    # exploit execute
    expExec = exploit.add_argument_group('exploit execute')
    expExec.add_argument("-u", "--url", help=u"指定目标URL")
    expExec.add_argument("-e", "--expfile", help=u"指定exploit文件")
    expExec.add_argument("--verify", action="store_true", help=u"验证模式")
    expExec.add_argument("--attack", action="store_true", help=u"攻击模式")
    expExec.add_argument("--cookie", help=u"指定Cookie")
    expExec.add_argument("--useragent", help=u"指定UserAgent")
    expExec.add_argument("--referer", help=u"指定referer")
    expExec.add_argument("--header", help=u"指定其他HTTP header,例如--header 'xxx=xxxx|yyy=yyyy'")
    expExec.add_argument("--ext", help=u"指定其他参数,例如--header 'xxx=xxxx|yyy=yyyy'")
    # exploit manage
    expManage = exploit.add_argument_group('exploit manage')
    expManage.add_argument("--update", help=u"更新exploit信息")
    expManage.add_argument("-s", "--search", help=u"根据exploit名称搜索")
    expManage.add_argument("-l", "--list", action="store_true", help=u"列举可用exploit")
    expManage.add_argument("--createdb", action="store_true", help=u"创建exploit信息数据库")
    expManage.add_argument("--delete", help=u"删除指定的exploit信息条目")
    expManage.set_defaults(func=doExploit)


    args = parser.parse_args()
    args.func(args)


