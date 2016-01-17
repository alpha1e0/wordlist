#!/usr/bin/env python
#coding: UTF-8

'''
Pentestdb, a database for penetration test.
Copyright (c) 2014-2015 alpha1e0
'''


import json
import poplib


def getMailServers(mailServersFile):
    return json.load(open(mailServersFile,"r"))


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