# PentestDB

## 1 介绍

本项目用于提供渗透测试的**辅助工具**、**资源文件**

**1、辅助工具**

提供轻量级的易扩展的工具，可以快速编写exploit、添加漏洞验证/扫描规则、添加指纹规则、爆破规则等；包含以下功能：

* Exploit系统。易扩展的exploit系统，可批量执行exploit
* 子域名爆破。爆破子域名，使用域传送、DNS爆破、GoogleHacking进行子域名爆破
* C段扫描。C段扫描，支持生成html格式输出文件
* CMS识别。识别CMS类型
* URI敏感资源爆破。爆破WEB敏感文件，整站备份、配置备份、敏感文件等
* 社工密码字典生成。根据社工信息生成密码爆破字典
* Google Hacking。GoogleHacking，生成URL字典
* 编解码等功能。支持非常丰富的编解码方式，方便做payload编码绕过

**2、资源文件**

各种渗透测试常用的资源文件，包括各种爆破字典、exploit、webshell、攻击payload等

---

## 2 安装

从[这里](https://github.com/alpha1e0/pentestdb)下载最新版本，或使用命令

    git clone https://github.com/alpha1e0/pentestdb.git

clone到本地

PentestDB支持Windows/Linux/MacOS，需使用python **2.6.x** 或 **2.7.x**运行

### 2.1 解决lxml依赖

项目中的脚本文件依赖于*lxml*

linux系统一般默认安装lxml，如果没有可通过以下方式安装：

    pip install lxml
    apt-get install lxml
    yum install lxml

windows可通过以下方式安装lxml：

1. 到[这里](http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml)找到对应系统的安装包，下载到本地
2. 安装安装包，pip install package.whl

### 2.2 解决nmap依赖

项目中的C段扫描依赖于*nmap扫描器*

到[这里](https://nmap.org/download.html)下载nmap相应版本

在windows下需要设置环境变量，让系统能够找到nmap.exe

---

## 3 使用

### 3.1 常用脚本

项目中的python脚本提供用有用的渗透辅助功能，根目录下的**pen.py**为脚本入口，另外script目录下也有其他一些脚本。

#### 3.1.1 Exploit系统

`pen.py`的**exploit**子命令提供了exploit模块相关操作，exploit模块是一个轻量级的exploit框架，可以编写各种web漏洞的exploit：

* 搜索exploit信息
* 增加、删除、修改exploit信息
* 执行某个exploit
* 搜索并批量执行exploit

exploit保存在项目根目录下的*exploit*目录下

例如：

    # 列举、搜索、注册、更新、删除
    pen.py exploit -l
    pen.py exploit -q appName:joomla
    pen.py exploit --register exploit
    pen.py exploit --update cms_joomla_3_4_session_object_injection.py
    pen.py exploit -d "Joomla 1.5~3.4 session对象注入漏洞exploit"
    pen.py exploit --detail "Joomla 1.5~3.4 session对象注入漏洞exploit"

    # 执行exploit
    pen.py exploit -e cms_joomla_3_4_session_object_injection.py -u http://127.0.0.1:1234 --attack
    pen.py exploit -s appName:joomla -u http://127.0.0.1:1234 --verify
    pen.py exploit -s appName:joomla -u @url.txt

#### 3.1.2 CMS识别

`pen.py`的**cms**子命令提供了CMS识别的功能，目前能够识别以下CMS类型：

    drupal discuz empirecms dedecms joomla phpcms phpwind qibo wordpress

例如：

    pen.py cms http://xxx.com

#### 3.1.3 社工密码字典生成

`pen.py`的**password**子命令提供了根据社工信息生成密码字典的功能，能够设置不同关键字生成密码字典

该模块可通过以下要素组合生成密码：

* 全名，--fullname，名字中各个字中间加空格，例如"lin zhi ling"
* 昵称，--nickname
* 英文名称，--englishname
* 伴侣名字，--partnername
* 生日，--birthday
* 手机号，--phone
* QQ号，--qq
* 公司名称，--company
* 域名，--domian
* 老密码，--oldpasswd
* 关键字，--keyword
* 关键数字，--keynumbers

例如：

    pen.py passwdgen --fullname "lin zhi ling" --birthday 1980-1-1 --phone 12344445555 --qq 34233888 -o password.txt

#### 3.1.4 URI敏感文件爆破

`pen.py`的**uribrute**子命令提供了URI敏感文件爆破，URI爆破字典生成的功能

例如：
    
    # 生成web打包备份、敏感文件字典，后缀名使用jsp和jspx，自定义关键字xxx，指定输出结果dict.txt
    pen.py uribrute -t webbak,interestfile -e jspx,jsp --keyword "xxx" -o dict.txt

    # 爆破目标站点，使用safeurl bypass waf
    pen.py uribrute -b -u http://127.0.0.1/discuz/6.0/ --safeurl "http://127.0.0.1/discuz/6.0/"

    # 爆破url.txt中的所有站点，爆破敏感文件，自定义notfound页面关键字为“找不到页面”
    pen.py uribrute -b -u @urls.txt -t interestfile --notfound "找不到页面"
    

#### 3.1.5 Google Hacking功能

`pen.py`的**search**子命令提供了Google Hacking的功能，目前支持以下搜索引擎：

* baidu
* bing
* google

例如：
    
    pen.py search "inurl:viewthread.php" -s 10 -o tmp.txt

    # --unique设定域名唯一，相同域名只记录一个搜索结果
    pen.py search "inurl:viewthread.php" -s 10 --unique -o tmp.txt

#### 3.1.6 子域名爆破

`pen.py`的**domain**子命令提供了子域名爆破功能：

该模块使用3种技术进行子域名爆破：

* 域传送漏洞检测、利用
* DNS字典爆破
* Google Hacking搜索

注：支持输出到html文件，使用*-o xxx.html*做为输出文件即可

例如：
    
    # 使用域传送技术、Google Hacking对aaa.com 进行子域名爆破
    pen.py domamin aaa.com -t zg

    # 使用字典爆破子域名，自定义字典文件domain_large.txt，同时指定爆破顶级域名
    pen.py domain aaa.com -t d --dict domain_large.txt --topdomian

#### 3.1.7 C段扫描

`pen.py`的**subnet**子命令提供了C段扫描功能。

注：支持输出到html文件，使用*-o xxx.html*做为输出文件即可

例如：

    pen.py subnet test.com -o result.html

#### 3.1.8 编码

`pen.py`的**encode**子命令提供了编码的功能

编码方式*-t/--type*支持：

> url url-all hex decimal unicode unicode-all md5 sha base64 base32 html html-all php-chr utf7 utf7-all

> 其中**-all编码会编码所有字符包括非特殊字符

非ASCII编码*-m/--method*支持：

> utf8 gbk gb2312 big5 utf16 utf7 等所有python支持的编码方式，具体请参考如下链接：

> [python支持的编解码格式](https://docs.python.org/2/library/codecs.html)


例如：

    pen.py encode -t unicode "aaa=你好"
    pen.py encode -t url-all -m gbk "id=你好"
    pen.py encode -t md5 "aaaaaaaa"

#### 3.1.9 解码

`pen.py`的**decode**子命令提供了解码的功能，并提供非ASCII编码编码推测功能

解码方式*-t/--type*支持：

> auto(默认) hex url unicode decimal base64 base32 html php-chr utf7

> 其中*auto*方式会自动检测url类型、hex类型的字符串并进行解码

非ASCII编码*-m/--method*支持：

> utf8 gbk gb2312 big5 utf16 utf7 等所有python支持的编码方式，具体请参考如下链接：

> [python支持的编解码格式](https://docs.python.org/2/library/codecs.html)

例如：

    pen.py decode -t base64 5ZOI5ZOI
    pen.py decode -m utf8 aaa%E5%93%88%E5%93%88
    pen.py encode -t hex "\x61\x61\xe5\x93\x88\xe5\x93\x88"

    # 推测编码
    pen.py decode -d "\x61\x61\xe5\x93\x88\xe5\x93\x88"

#### 3.1.10 文件处理功能

`pen.py`的**file**子命令提供了常用的文件操作，包括：文件编码推断、文件类型转换、文件hash计算、文件图片隐藏(制作php图片木马)

使用*--list*查看支持的文件编码格式，文件编码转换格式*--dtype*支持：

>  utf-32le utf-32le-bom utf-32 utf-32-bom utf-32be utf-32be-bom utf-16be utf-16be-bom utf-8 utf-8-bom utf-16 utf-16-bom utf-16le utf-16le-bom gbk gb2312 big5 ...

例如：

    pen.py file cmdb.jsp -d
    pen.py file cmdb.jsp --hash md5
    
    # 文件转换，转换为utf-16-bom类型文件(jsp/aspx的utf-16-bom类型文件可绕过一些安全软件)
    pen.py file cmd.jsp -c --dtype utf-16-bom --dfile dst.jsp

    # 制作图片木马
    pen.py file caidao.php --hfile aa.jpg --dfile picshell.jpg


#### 3.1.11 Mail账户验证/爆破

`script/mail.py`提供简单的Mail账户验证、爆破功能：

例如：

    # 验证/tmp/maillist.txt中的Mail账户
    mail.py -c -a @/tmp/maillist.txt

    # 爆破邮箱
    mail.py -b -u @mail.txt -p @pass.txt


#### 3.1.12 字典维护

`script/wordlist.py`提供了字典文件维护的功能，包括：

* 将多个字典文件merge到数据库中
* 对每个字典项进行*打分*计算
* 按照评分高低导出字典文件

例如：

    # 按照评分高低从数据库password.db中导出字典文件pass.txt，长度为100
    wordlist.py -d pass.txt ../user-password/password/password.db -s 100

    # 将字典文件test.txt merge 到数据库password.db中，重复项分值+1
    wordlist.py -l test.txt ../user-password/password/password.db

---

### 3.2 user-passwd字典

**password**目录包含密码字典文件

**user**目录包含用户名字典文件

---

### 3.3 dns字典

dns爆破字典

### 3.4 directory字典

web目录爆破字典，详见相关目录*readme.md*文件

### 3.5 attack-payload

各种攻击payload字典，详见相关目录*readme.md*文件

### 3.6 webshell

webshell收集，详见相关目录*readme.md*文件

### 3.7 script

常用脚本

### 3.8 exploit

一些有用的exploit，详见相关目录*readme.md*文件


---

## 4 备注

项目中的字典等文件统一使用“/**”作为注释符，注释符在一行开头，且只能注释单行

本项目仅供学习交流，请勿用于**未授权**的渗透活动

如果发现软件bug或对该项目感兴趣可联系<mailto:yan.shifm@foxmail.com>
