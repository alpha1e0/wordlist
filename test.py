
from collections import OrderedDict
import json

MAILSERVERS = { '163.com':{'server':"pop3.163.com"},
                'qq.com':{'server':"pop.qq.com",'ssl':True,'port':995},
                'foxmail.com':{'server':"pop.qq.com"},
                'sina.com':{'server':"pop.sina.com"},
                'vmeti.com':{'server':"vmeti.com"},
                'netwayer.com':{'server':"netwayer.com"},
                'ehanlin.com':{'server':"123.108.216.97"},
                'sootoo.com':{'server':"mail.sootoo.com"},
            }


mails = OrderedDict(MAILSERVERS)

dest = open("mail_server.json", "w")

json.dump(mails, dest, indent=4)