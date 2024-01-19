#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import time
import random
import pickle
from loguru import logger
import requests
import json

import ddddocr
import PIL.Image

int_char = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
ocr = ddddocr.DdddOcr(show_ad=False)


def recognize(captcha_bytes):
    with open('cache.jpg', 'wb') as f:
        f.write(captcha_bytes)
    image = PIL.Image.open('cache.jpg')
    image = image.rotate(-20)
    image.save('cache.jpg')
    with open('cache.jpg', 'rb') as f:
        captcha_bytes = f.read()
    res = ocr.classification(captcha_bytes)
    if len(res) < 3:
        return None
    if not (res[0] in int_char and res[2] in int_char):
        return None
    print(f"res = {res}")
    r1 = int(res[0])
    r2 = int(res[2])
    op = res[1]
    if op == '+':
        return r1 + r2
    elif op == '*' or op == 'x' or op == 'X':
        return r1 * r2
    elif op == '/':
        return r1 // r2
    else:
        return None


def recognize_login(captcha_bytes):
    return ocr.classification(captcha_bytes)

class Config:

    timeout = 5
    minIdle = 0
    maxIdle = 1.7777
    waitForUser = 60
    captchaRepeatTime = 5

class Login:
    page = 'https://sep.ucas.ac.cn'
    url = page + '/slogin'
    system = page + '/portal/site/226/821'
    pic = page + '/changePic'
    captcha_url = "https://sep.ucas.ac.cn/user/doUserVisit"


class Course:
    base = 'https://jwxk.ucas.ac.cn'
    identify = base + '/login?Identity='
    selected = base + '/courseManage/selectedCourse'
    selection = base + '/courseManage/main'
    category = base + '/courseManage/selectCourse?s='
    save = base + '/courseManage/saveCourse?s='
    score = base + '/score/yjs/all.json'
    captcha = base + '/captchaImage'


class BadNetwork(Exception):
    pass


class AuthInvalid(Exception):
    pass
def list_from_cookiejar(cj):
    cookie_list = list()
    for cookie in cj:
        # 可以根据需求去保存cookie的特征值
        cookie_list.append((cookie.name, cookie.value, cookie.path, cookie.domain))   
    return cookie_list

class Cli(object):
    headers = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
    }

    def __init__(self, user, password, user_id):
        super(Cli, self).__init__()
        self.student = None
        self.logger = logger
        self.user_id=user_id
        self.s = requests.Session()
        self.s.headers = self.headers
        self.s.timeout = Config.timeout
        self.login(user, password)
        self.getStudentInfo()

    def get(self, url, *args, **kwargs):
        r = self.s.get(url, *args, **kwargs)
        if r.status_code != requests.codes.ok:
            
            self.logger.info(f'{r.status_code}')
            raise BadNetwork
        return r

    def post(self, url, *args, **kwargs):
        r = self.s.post(url, *args, **kwargs)
        if r.status_code != requests.codes.ok:
            raise BadNetwork
        return r

    def login(self, user, password):
        # 打开登录页面
        res1 = self.get(Login.page)
        data = {
            'userName': user,
            'pwd': password,
            'sb': 'sb'
        }
        # 获取验证码
        login_captcha = self.get(Login.pic).content
        # 验证码识别
        cert_code = recognize_login(login_captcha)
        self.logger.debug(f'login cert code = {cert_code}')
        # 设置验证码
        data['certCode'] = cert_code
        response = self.s.post(Login.url, data=data)
        
        # identify
        r = self.get(Login.system)
        identity = r.text.split('<meta http-equiv="refresh" content="0;url=')
        if len(identity) < 2:
            self.logger.error('login fail')
            return False
        identity_url = identity[1].split('"')[0]
        
        # 获取选课系统cookie
        res = self.get(identity_url)
        return list_from_cookiejar(self.s.cookies)[1]
    
    def getCookie(self):
        return list_from_cookiejar(self.s.cookies)[1]
        
    def getStudentInfo(self):
        r = self.get(Course.score)
        if 'gpa' not in r.text:
            # <label id="loginSuccess" class="success"></label>
            raise AuthInvalid
        jsonobj = json.loads(r.text)
        self.student = jsonobj['student']
        self.logger.info(self.student['xm'])
        return self.student['xm']
