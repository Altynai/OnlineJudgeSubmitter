#!/usr/bin/python

import urllib
import re
import sys
import time
import httplib

username = None
userpass = None
problemId = None
languageId = None

def getLanguage(filetype):
    # c
    if filetype in ["c"]:
        return 1
    # c++
    if filetype in ["cpp","cc","cxx","c++","h","hpp","hxx","h++","inl","ipp","cp","C","hh"]:
        return 2
    # fpc(pascal)
    if filetype in ["pas","inc"]:
        return 3
    # java
    if filetype in ["java","bsh"]:
        return 4
    # python
    if filetype in ["py","rpy","pyw","cpy","py","SConstruct","Sconstruct","sconstruct","SConscript"]:
        return 5
    # perl
    if filetype in ["pl","pm","pod","t","PL"]:
        return 6
    # Scheme
    if filetype in ["scm","smd","ss"]:
        return 7
    # PHP
    if filetype in ["php"]:
        return 8
    else:
        return -1

def sendRequest(method="POST", path="", body="", headers={}):
    """get the response and html"""

    ojUrl = "acm.zju.edu.cn"
    connection = httplib.HTTPConnection(ojUrl)
    connection.request(method, path, body, headers)
    response = connection.getresponse()
    html = response.read()
    connection.close()
    return {"response": response, "html": html}


def getCookie(response):
    cookie = response.getheader("set-cookie")
    cookie = cookie.split(" ")[2]
    return cookie


def getCode():
    with open(sys.argv[2]) as fin:
        return str(''.join(fin.readlines()))


def submitCode(cookie):
    """submit the code and get the runId"""

    global problemId
    global languageId

    path = "/onlinejudge/submit.do"
    code = getCode()
    body = {"problemId": problemId, "languageId": languageId, "source": code}

    body = urllib.urlencode(body)
    headers = {"Cookie": cookie, "Content-Type": "application/x-www-form-urlencoded", "Content-Length": str(len(body))}
    responseDict = sendRequest("POST", path, body, headers)

    html = responseDict["html"]
    # print html
    text = re.compile("(\\d+)</font>")
    result = text.findall(html)
    return result[0]


def loginZOJ():
    path = "/onlinejudge/login.do"
    body = {"handle": username, "password": userpass}
    body = urllib.urlencode(body)
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Content-Length": str(len(body))}
    responseDict = sendRequest("POST", path, body, headers)
    response = responseDict["response"]

    if response.status == httplib.OK:
        error("username or password is wrong!")
    cookie = getCookie(response)[0:-1]
    return cookie


def getResult(cookie, runId):
    """get judge result (Accepted,Wrong Answer,etc.)"""

    path = "/onlinejudge/showRuns.do"
    body = {"contestId": 1,
            "search": "true",
            "firstId": -1,
            "lastId": -1,
            "problemCode": "",
            "handle": "",
            "idStart": runId,
            "idEnd": runId}
    body = urllib.urlencode(body)
    path = path + "?" + body
    responseDict = sendRequest("GET", path, "", {})

    html = responseDict["html"]
    # get JudgeStatus
    if html.find('Compilation Error</a>') != -1:
        judgeStatus = 'Compilation Error'
    else:
        p = re.compile("judgeReply\\w+\">\\s+(\\w+( \\w+)*)\\s+")
        judgeStatus = p.findall(html)[0][0]
    # get runTime
    p = re.compile("runTime\">(\\d+)</td>")
    runTime = p.findall(html)[0]
    # get memory
    p = re.compile("runMemory\">(\\d+)</td>")
    runMemory = p.findall(html)[0]
    return {"status": str(judgeStatus), "time": str(runTime), "memory": str(runMemory)}


def checkProblem(problemId):
    """ check whether the problem exists and get the real problem code"""

    path = "/onlinejudge/showProblem.do?problemCode=" + problemId
    responseDict = sendRequest("GET", path, "", {})
    html = responseDict["html"]
    if html.find("No such problem.") != -1:
        error("No such problem.")

    p = re.compile("submit.do\\?problemId=(\\d+)")
    return p.findall(html)[0]

def checkFile(file):
    p = re.compile("[^\\.]+\\.[^\\.]+")
    if p.match(file) is None:
        error("File is wrong(*.cpp *.py *.c *.java etc.)Please choose again.")


def init():
    if len(sys.argv) != 3:
        error("please check the args : submiter.py problemId file.cpp")
    # read user info
    global username
    global userpass
    global problemId
    global languageId

    problemId = sys.argv[1]

    # change problemId to submit
    problemId = checkProblem(problemId)
    checkFile(sys.argv[2])

    with open("user.config") as fin:
        username = fin.readline().split("=")[1]
        if username.find('\n')!=-1:
            username=username[0:-1]
        userpass = fin.readline().split("=")[1]
        if userpass.find('\n')!=-1:
            userpass=userpass[0:-1]
    # get file's type
    filetype = sys.argv[2][sys.argv[2].find(".") + 1:]
    languageId = getLanguage(filetype)
    if languageId == -1:
        error("ZOJ don't support this file.")

def main():
    cookie = loginZOJ()
    runId = submitCode(cookie)

    Queuing = False
    Running = False
    Waiting = False
    Compiling = False
    while True:
        result = getResult(cookie)
        status = result["status"]
        # Waiting or Running or Compiling or Queuing
        if status == "Queuing":
            if Queuing == False:
                sys.stdout.write("\nQueuing")
                Queuing = True
            else:
                sys.stdout.write(".")
            time.sleep(1)
        elif status == "Waiting":
            if Waiting == False:
                sys.stdout.write("\nWaiting")
                Waiting = True
            else:
                sys.stdout.write(".")
            time.sleep(1)
        elif status == "Compiling":
            if Compiling == False:
                sys.stdout.write("\nCompiling")
                Compiling = True
            else:
                sys.stdout.write(".")
            time.sleep(1)
        elif status == "Running & Judging" or status=="Running":
            if Running == False:
                sys.stdout.write("\nRunning & Judging")
                Running = True
            else:
                sys.stdout.write(".")
            time.sleep(1)
        else:
            sys.stdout.write("\n%s\t%s\t%s\n" % (result["status"], result["time"], result["memory"]))
            break


def error(errorStr):
    sys.stderr.write(errorStr + "\n")
    sys.exit(1)

if __name__ == '__main__':
    init()
    main()
