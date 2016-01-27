#!/usr/bin/env python
#coding: UTF-8

'''
Pentestdb, a database for penetration test.
Copyright (c) 2014-2015 alpha1e0
'''


import sys
import argparse
import os
import poplib

from script.commons import Database, PenError, DictError, WordList, Log
from script.mail import getMailServers, checkMail
from script.cms import CMSIdentify
from script.password import PasswdGenerator
from script.uribrute import URIBruter
from script.coder import Code

reload(sys)
sys.setdefaultencoding("utf-8")


#================================sub commands=====================================

def doDictParse(args):
    db = Database(args.database)

    if args.generate:
        db.generate(args.generate)
    elif args.wordlist:
        db.addWordlist(args.wordlist)

        db.dump()


def doGenPicShell(args):
    with open(args.pic, "rb") as fd:
        picData = fd.read()
    with open(args.shell, "rb") as fd:
        shellData = fd.read()
    with open(args.dest, "wb") as fd:
        fd.write(picData)
        fd.write(shellData)


def doMailChecks(args):
    log = Log()
    mailServers = getMailServers(os.path.join("else","mail_server.json"))
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

        log.info("checking '{0}' '{1}' '{2}'".format(user, passwd, server))
        if checkMail(server, user, passwd, port=port):
            log.warning("success, user is {0}, password is {1}".format(user,passwd))


def doMailBrute(args):
    log = Log()
    mailServers = getMailServers(os.path.join("else","mail_server.json"))

    users = WordList(args.user[1:]) if args.user.startswith("@") else [args.user]
    passwords = WordList(args.passwd[1:]) if args.passwd.startswith("@") else [args.passwd]

    for user in users:
        for password in passwords:
            server = user.split("@")[1].strip()
            server = mailServers.get(server, None)
            ssl = mailServers.get('ssl', False)
            port = server.get('port',None)
            if not server:
                continue

            log.info("checking '{0}' '{1}' '{2}'".format(user, passwd, server['server']))
            
            if checkMail(server['server'], user, passwd, ssl=ssl, port=port):
                log.warning("success, user is {0}, password is {1}".format(user,passwd))


def doCMSIdentify(args):
    if args.notfound:
        cms = CMSIdentify(args.url, notFoundPattern=args.notfound)
    else:
        cms = CMSIdentify(args.url)
    cms.identify()


def doGenPassword(args):
    pwgen = PasswdGenerator(fullname=args.fullname, nickname=args.nickname, englishname=args.englishname, \
        partnername=args.partnername, birthday=args.birthday, phone=args.phone, qq=args.qq, company=args.company, \
        domain=args.domain, oldpasswd=args.oldpasswd, keywords=args.keywords, keynumbers=args.keynumbers)

    for line in pwgen.generate():
        print line


def doFileBrute(args):
    if args.generate:
        bruter = URIBruter(stype=args.type, keywords=args.keywords, exts=args.ext)
        for line in bruter.genDict():
            print line
    else:
        bruter = URIBruter(baseURL=args.url ,stype=args.type, keywords=args.keywords, exts=args.ext, \
            notFoundPattern=args.notfound, safeURL=args.safeurl, timeout=args.timeout, delay=args.delay, encode=args.encode)
        bruter.bruteforce()


def doEncode(args):
    if args.list:
        print "[+]: Support encode type are:"
        print "[+]:", " ".join(Code.encodeTypes)
        return

    code = Code(args.code)
    print "[+]: Encode result:"
    print "[+]:", code.encode(args.type, args.method)


def doDecode(args):
    if args.list:
        print "[+]: Support decode type are:"
        print "[+]:", " ".join(Code.decodeTypes)
        return

    code = Code(args.code)
    print "[+]: Decode result:"
    print "[+]:", code.decode(args.type, args.method)


#=====================================main================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
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
    cms = subparser.add_parser("cmsidentify", help=u"CMS 识别")
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
    passwdgen.set_defaults(func=doGenPassword)

    # uri bruteforce
    uribrute = subparser.add_parser("uribrute", help=u"URI爆破字典")
    uribrute.add_argument("-u", "--url", help=u"指定目的URL")
    uribrute.add_argument("--type", help=u"指定server类型，支持：asp/aspx/php/jsp")
    uribrute.add_argument("--keywords", help=u"自定义关键字，用于生成备份文件爆破字典")
    uribrute.add_argument("--ext", help=u"自定义后缀名，例如：php7")
    uribrute.add_argument("--notfound", help=u"自定义notfound页面关键字")
    uribrute.add_argument("--safeurl", help=u"自定义安全URL，用于bypass安全软件")
    uribrute.add_argument("--generate", help=u"生成字典", action="store_true")
    uribrute.add_argument("--timeout", help=u"指定http请求超时事件, 默认为 10", type=int)
    uribrute.add_argument("--delay", help=u"指定http请求间隔时间, 默认无间隔", type=float)
    uribrute.add_argument("--encode", help=u"指定url非ASCII编码方式, 默认为UTF-8")
    uribrute.set_defaults(func=doFileBrute)

    # encode
    encode = subparser.add_parser("encode", help=u"编码工具")
    encode.add_argument("code", help=u"待编码字符串")
    encode.add_argument("-t", "--type", help=u"指定编码种类")
    encode.add_argument("-m", "--method", help=u"指定非ASCII字符编码方式")
    encode.add_argument("-l", "--list", help=u"查看支持的编码种类", action="store_true")
    encode.set_defaults(func=doEncode)

    # decode
    decode = subparser.add_parser("decode", help=u"解码工具")
    decode.add_argument("code", default="hello", help=u"解码字符串")
    decode.add_argument("-t", "--type", help=u"指定解码种类")
    decode.add_argument("-m", "--method", help=u"指定非ASCII字符解码方式")
    decode.add_argument("-l", "--list", help=u"查看支持的解码种类", action="store_true")
    decode.set_defaults(func=doDecode)

    args = parser.parse_args()
    args.func(args)


