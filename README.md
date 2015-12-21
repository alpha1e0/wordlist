# 渗透测试数据库

## 介绍

渗透测试数据库，为渗透测试提供常用的字典、攻击payload、webshell等，并且包含常用的脚本。

---

## 安装

从[这里](https://github.com/alpha1e0/pentestdb)下载最新版本，或使用命令

    git clone https://github.com/alpha1e0/pentestdb.git

clone到本地

wiper支持Windows/Linux/MacOS，需使用python **2.6.x** 或 **2.7.x**运行

---

## 使用

项目中的python脚本提供常用的辅助功能，根目录下的**pen.py**为脚本入口。

项目中的字典等文件统一使用“/**”作为注释符，注释符在一行开头，只能注释单行

### user-passwd

**password**目录包含密码字典文件

**user**目录包含用户名字典文件

### dns

dns爆破字典

### directory

web目录爆破字典

### attack

各种攻击payload字典

### webshell

webshell收集

### script

常用脚本


## 备注

请勿用于**未授权**的渗透测试
