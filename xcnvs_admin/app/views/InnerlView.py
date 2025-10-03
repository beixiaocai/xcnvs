from app.views.ViewsBase import *
from app.models import *
import threading

"""
内部服务调用的接口
"""

# 被xcms_zlm调用，用于实时获得not found的流信息
def api_on_stream_not_found(request):
    ret = False
    msg = "unknown error"
    key = ""

    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.debug("on_stream_not_found() params:%s" % str(params))

        _app = params.get("app", "").strip()
        _stream = params.get("stream", "").strip()
        _schema = params.get("schema", "").strip()
        _vhost = params.get("vhost", "").strip()
        # _mediaServerId = params.get("mediaServerId", "").strip()

        node_code = _app
        __node_ret, __node_msg, node = f_checkNode(node_code=node_code)
        if __node_ret:
            _stream_array = _stream.split("-")
            if len(_stream_array) >=2:
                stream_app = _stream_array[0]
                stream_name = "-".join(_stream_array[1:])
                dst_stream_app = _app
                dst_stream_name = _stream
                try:
                    headers = {
                        "User-Agent": PROJECT_UA,
                        "Content-Type": "application/json;",
                        "Safe": node.xcms_safe
                    }
                    data = {
                        "stream_app": stream_app,
                        "stream_name": stream_name,
                        "dst_stream_app": dst_stream_app,
                        "dst_stream_name": dst_stream_name,
                        "dst_host": g_config.externalHost,
                        "dst_rtsp_port": g_config.mediaRtspPort,
                        "dst_http_port": g_config.mediaHttpPort,
                        "dst_secret": g_config.mediaSecret
                    }
                    data_json = json.dumps(data)
                    res = requests.post(url='%s/stream/openAddStreamPusherProxy' % node.address,
                                        headers=headers, data=data_json, timeout=TIMEOUT)

                    g_logger.debug("on_stream_not_found() stream/openAddStreamPusherProxy res.json:%s" % str(res.json()))

                    if res.status_code == 200:
                        res_result = res.json()
                        msg = res_result.get("msg")
                        if int(res_result.get("code", 0)) == 1000:
                            key = res_result.get("key", "").strip()
                            ret = True
                            msg = "success"
                    else:
                        raise Exception("status=%d" % res.status_code)
                except Exception as e:
                    msg = str(e)
            else:
                msg = "unsupported stream app=%s,stream=%s"%(_app,_stream)
        else:
            msg = __node_msg
    else:
        msg = "request method not supported"

    res = {
        "code": 0,
        "msg": "success"
    }
    g_logger.debug("on_stream_not_found() stream/openAddStreamPusherProxy ret=%d,msg=%s,key=%s" % (ret, msg, str(key)))
    return f_responseJson(res)

def f_initThread():
    i = 0
    while True:
        isSyncNode = False
        if i == 0 or i % 60 == 0:
            isSyncNode = True

        if isSyncNode:
            pass
            # f_syncNode()

        time.sleep(g_config.checkInterval)
        i += 1

def __INIT__():
    g_logger.info("InnerView.__INIT__()")
    t1 = threading.Thread(target=f_initThread)
    t1.daemon = True
    t1.start()
    # t.join()

__INIT__()
