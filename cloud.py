# coding: utf-8

from leancloud import Engine
from leancloud import LeanEngineError
import leancloud
from utils.auth import Cli
from utils.getCourse import doCourse
import json

from loguru import logger
engine = Engine()

from io import StringIO


@engine.define
def bindSEPInfo(email, password, **params):
    user = engine.current.user

    UCAS_UserCredential = leancloud.Object.extend('UCAS_UserCredential')
    query = leancloud.Query('UCAS_UserCredential')
    query.equal_to('user', user)
    credential_list = query.find()
    credential = None
    if len(credential_list) == 0:
        # 没有绑定过，新建一个
        credential = UCAS_UserCredential()
        credential.set('user', user)
        credential.set('email', email)
        credential.set('RSA_password', password)
        credential.save()
    else:
        # 更新一下
        credential = credential_list[0]
        credential.set('email', email)
        credential.set('RSA_password', password)
        credential.save()
    leancloud.cloud.run('fetch_course')
    return {
        "code": 200,
        "objectId": credential.get('objectId'),
    }


def get_cookie(user, password, retry_times=5):
    if retry_times == 0:
        return -1
    try:
        print('trying')
        c = Cli(user, password, '123456')
        return c.getCookie(), c.getStudentInfo()
    except Exception as e:
        print(e)
        return get_cookie(user, password, retry_times - 1)


@engine.define
def fetch_course(**params):
    user = engine.current.user
    print(user)
    query = leancloud.Query('UCAS_UserCredential')
    query.equal_to('user', user)
    credential_list = query.find()
    if len(credential_list) == 0:
        return "Error"
    else:
        credential = credential_list[0]
        email = credential.get('email')
        password = credential.get('RSA_password')
        cokkies, realname = get_cookie(email, password, 3)
        credential.set('realname', realname)
        credential.save()

        print(cokkies, realname)
        if cokkies == -1:
            raise LeanEngineError(401, '错误次数超限，是否用户名密码错误？')
        class_array = doCourse(cokkies[1], user.get("objectId"))

        # 存储到表内
        UCAS_CourseCalendar = leancloud.Object.extend('UCAS_CourseCalendar')
        query2 = leancloud.Query('UCAS_CourseCalendar')
        query2.equal_to('user', user)
        course_list = query2.find()
        if len(course_list) == 0:
            # 第一次绑定课表
            course = UCAS_CourseCalendar()
            course.set('user', user)
            course.set('course_no', class_array)
            with open(f'./calendars/{user.get("objectId")}.ics', 'rb') as f:
                file = leancloud.File(f'{user.get("objectId")}.ics', f)
                file.save()
                course.set('course_ics', file)
                course.save()
        else:
            course = course_list[0]
            course.set('course_no', class_array)
            with open(f'./calendars/{user.get("objectId")}.ics', 'rb') as f:
                file = leancloud.File(f'{user.get("objectId")}.ics', f)
                file.save()
                course.set('course_ics', file)
                course.save()
        return {
            "code": 200,
            "courseId": course.get('objectId')
        }


