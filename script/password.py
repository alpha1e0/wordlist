#!/usr/bin/env python
# coding: UTF-8

'''
Pentestdb, a database for penetration test.
Copyright (c) 2014-2015 alpha1e0
'''

import time


class PasswdGenerator(object):
    numList = ['123456', '123123', '123123123', '112233', '445566', '456456', '789789', '778899', '321321', '520', '1314', '5201314', '1314520', '147369', '147258', '258', '147', '456', '789', '147258369', '111222', '123', '1234', '12345', '1234567', '12345678', '123456789', '987654321', '87654321', '7654321', '654321', '54321', '4321', '321']
    prefixList = ['a','qq','yy','aa','abc','qwer','woaini']

    def __init__(self, **kwargs):
        '''
        Parameters of kwargs:
        fullname:    specified the fullname, format: 'zhang san' 'wang ai guo'
        nickname:    specified the nickname
        englishname: specified the english name
        partnername: specified the partner name
        birthday:    specified the birthday day, format: '2000-1-10'
        phone:       specified the phone number
        qq:          specified the QQ number
        company:     specified the company
        domain:      specified the domain name
        oldpasswd:   specified the oldpassword
        keywords:    specified the keywords, example: 'keyword1 keyword2'
        keynumbers:  specified the keynumbers, example: '123 789'
        '''
        self.fullname = kwargs.fullname
        self.nickname = kwargs.nickname
        self.englishname = kwargs.englishname
        self.partnername = kwargs.partnername
        self.birthday = kwargs.birthday
        self.phone = kwargs.phone
        self.qq = kwargs.qq
        self.company = kwargs.company
        self.domain = kwargs.domain
        self.oldpasswd = kwargs.oldpasswd
        self.keywords = kwargs.keywords
        self.keynumbers = kwargs.keynumbers

        self.innerNumList = []
        self.innerPrefixList = []

        self.shortNameList = []
        self.fullNameList = []
        self.mixedkeywordList = []


    def genShortNameList(self, fullname=None):
        fullname = fullname if fullname else self.fullname
        if not fullname:
            return []
        else:
            result = []
            func = lambda x:[x, x.title(), x[0].lower(), x[0].upper()]
            nameSplited = fullname.split()
            if len(nameSplited) == 1:
                result += func(nameSplited[0])
            elif len(nameSplited) == 2:
                shortName = nameSplited[0][0].lower() + nameSplited[1][0].lower()
                result += func(shortName)
            else:
                shortName = nameSplited[0][0].lower() + nameSplited[1][0].lower() + nameSplited[2][0].lower
                result += func(shortName)
                shortNameRS = nameSplited[1][0].lower() + nameSplited[2][0].lower + nameSplited[0][0].lower()
                shortNameR = nameSplited[1][0].lower() + nameSplited[2][0].lower + nameSplited[0]
                result += [shortNameR, shortNameRS]

            return result


    def genFullNameList(self, fullname=None):
        fullname = fullname if fullname else self.fullname
        if not fullname:
            return []
        else:
            return ["".join(fullname.split())]


    def genInnerNumList(self):
        result = self.numListA
        for i in range(0,10):
            result += [str(i)*x for x in range(3,10)]

        endyear = int(time.strftime("%Y"))
        result += [str(x) for x in range(2000, endyear+1)]

        return result




