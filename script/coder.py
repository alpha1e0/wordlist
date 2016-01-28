#!/usr/bin/env python
# coding: UTF-8

'''
Pentestdb, a database for penetration test.
Copyright (c) 2014-2015 alpha1e0
========================================================
字符串编解码
'''

import sys
import hashlib
import urllib
import base64
import codecs
import cgi
import HTMLParser

import chardet


class DecodeError(Exception):
    def __init__(self, msg):
        self.msg = "DecodeError: " + msg

    def __str__(self):
        return self.msg


class EncodeError(Exception):
    def __init__(self, msg):
        self.msg = "EncodeError: " + msg
        
    def __str__(self):
        return self.msg


class Code(object):
    '''
    编解码模块
    input:
        code: the code to encode/decode
    '''
    decodeTypes = ['auto','hex','url','unicode','decimal','base64','html']
    decodeMethods = ['utf-8','gbk','gb2312','utf-7']
    encodeTypes = ['url','url-all','hex','decimal','unicode','unicode-all','md5','base64','html','html-all']
    encodeMethods = ['utf-8','gbk','gb2312','utf-7']

    def __init__(self, code):
        self.code = code.strip()


    def _autoPreDecode(self, code=None):
        '''
        解码预处理，从原始code中识别出url编码子串、HEX编码子串、原始（ASCII）子串；返回token数组，数组中每个元素是
        一个子串，格式为[type, substring]，目前type支持"urlcode"、"hexcode"、"unicode"、"raw"
        '''
        code = code if code else self.code

        current = code[0]=='%' and 'urlcode' or code[0:2]=='\\x' and 'hexcode' or code[0:2]=='\\u' and 'unicode' or 'raw'
        tokens = []
        tokens.append([current, ""])
        i = 0
        while i<len(code):
            if code[i] == '%':
                if current == 'urlcode':
                    tokens[len(tokens)-1][1] += chr(int(code[i+1:i+3],16))
                else:
                    current = 'urlcode'
                    tokens.append([current, chr(int(code[i+1:i+3],16))])
                i += 3
            elif code[i:i+2].lower() == '\\x' or code[i:i+2] == '0x':
                if current == "hexcode":
                    tokens[len(tokens)-1][1] += chr(int(code[i+2:i+4],16))
                else:
                    current = 'hexcode'
                    tokens.append([current, chr(int(code[i+2:i+4],16))])
                i += 4
            elif code[i:i+2].lower() == '\\u':
                if current == "unicode":
                    tokens[len(tokens)-1][1] += codecs.raw_unicode_escape_decode(code[i:i+6])[0]
                else:
                    current = 'unicode'
                    tokens.append([current, codecs.raw_unicode_escape_decode(code[i:i+6])[0]])
                i += 6
            else:
                if current not in ['urlcode','hexcode','unicode']:
                    tokens[len(tokens)-1][1] += code[i]
                else:
                    current = 'raw'
                    tokens.append([current, code[i:i+1]])
                i += 1

        return tokens


    def _urlPreDecode(self, code=None):
        code = code if code else self.code
        
        current = code[0]=='%' and 'urlcode' or 'raw'
        tokens = []
        tokens.append([current, ""])
        i = 0
        while i<len(code):
            if code[i] == '%':
                if current == 'urlcode':
                    tokens[len(tokens)-1][1] += chr(int(code[i+1:i+3],16))
                else:
                    current = 'urlcode'
                    tokens.append([current, chr(int(code[i+1:i+3],16))])
                i += 3
            else:
                if current != 'urlcode':
                    tokens[len(tokens)-1][1] += code[i]
                else:
                    current = 'raw'
                    tokens.append([current, code[i:i+1]])
                i += 1

        return tokens


    def _hexPreDecode(self, code=None):
        code = code if code else self.code
        
        current = code[0:2]=='\\x' and 'hexcode' or 'raw'
        tokens = []
        tokens.append([current, ""])
        i = 0
        while i<len(code):
            if code[i:i+2].lower() == '\\x' or code[i:i+2] == '0x':
                if current == "hexcode":
                    tokens[len(tokens)-1][1] += chr(int(code[i+2:i+4],16))
                else:
                    current = 'hexcode'
                    tokens.append([current, chr(int(code[i+2:i+4],16))])
                i += 4
            else:
                if current != 'hexcode':
                    tokens[len(tokens)-1][1] += code[i]
                else:
                    current = 'raw'
                    tokens.append([current, code[i:i+1]])
                i += 1

        return tokens


    def _unicodePreDecode(self, code=None):
        code = code if code else self.code

        current = code[0:2]=='\\u' and 'unicode' or 'raw'
        tokens = []
        tokens.append([current, ""])
        i = 0
        while i<len(code):
            if code[i:i+2].lower() == '\\u':
                if current == "unicode":
                    tokens[len(tokens)-1][1] += codecs.raw_unicode_escape_decode(code[i:i+6])[0]
                else:
                    current = 'unicode'
                    tokens.append([current, codecs.raw_unicode_escape_decode(code[i:i+6])[0]])
                i += 6
            else:
                if current != 'unicode':
                    tokens[len(tokens)-1][1] += code[i]
                else:
                    current = 'raw'
                    tokens.append([current, code[i:i+1]])
                i += 1

        return tokens


    def decode(self, dtype=None, dmethod=None):
        dtype = dtype.lower() if dtype else 'auto'
        dmethod = dmethod.lower() if dmethod else sys.stdout.encoding

        if dtype == 'decimal':
            tmp = [chr(int(x)) for x in self.code.split()]
            return "".join(tmp).decode(dmethod)
        if dtype == 'base64':
            try:
                return base64.b64decode(self.code).decode(dmethod)
            except TypeError:
                raise DecodeError("base64 incorrect padding")

        if dtype == 'unicode':
            tokens = self._unicodePreDecode()
            return "".join([x[1] for x in tokens])

        if dtype == 'url':
            tokens = self._urlPreDecode()
            result = []
            for token in tokens:
                try:
                    decodedStr = token[1].decode(dmethod)
                except UnicodeDecodeError:
                    decodedStr = '*' * len(token)
                result.append(decodedStr)
            return "\n".join(result)

        if dtype == 'hex':
            tokens = self._hexPreDecode()
            result = []
            for token in tokens:
                try:
                    decodedStr = token[1].decode(dmethod)
                except UnicodeDecodeError:
                    decodedStr = '*' * len(token)
                result.append(decodedStr)
            return "\n".join(result)

        if dtype == 'html':
            htmpparser = HTMLParser.HTMLParser()
            return htmpparser.unescape(self.code)

        if dtype == 'auto':
            tokens = self._autoPreDecode(self.code)
            result = []
            for token in tokens:
                try:
                    decodedStr = token[1] if token[0] == 'unicode' else token[1].decode(dmethod)
                except UnicodeDecodeError:
                    decodedStr = '*' * len(token)
                result.append(decodedStr)

            return "\n".join(result)

        raise DecodeError("unrecognized type, should be {0}".format(self.decodeTypes))


    def detect(self):
        hexstr = "".join([x[1] for x in self._hexPreDecode() if x[0]=='hexcode'])
        urlstr = "".join([x[1] for x in self._urlPreDecode() if x[0]=='urlcode'])
        rawstr = hexstr + urlstr

        return chardet.detect(rawstr)


    def encode(self, etype=None, emethod=None):
        etype = etype.lower() if etype else "url"
        emethod = emethod.lower() if emethod else sys.stdout.encoding

        if etype == 'md5':
            return hashlib.md5(self.code.decode(sys.stdout.encoding).encode(emethod)).hexdigest()
        if etype == 'base64':
            return base64.b64encode(self.code.decode(sys.stdout.encoding).encode(emethod))

        ecode = self.code.decode(sys.stdout.encoding).encode(emethod)
        if etype == 'hex':
            tmp = ['\\'+hex(ord(x))[1:] for x in ecode]
            return "".join(tmp)
        if etype == 'decimal':
            tmp = [str(ord(x)) for x in ecode]
            return " ".join(tmp)

        if etype == 'unicode':
            return codecs.raw_unicode_escape_encode(self.code.decode(sys.stdout.encoding))[0]
        if etype == 'unicode-all':
            result = ""
            tmp = codecs.raw_unicode_escape_encode(self.code.decode(sys.stdout.encoding))[0]
            current = 'unicode' if tmp[:2] == '\\u' else "raw"
            i = 0
            while i<len(tmp):
                if tmp[i:i+2].lower() == '\\u':
                    result += tmp[i:i+6]
                    if current != "unicode":
                        current = 'unicode'
                    i += 6
                else:
                    result += "\\u00" + hex(ord(tmp[i]))[2:]
                    if current != 'raw':
                        current = 'raw'
                    i += 1
            return result

        if etype == 'url':
            return urllib.quote(self.code.decode(sys.stdout.encoding).encode(emethod))
        if etype == 'url-all':
            tmp = ['%'+hex(ord(x))[2:] for x in ecode]
            return "".join(tmp)

        if etype == 'html':
            return cgi.escape(self.code, quote=True)
        if etype == 'html-all':
            hexstr = ["&#"+hex(ord(x))[1:]+";" for x in self.code]
            decstr = ["&#"+str(ord(x))+";" for x in self.code]
            return "".join(hexstr) + "\n\n" + "".join(decstr)
        
        raise EncodeError("unrecognized type, should be {0}".format(self.encodeTypes))

