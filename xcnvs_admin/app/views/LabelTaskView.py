import os
import shutil
import time
from datetime import datetime
from PIL import Image
from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render, redirect
from app.utils.Utils import buildPageLabels,gen_random_code_s
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
        if page_size > 20 or page_size < 10:
            page_size = 10
    except:
        page_size = 10

    skip = (page - 1) * page_size
    sql_data = "select * from xcnvs_label_task order by id desc limit %d,%d " % (
        skip, page_size)
    sql_data_num = "select count(id) as count from xcnvs_label_task "

    count = g_database.select(sql_data_num)

    if len(count) > 0:
        count = int(count[0]["count"])
        data = g_database.select(sql_data)
    else:
        count = 0

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
    context["storageDir_www"] = g_config.storageDir_www

    return render(request, 'app/labelTask/index.html', context)
def sample(request):
    context = {
        "settings": f_settingsReadData()
    }
    params = f_parseGetParams(request)

    task_code = params.get('task_code',"").strip()
    sample_code = params.get('sample_code', "").strip()

    task = LabelTaskModel.objects.filter(code=task_code).first()
    sample = None
    if task:
        sample = LabelTkSampleModel.objects.filter(code=sample_code).first()
        if not sample:
            sample = LabelTkSampleModel.objects.filter(task_code=task_code).order_by('-id').first()

    if task and sample:
        task_code = task.code
        sample_code = sample.code
        context["task_code"] = task_code
        context["sample_code"] = sample_code
        context["storageDir_www"] = g_config.storageDir_www
        return render(request, 'app/labelTask/sample.html', context)
    else:
        return redirect("/labelTask/index")

def add(request):
    if "POST" == request.method:
        __ret = False
        __msg = "未知错误"

        params = f_parsePostParams(request)
        handle = params.get("handle")
        code = params.get("code", "").strip()
        task_type = int(params.get("task_type",0))
        name = params.get("name", "").strip()
        remark = params.get("remark", "").strip()

        if "add" == handle and code:
            try:
                if name == "":
                    raise Exception("任务名称不能为空")

                if len(LabelTaskModel.objects.filter(code=code)) > 0:
                    raise Exception("任务编号已经存在")

                g_database.execute("update xcnvs_labeltk_sample set state=1 where task_code='%s'" % code)

                sample_count = g_database.select("select count(id) as count from xcnvs_labeltk_sample where task_code='%s'" % code)
                sample_count = int(sample_count[0]["count"])

                user = f_sessionReadUser(request)

                task = LabelTaskModel()
                task.sort = 0
                task.code = code
                task.user_id = user.get("id")
                task.username = user.get("username")
                task.task_type = task_type
                task.name = name
                task.remark = remark

                task.sample_annotation_count = 0
                task.sample_count = sample_count
                task.tags = ""

                task.create_time = datetime.now()
                task.create_timestamp = int(time.time())
                task.last_update_time = datetime.now()
                task.state = 0
                task.save()


                __msg = "添加成功"
                __ret = True

            except Exception as e:
                __msg = str(e)
        else:
            __msg = "请求参数不完整"

        res = {
            "code": 1000 if __ret else 0,
            "msg": __msg
        }
        return f_responseJson(res)


    else:
        context = {
            "settings": f_settingsReadData()
        }
        context["handle"] = "add"
        context["storageDir_www"] = g_config.storageDir_www
        context["task"] = {
            "code": gen_random_code_s("ltk"),
            "task_type": 1
        }
        return render(request, 'app/labelTask/add.html', context)


def edit(request):
    if "POST" == request.method:
        __ret = False
        __msg = "未知错误"

        params = f_parsePostParams(request)
        handle = params.get("handle")
        code = params.get("code", "").strip()
        name = params.get("name", "").strip()
        remark = params.get("remark", "").strip()

        if "edit" == handle and code:
            try:
                task = LabelTaskModel.objects.filter(code=code)
                if len(task) > 0:
                    task = task[0]
                else:
                    raise Exception("该任务不存在")

                sample_count, sample_annotation_count = f_readSampleCountAndAnnotationCount(task_code=code)

                task.name = name
                task.remark = remark
                # task.tags = ""
                task.sample_annotation_count = sample_annotation_count
                task.sample_count = sample_count

                task.save()


                __msg = "编辑成功"
                __ret = True

            except Exception as e:
                __msg = str(e)
        else:
            __msg = "请求参数不完整"

        res = {
            "code": 1000 if __ret else 0,
            "msg": __msg
        }
        return f_responseJson(res)

    else:
        context = {
            "settings": f_settingsReadData()
        }
        params = f_parseGetParams(request)
        code = params.get("code")
        if code:
            task = LabelTaskModel.objects.filter(code=code)
            if len(task) > 0:
                task = task[0]
                context["handle"] = "edit"
                context["storageDir_www"] = g_config.storageDir_www
                context["task"] = task
            else:
                return render(request, 'app/message.html',
                              {"msg": "请通过标注任务管理进入", "is_success": False, "redirect_url": "/labelTask/index"})

            return render(request, 'app/labelTask/add.html', context)
        else:
            return redirect("/labelTask/index")

def api_sync(request):
    ret = False
    msg = "未知错误"
    if request.method == 'GET':
        params = f_parseGetParams(request)

        tasks = LabelTaskModel.objects.all()
        for task in tasks:
            sample_count, sample_annotation_count = f_readSampleCountAndAnnotationCount(task_code=task.code)
            task.sample_count = sample_count
            task.sample_annotation_count = sample_annotation_count
            task.save()
        ret = True
        msg = "success"

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
        task_code = params.get("code", "").strip()
        task = LabelTaskModel.objects.filter(code=task_code)
        if len(task) > 0:
            task = task[0]

            del_sql = "delete from xcnvs_labeltk_sample where task_code='%s'" % task_code
            if not g_database.execute(del_sql):
                g_logger.error("del_sql=%s" % del_sql)

            task_dir = os.path.join(g_config.storageDir, "labelTask", task_code)
            try:
                if os.path.exists(task_dir):
                    shutil.rmtree(task_dir)
            except Exception as e:
                g_logger.error("api_postDel task_code=%s,task_dir=%s,e=%s"%(task_code,task_dir,str(e)))

            task.delete()
            ret = True
            msg = "删除成功"

        else:
            msg = "数据不存在！"
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    return f_responseJson(res)
