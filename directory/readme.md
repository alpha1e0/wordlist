
# web目录相关字典

本目录中的字典等文件用于路径爆破，敏感路径匹配等。

CMS 指纹信息，pen.py cms功能会使用该指纹文件

其中，每个fingerpring字段的定义为{need:True|False, path:urlpath, pattern:match_string}:

* need，为True表示该fingerprint必须匹配，如果不匹配则不属于相关的CMS类型
* path，fingerprint匹配的URL
* pattern，fingerprint匹配的path返回页面的内容，只能是字符串
