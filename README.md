# 渗透测试数据库

## 1 介绍

渗透测试数据库，为渗透测试提供常用的字典、攻击payload、webshell等，并且包含常用的脚本。

---

## 2 安装

从[这里](https://github.com/alpha1e0/pentestdb)下载最新版本，或使用命令

    git clone https://github.com/alpha1e0/pentestdb.git

clone到本地

wiper支持Windows/Linux/MacOS，需使用python **2.6.x** 或 **2.7.x**运行

### 2.1 依赖

项目中的脚本文件依赖与*requests*, *chardet*

    pip install requests
    pip install chardet
    pip install yaml
    pip install lxml

    windows 安装 lxml
    http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml
    pip install package.whl

---
---

## 3 使用

### 3.1 常用脚本

项目中的python脚本提供用有用的渗透辅助功能，根目录下的**pen.py**为脚本入口。

包括**CMS识别、URL资源爆破、Exploit执行、社工密码字典生成、编解码**等功能

#### 3.1.1 CMS识别

`pen.py`的**cmsidentify**子命令提供了CMS识别的功能，目前能够识别drupal discuz empirecms dedecms joomla phpcms phpwind qibo wordpress几种cms

例如：

    pen.py cmsidentify http://xxx.com

#### 3.1.2 密码字典生成

`pen.py`的**passwdgen**子命令提供了生成密码字典的功能，能够设置不同关键字生成密码字典

例如：

    pen.py passwdgen --fullname "lin zhi ling" --birthday 1980-1-1 --phone 12344445555 --qq 34233888 > password.txt

### 3.1.3 URI爆破

`pen.py`的**uribrute**子命令提供了URI资源爆破，URI爆破字典生成的功能

例如：

    python pen.py uribrute -u http://127.0.0.1/discuz/6.0/ --safeurl "http://127.0.0.1/discuz/6.0/"
    python pen.py uribrute --generate --type jsp --ext "jspx" --keyword "xxx"

### 3.1.4 Exploit功能

`pen.py`的**exploit**子命令提供了exploit模块相关操作，exploit模块是一个可灵活小巧的exploit框架，可以编写各种web漏洞的exploit，该模块的操作包括以下内容：

* 搜索exploit信息
* 增加、删除、修改exploit信息
* 执行某个exploit
* 搜索并批量执行exploit

exploit保存在项目根目录下的*exploit*目录下

例如：

    # 列举、搜索、注册、更新、删除
    python pen.py -l
    python pen.py -q appName:joomla
    python pen.py --register exploit
    python pen.py --update cms_joomla_3_4_session_object_injection.py
    python pen.py -d "Joomla 1.5~3.4 session对象注入漏洞exploit"
    python pen.py --detail "Joomla 1.5~3.4 session对象注入漏洞exploit"

    # 执行exploit
    python pen.py -e cms_joomla_3_4_session_object_injection.py -u http://127.0.0.1:1234 --attack
    python pen.py -s appName:joomla -u http://127.0.0.1:1234 --verify
    python pen.py -s appName:joomla -u @url.txt

### 3.1.5 编码

`pen.py`的**encode**子命令提供了编码的功能

编码方式*-t/--type*支持：

> url url-all hex decimal unicode unicode-all md5 sha base64 base32 html html-all

> 其中**-all编码会编码所有字符包括非特殊字符

非ASCII编码*-m/--method*支持：

> utf8 gbk gb2312 big5 utf16 utf7 等所有python支持的编码方式，具体请参考如下链接：

> [python支持的编解码](https://docs.python.org/2/library/codecs.html)


例如：

    python pen.py encode -t unicode "aaa=你好"
    python pen.py encode -t url-all -m gbk "id=你好"
    python pen.py encode -t md5 "aaaaaaaa"

### 3.1.6 解码

`pen.py`的**decode**子命令提供了解码的功能，并提供编码推测功能

解码方式*-t/--type*支持：

> auto hex url unicode decimal base64 base32 html

> 其中*auto*方式会自动检测url类型、hex类型、unicode类型的字符串并进行解码

非ASCII编码*-m/--method*支持：

> utf8 gbk gb2312 big5 utf16 utf7 等所有python支持的编码方式，具体请参考如下链接：

> [python支持的编解码](https://docs.python.org/2/library/codecs.html)

例如：

    python pen.py decode -t base64 5ZOI5ZOI
    python pen.py decode -m utf8 aaa%E5%93%88%E5%93%88
    python pen.py encode -t hex "\x61\x61\xe5\x93\x88\xe5\x93\x88"
    python pen.py decode -d @aaa.txt

#### 3.1.7 文件处理功能

`pen.py`的**file**子命令提供了常用的文件操作，包括：文件编码推断、文件类型转换、文件hash计算、文件图片隐藏(制作php图片木马)

文件编码转换方式*--dtype*支持：

> unicode-le unicode-be base32 base64 urf8 gbk gb2312 及其他python支持的编码方式

例如：

    pen file -f cmdb.jsp -d
    pen file -f cmdb.jsp --hash md5
    
    # 文件转换，转换为unicode-le类型文件(jsp/aspx的unicode-le/unicode-be类型文件可绕过一些安全软件)
    pen file -f cmd.jsp -c --dtype unicode-le --dfile dst.jsp

    # 制作图片木马
    pen file -f caidao.php --hfile aa.jpg --dfile picshell.php


#### 3.1.8 google hacking功能

`pen.py`的**gh**子命令提供了


#### 3.1.9 字典数据库维护

`pen.py`的**db**子命令提供简单的*字典数据库*维护功能，使用"-h"查看帮助

*字典数据库*是一个列表，其中每个记录由两部分组成，字符串和字符串频率统计

`pen.py`可以将不同的字典文件加入到数据库中，加入的过程会自动维护字符串的频率，例如

    pen.py db password.db -w user-password\password\user_defines.txt

`pen.py`可以根据指定的长度导出字典文件，例如生成top 1000的字典文件

    pen.py db password.db -g 1000


#### 3.1.10 邮箱账户验证

`pen.py`的**mailcheck**子命令提供了验证邮箱账户的功能，使用"-h"查看帮助

例如：

    pen.py mailcheck mail_accouts.txt

    mail_accounts.txt 为邮箱账户列表文件，每个记录格式为“xxx@xxx.com passwd” 


*注：邮箱账户验证功能需要邮件服务器支持POP3功能*

#### 3.1.11 邮箱账户爆破

`pen.py`的**mailbrute**子命令提供了邮箱账户爆破的功能，使用"-h"查看帮助

例如：

    pen.py mailbrute xxx@xxx.com @passwd.txt

    如果参数前加“@”说明指定的是字典文件

*注：邮箱账户爆破功能需要邮件服务器支持POP3功能*

---

### 3.2 user-passwd字典

**password**目录包含密码字典文件

**user**目录包含用户名字典文件

---

### 3.3 dns字典

dns爆破字典

### 3.4 directory字典

web目录爆破字典

### 3.5 attack-payload

各种攻击payload字典

### 3.6 webshell

webshell收集

### 3.7 script

常用脚本

### 3.8 exploit

一些有用的exploit


---

## 4 备注

项目中的字典等文件统一使用“/**”作为注释符，注释符在一行开头，且只能注释单行

本项目仅供学习交流，请勿用于**未授权**的渗透活动
