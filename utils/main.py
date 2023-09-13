# Configs
user = 'yuzhuohao23@mails.ucas.ac.cn'
# pass_raw = 'YvDAjkk.sbD7BD2g'
password = 'rBfo7WoCxou4ca6eNQx04+E1HHP/56asfYP0Twph4VKTNhBXQRPV0ZNUuuLAK25uvAJCaYIyIRhUeLXnVa7Kb1KoQoM9xgpVuHzUs9xYxqWpsGqFFr+k9NrRFFQYoOM/y55HuUlh6Vmy9RnpLvtVT8G56gCZg+26NiisCphwTtSIMatX4rTgUCqmazZUrExv/7w3BDB+Cc1YvyTimd2zK7zi4hLaENtdcBpZWLq1nOW5XURm3yzq0mCADIYpIK6qAiGyHtqfGGr7Pe0jJLfzEZ8sCwHNTVNaWXi39bYdb+JzbgSPSLQhR22Y3ZTyVC2Ehv41jwO7fuOBtnxmbg+CwQ=='

# 密码RSA处理
# import execjs
# js_file = './jdJsencrypt.min.js'
# with open(js_file, 'r', encoding='utf-8') as f:
#     js_code = f.read()
# js = execjs.compile(js_code)
# password = js.call('getRsaResult', pass_raw)
# print(password)
# 尝试登录
from auth import Cli
def getCookie(retry_times=5):
    if retry_times == 0:
        return -1
    try:
        c = Cli(user, password, '123456')
        return c.getCookie()
    except Exception as e:
        return getCookie(retry_times - 1)
cokkies = getCookie()
if cokkies == -1:
    print('错误次数超限，是否用户名密码错误？')
    exit(1)

# 获取课表
from getCourse import doCourse
doCourse(cokkies[1])
