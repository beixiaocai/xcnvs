import uuid
import random
import datetime, time
import os
import re
import platform
import math
import base64


def buildPageLabels(page, page_num):
    """
    :param page: 当前页面
    :param page_num: 总页数
    :return:
    返回式例：
        [{'page': 1, 'name': 1, 'cur': True}, {'page': 2, 'name': 2, 'cur': False}, {'page': 2, 'name': '下一页'}]

    """

    pageLabels = []
    if page > 1:
        pageLabels.append({
            "page": 1,
            "name": "首页"
        })
        pageLabels.append({
            "page": page - 1,  # 当前页点击时候触发的页数
            "name": "上一页"
        })
    if page == 1:
        pageArray = [1, 2, 3, 4]
    else:
        pageArray = list(range(page - 1, page + 3))  # page-1,page,page+1,page+2

    for p in pageArray:
        if p <= page_num:
            if page == p:
                cur = 1
            else:
                cur = 0
            pageLabels.append({
                "page": p,
                "name": p,
                "cur": cur
            })

    if page + 1 <= page_num:
        pageLabels.append({
            "page": page + 1,
            "name": "下一页"
        })
    if page_num > 0:
        pageLabels.append({
            "page": page_num,
            "name": "尾页"
        })
    return pageLabels

def gen_random_code_s(prefix,version=0):
    if version == 1:
        code = "%s%s%d" % (prefix, datetime.datetime.now().strftime('%Y%m%d%H%M%S'), random.randint(100, 999))
    elif version == 2:
        d = time.strftime("%Y%m%d%H%M%S")
        # d = time.strftime("%Y%m%d")
        val = str(uuid.uuid5(uuid.uuid1(), str(uuid.uuid1())))
        a = val.split("-")[0]
        code = "%s%s%s%d" % (prefix, d, a, random.randint(100000, 999999))
    else:
        val = str(uuid.uuid5(uuid.uuid1(), str(uuid.uuid1())))
        a = val.split("-")[0]
        a = str(a)[0:6]
        code = "%s%d%s" % (prefix, random.randint(1000, 9999), a)
    return code


def gen_dateArray(start_date, end_date,listType=True):
    __data = []
    curr_date = start_date
    while curr_date <= end_date:
        __data.append({
            # "date": curr_date,
            "ymd": "%04d%02d%02d" % (curr_date.year, curr_date.month, curr_date.day),
            "timestamp": int(curr_date.timestamp() * 1000), # 毫秒级时间戳
            "count": 0
        })
        curr_date += datetime.timedelta(1)
    if listType:
        return __data
    else:
        __dict = {}
        for d in __data:
            __dict[d["ymd"]] = d
        return __dict

def validate_chinese(s):
    for char in s:
        if '\u4e00' <= char <= '\u9fa5':
            return True
    return False

def validate_email(s):
    ex_email = re.compile(r'(^[\w][a-zA-Z0-9.]{4,19})@[a-zA-Z0-9]{2,10}.com')
    r = ex_email.match(s)

    if r:
        return True
    else:
        return False

def validate_tel(s):
    ex_tel = re.compile(r'(^[0-9\-]{11,15})')
    r = ex_tel.match(s)

    if r:
        return True
    else:
        return False
