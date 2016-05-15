#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
Pentestdb, a database for penetration test.
Copyright (c) 2014-2015 alpha1e0
=============================================================
服务识别模块
'''

import os

from thirdparty import requests as http
from lxml import etree

from commons import URL
from commons import YamlConf
from commons import PenError
from commons import Dict



class AppInfo(Dict):
    '''
    存储服务识别信息
    '''
    def __str__(self):
        return "info"


class Service(object):
    '''
    Identify the Web Application.
    html，robots在需要的时候加载，并保存为metainfo，metainfo最好封装一下
    '''
    def __init__(self, url):
        self._url = url.strip()
        if not URL.check(self._url):
            raise PenError("Service Identify, URL format error")
        self._target = URL.format(self._url)

        self._fp = YamlConf(os.path.join("script","data","app_fingerprint.yaml"))
        # metaInfo 页面元信息
        # url, statusCode, headers, html, title, robots
        self._metaInfo = dict()
        self._initMetaInfo()
        # result 中存储的信息
        # meta：_metaInfo
        # info：OS,Server,Language,Apps,Middleware,Else，信息以数组方式存储
        self._result = AppInfo()

        self._matchFuncs = dict()
        self._initHandleFuncs()        


    def _getTitle(self, html):
        tree = etree.HTML(html)
        titles = tree.xpath("//title/text()")
        if titles:
            return titles[0]
        else:
            return "blank"


    def _initMetaInfo(self):
        try:
            response = http.get(self._target.uri)
        except http.ConnectionError:
            raise PenError("Can not connect to {0}".format(self._target.uri))
        else:
            self._metaInfo['url'] = self._url
            self._metaInfo['statusCode'] = response.statusCode
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
        '''
        self._matchFuncs['uri'] = self._matchUri
        self._matchFuncs['headers'] = self._matchHeaders
        self._matchFuncs['html'] = self._matchHtml
        self._matchFuncs['requests'] = self._matchRequests
        self._matchFuncs['robots'] = self._matchRobots



    def identify(self):
        self._result['meta'] = self._metaInfo







