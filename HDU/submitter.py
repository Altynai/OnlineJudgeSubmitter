#!/usr/bin/python

import urllib
import re
import sys
import time
import httplib
import pprint
username = None
userpass = None
problemId = None
languageId = None


def getLanguage(filetype):
    # c
    if filetype in ["c"]:
        return 3
    # c++/g++
    if filetype in ["cpp", "cc", "cxx", "c++", "h", "hpp", "hxx", "h++", "inl", "ipp", "cp", "C", "hh"]:
        return 2
    # fpc(pascal)
    if filetype in ["pas", "inc"]:
        return 4
    # java
    if filetype in ["java", "bsh"]:
        return 5
    else:
        return -1


def sendRequest(method="POST", path="", body="", headers={}):
    """get the response and html"""

    ojUrl = "acm.hdu.edu.cn"
    connection = httplib.HTTPConnection(ojUrl)
    connection.request(method, path, body, headers)
    response = connection.getresponse()
    html = response.read()
    connection.close()
    return {"response": response, "html": html}


def getCookie(response):
    cookie = response.getheader("set-cookie")
    cookie = cookie.split(" ")[0]
    return cookie


def getCode():
    with open(sys.argv[2]) as fin:
        return str(''.join(fin.readlines()))


def submitCode(cookie):
    """submit the code and get the runId"""

    global problemId
    global languageId

    path = "/submit.php?action=submit"
    code = getCode()
    body = {"problemid": problemId, "language": languageId, "usercode": code, "check": 0}

    body = urllib.urlencode(body)
    headers = {"Cookie": cookie, "Content-Type": "application/x-www-form-urlencoded", "Content-Length": str(len(body))}
    sendRequest("POST", path, body, headers)


def loginHDU():
    path = "/userloginex.php?action=login"
    body = {"username": username, "userpass": userpass, "login": "Sign In"}
    body = urllib.urlencode(body)
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Content-Length": str(len(body))}
    responseDict = sendRequest("POST", path, body, headers)
    response = responseDict["response"]
    
    if response.status == httplib.OK:
        error("username or password is wrong!")
    cookie = getCookie(response)[0:-1]
    return cookie


def getResult(cookie):
    """get judge result (Accepted,Wrong Answer,etc.)"""

    global problemId
    global username
    path = "/status.php?pid=%s&user=%s" % (problemId, username)
    responseDict = sendRequest("GET", path, "", {})

    html = responseDict["html"]
    with open("temp.html","w") as fout:
        fout.write(html)
    p = re.compile(r"<td height=22px>\d+</td>((<td.*?\s*?.*?</td>){6})")
    lastrecord = p.findall(html)[0][0]

    p = re.compile(r"<td.*?>(.*?\s*?.*?)</td>")
    lastrecord = p.findall(lastrecord)
    # print lastrecord
    # judgeStatust
    p = re.compile(r"<font color=.+>(.* ?.*)</font>")
    judgeStatus = p.findall(lastrecord[1])[0]
    # time
    runTime = lastrecord[3]
    # memory
    runMemory = lastrecord[4]
    return {"status": str(judgeStatus), "time": str(runTime), "memory": str(runMemory)}


def checkProblem(problemId):
    """ check whether the problem exists and get the real problem code"""

    path = "/showproblem.php?pid=" + problemId
    responseDict = sendRequest("GET", path, "", {})
    html = responseDict["html"]
    if html.find("Invalid Parameter.") != -1:
        error("Can not find problem %s." % problemId)


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
    checkProblem(problemId)
    checkFile(sys.argv[2])

    with open("user.config") as fin:
        username = fin.readline().split("=")[1]
        if username.find('\n') != -1:
            username = username[0:-1]
        userpass = fin.readline().split("=")[1]
        if userpass.find('\n') != -1:
            userpass = userpass[0:-1]
    # get file's type
    filetype = sys.argv[2][sys.argv[2].find(".") + 1:]
    languageId = getLanguage(filetype)
    if languageId == -1:
        error("HDU don't support this file.")


def main():
    cookie = loginHDU()
    submitCode(cookie)

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
