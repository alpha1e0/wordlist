#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
Pentestdb, a database for penetration test.
Copyright (c) 2014-2015 alpha1e0
'''

import sys
import argparse

from script.penfuncs import main


reload(sys)
sys.setdefaultencoding("utf8")


if __name__ == "__main__":
    main()

