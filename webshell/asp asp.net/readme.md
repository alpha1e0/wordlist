
# asp asp.net相关木马

---

# bypass方式

更改编码asp/aspx文件编码方式可以绕过一些安全软件，例如 utf-16、utf-16be、utf-32

*使用pen.py file命令进行文件编码转换，例如：*

    pen.py file shell.aspx -c --dfile shell-utf16-bom.aspx --dtype utf-16le-bom