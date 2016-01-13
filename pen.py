#!/usr/local/env python
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
    pwgen = PasswdGenerator(args)

    for line in pwgen.generate():
        print line


def doFileBrute(args):
    if args.generate:
        bruter = URIBruter(stype=args.type, keywords=args.keywords, exts=args.ext, notFoundPattern=args.notfound)
        for line in bruter.genDict():
            print line
    else:
        bruter = URIBruter(baseURL=args.url ,stype=args.type, keywords=args.keywords, exts=args.ext, notFoundPattern=args.notfound, safeURL=args.safeurl)
        bruter.bruteforce()


#=====================================main================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(title="subcommands", description="use subcommands")

    # dbparse, add wordlist to database and generate new wordlists
    dbparse = subparser.add_parser("db", help="parse database, add wordlist to database, dump wordlist from database")
    dbparse.add_argument("database", help="specify the database file.")
    dbparse.add_argument("-g", "--generate", help="specify the size and generate a wordlist.", type=int)
    dbparse.add_argument("-w", "--wordlist", help="add a specify wordlist to database.")
    dbparse.set_defaults(func=doDictParse)

    # picshell, generate a picture webshell
    picshell = subparser.add_parser("picshell", help="generate picture webshell")
    picshell.add_argument("pic", help="specify the picture file or other files to contain the webshell.")
    picshell.add_argument("shell", help="specify the shell file.")
    picshell.add_argument("dest", help="specify the output file.")
    picshell.set_defaults(func=doGenPicShell)

    # mailcheck, check and find useful mail accounts
    mailcheck = subparser.add_parser("mailcheck", help="check and find useful mail accounts")
    mailcheck.add_argument("file", help="specify wordlist, wordlist format is 'xx@xx.com passwd'")
    mailcheck.add_argument("-s", "--server", help="specify the POP3 server.")  
    mailcheck.add_argument("-c", "--ssl", help="use ssl", action="store_true")
    mailcheck.add_argument("-p", "--port", help="specify the port", type=int)
    mailcheck.set_defaults(func=doMailChecks)

    # mail bruteforce
    mailbrute = subparser.add_parser("mailbrute", help="mail account brute force")
    mailbrute.add_argument("user", help="specify the user of the mail account, use @file to specify user wordlist")
    mailbrute.add_argument("passwd", help="specify the password of the mail account, use @file to specify password wordlist")
    mailbrute.add_argument("-s","--server", help="specify the POP3 server.")  
    mailbrute.add_argument("-c","--ssl", help="use ssl", action="store_true")
    mailbrute.add_argument("-p","--port", help="specify the port", type=int)
    mailbrute.set_defaults(func=doMailBrute)

    # cms identify
    cms = subparser.add_parser("cmsidentify", help="indentify the cms type")
    cms.add_argument("url", help="specify the URL of target.")
    cms.add_argument("--notfound", help="specify the notfound pattern.")
    cms.set_defaults(func=doCMSIdentify)

    # password generate
    passwdgen = subparser.add_parser("passwdgen", help="generate password list")
    passwdgen.add_argument("--fullname", help="specify the fullname, format: 'zhang san' 'lin zhi ling'")
    passwdgen.add_argument("--nickname", help="specify the nickname")
    passwdgen.add_argument("--englishname", help="specify the english name")
    passwdgen.add_argument("--partnername", help="specify the partner name")
    passwdgen.add_argument("--birthday", help="specify the birthday day, format: '2000-1-10'")
    passwdgen.add_argument("--phone", help="specify the phone number")
    passwdgen.add_argument("--qq", help="specify the QQ number")
    passwdgen.add_argument("--company", help="specify the company")
    passwdgen.add_argument("--domain", help="specify the domain name")
    passwdgen.add_argument("--oldpasswd", help="specify the oldpassword")
    passwdgen.add_argument("--keywords", help="specify the keywords, example: 'keyword1 keyword2'")
    passwdgen.add_argument("--keynumbers", help="specify the keynumbers, example: '123 789'")
    passwdgen.add_argument("--output", help="specify output wordlist file")
    passwdgen.set_defaults(func=doGenPassword)

    # file bruteforce
    uribrute = subparser.add_parser("uribrute", help="URI bruteforce")
    uribrute.add_argument("-u", "--url", help="spcify the target url")
    uribrute.add_argument("--type", help="spcify the server type asp/aspx/php/jsp")
    uribrute.add_argument("--keywords", help="spcify the keywords to generate wordlist")
    uribrute.add_argument("--ext", help="spcify the userdefined extensions")
    uribrute.add_argument("--notfound", help="specify the notfound pattern.")
    uribrute.add_argument("--safeurl", help="specify safe url.")
    uribrute.add_argument("--generate", help="generate password", action="store_true")
    uribrute.set_defaults(func=doFileBrute)

    args = parser.parse_args()
    args.func(args)