@engine.define
def calculateCollision(colId):
    print(colId)
    query = leancloud.Query('UCAS_Collision')
    query.equal_to('objectId', colId)
    result = query.find()[0]
    if result.get('shouldUpdate') == False:
        return result.get('collisionResult')
    joinedUsers = result.get('joinedUsers')
    week = result.get("week")
    resultTable = [
        [[], [], [], [], [], [], [], [], [], [], [], [], ],
        [[], [], [], [], [], [], [], [], [], [], [], [], ],
        [[], [], [], [], [], [], [], [], [], [], [], [], ],
        [[], [], [], [], [], [], [], [], [], [], [], [], ],
        [[], [], [], [], [], [], [], [], [], [], [], [], ],
        [[], [], [], [], [], [], [], [], [], [], [], [], ],
        [[], [], [], [], [], [], [], [], [], [], [], [], ],
    ]
    print(joinedUsers)
    for user in joinedUsers:
        print(user)
        userObj = leancloud.Object.extend("_User").create_without_data(user)
        query = None
        # find user name
        query = leancloud.Query('UCAS_UserCredential')
        query.equal_to('user', userObj)
        userRes = query.find()
        if userRes == None:
            continue
        userName = userRes[0].get('realname')

        query = None
        query = leancloud.Query('UCAS_CourseCalendar')
        query.equal_to('user', userObj)
        courseRes = query.find()[0]
        print("++++++++")
        print(courseRes)
        if courseRes == None:
            continue
        course_no = courseRes.get('course_no')
        for course in course_no:
            if course['week'] == week:
                resultTable[course['day'] - 1][course['lesson_n'] - 1].append({
                    "name": userName,
                })

    result.set('collisionResult', {'data': resultTable})
    result.set('shouldUpdate', False)
    result.save()
    return {"data": resultTable}


@engine.define
def acceptInvitation(colId):
    user = engine.current.user
    # 就是把user加到colId的那个
    query = leancloud.Query('UCAS_Collision')
    query.equal_to('objectId', colId)
    result = query.find()[0]
    joinedUsers = result.get('joinedUsers')
    if user.get('objectId') in joinedUsers:
        pass
    else:
        joinedUsers.append(user.get('objectId'))
        result.set('joinedUsers', joinedUsers)
        result.set('shouldUpdate', True)
        result.save()
    return {
        "code": 200,
    }


from pdfUtils import extractDox
import requests
import os


@engine.define
def pdfExtract(paperId="65aa3aa1c4e15d12aeee3594"):
    # https://files.puluter.cn/ttEgrvnNNSzOgU0KsvtHzNvSeDHKBt48/dong.pdf
    # 65aa39c67c88630c72653815

    # 清理当前目录和pdfUtils目录下的tmp.docx/tmp.pdf
    if os.path.exists('./pdfUtils/tmp.docx'):
        os.remove('./pdfUtils/tmp.docx')
        print(1)
    if os.path.exists('./pdfUtils/tmp.pdf'):
        os.remove('./pdfUtils/tmp.pdf')
        print(1)
    if os.path.exists('./tmp.docx'):
        os.remove('./tmp.docx')
        print(1)

    Paper = leancloud.Object.extend('ReadPaper_Paper')
    paper = Paper.create_without_data(paperId)
    paper.fetch()
    pdf = paper.get('pdf')
    print(pdf.url)
    # 下载pdf.url的文件，保存到pdfUtils/tmp.pdf
    r = requests.get(pdf.url)
    with open('pdfUtils/tmp.pdf', 'wb') as f:
        f.write(r.content)

    # pdf保存为 pdfUtils/tmp.pdf
    pdf_path = 'pdfUtils/tmp.pdf'
    extractDox.extract_text_from_pdf(pdf_path)

    # read from pdfUtils/work_file as json, and return
    result = {}
    with open('./work_file', 'r') as f:
        result = json.load(f)
        paper.set('pdfContent', result)
        paper.save()
        print(result)
        return result


@engine.define
def LLMOutline(paperId="65aa3aa1c4e15d12aeee3594"):
    Paper = leancloud.Object.extend('ReadPaper_Paper')
    paper = Paper.create_without_data(paperId)
    paper.fetch()

    pdfContent = paper.get('pdfContent')
    if pdfContent == None:
        logger.info('该文件未生成，生成一下')
        leancloud.cloud.run.local('pdfExtract', paperId=paperId)

    paper.fetch()
    pdfContent = paper.get('pdfContent')

    logger.info('开始LLM总结')
    from LLMUtils import jsonParser
    LLMContent = jsonParser.parse_from_json(pdfContent)

    paper.set('LLMContent', LLMContent)
    paper.save()

    return LLMContent
