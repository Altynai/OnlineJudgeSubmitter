#!/usr/bin/python
import sys
import os


def error(errorStr):
    sys.stderr.write(errorStr + "\n")
    sys.exit(1)


def checkArgs():
    if(len(sys.argv) != 4):
        error("main.py OJ(ZOJ,HDU,POJ) problemcode sourcefile(example:main.py ZOJ 1000 source.cpp)")
    OJ = sys.argv[1]
    if(OJ != "POJ" and OJ != "HDU" and OJ != "ZOJ"):
        error("main.py OJ(ZOJ,HDU,POJ) problemcode sourcefile(example:main.py ZOJ 1000 source.cpp)")


def main():
    checkArgs()
    exestr = "python %s/submitter.py %s %s" % (sys.argv[1], sys.argv[2], sys.argv[3])
    os.system(exestr)

if __name__ == '__main__':
    main()
