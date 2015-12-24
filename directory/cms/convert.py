#!/usr/bin/env python
# coding: UTF-8

'''
Pentestdb, a database for penetration test.
Copyright (c) 2014-2015 alpha1e0
====================================================================================================
This script convert 'cms_fingerprint.txt' to json format file 'cms_fingerprint.json'.
The 'pen.py cms' subcommand will use 'cms_fingerprint.json' to identify the cms type.
'''


import json
from collections import OrderedDict


if __name__ == '__main__':
    source = open("cms_fingerprint.txt", "r")
    dest = open("cms_fingerprint.json", "w")    

    result = OrderedDict()  

    for line in source:
        line = line.strip()
        if line and not line.startswith("/**"):
            l = line.split()
            if not result.get(l[0], None):
                result[l[0]] = []   

            result[l[0]].append({"need":True if l[1]=="+" else False, "path":l[2], "pattern":None if len(l)==3 else l[3]})  

    #print result
    json.dump(result, dest, indent=4)   

    source.close()
    dest.close()
