#!/usr/local/env python
#-*- coding: UTF-8 -*-

'''
Add new dict list to dict database.
'''

__author__ = "alpha1e0"

import argparse
import os

class DictError(Exception):
    pass

def WordList(fileName):
    if os.path.exists(fileName):
        with open(fileName, "r") as fd:
            for line in fd:
                if line and line[0].isalnum():
                    yield line.strip()


class Database(object):
    def __init__(self, dbfile):
        self.dbfile = dbfile
        self.list = []
        self._load()


    def _load(self):
        try:
            with open(self.dbfile, "r") as fd:
                for line in fd:
                    if line:
                        splited = line.strip().split(" ")
                        self.list.append([splited[0].strip(), int(splited[1])])
        except IOError as error:
            print "[!]: read all-file error, reason: " + str(error) + "loads empty."


    def dump(self):
        self.list.sort(key=lambda x: x[1], reverse=True)
        try:
            with open(self.dbfile, "w") as fd:
                for line in self.list:
                    fd.write("{0} {1}\r\n".format(line[0],line[1]))
        except IOError:
            raise DictError()


    def add(self, word):
        for line in self.list:
            if word == line[0]:
                line[1] += 1
        else:
            self.list.append([word, 1])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("sourcedir",help="specified the source worldlist directory.")
    parser.add_argument("database",help="specified the all dict file.")
    args = parser.parse_args()

    rawDictFiles = os.listdir(args.sourcedir)
    print "debug:>>>>>rawDictFiles", rawDictFiles
    dbfile = args.database

    db = Database(dbfile)
    print "here"
    for dictfile in rawDictFiles:
        dictfile = os.path.join(args.sourcedir, dictfile)
        for line in WordList(dictfile):
            print "debug:>>>>>read line", line, "from", dictfile
            db.add(line.strip())

    db.dump()





