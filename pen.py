#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
Pentestdb, a database for penetration test.
Copyright (c) 2014-2015 alpha1e0
'''

import sys
import argparse

from script.libs.commons import exceptionHook
from script.penfuncs import doCMSIdentify
from script.penfuncs import doGenPassword
from script.penfuncs import doURIBrute
from script.penfuncs import doExploit
from script.penfuncs import doEncode
from script.penfuncs import doDecode
from script.penfuncs import doFileOp
from script.penfuncs import doGoogleHacking



reload(sys)
sys.setdefaultencoding("utf8")


if __name__ == "__main__":
    sys.excepthook = exceptionHook

    parser = argparse.ArgumentParser(description=u"渗透测试辅助工具")
    subparser = parser.add_subparsers(title=u"子命令", description=u"使用子命令，使用 'pen.py 子命令 -h' 获得子命令帮助")

    # cms identify
    cms = subparser.add_parser("cms", help=u"CMS 识别")
    cms.add_argument("url", help=u"指定目的URL")
    cms.add_argument("--notfound", help=u"自定义notfound页面关键字")
    cms.set_defaults(func=doCMSIdentify)

    # password generate
    passwdgen = subparser.add_parser("password", help=u"社会工程密码字典生成")
    passwdgen.add_argument("--fullname", help=u"指定姓名汉语拼音全拼, 例如: 'zhang san' 'lin zhi ling'")
    passwdgen.add_argument("--nickname", help=u"指定昵称")
    passwdgen.add_argument("--englishname", help=u"指定英文名，例如: 'alice' 'tom'")
    passwdgen.add_argument("--partnername", help=u"指定爱人姓名汉语拼音全拼")
    passwdgen.add_argument("--birthday", help=u"指定生日, 格式: '2000-1-10'")
    passwdgen.add_argument("--phone", help=u"指定手机号")
    passwdgen.add_argument("--qq", help=u"指定QQ号")
    passwdgen.add_argument("--company", help=u"指定公司名")
    passwdgen.add_argument("--domain", help=u"指定域名")
    passwdgen.add_argument("--oldpasswd", help=u"指定老密码")
    passwdgen.add_argument("--keywords", help=u"指定关键字列表, 例如: 'keyword1 keyword2'")
    passwdgen.add_argument("--keynumbers", help=u"指定关键数字, 例如: '123 789'")
    passwdgen.add_argument("-o","--output", help=u"指定输出文件")
    passwdgen.set_defaults(func=doGenPassword)

    # uri bruteforce
    uribrute = subparser.add_parser("uribrute", help=u"URI资源爆破，支持网站备份文件爆破、配置文件爆破、敏感目录爆破、后台爆破", \
        description=u"URI资源爆破，支持网站备份文件爆破、配置文件爆破、敏感目录爆破、后台爆破")
    uribrute.add_argument("-g","--generate", help=u"生成字典文件")
    uribrute.add_argument("-t","--types", help=u"指定字典生成类型，以逗号分隔，支持{0}，默认使用所有类型，例如：-t webbak,cfgbak".format(str(URIBruter.allowTypes)))
    uribrute.add_argument("-k","--keywords", help=u"自定义关键字，以逗号分隔，该项仅影响生成备份文件爆破字典")
    uribrute.add_argument("-e","--exts", help=u"自定义文件后缀名，以逗号分隔，默认为php，例如：-e php,asp,aspx,jsp,html")
    uribrute.add_argument("-u", "--url", help=u"指定目的URL，或@file指定URL列表文件，如不指定则只生成字典文件")
    uribrute.add_argument("-b","--brute", action="store_true", help=u"生成字典文件")
    uribrute.add_argument("--size", help=u"指定生成字典的大小，目前只支持small和large，默认为small")
    uribrute.add_argument("--notfound", help=u"自定义notfound页面关键字")
    uribrute.add_argument("--safeurl", help=u"自定义安全URL，用于bypass安全软件")    
    uribrute.add_argument("--timeout", help=u"指定http请求超时事件, 默认为 10", type=int)
    uribrute.add_argument("--delay", help=u"指定http请求间隔时间, 默认无间隔", type=float)
    #uribrute.add_argument("--encode", help=u"指定url非ASCII编码方式, 默认为UTF-8")
    uribrute.set_defaults(func=doURIBrute)

    # exploit
    exploit = subparser.add_parser("exploit", help=u"exploit，批量exploit执行、exploit管理")
    # exploit 管理
    expManage = exploit.add_argument_group(u'exploit管理')
    expManage.add_argument("--createdb", action="store_true", help=u"创建exploit信息数据库")
    expManage.add_argument("--register", help=u"指定exploit目录或exploit文件注册exploit信息")
    expManage.add_argument("--update", help=u"根据exploit文件更新exploit注册信息")
    expManage.add_argument("--delete", help=u"根据exploit名字删除exploit注册信息")
    expManage.add_argument("-q", "--query", help=u"搜索exploit，参数格式column:keyword，column支持expName/os/webserver/language/appName，默认为expName")
    expManage.add_argument("-l", "--list", action="store_true", help=u"列举所有exploit")
    expManage.add_argument("--detail", help=u"根据exploit名称显示某个exploit的详细信息")
    # exploit 执行
    expExec = exploit.add_argument_group(u'exploit执行')
    expExec.add_argument("-e","--execute", help=u"exploit执行，参数格式column:keyword，column支持expName/os/webserver/language/appName，默认为expName")
    expExec.add_argument("-u", "--url", help=u"指定目标URL，使用@file指定url列表文件")
    expExec.add_argument("--verify", action="store_true", help=u"验证模式")
    expExec.add_argument("--attack", action="store_true", help=u"攻击模式")
    expExec.add_argument("--cookie", help=u"指定Cookie")
    expExec.add_argument("--useragent", help=u"指定UserAgent")
    expExec.add_argument("--referer", help=u"指定referer")
    expExec.add_argument("--header", help=u"指定其他HTTP header,例如--header 'xxx=xxxx#yyy=yyyy'")
    expExec.add_argument("--elseargs", help=u"指定其他参数,例如--elseargs 'xxx=xxxx#yyy=yyyy'")
    expManage.set_defaults(func=doExploit)

    # encode
    encode = subparser.add_parser("encode", help=u"编码工具", \
        description=u"编码工具，支持的编码种类有:{0}".format(" ".join(Code.encodeTypes)))
    encode.add_argument("code", help=u"待编码字符串，建议用引号包括")
    encode.add_argument("-t", "--type", help=u"指定编码种类")
    encode.add_argument("-m", "--method", help=u"指定非ASCII字符编码方式，例如：utf8、gbk")
    encode.set_defaults(func=doEncode)

    # decode
    decode = subparser.add_parser("decode", help=u"解码工具", \
        description=u"解码工具，支持的解码种类有: {0}，其中html不能和其他编码混合".format(" ".join(Code.decodeTypes)), \
        epilog="示例:\n  pen.py decode -m utf8 target\\x3Fid\\x3D\\xC4\\xE3\\xBA\\xC3\n  pen.py decode -t decimal '116 97 114 103 101 116 63 105 100 61 196 227 186 195'", \
        formatter_class=argparse.RawDescriptionHelpFormatter)
    decode.add_argument("code", default="hello", help=u"解码字符串，例如：ASCII、URL编码，\\xaa\\xbb、0xaa0xbb、\\uxxxx\\uyyyy、混合编码")
    decode.add_argument("-t", "--type", help=u"指定解码种类，建议用引号包括")
    decode.add_argument("-m", "--method", help=u"指定非ASCII字符解码方式，例如：utf8、gbk")
    decode.set_defaults(func=doDecode)

    # file操作
    fileop = subparser.add_parser("file", help=u"文件处理", \
        description=u"文件处理工具，支持文件编码转换、文件编码类型检测、文件hash计算、文件隐藏")
    fileop.add_argument("file", help=u"指定待处理文件")
    fileop.add_argument("--method", help=u"手工指定文件编码类型")
    fileop.add_argument("--dfile", help=u"指定目标文件")
    fileop.add_argument("-d", "--detect", action="store_true", help=u"文件编码类型检测")
    fileop.add_argument("--size", type=int, help=u"文件编码检测指定检测长度，默认为2048字节")
    fileop.add_argument("-c", "--convert", action="store_true", help=u"文件编码类型转换")
    fileop.add_argument("--dtype", help=u"文件编码转换指定目标编码类型，使用--list查看支持格式")
    fileop.add_argument("--list", action="store_true", help=u"显示编码转换支持的格式")
    fileop.add_argument("--hash", help=u"文件hash计算，支持{0}".format("/".join(File.hashMethod)))
    fileop.add_argument("--hfile", help=u"文件隐藏指定用来隐藏的图片文件")
    fileop.set_defaults(func=doFileOp)

    # google hacking功能
    gh = subparser.add_parser("search", help=u"Google Hacking功能，批量google hacking，生成字典")
    gh.add_argument("keywords", help=u"指定搜索关键字，windows下引号通过两个引号转义特殊字符")
    gh.add_argument("-e", "--engine", help=u"指定搜索引擎，目前支持baidu/bing/google，默认使用baidu")
    gh.add_argument("-s", "--size", type=int, help=u"指定搜索返回条目数，默认为200条")
    gh.add_argument("-o", "--output", help=u"指定输出文件，输出文件为URL列表")
    gh.add_argument("--unique", action="store_true", help=u"设置domain唯一")
    gh.set_defaults(func=doGoogleHacking)

    args = parser.parse_args()
    args.func(args)


