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
    if filetype in ["cpp", "cc", "cxx", "c++", "h", "hpp", "hxx", "h++", "inl", "ipp", "cp", "C", "hh"]:
        return 1
    else:
        return -1


def sendRequest(method="POST", path="", body="", headers={}):
    """get the response and html"""

    ojUrl = "acm.zjut.edu.cn"
    connection = httplib.HTTPConnection(ojUrl)
    connection.request(method, path, body, headers)
    response = connection.getresponse()
    html = response.read()
    connection.close()
    return {"response": response, "html": html}


def getCookie(response):
    cookie = response.getheader("set-cookie")
    cookie = cookie.split(" ")
    return cookie[0]+" "+cookie[3]


def getCode():
    with open(sys.argv[2]) as fin:
        return str(''.join(fin.readlines()))


def submitCode(cookie):
    """submit the code and get the runId"""

    global problemId
    global languageId

    viewstate = "/wEPDwUKMTA5NzA2MjUxMA9kFgJmD2QWAgIDD2QWAgIDD2QWAgIBD2QWAmYPZBYCAg0PEA8WAh4HQ2hlY2tlZGhkZGRkGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYDBRhjdGwwMCRMb2dpblN0YXR1czEkY3RsMDEFGGN0bDAwJExvZ2luU3RhdHVzMSRjdGwwMwUfY3RsMDAkY3BoUGFnZSRMb2dpbjEkUmVtZW1iZXJNZYwHArZGLeut30pqx0yBhCjX92RO"
    eventvalidation = "/wEWBgKE3q/0CwLh8vmTCAKEmvGlBgLg8d2aBwKX76a+DQKhlsmtCwCWCDEBQQnUZebfEN5mHwudPaWd"

    path = "/Submit.aspx"
    code = getCode()
    body = {"ShowID":1000,"ctl00$cphPage$Source":code,
            "ctl00$cphPage$LanguageList":0,"ctl00$cphPage$ProblemID":problemId,"ctl00$cphPage$EditButton":"Submit"}

    body = urllib.urlencode(body)
    headers = {"Cookie": cookie, "Content-Type": "application/x-www-form-urlencoded", "Content-Length": str(len(body))}
    responseDict = sendRequest("POST", path, body, headers)

    html = responseDict["html"]
    with open("temp.html","w") as fout:
        fout.write(html)
    # print html,responseDict["response"].status,cookie
    text = re.compile("(\\d+)</font>")
    result = text.findall(html)
    return result[0]


def loginZJUT():
    viewstate = "/wEPDwUKMTA5NzA2MjUxMA9kFgJmD2QWAgIDD2QWAgIDD2QWAgIBD2QWAmYPZBYCAg0PEA8WAh4HQ2hlY2tlZGhkZGRkGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYDBRhjdGwwMCRMb2dpblN0YXR1czEkY3RsMDEFGGN0bDAwJExvZ2luU3RhdHVzMSRjdGwwMwUfY3RsMDAkY3BoUGFnZSRMb2dpbjEkUmVtZW1iZXJNZYwHArZGLeut30pqx0yBhCjX92RO"
    eventvalidation = "/wEWBgKE3q/0CwLh8vmTCAKEmvGlBgLg8d2aBwKX76a+DQKhlsmtCwCWCDEBQQnUZebfEN5mHwudPaWd"
    path = "/SignIn.aspx"
    body = {"__VIEWSTATE":viewstate,"__EVENTVALIDATION":eventvalidation,"ctl00$cphPage$Login1$UserName": username, "ctl00$cphPage$Login1$Password": userpass, "ctl00$cphPage$Login1$LoginButton": "SignIn"}
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
    headers = {"Cookie": cookie, "Content-Type": "application/x-www-form-urlencoded", "Content-Length": str(len(body))}
    responseDict = sendRequest("POST", path, body, headers)

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

    path = "/ShowProblem.aspx?ShowID=" + problemId
    responseDict = sendRequest("GET", path, "", {})
    html = responseDict["html"]
    if html.find("error.aspx") != -1:
        error("No such problem.")


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
        username = fin.readline()[0:-1].split("=")[1]
        userpass = fin.readline()[0:-1].split("=")[1]
    # get file's type
    filetype = sys.argv[2][sys.argv[2].find(".") + 1:]
    languageId = getLanguage(filetype)
    if languageId == -1:
        error("ZJUT's OJ only support C/C++.")


def main():
    cookie = loginZJUT()
    runId = submitCode(cookie)

    Running = False
    Compiling = False
    while True:
        result = getResult(cookie, runId)
        status = result["status"]
        # Running or Compiling
        if status == "Compiling":
            if Compiling == False:
                sys.stdout.write("\nCompiling")
                Compiling = True
            else:
                sys.stdout.write(".")
            time.sleep(1)
        elif status == "Running":
            if Running == False:
                sys.stdout.write("\nRunning")
                Running = True
            else:
                sys.stdout.write(".")
            time.sleep(1)
        else:
            sys.stdout.write("\n%s\t%sms\t%sKB\n" % (result["status"], result["time"], result["memory"]))
            break


def error(errorStr):
    sys.stderr.write(errorStr + "\n")
    sys.exit(1)

if __name__ == '__main__':
    init()
    main()
