# coding: utf-8

from leancloud import Engine
from leancloud import LeanEngineError
import leancloud
from utils.auth import Cli
from utils.getCourse import doCourse

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
        cokkies, realname = get_cookie(email, password,3)
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
            #第一次绑定课表
            course = UCAS_CourseCalendar()
            course.set('user',user)
            course.set('course_no',class_array)
            with open(f'./calendars/{user.get("objectId")}.ics', 'rb') as f:
                # icsContent = f.read()
                # fileIO = StringIO(icsContent)
                # file = leancloud.File(f'{user.get("objectId")}.ics', fileIO, 'text/calendar')
                file = leancloud.File(f'{user.get("objectId")}.ics', f)
                file.save()
                course.set('course_ics', file)
                course.save()
        else:
            course = course_list[0]
            course.set('course_no',class_array)
            with open(f'./calendars/{user.get("objectId")}.ics', 'rb') as f:
                # icsContent = f.read()
                # fileIO = StringIO(icsContent)
                # file = leancloud.File(f'{user.get("objectId")}.ics', fileIO, 'text/calendar')
                file = leancloud.File(f'{user.get("objectId")}.ics', f)
                file.save()
                course.set('course_ics', file)
                course.save()
        return {
            "code": 200,
            "courseId": course.get('objectId')
        }

