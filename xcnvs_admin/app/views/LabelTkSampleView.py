import os
import time
from datetime import datetime
import random
from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render, redirect
from app.utils.Utils import buildPageLabels, gen_random_code_s
from app.utils.UploadUtils import UploadUtils
import cv2

def api_getIndex(request):
    ret = False
    msg = "未知错误"

    params = f_parseGetParams(request)
    page = params.get('p', 1)
    page_size = params.get('ps', 10)
    task_code = params.get('task_code', "").strip()

    try:
        page = int(page)
    except:
        page = 1
    try:
        page_size = int(page_size)
        if page_size > 20 or page_size < 10:
            page_size = 10
    except:
        page_size = 10


    skip = (page - 1) * page_size
    sql_data = "select * from xcnvs_labeltk_sample where task_code='%s' order by id desc limit %d,%d " % (task_code,skip, page_size)
    count = g_database.select("select count(id) as count from xcnvs_labeltk_sample where task_code='%s'" % task_code)
    count = int(count[0]["count"])
    if count > 0:
        data = g_database.select(sql_data)
    else:
        data = []

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
    ret = True
    msg = "success"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data,
        "pageData": pageData
    }
    return f_responseJson(res)


def api_postAdd(request):
    ret = False
    msg = "未知错误"
    if request.method == 'POST':
        params = f_parsePostParams(request)
        task_code = params.get("task_code", "").strip()
        task_type = int(params.get("task_type", 0))
        upload_type = int(params.get("upload_type", 0)) # 1:图片文件 2:图片文件夹 3:视频文件 4:labelme文件夹

        task = LabelTaskModel.objects.filter(code=task_code).first()
        task_state = 1 if task else 0
        user = f_sessionReadUser(request)

        success_count = 0
        error_count = 0
        labelme_jpg_dict = {}
        labelme_json_dict = {}

        upload_utils = UploadUtils()
        filenames = request.FILES.keys()
        for filename in filenames:
            file = request.FILES.get(filename)
            if upload_type == 1 or upload_type == 2:
                __ret, __msg, __info = upload_utils.upload_sample_image(storageDir=g_config.storageDir, task_code=task_code, file=file)

                if __ret:
                    old_filename = __info.get("old_filename")
                    new_filename = __info.get("new_filename")

                    sample_code = gen_random_code_s("tksample")

                    sample = LabelTkSampleModel()
                    sample.sort = 0
                    sample.code = sample_code
                    sample.user_id = user.get("id")
                    sample.username = user.get("username")
                    sample.task_type = task_type
                    sample.task_code = task_code
                    sample.old_filename = old_filename
                    sample.new_filename = new_filename
                    sample.remark = ""
                    sample.create_time = datetime.now()
                    sample.state = task_state
                    sample.annotation_user_id = 0
                    sample.annotation_state = 0
                    sample.save()

                    success_count += 1
                else:
                    error_count += 1
            elif upload_type == 3:
                __ret, __msg, __info = upload_utils.upload_sample_video(storageDir=g_config.storageDir,
                                                                        task_code=task_code, file=file)
                #print(__ret,__msg,__info)
                if __ret:
                    old_filename = __info.get("old_filename")
                    new_filenames = __info.get("new_filenames")

                    sample_code = gen_random_code_s("tksample")
                    i = 0
                    for new_filename in new_filenames:
                        sample = LabelTkSampleModel()
                        sample.sort = 0
                        sample.code = sample_code +"-"+str(i)
                        sample.user_id = user.get("id")
                        sample.username = user.get("username")
                        sample.task_type = task_type
                        sample.task_code = task_code
                        sample.old_filename = old_filename
                        sample.new_filename = new_filename
                        sample.remark = ""
                        sample.create_time = datetime.now()
                        sample.state = task_state
                        sample.annotation_user_id = 0
                        sample.annotation_state = 0
                        sample.save()
                        i += 1
                        success_count += 1

                else:
                    error_count += 1
            elif upload_type == 4:
                __ret, __msg, __info = upload_utils.upload_sample_labelme(storageDir=g_config.storageDir,
                                                                        task_code=task_code, file=file)
                if __ret:
                    old_filename_prefix = __info["old_filename_prefix"]
                    old_filename_suffix = __info["old_filename_suffix"]
                    if old_filename_suffix == "jpg":
                        labelme_jpg_dict[old_filename_prefix] = __info
                    elif old_filename_suffix == "json":
                        labelme_json_dict[old_filename_prefix] = __info

        if upload_type == 4:

            sample_code = gen_random_code_s("tksample")
            labelName_dict = {}
            i = 0
            for k in labelme_jpg_dict.keys():
                __jpg_info = labelme_jpg_dict.get(k)
                __json_info = labelme_json_dict.get(k)
                if __jpg_info and __json_info:
                    old_filename = __jpg_info.get("old_filename")
                    new_filename = __jpg_info.get("new_filename")

                    annotation_content = []
                    annotation = __json_info.get("annotation")

                    shapes = annotation.get("shapes")
                    imageWidth = annotation.get("imageWidth")
                    imageHeight = annotation.get("imageHeight")

                    for shape in shapes:
                        label = shape.get("label") # drive
                        labelName_dict[label] = labelName_dict.get(label,0) + 1

                        shape_type = shape.get("shape_type")
                        points = shape.get("points")

                        x1 = float(points[0][0])
                        y1 = float(points[0][1])
                        x2 = float(points[1][0])
                        y2 = float(points[1][1])

                        width = x2 - x1
                        height = y2 - y1

                        annotation_content.append({
                            "id": int(time.time()),
                            "x": x1,
                            "y": y1,
                            "width": width,
                            "height": height,
                            "category": label,
                            "categoryColor": "#EE0000",
                            "imageWidth": imageWidth,
                            "imageHeight": imageHeight,
                            "canvasWidth": imageWidth,
                            "canvasHeight": imageHeight
                        })

                    sample = LabelTkSampleModel()
                    sample.sort = 0
                    sample.code = sample_code + "-" + str(i)
                    sample.user_id = user.get("id")
                    sample.username = user.get("username")
                    sample.task_type = task_type
                    sample.task_code = task_code
                    sample.old_filename = old_filename
                    sample.new_filename = new_filename
                    sample.remark = ""
                    sample.create_time = datetime.now()
                    sample.state = task_state
                    sample.annotation_user_id = user.get("id")
                    sample.annotation_state = 1
                    sample.annotation_content= json.dumps(annotation_content)
                    sample.save()

                    i += 1
                    success_count += 1

            if task:
                task_tags = []
                task_tag_dict = {}
                try:
                    task_tags = json.loads(task.tags)
                    for task_tag in task_tags:
                        task_tag_dict[task_tag["category"]] = True
                except:pass

                for labelName in labelName_dict.keys():
                    if not task_tag_dict.get(labelName):
                        task_tags.append({
                            "id": int(time.time()),
                            "category": labelName,
                            "color": "#ff0000"
                        })
                task.tags = json.dumps(task_tags)
                task.save()


        msg = "成功%d条，失败%d条" % (success_count, error_count)
        if success_count > 0:
            ret = True

    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    return f_responseJson(res)



