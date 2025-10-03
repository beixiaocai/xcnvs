import os
import time
import platform
import requests
from datetime import datetime, timedelta
import json
from django.http import HttpResponse
from framework.settings import (BASE_DIR, PROJECT_UA,PROJECT_BUILT,PROJECT_VERSION, PROJECT_FLAG,PROJECT_ADMIN_START_TIMESTAMP,TIMEOUT,
                                PROJECT_SUPPORT_XCMS_MIN_VERSION,PROJECT_SUPPORT_V3_MIN_VERSION)
from app.utils.ZLMediaKit import ZLMediaKit
from app.utils.Settings import Settings
from app.utils.Config import Config
from app.utils.Logger import CreateLogger
from app.utils.OSSystem import OSSystem
from app.utils.Database import Database
from app.utils.AiInterfaceUtils import AiInterfaceUtils
from app.utils.PgSQLVectorUtils import PgSQLVectorUtils
from app.models import *
# BASE_DIR # xcnvs_admin目录的位置
BASE_PARENT_DIR = os.path.dirname(BASE_DIR)  # BASE_PARENT_DIR是软件根目录的位置
g_filepath_config_json = os.path.join(BASE_PARENT_DIR, "config.json")
g_filepath_config_ini = os.path.join(BASE_PARENT_DIR, "config.ini")
g_filepath_settings_json = os.path.join(BASE_DIR, "settings.json")

g_config = Config(filepath=g_filepath_config_json)
g_settings = Settings(filepath=g_filepath_settings_json)

__log_dir = os.path.join(BASE_PARENT_DIR, "log")
if not os.path.exists(__log_dir):
    os.makedirs(__log_dir)
g_logger = CreateLogger(filepath=os.path.join(__log_dir, "xcnvs_admin%s.log" % (datetime.now().strftime("%Y%m%d-%H%M%S"))),
                        is_show_console=False,
                        log_debug=g_config.logDebug)

g_logger.info("%s v%s,%s" % (PROJECT_UA,PROJECT_VERSION, PROJECT_FLAG))
g_logger.info(PROJECT_BUILT)
g_logger.info("g_filepath_config_json=%s" % g_filepath_config_json)
g_logger.info("g_filepath_config_ini=%s" % g_filepath_config_ini)
g_logger.info("g_filepath_settings_json=%s" % g_filepath_settings_json)
g_logger.info("config.json:%s" % g_config.getStr())
g_logger.info("settings.json:%s" % g_settings.getStr())
g_logger.info("logDebug=%d" % g_config.logDebug)
g_osSystem = OSSystem()
g_aiInterfaceUtils = AiInterfaceUtils(logger=g_logger, config=g_config)
g_pgSQLVectorUtils = PgSQLVectorUtils(logger=g_logger, config=g_config)
g_zlm = ZLMediaKit(logger=g_logger, config=g_config)
g_database = Database(logger=g_logger)
g_session_key_user = "user"
g_session_key_captcha = "captcha"

def f_parseGetParams(request):
    params = {}
    try:
        for k in request.GET:
            params.__setitem__(k, request.GET.get(k))
    except Exception as e:
        params = {}

    return params
def f_parsePostParams(request):
    params = {}
    for k in request.POST:
        params.__setitem__(k, request.POST.get(k))

    # 接收json方式上传的参数
    if not params:
        try:
            params = request.body.decode('utf-8')
            params = json.loads(params)
        except Exception as e:
            params = {}

    return params
def f_parseRequestIp(request):
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR') # 备用方案
    except Exception as e:
        g_logger.error("f_parseRequestIp() error: %s"%str(e))
        ip = "0.0.0.0"
    return ip
def f_parseRequestPort(request):
    return 0



def readUser(request):
    user = request.session.get(g_session_key_user)
    return user

def f_sessionReadUser(request):
    user = request.session.get(g_session_key_user)
    return user

def f_sessionReadUserId(request):
    try:
        user_id = f_sessionReadUser(request).get("id")
    except:
        user_id = 0
    return user_id

def f_sessionLogout(request):
    if request.session.has_key(g_session_key_user):
        del request.session[g_session_key_user]
    if request.session.has_key(g_session_key_captcha):
        del request.session[g_session_key_captcha]
