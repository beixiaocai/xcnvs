import json
import os
import shutil
import time
from datetime import datetime
import subprocess
import sys
import cv2
from app.utils.OSSystem import OSSystem
from app.utils.TrainUtils import TrainUtils
from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render, redirect
import random
from app.utils.Utils import buildPageLabels, gen_random_code_s
from app.utils.UploadUtils import UploadUtils
import threading
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
    sql_data = "select * from xcnvs_labeltk_train order by id desc limit %d,%d " % (
        skip, page_size)
    sql_data_num = "select count(id) as count from xcnvs_labeltk_train "

    count = g_database.select(sql_data_num)

    if len(count) > 0:
        count = int(count[0]["count"])
        mTrainUtils = TrainUtils(g_logger)
        data = g_database.select(sql_data)
        for d in data:
            if d["train_state"] == 1:
                if not mTrainUtils.checkProcessByPid(pid=d["train_pid"]):
                    d["train_state"] = 2
                    d["train_stop_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    train = LabelTkTrainModel.objects.filter(id=d["id"]).first()
                    train.train_state = 2
                    train.train_stop_time = datetime.now()
                    train.save()

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

    return render(request, 'app/labeltkTrain/index.html', context)
def add(request):

    if request.method == 'POST':
        ret = False
        msg = "未知错误"

        params = f_parsePostParams(request)
        task_code = params.get("task_code", "").strip()
        train_code = params.get("train_code", "").strip()
        algorithm_code = params.get("algorithm_code", "").strip()
        device = params.get("device", "cpu").strip()
        imgsz = int(params.get("imgsz", 640))
        epochs = int(params.get("epochs", 300))
        batch = int(params.get("batch", 32))
        save_period = int(params.get("save_period", 5))
        sample_ratio = int(params.get("sample_ratio", 5))
        extra = params.get("extra", "").strip()

        try:
            train = LabelTkTrainModel.objects.filter(code=train_code)
            if len(train) > 0:
                raise Exception("该训练编号已存在！")

            labelTask = LabelTaskModel.objects.filter(code=task_code).first()
            if not labelTask:
                raise Exception("该标注任务不存在！")

            user = f_sessionReadUser(request)

            train = LabelTkTrainModel()
            train.sort = 0
            train.code = train_code
            train.user_id = user.get("id")
            train.username = user.get("username")
            train.task_code = task_code
            train.algorithm_code = algorithm_code
            train.device = device
            train.imgsz = imgsz
            train.epochs = epochs
            train.batch = batch
            train.save_period = save_period
            train.sample_ratio = sample_ratio
            train.extra = extra
            train.create_time = datetime.now()
            train.train_datasets = ""
            train.train_process_name = ""
            train.train_pid = 0
            train.train_count = 0
            train.train_state = 0
            train.save()

            ret = True
            msg = "添加成功"

        except Exception as e:
            msg = str(e)

        res = {
            "code": 1000 if ret else 0,
            "msg": msg
        }
        return f_responseJson(res)
    else:

        context = {
            "settings": f_settingsReadData()
        }
        # params = f_parseGetParams(request)
        context["handle"] = "add"
        context["train_code"] = gen_random_code_s("tktrain")
        context["tasks"] = g_database.select("select * from xcnvs_label_task")
        context["algorithms"] = g_config.trainAlgorithms

        return render(request, 'app/labeltkTrain/add.html', context)

def train(request):
    context = {
        "settings": f_settingsReadData()
    }

    params = f_parseGetParams(request)

    train_code = params.get("code","").strip()
    train = LabelTkTrainModel.objects.filter(code=train_code)
    if len(train) > 0:
        train = train[0]
        train_dir = os.path.join(g_config.storageDir, "labeltkTrain", train.code)
        train_best_model_filepath = os.path.join(train_dir, "train/weights/best.pt")

        if not os.path.exists(train_best_model_filepath):
            train_best_model_filepath = ""

        context["handle"] = "train"
        context["storageDir_www"] = g_config.storageDir_www
        context["train_code"] = train_code
        context["train_best_model_filepath"] = train_best_model_filepath
        context["train"] = train

        return render(request, 'app/labeltkTrain/train.html', context)

    return redirect("/labeltkTrain/index")


def api_postDel(request):
    ret = False
    msg = "未知错误"
    if request.method == 'POST':
        params = f_parsePostParams(request)
        train_code = params.get("code", "").strip()
        train = LabelTkTrainModel.objects.filter(code=train_code)
        if len(train) > 0:
            train = train[0]
            if train.train_state == 1:
                msg = "训练中的任务不允许删除"
            else:
                sql = "delete from xcnvs_labeltk_predict where train_code='%s'" % train_code
                if not g_database.execute(sql):
                    g_logger.error("api_postDel() error: sql=%s"%sql)

                # 训练根目录
                train_dir = os.path.join(g_config.storageDir, "labeltkTrain", train.code)
                try:
                    if os.path.exists(train_dir):
                        shutil.rmtree(train_dir)
                except Exception as e:
                    g_logger.error("api_postDel() error: train_dir=%s,e=%s"%(train_dir,str(e)))
                train.delete()

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
def api_postGenDatasets(request):
    ret = False
    msg = "未知错误"
    if request.method == 'POST':
        params = f_parsePostParams(request)

        train_code = params.get("train_code", "").strip()
        try:
            train = LabelTkTrainModel.objects.filter(code=train_code).first()
            if not train:
                raise Exception("训练任务不存在!")

            labelTask = LabelTaskModel.objects.filter(code=train.task_code).first()
            if not labelTask:
                raise Exception("标注任务不存在!")

            labelNames = []
            try:
                tags = json.loads(labelTask.tags)
                if tags:
                    for tag in tags:
                        labelNames.append(tag["category"])
            except Exception as e:
                raise Exception("解析标注任务的标签失败:%s"%str(e))

            if len(labelNames) == 0:
                raise Exception("标注任务的标签不能为空")

            def __labelName2Index(labelName):
                i = 0
                for name in labelNames:
                    if labelName == name:
                        return i
                    i += 1
                return -1

            samples = g_database.select("select * from xcnvs_labeltk_sample where task_code='%s' and annotation_state=1 order by id asc" % labelTask.code)
            if len(samples) < 10:
                raise Exception("标注任务的样本总量不能低于10条")

            train_dir = os.path.join(g_config.storageDir, "labeltkTrain", train.code)
            train_datasets_dir = os.path.join(train_dir, "datasets")

            if os.path.exists(train_datasets_dir):
                shutil.rmtree(train_datasets_dir)

            train_datasets_train_dir = os.path.join(train_datasets_dir, "train")
            train_datasets_train_images_dir = os.path.join(train_datasets_train_dir, "images")
            train_datasets_train_labels_dir = os.path.join(train_datasets_train_dir, "labels")
            train_datasets_valid_dir = os.path.join(train_datasets_dir, "valid")
            train_datasets_valid_images_dir = os.path.join(train_datasets_valid_dir, "images")
            train_datasets_valid_labels_dir = os.path.join(train_datasets_valid_dir, "labels")
            if not os.path.exists(train_datasets_train_images_dir):
                os.makedirs(train_datasets_train_images_dir)
            if not os.path.exists(train_datasets_train_labels_dir):
                os.makedirs(train_datasets_train_labels_dir)
            if not os.path.exists(train_datasets_valid_images_dir):
                os.makedirs(train_datasets_valid_images_dir)
            if not os.path.exists(train_datasets_valid_labels_dir):
                os.makedirs(train_datasets_valid_labels_dir)

            train_data_yaml = os.path.join(train_datasets_dir, "data.yaml")
            f = open(train_data_yaml, "w")
            f.write("train: %s\n" % train_datasets_train_dir)
            f.write("val: %s\n" % train_datasets_valid_dir)
            f.write("nc: %d\n" % len(labelNames))
            f.write("names: [%s]\n" % ",".join(map(lambda x: "'" + str(x) + "'", labelNames)))
            f.close()

            # 开始生成训练样本文件start
            total_sample_count = 0
            for __sample in samples:
                new_filename = __sample["new_filename"]
                if new_filename.endswith(".jpg"):
                    src_image_filepath = os.path.join(g_config.storageDir, "labelTask", labelTask.code, "labeltkSample", new_filename)

                    if os.path.exists(src_image_filepath):
                        image = cv2.imread(src_image_filepath)
                        if image is not None:
                            total_sample_count += 1

                            imageHeight, imageWidth, _ = image.shape
                            __annotation_content = json.loads(__sample["annotation_content"])

                            dst_lines = [] # 转换为yolo格式的目标标记行
                            # 开始读取所有框start
                            for d in __annotation_content:
                                category = d["category"]
                                x1 = float(d["x"])
                                y1 = float(d["y"])
                                width = float(d["width"])
                                height = float(d["height"])
                                labelIndex = __labelName2Index(category)
                                if labelIndex > -1:
                                    x2 = x1 + width
                                    y2 = y1 + height
                                    if x1 > 0 and y1 > 0 and x2 < imageWidth and y2 < imageHeight:
                                        x_center = (x1 + x2) / 2 / float(imageWidth)
                                        y_center = (y1 + y2) / 2 / float(imageHeight)
                                        w = (x2 - x1) / float(imageWidth)
                                        h = (y2 - y1) / float(imageHeight)

                                        dst_line = "%d %.6f %.6f %.6f %.6f\n" % (labelIndex, x_center, y_center, w, h)
                                        dst_lines.append(dst_line)
                            # 开始读取所有框end

                            dst_image_filepath = os.path.join(train_datasets_train_images_dir, new_filename)
                            new_filename_prefix = new_filename[0:-4]
                            dst_label_filepath = os.path.join(train_datasets_train_labels_dir, "%s.txt" % new_filename_prefix)

                            shutil.copy(src_image_filepath, dst_image_filepath)
                            f = open(dst_label_filepath, "w")
                            for dst_line in dst_lines:
                                f.write(dst_line)
                            f.close()

                            print("处理的第%d条"%total_sample_count, dst_lines, "annotation_content:", __annotation_content)
            # 开始生成训练样本文件end

            # 训练集分割验证集start
            train_count, valid_count = TrainUtils.detect2detect(src_detect_dir=train_datasets_train_dir,
                                                                dst_detect_dir=train_datasets_valid_dir,
                                                                freq=train.sample_ratio + 1)
            # 训练集分割验证集end

            train.train_datasets = train_data_yaml
            train.train_datasets_remark = "总数量:%d 训练:%d 验证:%d" % (total_sample_count, train_count, valid_count)
            train.train_datasets_time = datetime.now()
            train.save()

            ret = True
            msg = "生成训练集成功"
        except Exception as e:
            msg = str(e)
            # raise e
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    return f_responseJson(res)
def api_postStartTrain(request):
    ret = False
    msg = "未知错误"
    if request.method == 'POST':
        params = f_parsePostParams(request)

        train_code = params.get("train_code", "").strip()
        try:

            train = LabelTkTrainModel.objects.filter(code=train_code).first()
            if not train:
                raise Exception("该训练任务不存在！")

            if train.train_state == 1:
                raise Exception("该任务正在训练中！")

            if train.train_datasets == "":
                raise Exception("训练集为空，无法训练！")

            if not os.path.exists(train.train_datasets):
                raise Exception("训练集路径不存在！")

            # 训练根目录
            train_dir = os.path.join(g_config.storageDir, "labeltkTrain", train.code)
            if not os.path.exists(train_dir):
                os.makedirs(train_dir)

            train_log_filepath = os.path.join(train_dir, "train.log") # 训练日志
            if os.path.exists(train_log_filepath):
                os.remove(train_log_filepath)

            # 确保删除已存在的训练根目录start
            __train_root_dir = os.path.join(train_dir, "train")
            if os.path.exists(__train_root_dir):
                shutil.rmtree(__train_root_dir)
            # 确保删除已存在的训练根目录end

            __start_process_info = None
            __train_command = None
            algorithm = g_config.trainAlgorithmDict.get(train.algorithm_code)

            if algorithm:
                yoloInstallDir = algorithm["install_dir"]
                yoloVenv = algorithm["venv"]
                yoloProcessName = algorithm["processName"]
                yoloDefaultWeight = os.path.join(yoloInstallDir, algorithm["defaultWeight"])

                osSystem = OSSystem()
                if osSystem.getSystemName() == "Windows":
                    # Windows系统，需要执行下切换盘符的步骤
                    dirve, tail = os.path.splitdrive(yoloInstallDir)
                    cd_dirve = "%s &&" % dirve
                else:
                    cd_dirve = ""

                __command_run = "{yoloProcessName} detect train model={yoloDefaultWeight} data={datasets} batch={batch}  epochs={epochs} imgsz={imgsz} save_period={save_period} device={device} project={project} > {train_log_filepath}".format(
                    yoloProcessName=yoloProcessName,
                    yoloDefaultWeight=yoloDefaultWeight,
                    datasets=train.train_datasets,
                    batch=train.batch,
                    epochs=train.epochs,
                    imgsz=train.imgsz,
                    save_period=train.save_period,
                    device=train.device,
                    project=train_dir,
                    train_log_filepath=train_log_filepath
                )
                __train_command = "{cd_dirve} cd {yoloInstallDir} && {yoloVenv} && {command_run}".format(
                    cd_dirve=cd_dirve,
                    yoloInstallDir=yoloInstallDir,
                    yoloVenv=yoloVenv,
                    command_run=__command_run
                )
                print("__train_command: %s" % __train_command)
                g_logger.info("__train_command: %s" % __train_command)


                def __run(command):
                    try:
                        # proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True, encoding='utf-8')
                        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True)
                        # print(type(proc),proc)
                        # print("proc.pid=",proc.pid)
                        stdout, stderr = proc.communicate()
                        # print(type(stdout), stdout)
                        # print(type(stderr), stderr)
                    except Exception as e:
                        print("__train_command_run() error: %s" % str(e))
                        g_logger.error("__train_command_run() error: %s" % str(e))

                t = threading.Thread(target=__run, args=(__train_command,))
                t.daemon = True
                t.start()

                # 检测训练是否正常启动
                mTrainUtils = TrainUtils(g_logger)
                for i in range(5):
                    time.sleep(i)
                    __info = mTrainUtils.getProcessInfoByName(processName=yoloProcessName)
                    if __info["state"]:
                        __start_process_info = __info
                        break
            else:
                raise Exception("不支持的算法")

            print("__start_process_info:",__start_process_info)

            if __start_process_info and __start_process_info["state"]:
                g_logger.info("训练启动成功: %s" % str(__start_process_info))
                if __train_command:
                    train.train_command = __train_command
                train.train_count += 1
                train.train_process_name = __start_process_info["process_name"]
                train.train_pid = __start_process_info["pid"]
                train.train_state = __start_process_info["state"] # 1:训练中 0:已停止
                train.train_start_time = datetime.now()
                train.train_stop_time = None
                train.save()

                ret = True
                msg = "训练启动成功"
            else:
                g_logger.error("训练启动失败: %s" % str(__start_process_info))
                msg = "训练启动失败"

        except Exception as e:
            raise e
            msg = str(e)
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    return f_responseJson(res)

