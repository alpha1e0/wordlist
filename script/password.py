#!/usr/bin/env python
# coding: UTF-8

'''
Pentestdb, a database for penetration test.
Copyright (c) 2014-2015 alpha1e0
'''

import time
import itertools


class PasswdGenerator(object):
    # 常用密码关键数字
    numList = ['123456', '123123', '123123123', '112233', '445566', '456456', '789789', '778899', '321321', '520', '1314', '5201314', '1314520', '147369', '147258', '258', '147', '456', '789', '147258369', '111222', '123', '1234', '12345', '1234567', '12345678', '123456789', '987654321', '87654321', '7654321', '654321', '54321', '4321', '321']
    # 常用前缀列表
    prefixList = ['a','qq','yy','aa','abc','qwer','woaini']
    # 常用密码
    commonPasswd = ['123456', '123456.', 'a123456', 'a123456.', '123456a', '123456a.', '123456abc', '123456abc.', 'abc123456', 'abc123456.', 'woaini1314', 'woaini1314.', 'qq123456', 'qq123456.', 'woaini520', 'woaini520.', 'woaini123', 'woaini123.', 'woaini521', 'woaini521.', 'qazwsx', 'qazwsx.', '1qaz2wsx', '1qaz2wsx.', '1q2w3e4r', '1q2w3e4r.', '1q2w3e4r5t', '1q2w3e4r5t.', '1q2w3e', '1q2w3e.', 'qwertyuiop', 'qwertyuiop.', 'zxcvbnm', 'zxcvbnm.']
    # 和partner混合的常用前缀列表
    partnerPrefixList = ['520','5201314','1314','iloveu','iloveyou']
    # 和domian，company组合的前缀列表
    domainPrefixList = ['admin','root','manager','system']

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

        # 常用数字列表，用户和用户名、昵称、英文名、关键字等混合
        self.innerNumList = []
        # 常用前缀列表，用于和手机号、QQ号混合
        self.innerPrefixList = []

        # 段名列表，由原始全名生成
        self.shortNameList = []
        # 全名列表，由原始全名生成
        self.fullNameList = []
        # 待混合的keyword列表，由于用户名、昵称、英文名、关键字的混合规则一致，因此放到这一个列表内进行混合
        self.mixedkeywordList = []

        self.result = []


    def genShortNameList(self, fullname=None):
        fullname = fullname if fullname else self.fullname
        if not fullname:
            return []
        else:
            result = []
            func = lambda x:[x, x.title(), x[0].lower(), x[0].upper(), x.upper()]
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
                result += [shortNameR, shortNameRS, shortNameRS.upper()]

            return result


    def genFullNameList(self, fullname=None):
        fullname = fullname if fullname else self.fullname
        if not fullname:
            return []
        else:
            result = []
            nameSplited = fullname.split()
            if len(nameSplited) == 1:
                result.append(nameSplited[0])
            elif len(nameSplited) == 2:
                result += ["".join(nameSplited), nameSplited[1]+nameSplited[0]]
            else:
                result += [nameSplited[0]+nameSplited[1]+nameSplited[2], nameSplited[1]+nameSplited[2]+nameSplited[0]]
            
            return result + [x.upper() for x in result]


    def genInnerNumList(self):
        result = self.numListA
        for i in range(0,10):
            result += [str(i)*x for x in range(1,10)]

        endyear = int(time.strftime("%Y"))
        result += [str(x) for x in range(2000, endyear+1)]

        if self.keynumbers:
            result += self.keynumbers.split()
        if self.oldpasswd:
            result.append(self.oldpasswd)

        return result


    def genDateList(self, date):
        if not date:
            return []
        else:
            result = []
            dateSplited = date.split()
            if len(dateSplited) == 1:
                result.append(dateSplited[0])
            elif len(dateSplited) == 2:
                result += [dateSplited[0], dateSplited[0]+dateSplited[1], dateSplited[0][-2:]+dateSplited[1]]
            elif:
                result += [dateSplited[0], dateSplited[0]+dateSplited[1], dateSplited[0]+dateSplited[1]+dateSplited[2]]
                result += [dateSplited[0][-2:]+dateSplited[1], dateSplited[0][-2:]+dateSplited[1]+dateSplited[2]]

            return result

    def mixed(self, listA, listB):
        if not listA and not listB:
            return []
        elif not listA:
            return listB
        elif not listB:
            return listA
        result = []
        for a,b in itertools.product(listA, listB):
            if len(a+b)>5 and len(a+b)<17:
                result.append(a+b)
                result.append(a+"@"+b)

        return result


    def preHandlePhase(self):
        self.innerNumList = self.genInnerNumList()
        self.innerPrefixList = self.prefixList + [x.upper() for x in self.prefixList]
        self.shortNameList = self.genShortNameList()
        self.fullNameList = self.genFullNameList()

        self.mixedkeywordList += self.shortNameList
        self.mixedkeywordList += self.fullNameList
        if self.nickname:
            self.mixedkeywordList.append(self.nickname)
        if self.englishname:
            self.mixedkeywordList.append(self.englishname)
        if self.keywords:
            self.mixedkeywordList += self.keywords.split()

        self.result += self.commonPasswd


    def mixedPhase(self):
        self.result += self.mixed(self.mixedkeywordList, self.innerNumList)
        self.result += self.mixed(["520"], self.mixedkeywordList)
        if self.phone:
            self.result += self.mixed(self.innerPrefixList+self.mixedkeywordList, self.phone)
        if self.qq:
            self.result += self.mixed(self.innerPrefixList+self.mixedkeywordList, self.qq)
        if self.partnername:
            nameList = self.shortNameList(self.partnername)
            nameList += self.fullNameList(self.partnername)
            self.result += self.mixed(self.partnerPrefixList, nameList)
        if self.birthday:
            dateList = self.genDateList(self.birthday)
            self.result += self.mixed(self.innerPrefixList+self.mixedkeywordList, dateList)
        if self.domain:
            self.result += self.mixed(self.domainPrefixList, [self.domain])
        if self.company:
            self.result += self.mixed(self.domainPrefixList, [self.company])


    def lastHandlePhase(self):
        self.result += [x+"." for x in self.result]


    def generate(self):
        self.preHandlePhase()
        self.mixedPhase()
        self.lastHandlePhase()




