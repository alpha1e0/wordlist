#!/usr/local/env python
#coding: UTF-8

'''
Pentestdb, a database for penetration test.
Copyright (c) 2014-2015 alpha1e0
==================================================================================
URI bruteforce.
bruteforce backup files, configure files, consoles and other interesting files.
'''

import json

import requests


# 生成字典的时候，允许用户自定义keyword(例如domain)
class URIBruter(object):
    '''
    URI bruteforce.
    Input:
        stype: specify the server type, support asp/php/java. when stype is 'None', user all server types.
    '''
    def __init__(self, stype=None, keywords=None):
        self.stype = stype
        pass


    def genBKFDict(self):
        pass


    def genCFGDict(self):
        pass


    def genConsoleDict(self):
        pass


    def 