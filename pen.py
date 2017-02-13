#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
Pentestdb, a database for penetration test.
Copyright (c) 2015 alpha1e0
'''


try:
    from pentest.penfuncs import main
except ImportError:
    print u"pentest未安装，请先安装后使用"


if __name__ == "__main__":
    main()

