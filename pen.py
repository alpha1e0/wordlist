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

from script.commons import Database, PenError, DictError, WordList, Log, Output
from script.mail import getMailServers, checkMail
from script.cms import CMSIdentify
from script.password import PasswdGenerator
from script.uribrute import URIBruter
from script.coder import Code
from script.exploit import Exploit, ExpInfo, ExploitError, loadExpClass
from script.orm import DBError


reload(sys)
sys.setdefaultencoding("utf8")


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


def execExploit(expFile, args):
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
        return (False, {})
    
    if not args.url:
        Output.red(u"\n缺少参数 -u/--url")
        return (False, {})
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
        for param in args.header.split("/"):
            paramSplited = param.strip().split("=")
            headers[paramSplited[0]] = paramSplited[1]

    elseArgs = dict()
    if args.elseargs:
        for param in args.elseargs.split("/"):
            paramSplited = param.strip().split("=")
            elseArgs[paramSplited[0]] = paramSplited[1]

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

    # 列举所有exploit
    if args.list:
        exploits = ExpInfo.gets('expName','expFile')
        with Output(u"Exploit信息管理") as out:
            for exp in exploits:
                out.raw(out.R("expName: ") + exp.expName)
                out.raw(out.R("expFile: ") + exp.expFile + "\n")
        return True

    # 搜索exploit
    if args.search:
        column, keyword = parseSearchParam(args.search)
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
        
    # Exploit扫描
    if args.scan:
        column, keyword = parseSearchParam(args.scan)
        if not column: return False

        exploits = ExpInfo.search(column, keyword)
        with Output(u"Exploit扫描") as out:
            if exploits:    
                for exp in exploits:
                    expName, result = execExploit(exp.expFile, args)
                    if not expName: continue
                    out.raw(out.R("Exploit: ") + expName)
                    out.raw(out.R("Target:  ") + args.url + "\n")
                    out.raw(result)
                    out.raw("----------------------------------------------------------")
            else:
                out.red(u"在 '{0}' 列中未搜索到包含关键词 '{1}' 的exploit".format(column,keyword))
    # exploit操作
    if args.expfile:
        if args.update:
            try:
                expClass = loadExpClass(args.expfile)
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
        
        expName, result = execExploit(args.expfile, args)

        with Output(u"Exploit执行") as out:
            out.raw(out.R("Exploit: ") + expName)
            out.raw(out.R("Target:  ") + args.url + "\n")
            out.raw(result)


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
    exploit = subparser.add_parser("exploit", help=u"exploit操作")
    # exploit execute
    expExec = exploit.add_argument_group(u'exploit执行')
    expExec.add_argument("-u", "--url", help=u"指定目标URL")
    expExec.add_argument("-e", "--expfile", help=u"指定exploit文件")
    expExec.add_argument("--verify", action="store_true", help=u"验证模式")
    expExec.add_argument("--attack", action="store_true", help=u"攻击模式")
    expExec.add_argument("--cookie", help=u"指定Cookie")
    expExec.add_argument("--useragent", help=u"指定UserAgent")
    expExec.add_argument("--referer", help=u"指定referer")
    expExec.add_argument("--header", help=u"指定其他HTTP header,例如--header 'xxx=xxxx/yyy=yyyy'")
    expExec.add_argument("--elseargs", help=u"指定其他参数,例如--elseargs 'xxx=xxxx/yyy=yyyy'")
    # exploit manage
    expManage = exploit.add_argument_group(u'exploit管理')
    expManage.add_argument("--update", action="store_true", help=u"更新exploit信息")
    expManage.add_argument("-s", "--search", help=u"搜索exploit，参数格式column:keyword，column支持expName/os/webserver/language/appName，默认为expName")
    expManage.add_argument("-l", "--list", action="store_true", help=u"列举所有exploit")
    expManage.add_argument("--createdb", action="store_true", help=u"创建exploit信息数据库")
    expManage.add_argument("--delete", help=u"根据exploit名字删除exploit信息条目")
    # Exploit扫描
    expManage = exploit.add_argument_group(u'exploit批量扫描')
    expManage.add_argument("--scan", help=u"Exploit扫描，参数格式column:keyword，column支持expName/os/webserver/language/appName，默认为expName")

    expManage.set_defaults(func=doExploit)


    args = parser.parse_args()
    args.func(args)


