#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
Pentestdb, a database for penetration test.
Copyright (c) 2014-2015 alpha1e0
================================================================
Common functions.
'''


import os
import sys
import logging


class PenError(Exception):
    def __init__(self, errorMsg):
        self.errorMsg = errorMsg

    def __str__(self):
        return str(self.errorMsg)


class DictError(PenError):
    def __str__(self):
        return str(" ".join(["Dict error", self.errorMsg]))


def WordList(fileName):
    result = set()
    if os.path.exists(fileName):
        with open(fileName, "r") as fd:
            for line in fd:
                if line.strip() and not line.strip().startswith("/**"):
                    yield line.strip()


class Dict(dict):
    def __init__(self, **kwargs):
        super(Dict, self).__init__(**kwargs)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError("object dose not have attribute '{0}'".format(key))

    def __setattr__(self, key, value):
        self[key] = value


class Output(object):
    RED = '\033[31m'
    BLUE = '\033[34m'
    YELLOW = '\033[33m'
    GREEN = '\033[32m'
    EOF = '\033[0m'

    def __init__(self, title):
        self.title = title
        
    @classmethod
    def raw(cls, msg):
        print msg

    @classmethod
    def R(cls, msg):
        return cls.RED + msg + cls.EOF

    @classmethod
    def red(cls, msg):
        print cls.R(msg)

    @classmethod
    def B(cls, msg):
        return cls.BLUE + msg + cls.EOF

    @classmethod
    def blue(cls, msg):
        print cls.B(msg)

    @classmethod
    def Y(cls, msg):
        return cls.YELLOW + msg + cls.EOF

    @classmethod
    def yellow(cls, msg):
        print cls.Y(msg)

    @classmethod
    def G(cls, msg):
        return cls.GREEN + msg + cls.EOF

    @classmethod
    def green(cls, msg):
        print cls.G(msg)


    def __enter__(self):
        print self.Y(u"\n[+]: "+self.title)
        print self.R("======================================================================")
        return self

    def __exit__(self, *args):
        print self.R("======================================================================\n")


class Database(object):
    def __init__(self, dbfile):
        self.dbfile = dbfile
        self.list = []
        self._load()


    def _load(self):
        if not os.path.exists(self.dbfile):
            return
        try:
            with open(self.dbfile, "r") as fd:
                for line in fd:
                    if line:
                        splited = line.strip().split()
                        self.list.append([splited[0].strip(), int(splited[1])])
        except IOError as error:
            print "[!] load database file error, reason:", str(error)


    def dump(self):
        self.list.sort(key=lambda x: x[1], reverse=True)
        try:
            with open(self.dbfile, "w") as fd:
                for line in self.list:
                    fd.write("{0} {1}\n".format(line[0],line[1]))
        except IOError:
            raise DictError()


    def generate(self, count):
        pos = self.dbfile.rfind(".")
        prefix = self.dbfile[:pos] if pos!=-1 else self.dbfile
        wordlistFileName = prefix + "_top_" + str(count) + ".txt"

        fileLen = count if count<len(self.list) else len(self.list)
        with open(wordlistFileName, "w") as fd:
            for i in range(fileLen):
                fd.write(self.list[i][0]+"\n")


    def addWord(self, word):
        if not self.list:
            self.list.append([word, 1])
            return
        for line in self.list:
            if word == line[0]:
                line[1] += 1
                break
        else:
            self.list.append([word, 1])


    def addWordlist(self, dictFile):
        for line in WordList(dictFile):
            self.addWord(line.strip())


class Log(object):
    '''
    Log class, support:critical, error, warning, info, debug, notset
    input:
        logname: specify the logname
        toConsole: whether outputing to console
        toFile: whether to logging to file
    '''
    def __new__(cls, logname=None, toConsole=True, toFile="pen"):
        logname = logname if logname else "pen"

        #logging.basicConfig(datefmt="%Y-%m-%d %H:%M:%S")

        log = logging.getLogger(logname)
        log.setLevel(logging.DEBUG)

        if toConsole:
            streamHD = logging.StreamHandler()
            streamHD.setLevel(logging.DEBUG)
            formatter = logging.Formatter('[%(asctime)s] <%(levelname)s> %(message)s' ,datefmt="%Y-%m-%d %H:%M:%S")
            streamHD.setFormatter(formatter)
            log.addHandler(streamHD)

        if toFile:
            fileName = os.path.join(sys.path[0],"script","log",'{0}.log'.format(toFile))
            if not os.path.exists(fileName):
                try:
                    os.mkdir(os.path.join(sys.path[0],"script","log"))
                except WindowsError, OSError:
                    pass
                with open(fileName,"w") as fd:
                    fd.write("{0} log start----------------\r\n".format(toFile))
            fileHD = logging.FileHandler(fileName)
            fileHD.setLevel(logging.DEBUG)
            formatter = logging.Formatter('[%(asctime)s] <%(levelname)s> %(message)s' ,datefmt="%Y-%m-%d %H:%M:%S")
            fileHD.setFormatter(formatter)
            log.addHandler(fileHD)

        return log


class Nmap(object):
    '''
    Nmap scan.
    '''
    @classmethod
    def scan(cls, cmd):
        '''
        Nmap scan.
        output:
            a list of host, each host has attribute 'ip' 'port' 'protocol'
        '''
        result = list()

        if "-oX" not in cmd:
            cmd = cmd + " -oX -"
        if CONF.nmap:
            cmd.replace("nmap", CONF.nmap)

        popen = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
        scanResult = popen.stdout.read()

        #parse the nmap scan result     
        xmlDoc = BeautifulStoneSoup(scanResult)
        hosts = xmlDoc.findAll("host")
        for host in hosts:
            if isinstance(host, NavigableString) or host.name!="host" or host.status['state']!="up":
                continue
            ip = host.address['addr']
            #url = host.hostnames.hostname['name']
            try:
                ports = host.ports.contents
            except AttributeError:
                result.append(Dict(**{'ip':ip}))
                continue
            else:
                for port in ports:
                    if isinstance(port, NavigableString) or port.name != "port" or port.state['state']!="open": 
                        continue
                    result.append(Dict(ip=ip,port=port['portid'],protocol=port.service['name']))

        return result


class DnsResolver(object):
    '''
    Dns operation.
    The records format is [domain, value, type]
    '''
    def __init__(self, domain=None, timeout=None):
        self.domain = domain

        self.resolver = resolver.Resolver()
        self.resolver.nameservers = CONF.dns.servers
        self.resolver.timeout = timeout if timeout else CONF.dns.timeout

        self.axfr = query.xfr


    def domain2IP(self, domain=None):
        '''
        Parse domain to IP.
        '''
        domainToResolve = domain if domain else self.domain
        try:
            response = self.resolver.query(domainToResolve, "A")
        except DNSException:
            return None
        else:
            return response[0].to_text()
            #return [x.to_text for x in response]


    def IP2domain(self, ip):
        '''
        Parse IP to domain. The most dns server dose not support this operation.
        '''
        return reversename.from_address(ip)


    def getRecords(self, rtype, domain=None):
        '''
        Get dns records, records type supports "A", "CNAME", "NS", "MX", "SOA", "TXT"
        Example:
            dns.getRecords("A")
        '''
        if not rtype in ["A", "CNAME", "NS", "MX", "SOA", "TXT", "a", "cname", "ns", "mx", "soa", "txt"]:
            return []

        domainToResolve = domain if domain else self.domain
        try:
            response = self.resolver.query(domainToResolve, rtype)
        except DNSException:
            return []

        if not response:
            return []

        if rtype in ["MX","mx"]:
            return [[domainToResolve, line.to_text().rstrip(".").split()[-1], rtype] for line in response]
        return [[domainToResolve, line.to_text().rstrip("."), rtype] for line in response]


    def getZoneRecords(self, domain=None):
        '''
        Check and use dns zone transfer vulnerability. This function will traverse all the 'ns' server
        Usage:
            dnsresolver = DnsResolver('aaa.com')
            records = dnsresolver.getZoneRecords()
        '''
        domainToResolve = domain if domain else self.domain

        records = list()
        nsRecords = self.getRecords("NS", domainToResolve)
        for serverRecord in nsRecords:
            xfrHandler = self.axfr(serverRecord[1], domainToResolve)
            try:
                for response in xfrHandler:
                    topDomain = response.origin.to_text().rstrip(".")
                    for line in response.answer:
                        # A records
                        if line.rdtype == 1:
                            lineSplited = line.to_text().split()
                            if lineSplited[0] != "@":
                                subDomain = lineSplited[0] + "." + topDomain
                                ip = lineSplited[-1]
                                records.append([subDomain, ip, "A"])
                        # CNAME records
                        elif line.rdtype == 5:
                            lineSplited = line.to_text().split()
                            if lineSplited[0] != "@":
                                subDomain = lineSplited[0] + "." + topDomain
                                aliasName = lineSplited[-1]
                                records.append([subDomain, aliasName, "CNAME"])
            except:
                pass

        return records


    def getZoneRecords2(self, server, domain=None):
        '''
        Use the specified ns server, check and use dns zone transfer vulnerability.
        Usage:
            dnsresolver = DnsResolver('aaa.com')
            records = dnsresolver.getZoneRecords2()
        '''
        domainToResolve = domain if domain else self.domain

        records = list()

        xfrHandler = self.axfr(server, domainToResolve)

        try:
            for response in xfrHandler:
                topDomain = response.origin.to_text().rstrip(".")
                for line in response.answer:
                    # A records
                    if line.rdtype == 1:
                        lineSplited = line.to_text().split()
                        if lineSplited[0] != "@":
                            subDomain = lineSplited[0] + "." + topDomain
                            ip = lineSplited[-1]
                            records.append([subDomain, ip, "A"])
                    # CNAME records
                    elif line.rdtype == 5:
                        lineSplited = line.to_text().split()
                        subDomain = lineSplited[0] + "." + topDomain
                        if lineSplited[0] != "@":
                            aliasName = lineSplited[-1]
                            records.append([subDomain, aliasName, "CNAME"])
        except:
            pass

        return records


    def resolveAll(self, domain=None):
        domainToResolve = domain if domain else self.domain
        types = ["A", "CNAME", "NS", "MX", "SOA", "TXT"]
        records = list()

        for t in types:
            records += self.getRecords(t, domainToResolve)

        records += self.getZoneRecords(domainToResolve)

        return records



class DnsBrute(object):
    '''
    Use wordlist to bruteforce subdomain.
    input:
        domain: the domain to bruteforce
        dictfiles: the dict files
        bruteTopDomain: wither to check top domain
    '''
    def __init__(self, domain, dictfiles, bruteTopDomain=False):
        self.domain = domain
        self.dictfiles = dictfiles
        self.bruteTopDomain = bruteTopDomain
        self.dnsresolver = DnsResolver()


    def checkDomain(self, domain):
        ip = self.dnsresolver.domain2IP(domain)
        if ip:
            return ip


    def __iter__(self):
        return self.brute()


    def brute(self):
        #partDoman示例：aaa.com partDomain为aaa，aaa.com.cn partDomain为aaa
        pos = self.domain.rfind(".com.cn")
        if pos==-1: pos = self.domain.rfind(".")
        partDomain = self.domain if pos==-1 else self.domain[0:pos]

        if self.bruteTopDomain:
            dlist = os.path.join("data","wordlist","toplevel.txt")
            for line in DictFileEnum(dlist):
                domain = partDomain + "." + line
                ip = self.checkDomain(domain)
                if ip:
                    yield Dict(url=domain, ip=ip, description="Generated by dnsbrute plugin.")

        for dlist in self.dictfiles:
            for line in DictFileEnum(dlist):
                domain = line + "." + self.domain
                ip = self.checkDomain(domain)
                if ip:
                    yield Dict(url=domain, ip=ip, description="Generated by dnsbrute plugin.")


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