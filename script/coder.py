#!/usr/bin/env python
# coding: UTF-8

'''
Pentestdb, a database for penetration test.
Copyright (c) 2014-2015 alpha1e0
========================================================
字符串编解码
'''

import sys

def decode(ctype, code):
    result = "".join([chr(int(x,16)) for x in code.strip("%").split("%")])
    print result.decode(ctype)


class Coder(object):
    '''
    '''
    typeList = ['utf8','utf-8','gbk','gb2312','utf7','utf-7']

    def __init__(self, code):
        self.code = code
        self.codeList = []


    def _preDecode(self, code):
        clen = len(code)
        current = code[0]
        self.codeList.append("")
        i = 0
        while i<clen:
            if code[i] == '%':
                if current == '%':
                    self.codeList[len(self.codeList)-1] += chr(int(code[i+1:i+3],16))
                else:
                    current = '%'
                    self.codeList.append(chr(int(code[i+1:i+3],16)))
                i += 3
            elif code[i:i+2] == '\\x':
                if current == "\\":
                    self.codeList[len(self.codeList)-1] += chr(int(code[i+2:i+4],16))
                else:
                    current = '\\'
                    self.codeList.append(chr(int(code[i+2:i+4],16)))
                i += 4
            else:
                if current != '%' and current != '%':
                    self.codeList[len(self.codeList)-1] += code[i]
                else:
                    current = code[i]
                    self.codeList.append(code[i:i+1])
                i += 1


    def decode(self, dtype):
        result = ""
        self._preDecode(self.code)
        for item in self.codeList:
            result += item.decode(dtype)

        return result


    def encode(self, etype):
        return str(self.code.encode(etype))


if __name__ == '__main__':
    #code = "short_desc=show+ssl\\xE4\\xBC\\x9A%E8%AF%9D%E4%BF%9D%E6%8C%81%E8%A1%A8%E9%A1%B9%E7%9A%84%E6%97%B6%E5%80%99%EF%BC%8Cclear%E8%A1%A8%E9%A1%B9%EF%BC%8Cvtysh%E8%BF%9B%E7%A8%8B%E9%98%BB%E5%A1%9E"
    coder = Coder(sys.argv[1])
    
    print sys.argv[1]
    #coder._preDecode(sys.argv[1])
    print coder.codeList
    print coder.decode(sys.argv[2])