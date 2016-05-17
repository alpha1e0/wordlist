#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
Pentestdb, a database for penetration test.
Copyright (c) 2014-2015 alpha1e0
========================================================
字符串编解码
'''


import os
import sys
import hashlib
import urllib
import base64
import codecs
import cgi
import HTMLParser
import codecs
import binascii
import re

import thirdparty.chardet as chardet



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



class FileError(Exception):
    def __init__(self, msg):
        self.msg = "FileError: " + msg
        
    def __str__(self):
        return self.msg


def utf7EncodeAll(code):
    utf16Encoded = code.encode('utf-16-be')
    result = base64.b64encode(utf16Encoded)
    return "+" + result.rstrip("=") + "-"


class Code(object):
    '''
    编解码模块
    input:
        code: the code to encode/decode
    '''
    decodeTypes = ['auto','hex','url','unicode','decimal','base64','base32','html','php-chr','utf7']
    encodeTypes = ['url','url-all','hex','decimal','unicode','unicode-all','md5','sha','base64','base32','html','html-all','php-chr','utf7','utf7-all']

    def __init__(self, code):
        self.code = code.strip()


    def _autoPreDecode(self, code=None):
        '''
        解码预处理，从原始code中识别出url编码子串、HEX编码子串、unicode编码、原始（ASCII）子串；
        返回token数组，数组中每个元素是一个子串，格式为[type, substring]，目前type支持"urlcode"、"hexcode"、"unicode"、"raw"
        '''
        code = code if code else self.code
        if "%" in code:
            code = code.replace("+"," ")

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
        code = code.replace("+"," ")
        
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
            if "," in self.code:
                tmp = [chr(int(x.strip())) for x in self.code.split(",")]
            else:
                tmp = [chr(int(x)) for x in self.code.split()]
            rawstr = "".join(tmp)
            try:
                return [rawstr.decode(dmethod)]
            except UnicodeDecodeError:
                return [repr(rawstr)]
        if dtype == 'base64':
            try:
                paddingLen = 4 - len(self.code)%4
                padding = paddingLen * "="
                basestr = base64.b64decode(self.code+padding)
                return [basestr.decode(dmethod)]
            except TypeError:
                raise DecodeError("base64 decode error")
            except UnicodeDecodeError:
                return [repr(basestr)]
        if dtype == 'base32':
            try:
                basestr = base64.b32decode(self.code)
                return [basestr.decode(dmethod)]
            except TypeError:
                raise DecodeError("base32 incorrect padding")
            except UnicodeDecodeError:
                return [repr(basestr)]

        if dtype == 'unicode':
            tokens = self._unicodePreDecode()
            return ["".join([x[1] for x in tokens])]

        if dtype == 'url':
            tokens = self._urlPreDecode()
            result = []
            tokenStr = "".join([x[1] for x in tokens])
            try:
                decodedStr = tokenStr.decode(dmethod)
            except UnicodeDecodeError:
                decodedStr = repr(tokenStr)

            return [decodedStr]
#            for token in tokens:
#                try:
#                    decodedStr = token[1].decode(dmethod)
#                except UnicodeDecodeError:
#                    decodedStr = repr(token[1])
#                result.append(decodedStr)
#            return ["".join(result)]

        if dtype == 'hex':
            tokens = self._hexPreDecode()
            result = []
            tokenStr = "".join([x[1] for x in tokens])
            try:
                decodedStr = tokenStr.decode(dmethod)
            except UnicodeDecodeError:
                decodedStr = repr(tokenStr)
            return [decodedStr]

        if dtype == 'html':
            htmpparser = HTMLParser.HTMLParser()
            return [htmpparser.unescape(self.code)]

        if dtype == 'auto':
            tokens = self._autoPreDecode(self.code)
            result = []
            tokenStr = "".join([x[1] for x in tokens])
            try:
                decodedStr = tokenStr.decode(dmethod)
            except UnicodeDecodeError:
                decodedStr = repr(tokenStr)
            return [decodedStr]

        if dtype == 'utf7':
            tokens = self._autoPreDecode(self.code)
            result = []
            tokenStr = "".join([x[1] for x in tokens])
            try:
                decodedStr = tokenStr.decode('utf7')
            except UnicodeDecodeError:
                decodedStr = repr(tokenStr)
            return [decodedStr]

        if dtype == 'php-chr':
            dlist = re.findall(r"\d+", self.code)
            hlist = [chr(int(x)) for x in dlist]
            rawstr = "".join(hlist)
            try:
                return [rawstr.decode(dmethod)]
            except UnicodeDecodeError:
                return [repr(rawstr)]

        raise DecodeError("unrecognized type, should be {0}".format(self.decodeTypes))


    def detect(self):
        rawstr = "".join([x[1] for x in self._autoPreDecode()])
        return chardet.detect(rawstr)


    def encode(self, etype=None, emethod=None):
        etype = etype.lower() if etype else "url"
        emethod = emethod.lower() if emethod else sys.stdout.encoding

        ecode = self.code.decode(sys.stdout.encoding).encode(emethod)

        if etype == 'md5':
            return [hashlib.md5(ecode).hexdigest()]
        if etype == 'sha':
            result = []
            result.append("sha1: " + hashlib.sha1(ecode).hexdigest() + "\n")
            result.append("sha224: " + hashlib.sha224(ecode).hexdigest() + "\n")
            result.append("sha256: " + hashlib.sha256(ecode).hexdigest() + "\n")
            result.append("sha384: " + hashlib.sha384(ecode).hexdigest() + "\n")
            result.append("sha512: " + hashlib.sha512(ecode).hexdigest() + "\n")
            return result
        if etype == 'base64':
            return [base64.b64encode(ecode)]
        if etype == 'base32':
            return [base64.b32encode(ecode)]
        
        if etype == 'hex':
            tmp1 = ['\\'+hex(ord(x))[1:] for x in ecode]
            tmp2 = ['0'+hex(ord(x))[1:] for x in ecode]
            return ["".join(tmp1), "".join(tmp2), ",".join(tmp2)]
        if etype == 'decimal':
            tmp = [str(ord(x)) for x in ecode]
            return [" ".join(tmp), ",".join(tmp)]

        if etype == 'unicode':
            return [codecs.raw_unicode_escape_encode(self.code.decode(sys.stdout.encoding))[0]]
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
            return [result]

        if etype == 'url':
            return [urllib.quote(ecode)]
        if etype == 'url-all':
            tmp = ['%'+hex(ord(x))[2:] for x in ecode]
            return ["".join(tmp)]

        if etype == 'html':
            return [cgi.escape(self.code, quote=True)]
        if etype == 'html-all':
            hexstr = ["&#"+hex(ord(x))[1:]+";" for x in self.code]
            decstr = ["&#"+str(ord(x))+";" for x in self.code]
            return ["".join(hexstr), "".join(decstr)]

        if etype == 'php-chr':
            tmp = ["chr({0})".format(ord(x)) for x in ecode]
            return [".".join(tmp)]

        if etype == 'utf7':
            return [self.code.decode(sys.stdout.encoding).encode('utf7')]

        if etype == 'utf7-all':
            return [utf7EncodeAll(self.code.decode(sys.stdout.encoding))]

        
        raise EncodeError("unrecognized type, should be {0}".format(self.encodeTypes))



class File(object):
    '''
    文件处理，编码推断/编码转换/hash计算/jpg隐藏
    '''
    hashMethod = ["md5","sha","sha1","sha224","sha256","sha384","sha512","crc32"]
    _bomList = {
        "utf-8": codecs.BOM_UTF8,
        "utf-16": codecs.BOM_UTF16,
        "utf-16le": codecs.BOM_UTF16_LE,
        "utf-16be": codecs.BOM_UTF16_BE,
        "utf-32": codecs.BOM_UTF32,
        "utf-32le": codecs.BOM_UTF32_LE,
        "utf-32be": codecs.BOM_UTF32_BE,
    }

    def __init__(self, fileName, fileType):
        self.fileName = fileName
        if not os.path.exists(self.fileName):
            raise FileError("file '{0}' not exists".format(os.path.abspath(self.fileName)))

        self.fileType = fileType if fileType else self.detect()['encoding']


    def __eq__(self, dstFile):
        if isinstance(dstFile, File):
            return self.hash() == dstFile.hash()
        elif isinstance(dstFile, basestring):
            return self.hash() == File(dstFile).hash
        else:
            return False


    def detect(self, size=2048):
        '''
        文件编码类型推断
        '''
        content = open(self.fileName,"rb").read(size)
        result = dict()
        for key,value in self._bomList.iteritems():
            if content.startswith(value):
                result['encoding'] = key + "-bom"
                result['confidence'] = 0.80
                break
        else:
            result = chardet.detect(content)

        return result


    def hash(self, method="md5"):
        '''
        文件hash计算
        '''
        content = open(self.fileName,"rb").read()
        if method == "md5":
            return hashlib.md5(content).hexdigest()
        if method == "sha" or method == "sha1":
            return hashlib.sha1(content).hexdigest()
        if method == "sha224":
            return hashlib.sha224(content).hexdigest()
        if method == "sha256":
            return hashlib.sha256(content).hexdigest()
        if method == "sha384":
            return hashlib.sha384(content).hexdigest()
        if method == "sha512":
            return hashlib.sha512(content).hexdigest()
        if method == "crc32":
            return "{0:x}".format(binascii.crc32(content) & 0xffffffff)
    

    def hide(self, srcFile, dstFile):
        '''
        文件隐藏，将一个文件追加到图片文件后面
        '''
        hideData = open(self.fileName,"rb").read()
        with open(srcFile, "rb") as fd:
            srcData = fd.read()
        with open(dstFile, "wb") as fd:
            fd.write(srcData)
            fd.write(hideData)


    @property
    def convertType(self):
        convertList = list()
        for key in self._bomList:
            convertList.append(key)
            convertList.append(key+"-bom")

        return convertList + ["gbk","gb2312","big5","..."]


    def convert(self, dstFile, dstType):
        '''
        文件类型转换
        Input:
            dstFile: 目标文件
            dstType: 目标类型
        '''
        dstType = dstType.strip().lower()
        if dstType.startswith("utf"):
            bomed = True if dstType.endswith("-bom") else False
            dstType = dstType.replace("-bom","") if bomed else dstType
            dstType = "utf-16le" if dstType=="utf-16" else dstType
            dstType = "utf-32le" if dstType=="utf-32" else dstType
            srcContent = open(self.fileName).read()

            try:
                dstContent = srcContent.decode(self.fileType).encode(dstType)
            except LookupError as error:
                raise FileError("encode/decode type error, '{0}'".format(str(error)))

            bom = ""
            if bomed:
                for key in self._bomList:
                    if dstType.startswith(key):
                        bom = self._bomList[key]
                        break
                else:
                    raise FileError("file type '{0}' not support".format(dstType))
            else:
                bom = ""

            with open(dstFile, "wb") as fd:
                fd.write(bom + dstContent)

        elif dstType == "base32":
            srcContent = open(self.fileName).read()
            dstContent = base64.b32encode(srcContent)
            with open(dstFile,'w') as fd:
                fd.write(dstContent)

        elif dstType == "base64":
            srcContent = open(self.fileName).read()
            dstContent = base64.b64encode(srcContent)
            with open(dstFile,'w') as fd:
                fd.write(dstContent)

        else:
            srcContent = open(self.fileName).read()
            try:
                dstContent = srcContent.decode(self.fileType).encode(dstType)
            except LookupError:
                raise FileError("encode/decode type error, '{0}'".format(str(error)))
            with open(dstFile, "wb") as fd:
                fd.write(dstContent)
