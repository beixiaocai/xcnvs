import os
from app.models import *
from app.views.ViewsBase import *
from django.shortcuts import render

def api_getIndex(request):
    # highcharts 例子 https://www.highcharts.com.cn/demo/highcharts/dynamic-update
    ret = False
    msg = "未知错误"

    appInfo = {}
    osInfo = {}

    if request.method == 'GET':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            # params = f_parseGetParams(request)

            osSystem = OSSystem()
            appInfo = {
                "project_ua": PROJECT_UA,
                "project_version": PROJECT_VERSION,
                "project_flag": PROJECT_FLAG,
                "project_built": PROJECT_BUILT,
                "start_timestamp": PROJECT_ADMIN_START_TIMESTAMP
            }
            osInfo = osSystem.getOSInfo()

            ret = True
            msg = "success"
        else:
            msg = __check_msg
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "osInfo": osInfo,
        "appInfo": appInfo
    }
    return f_responseJson(res)
def api_getZlmProcessData(request):
    ret = False
    msg = "未知错误"
    info ={}
    if request.method == 'GET':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            # params = f_parseGetParams(request)

            is_online = g_zlm.version()
            if is_online:
                media_data = g_zlm.getMediaList()
                total_media_count = len(media_data)
            else:
                total_media_count = 0

            info["process_state"] = 1 if is_online else 0
            info["total_media_count"] = total_media_count

            ret = True
            msg = "success"
        else:
            msg = __check_msg
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "info": info
    }
    return f_responseJson(res)
def api_getAllCoreProcessData(request):
    ret = False
    msg = "未知错误"
    data = []
    info = {}

    if request.method == 'GET':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parseGetParams(request)
            g_logger.info("OpenView.getAllCoreProcessData() params:%s" % str(params))
            node_code = str(params.get('node_code', "")).strip()
            __node_ret,__node_msg,node = f_checkNode(node_code=node_code)
            if __node_ret:
                try:

                    headers = {
                        "User-Agent": PROJECT_UA,
                        "Content-Type": "application/json;",
                        "Safe": node.xcms_safe
                    }
                    res = requests.get(url='%s/open/getAllCoreProcessData' % node.address,
                                       headers=headers, timeout=TIMEOUT)

                    if res.status_code == 200:
                        res_result = res.json()
                        msg = res_result.get("msg")
                        if int(res_result.get("code", 0)) == 1000:
                            data = res_result.get("data")
                            info = res_result.get("info")

                            ret = True

                    else:
                        raise Exception("status=%d" % res.status_code)
                except Exception as e:
                    msg = str(e)
            else:
                msg = __node_msg
        else:
            msg = __check_msg
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data,
        "info": info
    }
    g_logger.debug("OpenView.getAllCoreProcessData() res:%s" % str(res))

    return f_responseJson(res)

def api_getAllCoreProcessData2(request):
    ret = False
    msg = "未知错误"
    info = {}

    if request.method == 'GET':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parseGetParams(request)
            g_logger.info("OpenView.getAllCoreProcessData2() params:%s" % str(params))
            node_code = str(params.get('node_code', "")).strip()

            __node_ret, __node_msg, node = f_checkNode(node_code=node_code)
            if __node_ret:
                try:

                    headers = {
                        "User-Agent": PROJECT_UA,
                        "Content-Type": "application/json;",
                        "Safe": node.xcms_safe
                    }
                    res = requests.get(url='%s/open/getAllCoreProcessData2' % node.address,
                                       headers=headers, timeout=TIMEOUT)

                    if res.status_code == 200:
                        res_result = res.json()
                        msg = res_result.get("msg")
                        if int(res_result.get("code", 0)) == 1000:
                            info = res_result.get("info")

                            ret = True

                    else:
                        raise Exception("status=%d" % res.status_code)
                except Exception as e:
                    msg = str(e)
            else:
                msg = __node_msg
        else:
            msg = __check_msg
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "info": info
    }
    g_logger.debug("OpenView.getAllCoreProcessData2() res:%s" % str(res))

    return f_responseJson(res)
def api_getAllStreamData(request):
    ret = False
    msg = "未知错误"
    data = []

    if request.method == "GET":
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parseGetParams(request)
            g_logger.debug("OpenView.getAllStreamData() params=%s" % str(params))
            node_code = str(params.get('node_code', "")).strip()

            __node_ret, __node_msg, node = f_checkNode(node_code=node_code)
            if __node_ret:
                try:
                    if node.version < 4:
                        raise Exception("v3系列节点不支持该功能")
                    
                    headers = {
                        "User-Agent": PROJECT_UA,
                        "Content-Type": "application/json;",
                        "Safe": node.xcms_safe
                    }
                    res = requests.get(url='%s/open/getAllStreamData' % node.address,
                                       headers=headers, timeout=TIMEOUT)

                    if res.status_code == 200:
                        res_result = res.json()
                        msg = res_result.get("msg")
                        if int(res_result.get("code", 0)) == 1000:
                            data = res_result.get("data")
                            ret = True

                    else:
                        raise Exception("status=%d" % res.status_code)
                except Exception as e:
                    msg = str(e)
            else:
                msg = __node_msg

        else:
            msg = __check_msg
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data
    }
    return f_responseJson(res)
def api_getControl(request):
    ret = False
    msg = "未知错误"
    info = {}
    if request.method == "GET":
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parseGetParams(request)
            g_logger.debug("OpenView.getControl() params=%s" % str(params))
            control_code = params.get("code","").strip()
            node_code = str(params.get('node_code', "")).strip()

            __node_ret, __node_msg, node = f_checkNode(node_code=node_code)
            if __node_ret:
                try:
                    if node.version < 4:
                        raise Exception(
                            "v3系列节点不支持该功能")
                    
                    headers = {
                        "User-Agent": PROJECT_UA,
                        "Content-Type": "application/json;",
                        "Safe": node.xcms_safe
                    }
                    res = requests.get(url='%s/open/getControl?code=%s' % (node.address,control_code),
                                       headers=headers, timeout=TIMEOUT)

                    if res.status_code == 200:
                        res_result = res.json()
                        msg = res_result.get("msg")
                        if int(res_result.get("code", 0)) == 1000:
                            info = res_result.get("info")

                            ret = True

                    else:
                        raise Exception("status=%d" % res.status_code)
                except Exception as e:
                    msg = str(e)
            else:
                msg = __node_msg
        else:
            msg = __check_msg
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "info": info
    }
    return f_responseJson(res)


