#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
Pentestdb, a database for penetration test.
Copyright (c) 2014-2015 alpha1e0
=============================================================
服务识别模块
'''

import os
import re

from thirdparty import requests as http
from lxml import etree

from commons import URL
from commons import YamlConf
from commons import PenError
from commons import Dict
from commons import Log
from commons import Output



class AppInfo(Dict):
    '''
    存储服务识别信息
    '''
    def __str__(self):
        resultStr = Output.Y(u"原始信息:\n")
        resultStr = resultStr + Output.B("{0:>11} : ".format('URL')) + self['meta']['url'] + "\n"
        resultStr = resultStr + Output.B("{0:>11} : ".format('Status')) + str(self['meta']['statusCode']) + "\n"
        resultStr = resultStr + Output.B("{0:>11} : ".format('Headers')) + "\n"
        for key,value in self['meta']['headers'].iteritems():
            resultStr = resultStr + Output.G("{0:>20} : ".format(key)) + value + "\n"

        resultStr = resultStr + Output.Y(u"\n识别结果:\n")
        for key,value in self['apps'].iteritems():
            appsInfo = ""
            for line in value:
                if line[3]:
                    appsInfo = appsInfo + line[0] + " " + line[3] + " ; "
                else:
                    appsInfo = appsInfo + line[0] + " ; "
            resultStr = resultStr + Output.Y("{0:>11} : ".format(key)) + appsInfo + "\n"

        return resultStr



def stripPattern(pattern):
    return pattern.replace("\\\\","\\")


class Service(object):
    '''
    Identify the Web Application.
    html，robots在需要的时候加载，并保存为metainfo，metainfo最好封装一下
    '''
    def __init__(self, url, notFoundPattern=None):
        self._url = url.strip()
        self._notFoundPattern = notFoundPattern
        if not URL.check(self._url):
            raise PenError("Service Identify, URL format error")

        self._target = URL.format(self._url)

        self._fp = YamlConf(os.path.join("script","data","app_fingerprint.yaml"))

        # debug>>>>>>>>>>>>>>>>>>>
        name = 'Apache'
        ddddd = self._fp['Applications'][name]
        self._fp['Applications'] = {name:ddddd}
        # debug>>>>>>>>>>>>>>>>>>>>>

        # metaInfo 页面元信息
        # url, statusCode, headers, html, title, robots
        self._metaInfo = {}
        self._initMetaInfo()
        # result 中存储的信息
        # meta：_metaInfo
        # info：OS,Server,Language,Apps,Middleware,Else，信息以数组方式存储，其中每一项为一个匹配result
        #   匹配result格式：[apptype, match_place, match_str, version_info]，例如['Apache', 'headers_Server', 'Apache/2.4.18', '2.4.18']
        self._result = AppInfo()
        self._initResult()

        self._matchFuncs = {}
        self._initHandleFuncs()

        self._log = Log("service_identify")


    def _getTitle(self, html):
        tree = etree.HTML(html)
        titles = tree.xpath("//title/text()")
        if titles:
            return titles[0]
        else:
            return "blank"


    def _initMetaInfo(self):
        self._metaInfo['url'] = self._url
        self._metaInfo['target'] = self._target
        try:
            response = http.get(self._target.uri)
        except http.ConnectionError:
            raise PenError("Can not connect to {0}".format(self._target.uri))
        else:
            self._metaInfo['statusCode'] = response.status_code
            self._metaInfo['headers'] = response.headers
            self._metaInfo['html'] = response.content
            self._metaInfo['title'] = self._getTitle(response.content)

        self._metaInfo['robots'] = ""
        try:
            response = http.get(self._target.baseURL+"robots.txt")
        except http.ConnectionError:
            pass
        else:
            if response.status_code == 200:
                self._metaInfo['robots'] = response.content



    def _initHandleFuncs(self):
        '''
        初始化匹配函数字典，对应app_figerprint中的match定义
        目前支持：uri, headers, html, requests, robots
        matchFunc定义：
            输入：fingerprint定义
            输出：[match_place,match_str,version_info]
                match_place(必须)为url/headers/html等，match_str(必须)为匹配信息，version_info(必须)为版本信息
                如果没有相关信息则为None
            例如：
                self._matchHeaders(fp)  返回  ['headers_Server', 'Apache/2.4.18', '2.4.18']
        '''
        self._matchFuncs['uri'] = self._matchUri
        self._matchFuncs['headers'] = self._matchHeaders
        self._matchFuncs['html'] = self._matchHtml
        self._matchFuncs['requests'] = self._matchRequests
        self._matchFuncs['robots'] = self._matchRobots



    def _initResult(self):
        self._result['apps'] = {}
        for key,value in self._fp['Categories'].iteritems():
            self._result['apps'][key] = []

        self._result['meta'] = self._metaInfo



    def identify(self):
        #import pdb
        #pdb.set_trace()
        for fkey,fvalue in self._fp['Applications'].iteritems():
            bestMatch = []
            for mkey,mvalue in fvalue['matchs'].iteritems():
                try:
                    func = self._matchFuncs[mkey]
                except KeyError:
                    self._log.warnning("the function which handle {0} dose not exists".format(mkey))
                    continue
                r = self._matchFuncs[mkey](mvalue)
                if r[1]:
                    if not bestMatch:
                        bestMatch = r
                    else:
                        if r[2] and not bestMatch[2]:
                            bestMatch = r
            if bestMatch:
                for cat in fvalue['cats']:
                    self._result['apps'][cat].append([fkey]+bestMatch)

        return self._result



    def _matchUri(self, fp):
        match = re.search(stripPattern(fp), self._metaInfo['target'].uri)
        if match:
            subMatch = match.groups()[0] if match.groups() else None
            return ['uri', match.group(), subMatch]
        else:
            return ['uri', None, None]


    def _matchHeaders(self, fp):
        for key,value in fp.iteritems():
            bestMatch = []
            match = re.search(stripPattern(value), self._metaInfo['headers'].get(key.lower(),""))
            if match:
                subMatch = match.groups()[0] if match.groups() else None
                if not bestMatch:
                    bestMatch = ['headers_{0}'.format(key), match.group(), subMatch]
                else:
                    if subMatch and not bestMatch[2]:
                        bestMatch = ['headers_{0}'.format(key), match.group(), subMatch]

        return bestMatch if bestMatch else ['headers',None,None]


    def _matchHtml(self, fp):
        if isinstance(fp,list):
            for pattern in fp:
                bestMatch = []
                match = re.search(stripPattern(pattern), self._metaInfo['html'])
                if match:
                    subMatch = match.groups()[0] if match.groups() else None
                    if not bestMatch:
                        bestMatch = ['html'.format(key), match.group(), subMatch]
                    else:
                        if subMatch and not bestMatch[2]:
                            bestMatch = ['html'.format(key), match.group(), subMatch]
            return bestMatch if bestMatch else ['html',None,None]
        else:
            match = re.search(stripPattern(fp), self._metaInfo['html'])
            if match:
                subMatch = match.groups()[0] if match.groups() else None
                return ['html', match.group, subMatch]
            else:
                return ['html', None, None]


    def _matchRobots(self, fp):
        if isinstance(fp,list):
            for pattern in fp:
                bestMatch = []
                match = re.search(stripPattern(pattern), self._metaInfo['robots'])
                if match:
                    subMatch = match.groups()[0] if match.groups() else None
                    if not bestMatch:
                        bestMatch = ['robots'.format(key), match.group(), subMatch]
                    else:
                        if subMatch and not bestMatch[2]:
                            bestMatch = ['robots'.format(key), match.group(), subMatch]
            return bestMatch if bestMatch else ['robots',None,None]
        else:
            match = re.search(stripPattern(fp), self._metaInfo['robots'])
            if match:
                subMatch = match.groups()[0] if match.groups() else None
                return ['robots', match.group, subMatch]
            else:
                return ['robots', None, None]


    def _matchRequests(self, fp):
        matchs = []
        for line in fp:
            uri = self._metaInfo['target'].baseURL.rstrip("/") + line
            try:
                response = http.get(uri, allow_redirects=False)
            except http.ConnectionError:
                continue
            else:
                if response.status_code == 200:
                    if self._notFoundPattern:
                        if self._notFoundPattern in response.content:
                            continue
                        else:
                            matchs.append(uri)
                    else:
                        matchs.append(uri)
                else:
                    continue

        if len(matchs) == len(fp):
            return ['requests', str(matchs), None]
        else:
            return ['requests', None, None]



    