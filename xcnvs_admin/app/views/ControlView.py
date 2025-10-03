import time
from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render, redirect
from app.utils.Utils import gen_random_code_s


def index(request):
    context = {
        "settings": f_settingsReadData()
    }
    params = f_parseGetParams(request)

    node_code = params.get("node_code","").strip()
    nodes = g_database.select("select code,nickname from xcnvs_node where state=1 order by id desc")
    # 填充默认选中的节点start
    if node_code == "":
        if len(nodes) > 0:
            node_code = nodes[0]["code"]
    # 填充默认选中的节点end
    context["node_code"] = node_code
    context["nodes"] = nodes

    return render(request, 'app/control/index.html', context)

def add(request):
    ret = False
    msg = "未知错误"
    context = {}
    if request.method == 'GET':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parseGetParams(request)
            g_logger.debug("ControlView.add() params:%s" % str(params))

            node_code = str(params.get('node_code', "")).strip()
            if node_code == "":
                return redirect("/control/index")

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
                    res = requests.get(url='%s/control/openAddContext' % node.address,
                                       headers=headers, timeout=TIMEOUT)

                    if res.status_code == 200:
                        res_result = res.json()
                        msg = res_result.get("msg")
                        if int(res_result.get("code", 0)) == 1000:
                            context = res_result.get("context")

                            print(context)
                            context["settings"] = f_settingsReadData()
                            # 替换视频流地址start
                            streams = context.get("streams")
                            for stream in streams:
                                new_stream_app = node_code
                                new_stream_name = "%s-%s"%(stream.get("app"),stream.get("name"))
                                wsMp4Url = g_zlm.get_wsMp4Url(app=new_stream_app, name=new_stream_name)
                                stream["wsMp4Url"] = wsMp4Url
                            # 替换视频流地址end

                            context["node_code"] =node_code
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

    if ret:
        return render(request, 'app/control/add.html', context)
    else:
        return render(request, 'app/message.html',
                      {"msg": msg, "is_success": False, "redirect_url": "/control/index"})

def api_openAdd(request):
    ret = False
    msg = "未知错误"
    if request.method == 'POST':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parsePostParams(request)
            g_logger.info("ControlView.openAdd() params:%s" % str(params))
            node_code = str(params.get('node_code', "")).strip()

            __node_ret, __node_msg, node = f_checkNode(node_code=node_code)
            if __node_ret:
                try:
                    headers = {
                        "User-Agent": PROJECT_UA,
                        "Content-Type": "application/json;",
                        "Safe": node.xcms_safe
                    }
                    res = requests.post(url='%s/control/openAdd' % node.address,
                                        headers=headers, data=json.dumps(params), timeout=TIMEOUT)

                    if res.status_code == 200:
                        res_result = res.json()
                        msg = res_result.get("msg")
                        if int(res_result.get("code", 0)) == 1000:
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
        "msg": msg
    }
    g_logger.info("ControlView.openAdd() res:%s" % str(res))
    return f_responseJson(res)
def edit(request):
    ret = False
    msg = "未知错误"
    context = {}
    if request.method == 'GET':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parseGetParams(request)
            g_logger.debug("ControlView.edit() params:%s" % str(params))

            code = params.get('code', "")
            node_code = str(params.get('node_code', "")).strip()
            if node_code == "":
                return redirect("/control/index")

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
                    res = requests.get(url='%s/control/openEditContext?code=%s' % (node.address,code),
                                       headers=headers, timeout=TIMEOUT)

                    if res.status_code == 200:
                        res_result = res.json()
                        msg = res_result.get("msg")
                        if int(res_result.get("code", 0)) == 1000:

                            context = res_result.get("context")
                            print(context)
                            context["settings"] =f_settingsReadData()

                            # 替换视频流地址start
                            control_stream = context.get("control_stream")
                            new_stream_app = node_code
                            new_stream_name = "%s-%s"%(control_stream.get("app"),control_stream.get("name"))
                            wsMp4Url = g_zlm.get_wsMp4Url(app=new_stream_app, name=new_stream_name)
                            context["control_stream"]["wsMp4Url"] = wsMp4Url
                            # 替换视频流地址end
                            context["node_code"] = node_code
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

    if ret:
        return render(request, 'app/control/add.html', context)
    else:
        return render(request, 'app/message.html',
                      {"msg": msg, "is_success": False, "redirect_url": "/control/index"})

