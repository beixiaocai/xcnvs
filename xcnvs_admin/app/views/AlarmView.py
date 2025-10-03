import os
import time
import base64
import random
from app.views.ViewsBase import *
from app.models import *
from app.utils.TarUtils import TarUtils
from app.utils.AlarmUtils import AlarmUtils
from app.utils.Utils import gen_random_code_s
from django.shortcuts import render, redirect
from app.utils.Utils import buildPageLabels
from app.utils.OSSystem import OSSystem

def f_getAlarmInfoByCode(alarm_code):

    alarm = NodeAlarmModel.objects.filter(code=alarm_code).first()
    if alarm:
        video_count = alarm.video_count
        video_is_wav = 0
        if video_count > 0:
            videoUrl = g_config.storageDir_www + alarm.video_path
            if alarm.video_path.endswith("wav"):
                video_is_wav = 1
        else:
            videoUrl = ""

        image_count = alarm.image_count
        other_image_count = alarm.other_image_count

        if image_count > 0:
            imageUrl = g_config.storageDir_www + alarm.image_path
        else:
            imageUrl = "/static/images/720p.jpg"

        # 获取并拼接所有图片start
        imageUrlArray = []
        if image_count > 0:
            imageUrlArray.append(imageUrl)
            image_path = alarm.image_path

            if other_image_count > 0:
                image_path_ss = image_path.split(".")
                if len(image_path_ss) == 2:
                    image_path_l = image_path_ss[0]
                    image_path_r = image_path_ss[1]
                    for i in range(other_image_count):
                        __imageUrl = g_config.storageDir_www + "%s_%d.%s" % (image_path_l, (i + 1), image_path_r)
                        imageUrlArray.append(__imageUrl)
        # 获取并拼接所有图片end

        alarm_info = {
            "id": alarm.id,
            "code": alarm.code,
            "stream_code": alarm.stream_code,
            "control_code": alarm.control_code,
            "flow_code": alarm.flow_code,
            "flow_name": alarm.flow_name,
            "flag": alarm.flag,
            "draw_type": alarm.draw_type,
            "video_count": video_count,
            "video_is_wav": video_is_wav,
            "videoUrl": videoUrl,
            "image_count": image_count,
            "imageUrl": imageUrl,
            "imageUrlArray": imageUrlArray,  # 所有图片的地址，包括：主封面+其余图
            "desc": alarm.desc,
            "create_time": alarm.create_time,
            # "create_time_str": alarm.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "state": alarm.state,
            "review_remark": alarm.review_remark
        }
        return alarm_info

    return None
def index(request):
    context = {
        "settings": f_settingsReadData()
    }
    # http://127.0.0.1:9001/open/getAllControlData

    stream_data = g_database.select("select stream_code as code,stream_nickname as nickname from xcnvs_node_stream where state=0 ")
    flow_data = g_database.select("select flow_code as code,flow_name as name from xcnvs_node_algorithm_flow where state=0 ")

    # control_data = f_dbReadControlData()
    # stream_data = f_dbReadStreamData()
    # flow_data = f_dbReadAlgorithmFlowData()
    #
    # context["controls"] = control_data
    context["streams"] = stream_data
    context["flows"] = flow_data

    now_date = datetime.now()
    context["startDate"] = (now_date - timedelta(days=6)).strftime("%Y-%m-%d")
    context["endDate"] = now_date.strftime("%Y-%m-%d")

    return render(request, 'app/alarm/index.html', context)
