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

项目中的脚本文件依赖与*requests*, *pocsuite*, *chardet*

    pip install requests
    pip install pocsuite
    pip install chardet

---

## 3 使用

### 3.1 常用脚本

项目中的python脚本提供用有用的渗透辅助功能，根目录下的**pen.py**为脚本入口。

#### 3.1.1 字典数据库维护

`pen.py`的**db**子命令提供简单的*字典数据库*维护功能，使用"-h"查看帮助

*字典数据库*是一个列表，其中每个记录由两部分组成，字符串和字符串频率统计

`pen.py`可以将不同的字典文件加入到数据库中，加入的过程会自动维护字符串的频率，例如

    pen.py db password.db -w user-password\password\user_defines.txt

`pen.py`可以根据指定的长度导出字典文件，例如生成top 1000的字典文件

    pen.py db password.db -g 1000

#### 3.1.2 生成图片木马

`pen.py`的**picshell**子命令提供了*生成图片木马*的功能，使用"-h"查看帮助

例如：

     pen.py picshell avatar.png sample.php dest.png

#### 3.1.3 邮箱账户验证

`pen.py`的**mailcheck**子命令提供了验证邮箱账户的功能，使用"-h"查看帮助

例如：

    pen.py mailcheck mail_accouts.txt

    mail_accounts.txt 为邮箱账户列表文件，每个记录格式为“xxx@xxx.com passwd” 


*注：邮箱账户验证功能需要邮件服务器支持POP3功能*

#### 3.1.4 邮箱账户爆破

`pen.py`的**mailbrute**子命令提供了邮箱账户爆破的功能，使用"-h"查看帮助

例如：

    pen.py mailbrute xxx@xxx.com @passwd.txt

    如果参数前加“@”说明指定的是字典文件

*注：邮箱账户爆破功能需要邮件服务器支持POP3功能*

#### 3.1.5 CMS识别

`pen.py`的**cmsidentify**子命令提供了CMS识别的功能，目前能够识别drupal discuz empirecms dedecms joomla phpcms phpwind qibo wordpress几种cms

例如：

    pen.py cmsidentify http://xxx.com

#### 3.1.6 密码字典生成

`pen.py`的**passwdgen**子命令提供了生成密码字典的功能，能够设置不同关键字生成密码字典

例如：

    pen.py passwdgen --fullname "lin zhi ling" --birthday 1980-1-1 --phone 12344445555 --qq 34233888 > password.txt

### 3.1.7 URI爆破

`pen.py`的**uribrute**子命令提供了URI资源爆破，URI爆破字典生成的功能

例如：

    python pen.py uribrute -u http://127.0.0.1/discuz/6.0/ --safeurl "http://127.0.0.1/discuz/6.0/"
    python pen.py uribrute --generate --type jsp --ext "jspx" --keyword "xxx"


### 3.2 user-passwd字典

**password**目录包含密码字典文件

**user**目录包含用户名字典文件

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

exploit使用pocsuite框架编写，pocsuite框架介绍[知道创宇Pocsuite项目](https://github.com/knownsec/Pocsuite)

---

## 4 备注

项目中的字典等文件统一使用“/**”作为注释符，注释符在一行开头，且只能注释单行

本项目仅供学习交流，请勿用于**未授权**的渗透活动