def api_openEdit(request):
    ret = False
    msg = "未知错误"
    if request.method == 'POST':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parsePostParams(request)
            g_logger.info("ControlView.openEdit() params:%s" % str(params))
            node_code = str(params.get('node_code', "")).strip()

            __node_ret, __node_msg, node = f_checkNode(node_code=node_code)
            if __node_ret:
                try:
                    headers = {
                        "User-Agent": PROJECT_UA,
                        "Content-Type": "application/json;",
                        "Safe": node.xcms_safe
                    }
                    res = requests.post(url='%s/control/openEdit' % node.address,
                                        headers=headers, data=json.dumps(params), timeout=TIMEOUT)

                    if res.status_code == 200:
                        res_result = res.json()
                        msg = res_result.get("msg")
                        if int(res_result.get("code", 0)) == 1000:
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
        "msg": msg
    }
    g_logger.info("ControlView.openEdit() res:%s" % str(res))
    return f_responseJson(res)

def api_openDel(request):
    ret = False
    msg = "未知错误"
    if request.method == 'POST':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parsePostParams(request)
            g_logger.info("ControlView.openDel() params:%s" % str(params))
            node_code = str(params.get('node_code', "")).strip()

            __node_ret, __node_msg, node = f_checkNode(node_code=node_code)
            if __node_ret:
                try:
                    headers = {
                        "User-Agent": PROJECT_UA,
                        "Content-Type": "application/json;",
                        "Safe": node.xcms_safe
                    }
                    res = requests.post(url='%s/control/openDel' % node.address,
                                        headers=headers, data=json.dumps(params), timeout=TIMEOUT)

                    if res.status_code == 200:
                        res_result = res.json()
                        msg = res_result.get("msg")
                        if int(res_result.get("code", 0)) == 1000:

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
        "msg": msg
    }
    g_logger.info("ControlView.openDel() res:%s" % str(res))
    return f_responseJson(res)

def api_openCopy(request):
    ret = False
    msg = "未知错误"
    if request.method == 'POST':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parsePostParams(request)
            g_logger.info("ControlView.openCopy() params:%s" % str(params))
            node_code = str(params.get('node_code', "")).strip()

            __node_ret, __node_msg, node = f_checkNode(node_code=node_code)
            if __node_ret:
                try:
                    headers = {
                        "User-Agent": PROJECT_UA,
                        "Content-Type": "application/json;",
                        "Safe": node.xcms_safe
                    }
                    res = requests.post(url='%s/control/openCopy' % node.address,
                                        headers=headers, data=json.dumps(params), timeout=TIMEOUT)

                    if res.status_code == 200:
                        res_result = res.json()
                        msg = res_result.get("msg")
                        if int(res_result.get("code", 0)) == 1000:

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
        "msg": msg
    }
    g_logger.info("ControlView.openCopy() res:%s" % str(res))
    return f_responseJson(res)

def api_openSettings(request):
    # 快捷设置
    ret = False
    msg = "未知错误"
    if request.method == 'POST':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parsePostParams(request)
            g_logger.info("ControlView.openSettings() params:%s" % str(params))
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
                    res = requests.post(url='%s/control/openSettings' % node.address,
                                        headers=headers, data=json.dumps(params), timeout=TIMEOUT)

                    if res.status_code == 200:
                        res_result = res.json()
                        msg = res_result.get("msg")
                        if int(res_result.get("code", 0)) == 1000:
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
        "msg": msg
    }
    g_logger.info("ControlView.openSettings() res:%s" % str(res))
    return f_responseJson(res)

