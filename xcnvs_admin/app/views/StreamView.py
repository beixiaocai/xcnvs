from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render, redirect
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

    return render(request, 'app/stream/index.html', context)

def api_openIndex(request):
    ret = False
    msg = "未知错误"
    data = []
    pageData = []
    extra = {}

    if request.method == 'GET':
        params = f_parseGetParams(request)
        # g_logger.info("StreamView.getIndex() params:%s" % str(params))

        page = params.get('p', 1)
        page_size = params.get('ps', 10)
        search_text = str(params.get('search_text', "")).strip()
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
                res = requests.get(url='%s/stream/openIndex?p=%s&ps=%s&search_text=%s' % (node.address, page, page_size, search_text),
                                   headers=headers, timeout=TIMEOUT)

                if res.status_code == 200:
                    res_result = res.json()
                    msg = res_result.get("msg")
                    if int(res_result.get("code", 0)) == 1000:
                        data = res_result.get("data")
                        pageData = res_result.get("pageData")
                        extra = res_result.get("extra")

                        ret = True
                else:
                    raise Exception("status=%d" % res.status_code)
            except Exception as e:
                msg = str(e)
        else:
            msg = __node_msg
    else:
        msg = "request method not supported"
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data,
        "pageData": pageData,
        "extra": extra
    }
    # g_logger.info("StreamView.getIndex() res:%s" % str(res))
    return f_responseJson(res)

def api_openAddStreamProxy(request):
    ret = False
    msg = "未知错误"
    if request.method == 'POST':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parsePostParams(request)
            g_logger.info("StreamView.openAddStreamProxy() params:%s" % str(params))

            node_code = str(params.get('node_code', "")).strip()
            __node_ret, __node_msg, node = f_checkNode(node_code=node_code)
            if __node_ret:
                try:

                    headers = {
                        "User-Agent": PROJECT_UA,
                        "Content-Type": "application/json;",
                        "Safe": node.xcms_safe
                    }
                    res = requests.post(url='%s/stream/openAddStreamProxy' % node.address,
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
    g_logger.info("StreamView.openAddStreamProxy() res:%s" % str(res))
    return f_responseJson(res)

def api_openDelStreamProxy(request):
    ret = False
    msg = "未知错误"
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("StreamView.openDelStreamProxy() params:%s" % str(params))

        node_code = str(params.get('node_code', "")).strip()
        __node_ret, __node_msg, node = f_checkNode(node_code=node_code)
        if __node_ret:
            try:

                headers = {
                    "User-Agent": PROJECT_UA,
                    "Content-Type": "application/json;",
                    "Safe": node.xcms_safe
                }
                res = requests.post(url='%s/stream/openDelStreamProxy' % node.address,
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
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("StreamView.openDelStreamProxy() res:%s" % str(res))
    return f_responseJson(res)
def api_openHandleAllStreamProxy(request):
    ret = False
    msg = "未知错误"

    if request.method == 'POST':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parsePostParams(request)
            g_logger.info("StreamView.openHandleAllStreamProxy() params:%s" % str(params))

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
                    res = requests.post(url='%s/stream/openHandleAllStreamProxy' % node.address,
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
    g_logger.info("StreamView.openHandleAllStreamProxy() res:%s" % str(res))
    return f_responseJson(res)
def api_openDel(request):
    ret = False
    msg = "未知错误"
    if request.method == 'POST':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parsePostParams(request)
            g_logger.info("StreamView.openDel() params:%s" % str(params))

            node_code = str(params.get('node_code', "")).strip()
            __node_ret, __node_msg, node = f_checkNode(node_code=node_code)
            if __node_ret:
                try:
                    headers = {
                        "User-Agent": PROJECT_UA,
                        "Content-Type": "application/json;",
                        "Safe": node.xcms_safe
                    }
                    res = requests.post(url='%s/stream/openDel' % node.address,
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
    g_logger.info("StreamView.openDel() res:%s" % str(res))
    return f_responseJson(res)
def player(request):
    context = {
        "settings": f_settingsReadData()
    }
    params = f_parseGetParams(request)
    g_logger.debug("StreamView.player() params:%s" % str(params))

    stream_app = params.get('app', "").strip()
    stream_name = params.get('name', "").strip()
    node_code = params.get('node_code', "").strip()

    __node_ret, __node_msg, node = f_checkNode(node_code=node_code)
    if stream_app and  stream_name and __node_ret:
        app = node_code
        name = "%s-%s"%(stream_app,stream_name)
        info = {
            "node_code": node_code,
            "stream_app":stream_app,
            "stream_name":stream_name,
            "wsHost":g_zlm.get_wsHost(),
            "wsMp4Url":g_zlm.get_wsMp4Url(app=app, name=name),
            "httpMp4Url":g_zlm.get_httpMp4Url(app=app, name=name),
            "rtspUrl":g_zlm.get_rtspUrl(app=app, name=name)
        }
        context["info"] = info
        g_logger.debug("StreamView.player() info:%s" % str(info))

        return render(request, 'app/stream/player.html', context)
    else:
        return redirect("/stream/index")