def f_checkRequestSafe(request):
    ret = False
    msg = "未知错误"
    # 检查请求是否安全
    user_id = f_sessionReadUserId(request)
    if user_id:
        ret = True
        msg = "success"
    else:
        headers = request.headers
        Safe = headers.get("Safe")
        if Safe and Safe == g_config.xcnvsSafe:
            ret = True
            msg = "success"
        else:
            msg = "safe verify error"
    return ret,msg


def f_readSampleCountAndAnnotationCount(task_code):
    sample_count = g_database.select("select count(id) as count from xcnvs_labeltk_sample where task_code='%s'" % task_code)
    sample_count = int(sample_count[0]["count"])
    sample_annotation_count = g_database.select(
        "select count(id) as count from xcnvs_labeltk_sample where task_code='%s' and annotation_state=1" % task_code)
    sample_annotation_count = int(sample_annotation_count[0]["count"])

    return sample_count, sample_annotation_count

def f_responseJson(res):
    def json_dumps_default(obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            raise TypeError

    return HttpResponse(json.dumps(res, default=json_dumps_default), content_type="application/json")

def f_settingsReadData():
    return g_settings.data

def f_checkNode(node_code):
    ret = False
    msg = "未知错误"
    node = None
    node = NodeModel.objects.filter(code=node_code)
    if len(node) > 0:
        node = node[0]
        if node.state == 0:
            msg = "节点未同步"
        elif node.state == 1:
            ret = True
            msg = "success"
        elif node.state == 2:
            msg = "节点离线"
        else:
            msg = "节点版本低于%.3f" % PROJECT_SUPPORT_XCMS_MIN_VERSION
    else:
        msg = "节点不存在"

    return ret, msg, node

class XcmsApi():

    def openDiscover(self,node):
        is_online = False
        ret = False
        msg = "未知错误"
        info = {}
        try:
            headers = {
                "User-Agent": PROJECT_UA,
                "Content-Type": "application/json;",
                "Safe": node.xcms_safe
            }
            res = requests.get(url='%s' % node.address,headers=headers, timeout=TIMEOUT)
            is_online = True # 表示节点在线
            try:
                res = requests.get(url='%s/open/discover?is_auth=1' % node.address,
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
                raise e
        except Exception as e:
            msg = str(e)
        print(is_online,ret,msg,info)
        return is_online,ret, msg, info
    def getAllStreamData(self,node):
        ret = False
        msg = "未知错误"
        data = []
        try:
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

        return ret, msg, data
    def getAllAlgroithmFlowData(self,node):
        ret = False
        msg = "未知错误"
        data = []
        try:
            headers = {
                "User-Agent": PROJECT_UA,
                "Content-Type": "application/json;",
                "Safe": node.xcms_safe
            }
            res = requests.get(url='%s/open/getAllAlgroithmFlowData' % node.address,
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

        return ret, msg, data


def f_syncNode(code=None):
    g_logger.info("f_syncNode() code=%s"%str(code))

    xcms_api = XcmsApi()

    success_count = 0
    error_count = 0
    if code:
        # 指定节点
        nodes = []
        node = NodeModel.objects.filter(code=code).first()
        nodes.append(node)
    else:
        # 所有节点
        nodes = NodeModel.objects.all()

    for node in nodes:
        __is_online = False
        __ret = False
        __msg = "未知错误"

        try:
            __is_online, __ret, __msg, __info = xcms_api.openDiscover(node)
            if __is_online:
                if __ret:
                    project_version = float(__info.get("project_version", 0))

                    node.version = project_version
                    node.flag = __info.get("project_flag")
                    node.system_name = __info.get("system_name")
                    node.machine_node = __info.get("machine_node")

                    node_code = __info.get("code","").strip()
                    if node_code:
                        node.node_code = node_code
                    else:
                        node.node_code = __info.get("name","").strip()

                    node.node_host = __info.get("host","").strip()

                    # 授权信息start
                    __info_auth = __info.get("auth")
                    if __info_auth:
                        __info_auth_info = __info_auth.get("info")
                        if __info_auth_info:
                            node.machine_mac = __info_auth_info.get("machineMac")
                            node.is_auth = int(__info_auth_info.get("isAuth", 0))
                            node.is_multi_process = int(__info_auth_info.get("isMultiProcess", 0))
                            node.max_count = int(__info_auth_info.get("maxCount", 0))
                            node.desc = __info_auth_info.get("desc")
                    node.auth_info = json.dumps(__info_auth)
                    # 授权信息end

                    isSyncNodeData = True

                    if isSyncNodeData:
                        g_logger.info("f_syncNode() 开始同步节点视频数据 node_code=%s"%node.code)
                        __ret,__msg,__stream_data = xcms_api.getAllStreamData(node)
                        now = datetime.now()
                        for d in __stream_data:
                            stream_code = d.get("code")
                            stream_nickname = d.get("nickname")
                            nodeStream = NodeStreamModel.objects.filter(stream_code=stream_code).first()
                            if nodeStream:
                                nodeStream.stream_nickname = stream_nickname
                                node_codes = nodeStream.node_codes
                                node_codes_list = node_codes.split(",")
                                node_codes_set = set(node_codes_list)
                                node_codes_set.add(node.code)
                                node_codes_list = list(node_codes_set)
                                nodeStream.node_codes = ",".join(node_codes_list)
                            else:
                                nodeStream = NodeStreamModel()
                                nodeStream.sort = 0
                                nodeStream.stream_code = stream_code
                                nodeStream.stream_nickname = stream_nickname
                                nodeStream.node_codes = node.code
                                nodeStream.state = 0
                                nodeStream.create_time = now
                            nodeStream.last_update_time = now
                            nodeStream.save()

                        g_logger.info("f_syncNode() 开始同步节点算法数据 node_code=%s" % node.code)
                        __ret,__msg,__flow_data = xcms_api.getAllAlgroithmFlowData(node)
                        for d in __flow_data:
                            flow_code = d.get("code")
                            flow_name = d.get("name")
                            nodeFlow = NodeAlgorithmFlowModel.objects.filter(flow_code=flow_code).first()
                            if nodeFlow:
                                nodeFlow.flow_name = flow_name

                                node_codes = nodeFlow.node_codes
                                node_codes_list = node_codes.split(",")
                                node_codes_set = set(node_codes_list)
                                node_codes_set.add(node.code)
                                node_codes_list = list(node_codes_set)
                                nodeFlow.node_codes = ",".join(node_codes_list)
                            else:
                                nodeFlow = NodeAlgorithmFlowModel()
                                nodeFlow.sort = 0
                                nodeFlow.flow_code = flow_code
                                nodeFlow.flow_name = flow_name
                                nodeFlow.node_codes = node.code
                                nodeFlow.state = 0
                                nodeFlow.create_time = now
                            nodeFlow.last_update_time = now
                            nodeFlow.save()

                    node.state = 1
                    if project_version > 4:
                        if project_version < PROJECT_SUPPORT_XCMS_MIN_VERSION:
                            node.state = 3
                            raise Exception("v4版本不能低于%.3f" % PROJECT_SUPPORT_XCMS_MIN_VERSION)

                    elif project_version > 3:
                        if project_version < PROJECT_SUPPORT_V3_MIN_VERSION:
                            node.state = 3
                            raise Exception("v3版本不能低于%.3f" % PROJECT_SUPPORT_V3_MIN_VERSION)
                    else:
                        raise Exception("节点版本不支持")

                else:
                    # node.state = 4
                    # raise Exception("读取节点信息失败")
                    node.state = 3
                    raise Exception("节点版本不支持")
            else:
                node.state = 2
                raise Exception("节点离线")
        except Exception as e:
            __msg = str(e)
            print("f_syncNode() node.code=%s,msg=%s" % (node.code, __msg))
            g_logger.error("f_syncNode() node.code=%s,msg=%s" % (node.code, __msg))

        if __ret:
            success_count += 1
        else:
            error_count += 1
        node.last_update_time = datetime.now()
        node.save()



    ret = True
    msg = "成功%d条，失败%d条" % (success_count, error_count)
    print("f_syncNode() ret=%d,msg=%s"%(ret,msg))
    g_logger.info("f_syncNode() ret=%d,msg=%s"%(ret,msg))

    return ret, msg


