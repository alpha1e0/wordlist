#!/usr/bin/env python
# coding: UTF-8

'''
Pentestdb, a database for penetration test.
Copyright (c) 2014-2015 alpha1e0
'''


import os
import json


class CMSIdentify(object):
    def __init__(self, fingerprintFile=None):
        self.fpfile = fingerprintFile if fingerprintFile else os.path.join("directory","cms","cms_identify.json")
        pass