def api_openIndex(request):
    ret = False
    msg = "未知错误"

    top_msg = ""
    data = []
    pageData = {}
    __check_ret, __check_msg = f_checkRequestSafe(request)
    if __check_ret:
        params = f_parseGetParams(request)
        page = params.get('p', 1)
        page_size = params.get('ps', 10)
        drawType = str(params.get('drawType', "-1"))
        controlCode = str(params.get('controlCode', "-1"))
        streamCode = str(params.get('streamCode', "-1"))
        flowCode = str(params.get('flowCode', "-1"))

        dateRange = str(params.get('dateRange'))

        startTimestamp = 0
        endTimestamp = 0
        try:
            dateRangeV = dateRange.split("to")
            if len(dateRangeV) == 2:
                startDate = dateRangeV[0].strip()
                endDate = dateRangeV[1].strip()
                startTimestamp = int(datetime.strptime(startDate, "%Y-%m-%d").timestamp())
                endTimestamp = int(datetime.strptime(endDate, "%Y-%m-%d").timestamp())
        except:
            pass

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

        search_fields = []
        if drawType != "-1":
            search_fields.append(" xcnvs_node_alarm.draw_type = {field} ".format(field=int(drawType)))
        if controlCode != "-1":
            search_fields.append(" xcnvs_node_alarm.control_code = '{field}' ".format(field=controlCode))
        if streamCode != "-1":
            search_fields.append(" xcnvs_node_alarm.stream_code = '{field}' ".format(field=streamCode))
        if flowCode != "-1":
            search_fields.append(" xcnvs_node_alarm.flow_code = '{field}' ".format(field=flowCode))

        if startTimestamp > 0 and endTimestamp > 0:
            search_fields.append(
                " xcnvs_node_alarm.create_timestamp>={startTimestamp} and xcnvs_node_alarm.create_timestamp<={endTimestamp} ".format(
                    startTimestamp=startTimestamp, endTimestamp=endTimestamp))
        # 拼接where
        where_count = "where xcnvs_node_alarm.state!=5 "
        if len(search_fields) > 0:
            where_count += " and " + "and".join(search_fields)

        where_unread_count = "where xcnvs_node_alarm.state=0 "
        if len(search_fields) > 0:
            where_unread_count += " and " + "and".join(search_fields)

        # 查询满足where条件的数量
        count = g_database.select("select count(id) as count from xcnvs_node_alarm %s" % where_count)
        count = int(count[0]["count"])

        unread_count = 0
        if count > 0:
            # 查询满足where的数据
            skip = (page - 1) * page_size
            __data = g_database.select("select xcnvs_node_alarm.* from xcnvs_node_alarm %s order by xcnvs_node_alarm.id desc limit %d,%d " % (
                where_count, skip,page_size))

            for d in __data:
                video_count = d["video_count"]
                if video_count > 0:
                    videoUrl = g_config.storageDir_www + d["video_path"]
                else:
                    videoUrl = ""

                image_count = d["image_count"]
                if image_count > 0:
                    imageUrl = g_config.storageDir_www + d["image_path"]
                else:
                    imageUrl = "/static/images/720p.jpg"

                data.append({
                    "id": d["id"],
                    "code": d["code"],
                    "video_count": video_count,
                    "videoUrl": videoUrl,
                    "image_count": image_count,
                    "imageUrl": imageUrl,
                    "desc": d["desc"],
                    "create_time": d["create_time"],
                    "create_time_str": d["create_time"].strftime("%Y-%m-%d %H:%M:%S"),
                    "state": d["state"],
                    "flow_code": d["flow_code"],
                    "flow_name": d["flow_name"],
                })
            # 查询满足where条件的未读数量
            unread_count = g_database.select("select count(id) as count from xcnvs_node_alarm %s" % where_unread_count)
            if len(unread_count) > 0:
                unread_count = int(unread_count[0]["count"])
            else:
                unread_count = 0

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
        if count > 0:
            top_msg = "总计%d条，未处理%d条" % (count,unread_count)
        else:
            top_msg = "暂无数据"

        ret = True
        msg = "success"
    else:
        msg = __check_msg

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data,
        "pageData": pageData,
        "top_msg": top_msg
    }
    return f_responseJson(res)
def edit(request):
    context = {
        "settings": f_settingsReadData()
    }
    if request.method == 'POST':
        ret = False
        msg = "未知错误"

        params = f_parsePostParams(request)
        g_logger.info("AlarmView.edit() params:%s" % str(params))

        code = params.get("code")
        state = params.get("state", 1)
        review_remark = params.get("review_remark", "")


        alarm = NodeAlarmModel.objects.filter(code=code)
        if len(alarm) > 0:
            alarm = alarm[0]
            alarm.state = state
            alarm.review_remark = review_remark
            alarm.save()
            ret = True
            msg = "success"
        else:
            msg = "the data does not exist"

        res = {
            "code": 1000 if ret else 0,
            "msg": msg
        }
        g_logger.info("AlarmView.edit() res:%s" % str(res))
        return f_responseJson(res)
    else:
        params = f_parseGetParams(request)
        code = params.get("code", "")
        if code:
            alarm = f_getAlarmInfoByCode(alarm_code=code)
            if alarm:
                context["alarm"] = alarm
                return render(request, 'app/alarm/edit.html', context)
            else:
                return render(request, 'app/message.html',
                              {"msg": "该报警数据不存在", "is_success": False, "redirect_url": "/alarm/index"})
        else:
            return redirect("/alarm/index")
