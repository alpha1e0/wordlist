#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
Pentestdb, a database for penetration test.
Copyright (c) 2014-2015 alpha1e0
=============================================================
服务识别模块
'''

from commons import URL

class Service(object):
    '''
    Identify the Web Application.
    html，robots在需要的时候加载，并保存为metainfo，metainfo最好封装一下
    '''
    def __init__(self, url):
        self.url = url

        self._metaInfo = dict()


    def init(self):
        '''
        初始化metaInfo，下载页面，将信息提取出来
        初始化指纹信息库
        初始化“处理函数表”
        '''

    def identify(self):