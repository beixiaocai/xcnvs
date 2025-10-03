import os
import time

from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render, redirect
from app.utils.Utils import buildPageLabels, gen_random_code_s
from app.utils.UploadUtils import UploadUtils

def index(request):
    context = {
        "settings": f_settingsReadData()
    }

    data = []

    params = f_parseGetParams(request)

    page = params.get('p', 1)
    page_size = params.get('ps', 10)
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

    skip = (page - 1) * page_size
    sql_data = "select * from xcnvs_node order by id desc limit %d,%d " % (skip,page_size)
    sql_data_num = "select count(id) as count from xcnvs_node "

    count = g_database.select(sql_data_num)
    count = int(count[0]["count"])


    if count > 0:
        data = g_database.select(sql_data)


    page_num = int(count / page_size)  # 总页数
    if count % page_size > 0:
        page_num += 1
    pageLabels = buildPageLabels(page=page, page_num=page_num)
    pageData = {
        "page": page,
        "page_size": page_size,
        "page_num": page_num,
        "count": count,
        "pageLabels": pageLabels
    }

    context["data"] = data
    context["pageData"] = pageData
    return render(request, 'app/node/index.html', context)


def add(request):
    if "POST" == request.method:
        __ret = False
        __msg = "未知错误"

        params = f_parsePostParams(request)
        g_logger.info("NodeView.add() params:%s" % str(params))

        handle = params.get("handle")

        sort = int(params.get("sort",0))
        code = params.get("code", "").strip()
        nickname = params.get("nickname", "").strip()
        address = params.get("address", "").strip()
        xcms_safe = params.get("xcms_safe", "").strip()
        media_secret = params.get("media_secret", "").strip()
        try:
            if handle != "add":
                raise Exception("request parameters are incorrect")
            if nickname == "":
                raise Exception("nickname cannot be empty")
            if address == "":
                raise Exception("address cannot be empty")
            if xcms_safe == "":
                raise Exception("xcms_safe cannot be empty")
            if media_secret == "":
                raise Exception("media_secret cannot be empty")
            node = NodeModel.objects.filter(code=code).first()
            if node:
                raise Exception("the data already exists")

            user_id = f_sessionReadUserId(request)

            node = NodeModel()
            node.user_id = user_id
            node.sort = sort
            node.code = code
            node.nickname = nickname
            node.version = 0
            node.flag = ""
            node.system_name = ""
            node.machine_node = ""
            node.address = address
            node.xcms_safe = xcms_safe
            node.media_secret = media_secret
            node.machine_mac = ""
            node.is_auth = 0
            node.is_multi_process =0
            node.max_count = 0
            node.desc = ""
            node.auth_info = ""
            node.state = 0  # 默认0  0:未同步 1:在线 2:掉线

            node.image_path = ""
            node.expand1 = ""
            node.expand2 = ""
            node.create_time = datetime.now()
            node.last_update_time = datetime.now()
            node.node_code = ""
            node.node_host = ""

            node.save()
            # f_syncNode(code=node.code)
            __msg = "添加成功"
            __ret = True

        except Exception as e:
            __msg = str(e)

        if __ret:
            redirect_url = "/node/index"
        else:
            redirect_url = "/node/add"

        g_logger.info("NodeView.add() ret=%d,msg=%s" %(__ret, __msg))

        return render(request, 'app/message.html',
                      {"msg": __msg, "is_success": __ret, "redirect_url": redirect_url})
    else:
        context = {
            "settings": f_settingsReadData()
        }
        context["handle"] = "add"

        context["node"] = {
            "sort": 0,
            "code": gen_random_code_s("node"),
        }

        return render(request, 'app/node/add.html', context)


def edit(request):
    if "POST" == request.method:
        __ret = False
        __msg = "未知错误"

        params = f_parsePostParams(request)
        print(params)


        g_logger.info("NodeView.edit() params:%s" % str(params))
        handle = params.get("handle")
        sort = int(params.get("sort", 0))
        code = params.get("code", "").strip()
        nickname = params.get("nickname", "").strip()
        address = params.get("address", "").strip()
        xcms_safe = params.get("xcms_safe", "").strip()
        media_secret = params.get("media_secret", "").strip()

        try:
            if handle != "edit":
                raise Exception("request parameters are incorrect")
            if nickname == "":
                raise Exception("nickname cannot be empty")
            if address == "":
                raise Exception("address cannot be empty")
            if xcms_safe == "":
                raise Exception("xcms_safe cannot be empty")
            if media_secret == "":
                raise Exception("media_secret cannot be empty")

            node = NodeModel.objects.filter(code=code)
            if len(node) > 0:
                node = node[0]

                node.sort = sort
                node.nickname = nickname
                # node.version = 0
                # node.flag = ""
                # node.system_name = ""
                # node.machine_node = ""

                node.address = address
                node.xcms_safe = xcms_safe
                node.media_secret = media_secret
                # node.machine_mac = ""
                # node.is_auth = 0
                # node.is_multi_process = 0
                # node.max_count = 0
                # node.desc = ""
                # node.auth_info = ""
                # node.state = 0  # 默认0  0:未同步 1:在线 2:掉线

                # node.image_path = ""
                # node.expand1 = ""
                # node.expand2 = ""
                # node.create_time = datetime.now()
                node.last_update_time = datetime.now()
                # node.node_code = ""
                # node.node_host = ""
                node.save()

                #f_syncNode(code=node.code)

                __msg = "编辑成功"
                __ret = True
            else:
                __msg = "the data does not exist"
        except Exception as e:
            __msg = str(e)

        if __ret:
            redirect_url = "/node/index"
        else:
            redirect_url = "/node/edit?code=" + code
        g_logger.info("NodeView.edit() ret=%d,msg=%s" % (__ret, __msg))
        return render(request, 'app/message.html',
                      {"msg": __msg, "is_success": __ret, "redirect_url": redirect_url})

    else:
        context = {
            "settings": f_settingsReadData()
        }
        params = f_parseGetParams(request)
        code = params.get("code")
        if code:
            node = NodeModel.objects.filter(code=code)
            if len(node) > 0:
                node = node[0]
                context["handle"] = "edit"
                context["node"] = node
                return render(request, 'app/node/add.html', context)
            else:
                return render(request, 'app/message.html',
                              {"msg": "该节点不存在", "is_success": False, "redirect_url": "/node/index"})
        else:
            return redirect("/node/index")