def api_postStopTrain(request):
    ret = False
    msg = "未知错误"
    if request.method == 'POST':
        params = f_parsePostParams(request)

        train_code = params.get("train_code", "").strip()
        train = LabelTkTrainModel.objects.filter(code=train_code)
        if len(train) > 0:
            train = train[0]
            if train.train_state == 1:
                mTrainUtils = TrainUtils(g_logger)
                mTrainUtils.stopProcessByPid(train.train_pid)
                train.train_state = 2
                train.train_stop_time = datetime.now()
                train.save()

                ret = True
                msg = "停止训练成功"
            else:
                msg = "该训练任务已经停止"
        else:
            msg = "该训练任务不存在！"
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    return f_responseJson(res)

def api_getLog(request):
    ret = False
    msg = "未知错误"
    contents = []

    if request.method == 'GET':
        params = f_parseGetParams(request)
        task_code = params.get("task_code", "").strip()
        train_code = params.get("train_code", "").strip()
        logIndex = int(params.get("logIndex", 0))

        task = LabelTaskModel.objects.filter(code=task_code)
        if len(task) > 0:
            task = task[0]
            train_dir = os.path.join(g_config.storageDir, "labeltkTrain" , train_code)
            train_log_filepath = os.path.join(train_dir, "train.log")

            if os.path.exists(train_log_filepath):
                f = open(train_log_filepath, "r",encoding="utf-8")
                lines = f.readlines()
                f.close()

                contents = lines[logIndex:]
                ret = True
                msg = "success"
            else:
                msg = "train.log does not exist"
        else:
            msg = "训练任务不存在！"
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "contents": contents
    }
    return f_responseJson(res)

def f_initThread():
    i = 0
    mTrainUtils = TrainUtils(g_logger)
    while True:
        i += 1
        trains = LabelTkTrainModel.objects.filter(train_state=1)
        if len(trains) > 0:
            for train in trains:
                if not mTrainUtils.checkProcessByPid(pid=train.train_pid):
                    train.train_state = 2
                    train.train_stop_time = datetime.now()
                    train.save()
        # labelu

        time.sleep(30)

def __INIT__():
    g_logger.info("LabelTkTrainView.__INIT__()")
    t1 = threading.Thread(target=f_initThread, )
    t1.daemon = True
    t1.start()


__INIT__()