def api_openAdd(request):
    ret = False
    msg = "未知错误"

    if request.method == 'POST':
        params = f_parsePostParams(request)
        # del params["videoArray"]
        # del params["imageArray"]
        # print("AlarmView.openAdd()",params)
        g_logger.debug("AlarmView.openAdd() params:%s"%str(params))

        try:
            nodeCode = params.get("nodeCode", "").strip()
            streamNickname = params.get("streamNickname", "").strip()
            streamDeviceId = params.get("streamDeviceId", "").strip()
            streamApp = params.get("streamApp", "").strip()
            streamName = params.get("streamName", "").strip()
            streamName = params.get("streamName", "").strip()
            streamCode = params.get("streamCode", "").strip()
            controlCode = params.get("controlCode", "").strip()
            flowCode = params.get("flowCode", "").strip()
            flowName = params.get("flowName", "").strip()
            flowMode = int(params.get("flowMode", 0))
            drawType = int(params.get("drawType", 0))
            flag = params.get("flag", "").strip()
            desc = params.get("desc", "").strip()
            videoCount = int(params.get("videoCount", 0))
            videoArray = params.get("videoArray")
            imageCount = int(params.get("imageCount", 0))
            imageArray = params.get("imageArray")
            imageDetects = params.get("imageDetects")
            extendParams = params.get("extendParams")
            createTime = params.get("createTime") # 报警源端的时间，示例：2025/09/18 12:30:45

            # if not nodeCode:
            #     raise Exception("nodeCode cannot be empty")
            # nodeModel = NodeModel.objects.filter(node_code=nodeCode).filter()
            # if not nodeModel:
            #     raise Exception("nodeModel does not exist,nodeCode=%s"%nodeCode)

            if not streamNickname:
                raise Exception("streamNickname cannot be empty")
            if not streamCode:
                raise Exception("streamCode cannot be empty")
            if not flowCode:
                raise Exception("flowCode cannot be empty")
            if not streamCode:
                raise Exception("streamCode cannot be empty")

            if imageCount < 1:
                raise Exception("imageCount must be greater than 0")

            now_date = datetime.now()
            file_dir = "alarm/{nodeCode}/{controlCode}/{ymd}/{date}/{drawType}".format(
                nodeCode=nodeCode,
                controlCode=controlCode,
                ymd=now_date.strftime("%Y%m%d"),
                date=now_date.strftime("%Y%m%d%H%M%S")+str(random.randint(100,999)),
                drawType=drawType
            )
            file_dir_abs = os.path.join(g_config.storageDir,file_dir)
            if not os.path.exists(file_dir_abs):
                os.makedirs(file_dir_abs)

            video_path = ""
            image_path = ""
            filename = now_date.strftime("%Y%m%d%H%M%S")
            if videoCount > 0:
                videoPath = videoArray[0]["videoPath"]
                if videoPath.endswith(".mp4"):
                    base64Str = videoArray[0]["base64Str"]
                    video_byte = base64.b64decode(base64Str)
                    print(videoCount,"视频序号:0")

                    video_path = "%s/%s"%(file_dir,"%s.mp4"%filename)
                    __video_path_abs = "%s/%s"%(file_dir_abs,"%s.mp4"%filename)
                    f = open(__video_path_abs, 'wb')
                    f.write(video_byte)
                    f.close()
                else:
                    pass
                    #TODO 2.0 暂不考虑.wav格式的音频文件
            other_image_count = imageCount - 1 if imageCount > 0 else 0  # 计算非主图的报警图片数量（一般该值都是等于0）
            if imageCount > 0:

                for i in range(len(imageArray)):
                    base64Str = imageArray[i]["base64Str"]
                    image_byte = base64.b64decode(base64Str)
                    print(imageCount,"图片序号:",i)
                    if i == 0:
                        image_path = "%s/%s"%(file_dir,"%s.jpg"%filename)
                        __image_path_abs = "%s/%s"%(file_dir_abs,"%s.jpg"%filename)
                        f = open(__image_path_abs, 'wb')
                        f.write(image_byte)
                        f.close()
                    else:
                        __other_image_path = "%s/%s"%(file_dir, "%s_%d.jpg" % (filename,i))
                        __other_image_path_abs = "%s/%s"%(file_dir_abs, "%s_%d.jpg" % (filename,i))
                        f = open(__other_image_path_abs, 'wb')
                        f.write(image_byte)
                        f.close()

            alarm = NodeAlarmModel()
            alarm.sort = 0
            alarm.code = gen_random_code_s(prefix="alarm")
            alarm.draw_type = drawType # 1:画框 0:未画框
            alarm.flag = flag
            alarm.control_code = controlCode
            alarm.desc = desc
            alarm.video_path = video_path
            alarm.video_count = videoCount
            alarm.image_path = image_path
            alarm.image_count = imageCount
            alarm.other_image_count = other_image_count
            alarm.level = 0 # 0:普通 1:警告 2:严重
            alarm.state = 0  # 0:未处理 1:已处理（正常报警） 2:已处理（误报） 5:逻辑删除
            alarm.is_check = 0 # 0 未被检测到报警 1 已被页面检测到报警

            alarm.review_remark = ""
            alarm.stream_app = streamApp
            alarm.stream_name = streamName
            alarm.stream_code = streamCode
            alarm.flow_mode = flowMode
            alarm.flow_code = flowCode
            alarm.flow_name = flowName
            # v4.610新增
            alarm.main_plate_color = 0
            alarm.main_plate_type = 0
            alarm.main_plate_no = ""
            alarm.main_track_max_code = ""
            alarm.main_track_max_custom_code = ""
            alarm.main_track_max_similary = 0
            alarm.expand1 = ""
            alarm.expand2 = ""

            alarm.create_time = now_date
            alarm.create_timestamp = int(time.time())
            alarm.last_update_time = now_date

            alarm.node_code = nodeCode
            alarm.save()

            msg = "success"
            ret = True

        except Exception as e:
            msg = "AlarmView.openAdd() error:%s"%str(e)
            g_logger.error(msg)

    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.debug("AlarmView.openAdd() res:%s" % str(res))

    return f_responseJson(res)