def api_openDel(request):
    ret = False
    msg = "未知错误"
    if request.method == 'POST':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parsePostParams(request)
            g_logger.info("NodeView.openDel() params:%s" % str(params))

            code = params.get("code")
            node = NodeModel.objects.filter(code=code)
            if len(node) > 0:
                node = node[0]
                if node.delete():
                    ret = True
                    msg = "success"
                else:
                    msg = "failed to delete model"
            else:
                msg = "the data does not exist"
        else:
            msg = __check_msg
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("NodeView.openDel() res:%s" % str(res))
    return f_responseJson(res)

def api_openSync(request):
    ret = False
    msg = "未知错误"
    if request.method == 'POST':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            pass
            params = f_parsePostParams(request)
            g_logger.info("NodeView.openSync() params:%s" % str(params))
            ret,msg = f_syncNode()
        else:
            msg = __check_msg
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("NodeView.openSync() res:%s" % str(res))
    return f_responseJson(res)
def api_openInfo(request):
    ret = False
    msg = "未知错误"
    info = {

    }
    if request.method == 'GET':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parseGetParams(request)
            g_logger.info("NodeView.openInfo() params:%s" % str(params))

            sql_data_num = "select count(id) as count from xcnvs_node "
            count = g_database.select(sql_data_num)
            count = int(count[0]["count"])

            info = {
                "node_count": count
            }

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
    g_logger.info("NodeView.openInfo() res:%s" % str(res))
    return f_responseJson(res)
def api_openImportUpdate(request):
    # 导入升级包
    ret = False
    msg = "未知错误"
    if request.method == 'POST':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parsePostParams(request)
            g_logger.info("NodeView.openImportUpdate() params:%s" % str(params))
            node_code = str(params.get('node_code', "")).strip()
            __node_ret, __node_msg, node = f_checkNode(node_code=node_code)
            if __node_ret:
                import_filepath= None
                try:

                    file = request.FILES.get("file")
                    upload_utils = UploadUtils()
                    __ret, __msg, __filename,__filepath = upload_utils.upload_file2(file=file, upload_dir=g_config.uploadTempDir)

                    download_url = "http://%s:%d/static/upload/temp/%s" % (g_config.externalHost, g_config.adminPort, __filename)
                    g_logger.info("NodeView.openImportUpdate() ret=%d,msg=%s,filename=%s,filepath=%s,download_url=%s" % (__ret, __msg, str(__filename),str(__filepath),download_url))
                    if not __ret:
                        raise Exception(__msg)

                    if not os.path.exists(__filepath):
                        raise Exception("import failed")

                    import_filepath = __filepath

                    try:
                        headers = {
                            "User-Agent": PROJECT_UA,
                            "Content-Type": "application/json;",
                            "Safe": node.xcms_safe
                        }
                        res = requests.post(url='%s/system/openImportUpdate2' % node.address,
                                            headers=headers,
                                            data=json.dumps({
                                                "url": download_url,
                                            }), timeout=300)

                        if res.status_code == 200:
                            res_result = res.json()
                            msg = res_result.get("msg")
                            if int(res_result.get("code", 0)) == 1000:

                                ret = True
                                msg = "success"
                        else:
                            raise Exception("status=%d" % res.status_code)

                    except Exception as e:
                        g_logger.error("NodeView.openImportUpdate() error:%s" % str(e))
                        time.sleep(10)
                        f_syncNode(code=node.code)
                        ret = True
                        raise Exception("更新完成")

                except Exception as e:
                    msg = str(e)

                if import_filepath:
                    try:
                        if os.path.exists(import_filepath):
                            os.remove(import_filepath)
                    except Exception as e:
                        g_logger.error("NodeView.openImportUpdate() error:%s" % str(e))
                        


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
    g_logger.info("NodeView.openImportUpdate() res:%s" % str(res))
    return f_responseJson(res)