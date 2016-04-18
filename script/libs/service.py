#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
Pentestdb, a database for penetration test.
Copyright (c) 2014-2015 alpha1e0
=============================================================
服务识别模块
'''


class ServiceIdentify(object):
    '''
    Service identify plugin.
    Input:
        ptype: plugin running type.
            0: default, recognize service with default portList
            1: do not scan port, just do http recognize
            2: scan nmap inner portList
            3: scan 1-65535 port
        kwargs:
            ip: the ip address of the target
            url: the url of the target
            protocol: the protocol of the target
            port: the port of the target
    '''
    def __init__(self, ptype=0, **kwargs):
        try:
            with open(os.path.join("plugin","config","portmapping.yaml"), "r") as fd:
                self.portDict = yaml.load(fd)
        except IOError:
            raise PluginError("cannot load portmapping configure file 'portmapping.yaml'")
        
        if ptype == 1:
            self.cmd = ""
        elif ptype == 2:
            self.cmd = "nmap -n -Pn -oX - "
        elif ptype == 3:
            self.cmd = "nmap -n -Pn -p1-65535 -oX - "
        else:
            portList = [key for key in self.portDict]
            portStr = ",".join([str(x) for x in portList])
            self.cmd = "nmap -n -Pn -p{ports} -oX - ".format(ports=portStr)

        self.type = ptype
        self.host = Dict(**kwargs)
        #requests.packages.urllib3.disable_warnings()
        self.httpTimeout = CONF.http.timeout


    def __iter__(self):
        return self.identify()


    def identify(self):
        if self.cmd:
            hostAddr = self.host.get('url',None) if self.host.get('url',None) else self.host.get('ip',None)
            nmapCmd = self.cmd + hostAddr
            result = Nmap.scan(nmapCmd)
        else:
            result = [self.host]

        for host in result:
            if 'protocol' in host: host.title = host.protocol + "_service"
            try:
                host.protocol = self.portDict[int(host.port)]['protocol']
            except (AttributeError, KeyError):
                pass
            
            try:
                if host.protocol == "http":
                    self.HTTPIdentify(host)
                elif host.protocol == "https":
                    self.HTTPIdentify(host, https=True)
            except AttributeError:
                pass

            yield host


    def getTitle(self, rawContent):
        titlePattern = re.compile(r"(?:<title>)(.*)(?:</title>)")
        charset = None
        charsetPos = rawContent[0:1000].lower().find("charset")
        if charsetPos != -1:
            charsetSlice = rawContent[charsetPos:charsetPos+18]
            charsetList = {"utf-8":"utf-8","utf8":"utf-8","gbk":"gbk","gb2312":"gb2312"}
            for key,value in charsetList.iteritems():
                if key in charsetSlice:
                    charset = value
                    break
        if not charset:
            charset = "utf-8"

        match = titlePattern.search(rawContent)
        return match.groups()[0].decode(charset) if match else "title not found"


    def HTTPIdentify(self, host, https=False):
        try:
            url = host.url
        except AttributeError:
            url = host.ip
        try:
            port = host.port
        except AttributeError:
            port = 443 if https else 80

        method = "https://" if https else "http://"
        url = method + url + ":" + str(port)
        try:
            response = requests.get(url, verify=False, timeout=self.httpTimeout)
        except:
            return

        host.title = self.getTitle(response.content)
        try:
            server = response.headers['server']
        except (IndexError, KeyError):
            pass
        else:
            host.server_info = server

        try:
            middleware = response.headers['x-powered-by']
        except (IndexError, KeyError):
            pass
        else:
            host.middleware = middleware

        if 'ip' not in host:
            dnsresolver = DnsResolver()
            host.ip = dnsresolver.domain2IP(host.url)


    def FTPIdentify(self, host):
        pass