def api_postDel(request):
    ret = False
    msg = "未知错误"
    if request.method == 'POST':
        params = f_parsePostParams(request)
        code = params.get("code", "").strip()
        sample = LabelTkSampleModel.objects.filter(code=code)
        if len(sample) > 0:
            sample = sample[0]

            new_filename_abs = os.path.join(
                g_config.storageDir, 
                'labelTask',
                sample.task_code, 
                'labeltkSample',
                sample.new_filename
            )
            if os.path.exists(new_filename_abs):
                os.remove(new_filename_abs)
            sample.delete()

            ret = True
            msg = "删除成功"

        else:
            msg = "该样本不存在！"
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    return f_responseJson(res)



def api_getInfo(request):
    ret = False
    msg = "未知错误"

    params = f_parseGetParams(request)
    task_code = params.get('task_code',"").strip()
    sample_code = params.get('sample_code',"").strip()

    sample = {}
    tags = 0
    preSampleCode = sample_code
    nextSampleCode = sample_code
    curIndex = 0
    totalCount = 0

    task = LabelTaskModel.objects.filter(code=task_code).first()
    if task:
        tags = task.tags
        sample = g_database.select("select * from xcnvs_labeltk_sample where code='%s' limit 1" % sample_code)
        if len(sample) > 0:
            sample = sample[0]
            samples = g_database.select("select code from xcnvs_labeltk_sample where task_code='%s' and state=1" % task_code)
            curIndex = 0
            totalCount = len(samples)

            i = 0
            for d in samples:
                if d["code"] == sample_code:
                    curIndex = i
                    break
                i += 1

            try:
                preSampleCode = samples[curIndex - 1]["code"]
            except:
                pass

            try:
                if curIndex == totalCount - 1:
                    nextSampleCode = samples[0]["code"]
                else:
                    nextSampleCode = samples[curIndex + 1]["code"]
            except:
                pass

            ret = True
            msg = "success"

        else:
            msg = "样本不存在"
    else:
        msg = "标注任务不存在"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "task_code":task_code,
        "sample_code":sample_code,
        "tags":tags,
        "sample": sample,
        "statistics": {
            "pre_sample_code":preSampleCode,
            "next_sample_code":nextSampleCode,
            "cur_index":curIndex,
            "total_count":totalCount
        }
    }
    return f_responseJson(res)


def api_postSaveAnnotation(request):
    ret = False
    msg = "未知错误"
    if request.method == 'POST':
        params = f_parsePostParams(request)
        sample_code = params.get("sample_code", "").strip()
        annotation_content = params.get("annotation_content", "").strip()
        tags = params.get("tags", "").strip()

        user = f_sessionReadUser(request)
        user_id = user.get("id")
        username = user.get("username")

        sample = LabelTkSampleModel.objects.filter(code=sample_code).first()
        if sample:
            sample.annotation_user_id = user_id
            sample.annotation_username = username
            sample.annotation_time = datetime.now()
            sample.annotation_content = annotation_content
            sample.annotation_state = 1
            sample.save()

            task = LabelTaskModel.objects.filter(code=sample.task_code).first()
            if task:
                task.tags = tags
                task.save()

            ret = True
            msg = "保存标注成功"
        else:
            msg = "该样本不存在！"
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    return f_responseJson(res)
def api_postDelAnnotation(request):
    ret = False
    msg = "未知错误"
    if request.method == 'POST':
        params = f_parsePostParams(request)
        sample_code = params.get("sample_code", "").strip()

        sample = LabelTkSampleModel.objects.filter(code=sample_code).first()
        if sample:
            sample.annotation_state = 0
            sample.annotation_content = None
            sample.save()

            ret = True
            msg = "删除标注成功"
        else:
            msg = "该样本不存在！"
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    return f_responseJson(res)