def api_openInfo(request):
    ret = False
    msg = "未知错误"
    info = {}
    if request.method == 'GET':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parseGetParams(request)
            g_logger.info("AlarmView.openInfo() params:%s" % str(params))

            alarm_code = params.get("code", "")
            alarm_info = f_getAlarmInfoByCode(alarm_code=alarm_code)
            if alarm_info:
                info = alarm_info
                ret = True
                msg = "success"
            else:
                msg = "the data does not exist"
        else:
            msg = __check_msg
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "info": info
    }
    g_logger.info("AlarmView.openInfo() res:%s" % str(res))

    return f_responseJson(res)

def api_openHandle(request):
    ret = False
    msg = "未知错误"

    if request.method == 'POST':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parsePostParams(request)
            g_logger.info("AlarmView.openHandle() params:%s" % str(params))

            alarm_ids_str = params.get("alarm_ids_str", "")
            handle = params.get("handle", None)
            if handle == "deleteAll": # 全部删除（逻辑删除）
                data = g_database.select("select count(1) as count from xcnvs_node_alarm where state!=5")
                count = data[0]["count"]
                if count > 0:
                    g_database.execute("update xcnvs_node_alarm set state = 5")
                    msg = "success"
                    ret = True
                else:
                    msg = "暂无待删除数据"
            elif handle == "clearCache":
                # 清理报警缓存
                ret, msg = AlarmUtils(g_logger, g_database, g_config.storageDir).clearAlarm()
            elif handle == "delete":  # 批量删除（逻辑删除）

                alarm_ids = alarm_ids_str.split(",")
                if len(alarm_ids) > 0:
                    success_count = 0
                    error_count = 0
                    for alarm_id in alarm_ids:
                        alarm = NodeAlarmModel.objects.filter(id=alarm_id)
                        if len(alarm) > 0:
                            alarm = alarm[0]
                            alarm.state = 5
                            alarm.save()
                            success_count += 1
                        else:
                            error_count += 1

                    msg = "成功%d条，失败%d条" % (success_count, error_count)
                    ret = True
                else:
                    msg = "请至少选择一条数据"
            else:
                msg = "不支持的操作类型"
        else:
            msg = __check_msg
    else:
        msg = "request method not supported"
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("AlarmView.openHandle() res:%s" % str(res))
    return f_responseJson(res)

def api_openExport(request):
    ret = False
    msg = "未知错误"
    info = {}

    if request.method == 'POST':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            pass
        else:
            msg = __check_msg
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "info": info
    }
    g_logger.info("AlarmView.openExport() res:%s" % str(res))
    return f_responseJson(res)