def api_openLog(request):
    ret = False
    msg = "未知错误"
    data = []
    if request.method == 'GET':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parseGetParams(request)
            g_logger.info("ControlView.openLog() params:%s" % str(params))

            controlCode = params.get("controlCode")
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
                    res = requests.get(url='%s/control/openLog?controlCode=%s' % (node.address, controlCode),
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
    g_logger.info("ControlView.openLog() res:%s" % str(res))
    return f_responseJson(res)

def api_openIndex(request):
    ret = False
    msg = "未知错误"
    data = []
    pageData = {}

    if request.method == 'GET':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parseGetParams(request)
            page = params.get('p', 1)
            page_size = params.get('ps', 10)
            search_text = str(params.get('search_text', "")).strip() # v4.638新增
            node_code = str(params.get('node_code', "")).strip()

            __node_ret, __node_msg, node = f_checkNode(node_code=node_code)
            if __node_ret:
                try:
                    page = int(page)
                except:
                    page = 1
                try:
                    page_size = int(page_size)
                    if page_size < 1:
                        page_size = 1
                except:
                    page_size = 10

                try:

                    headers = {
                        "User-Agent": PROJECT_UA,
                        "Content-Type": "application/json;",
                        "Safe": node.xcms_safe
                    }

                    res = requests.get(url='%s/control/openIndex?p=%s&ps=%s&search_text=%s' % (node.address, page, page_size, search_text),
                                       headers=headers, timeout=TIMEOUT)

                    if res.status_code == 200:
                        res_result = res.json()
                        msg = res_result.get("msg")
                        if int(res_result.get("code", 0)) == 1000:
                            data = res_result.get("data")
                            pageData = res_result.get("pageData")

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
        "pageData": pageData
    }
    return f_responseJson(res)
def api_openHandleAllControl(request):
    ret = False
    msg = "未知错误"
    if request.method == 'POST':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parsePostParams(request)
            g_logger.info("ControlView.openHandleAllControl() params:%s" % str(params))
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

                    res = requests.post(url='%s/control/openHandleAllControl' % node.address,
                                        headers=headers, data=json.dumps(params), timeout=TIMEOUT)

                    if res.status_code == 200:
                        res_result = res.json()
                        msg = res_result.get("msg")
                        if int(res_result.get("code", 0)) == 1000:

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
        "msg": msg
    }
    g_logger.info("ControlView.openHandleAllControl() res:%s" % str(res))
    return f_responseJson(res)
def api_openStartControl(request):
    # 开始执行布控
    ret = False
    msg = "未知错误"

    if request.method == 'POST':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parsePostParams(request)
            g_logger.info("ControlView.openStartControl() params:%s" % str(params))

            node_code = str(params.get('node_code', "")).strip()

            __node_ret, __node_msg, node = f_checkNode(node_code=node_code)
            if __node_ret:
                try:
                    headers = {
                        "User-Agent": PROJECT_UA,
                        "Content-Type": "application/json;",
                        "Safe": node.xcms_safe
                    }

                    res = requests.post(url='%s/control/openStartControl' % node.address,
                                        headers=headers, data=json.dumps(params), timeout=TIMEOUT)

                    if res.status_code == 200:
                        res_result = res.json()
                        msg = res_result.get("msg")
                        if int(res_result.get("code", 0)) == 1000:

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
        "msg": msg
    }
    g_logger.info("ControlView.openStartControl() res:%s" % str(res))
    return f_responseJson(res)
def api_openStopControl(request):
    # 停止执行布控
    ret = False
    msg = "未知错误"

    if request.method == 'POST':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parsePostParams(request)
            g_logger.info("ControlView.openStopControl() params:%s" % str(params))

            node_code = str(params.get('node_code', "")).strip()

            __node_ret, __node_msg, node = f_checkNode(node_code=node_code)
            if __node_ret:
                try:
                    headers = {
                        "User-Agent": PROJECT_UA,
                        "Content-Type": "application/json;",
                        "Safe": node.xcms_safe
                    }
                    res = requests.post(url='%s/control/openStopControl' % node.address,
                                        headers=headers, data=json.dumps(params), timeout=TIMEOUT)

                    if res.status_code == 200:
                        res_result = res.json()
                        msg = res_result.get("msg")
                        if int(res_result.get("code", 0)) == 1000:

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
        "msg": msg
    }
    g_logger.info("ControlView.openStopControl() res:%s" % str(res))
    return f_responseJson(res)
