import os
from app.views.ViewsBase import *
from django.shortcuts import render, redirect
from app.utils.Utils import buildPageLabels, gen_random_code_s
import random
import base64
import numpy as np
import cv2

def index(request):
    context = {
        "settings": f_settingsReadData()
    }
    return render(request, 'app/media/index.html', context)
def api_openIndex(request):
    ret = False
    msg = "未知错误"
    t1 = time.time()
    data = []

    if request.method == 'GET':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parseGetParams(request)

            page = params.get('p', 1)
            page_size = params.get('ps', 10)
            search_text = params.get('search_text', "").strip()

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
                skip = (page - 1) * page_size

                if search_text != "":
                    top_k = skip + page_size

                    embedding = g_aiInterfaceUtils.calcu_content_embedding(content=search_text)
                    media_keys = g_pgSQLVectorUtils.query_media_dim1024(query_embedding=embedding,top_k=top_k)
                    # print(type(media_keys),len(media_keys),media_keys)

                    if len(media_keys) > 0:
                        media_codes = []
                        for media_key in media_keys:
                            media_code = media_key["media_code"]
                            media_codes.append("'"+media_code+"'")

                        media_codes = media_codes[skip:skip+page_size]
                        if len(media_codes) > 0:
                            sql = "select * from xcnvs_node_media where code in(%s) " % ",".join(media_codes)
                            # print(sql)
                            __data = g_database.select(sql)
                            for d in __data:
                                content = d["content"]
                                d["title"] = content[0:30]+"..."
                                d["summary"] = content
                                d["location"] = d["id"]
                                d["media_url"] = "/static/storage/" + d["media_path"]
                                d["last_update_time"] = d["last_update_time"].strftime("%Y/%m/%d %H:%M:%S")
                                data.append(d)
                            ret = True
                            msg = "success"
                        else:
                            msg = "无更多数据"
                    else:
                        msg = "未匹配到数据"
                else:
                    sql = "select * from xcnvs_node_media order by id desc limit %d,%d" % (skip,page_size)
                    __data = g_database.select(sql)
                    for d in __data:
                        content = d["content"]
                        d["title"] = content[0:30] + "..."
                        d["summary"] = content
                        d["location"] = d["id"]
                        d["media_url"] = "/static/storage/" + d["media_path"]
                        d["last_update_time"] = d["last_update_time"].strftime("%Y/%m/%d %H:%M:%S")
                        data.append(d)

                    ret = True
                    msg = "success"

            except Exception as e:
                msg = str(e)
                g_logger.error("search() error: %s" % str(e))
        else:
            msg = __check_msg
    else:
        msg = "request method not supported"
    t2 = time.time()
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data,
        "duration": round(t2 - t1, 3)
    }
    return f_responseJson(res)
def api_openAdd(request):
    ret = False
    msg = "未知错误"

    if request.method == 'POST':
        params = f_parsePostParams(request)
        # print("MediaView.openAdd()",params)
        g_logger.debug("MediaView.openAdd() params:%s"%str(params))
        
        try:
            image_base64 = params.get("image_base64", None)  # 接收base64编码的图片并转换成cv2的图片格式
            nodeCode = params.get("nodeCode", "").strip()
            controlCode = params.get("controlCode", "").strip()
            streamCode = params.get("streamCode", "").strip()
            streamApp = params.get("streamApp", "").strip()
            streamName = params.get("streamName", "").strip()
            flowMode = int(params.get("flowMode", 5))
            flowCode = params.get("flowCode", "").strip()
            if not image_base64:
                raise Exception("image_base64 cannot be empty")
            if not streamCode:
                raise Exception("streamCode cannot be empty")
            if not flowCode:
                raise Exception("flowCode cannot be empty")
            if not streamCode:
                raise Exception("streamCode cannot be empty")
            # if not nodeCode:
            #     raise Exception("nodeCode cannot be empty")
            # nodeModel = NodeModel.objects.filter(node_code=nodeCode).filter()
            # if not nodeModel:
            #     raise Exception("nodeModel does not exist,nodeCode=%s" % nodeCode)

            encoded_image_byte = base64.b64decode(image_base64)
            image_array = np.frombuffer(encoded_image_byte, np.uint8)
            # image = turboJpeg.decode(image_array)  # turbojpeg 解码
            image = cv2.imdecode(image_array, cv2.COLOR_RGB2BGR)  # opencv 解码

            media_code = gen_random_code_s(prefix="media")
            content = g_aiInterfaceUtils.calcu_image(image=image)
            embedding = g_aiInterfaceUtils.calcu_content_embedding(content=content)
            # 首先写入向量
            g_pgSQLVectorUtils.add_media_dim1024(media_code, content, embedding)

            now_date = datetime.now()
            file_dir = "media/{nodeCode}/{controlCode}/{ymd}/{date}".format(
                nodeCode=nodeCode,
                controlCode=controlCode,
                ymd=now_date.strftime("%Y%m%d"),
                date=now_date.strftime("%Y%m%d%H%M%S")+str(random.randint(100,999))
            )

            file_dir_abs = os.path.join(g_config.storageDir,file_dir)
            if not os.path.exists(file_dir_abs):
                os.makedirs(file_dir_abs)
            filename = now_date.strftime("%Y%m%d%H%M%S")
            image_path = "%s/%s" % (file_dir, "%s.jpg" % filename)
            image_path_abs = "%s/%s" % (file_dir_abs, "%s.jpg" % filename)
            cv2.imwrite(image_path_abs, image)

            mediaModel = NodeMediaModel()
            mediaModel.code = media_code
            mediaModel.media_type = 1  # 1:图片 2:视频
            mediaModel.media_duration = 0
            mediaModel.media_path = image_path
            mediaModel.node_code = nodeCode
            mediaModel.control_code = controlCode
            mediaModel.stream_code = streamCode
            mediaModel.stream_app = streamApp
            mediaModel.stream_name = streamName
            mediaModel.flow_mode = flowMode
            mediaModel.flow_code = flowCode
            mediaModel.flow_name = flowCode
            mediaModel.content = content
            mediaModel.create_time = now_date
            mediaModel.create_timestamp = int(time.time())
            mediaModel.last_update_time = now_date

            mediaModel.save()

            ret = True
            msg = "success"

        except Exception as e:
            msg = "MediaView.openAdd() error:%s"%str(e)
            g_logger.error(msg)
            print(msg)
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "result": {  # 注：这里返回result，是为了兼容v3.52+或v4.709+的请求在接收接口返回值时，避免出错
            "happen": False,
            "happenScore": 0,
            "happenDesc": "",
            "detects": []
        }
    }
    g_logger.debug("MediaView.openAdd() res:%s" % str(res))

    return f_responseJson(res)
