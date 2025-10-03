import json
import os
import shutil
import time
from datetime import datetime
import subprocess
from app.views.ViewsBase import *
from app.models import *
import random
from app.utils.UploadUtils import UploadUtils
from app.utils.Utils import gen_random_code_s

def api_postDel(request):
    ret = False
    msg = "未知错误"
    if request.method == 'POST':
        params = f_parsePostParams(request)
        predict_code = params.get("code", "").strip()
        test = LabelTkPredictModel.objects.filter(code=predict_code)
        if len(test) > 0:
            test = test[0]
            # 训练根目录
            train_dir = os.path.join(g_config.storageDir, "labeltkTrain", test.train_code)
            predict_dir = os.path.join(train_dir, "predict", predict_code)
            if not os.path.exists(predict_dir):
                os.makedirs(predict_dir)

            try:
                if os.path.exists(predict_dir):
                    shutil.rmtree(predict_dir)
            except Exception as e:
                g_logger.error("api_postDel predict_dir=%s,e=%s" % (predict_dir, str(e)))

            test.delete()
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
def api_postAdd(request):
    ret = False
    msg = "未知错误"
    if request.method == 'POST':
        params = f_parsePostParams(request)
        train_code = params.get("train_code", "").strip()
        file_type = int(params.get("file_type", 0))

        try:
            train = LabelTkTrainModel.objects.filter(code=train_code).first()
            if not train:
                raise Exception("该训练任务不存在！")

            # 训练根目录
            train_dir = os.path.join(g_config.storageDir, "labeltkTrain", train.code)
            if not os.path.exists(train_dir):
                raise Exception("该训练任务暂未训练！")
            predict_code =  gen_random_code_s("tkpredict")
            predict_dir = os.path.join(train_dir, "predict", predict_code)
            if not os.path.exists(predict_dir):
                os.makedirs(predict_dir)

            train_best_model_filepath = os.path.join(train_dir, "train", "weights", "best.pt")
            if not os.path.exists(train_best_model_filepath):
                raise Exception("该训练任务暂无模型！")

            file = request.FILES.get("file0")
            if not file:
                raise Exception("请选择上传文件！")

            upload_utils = UploadUtils()

            if file_type == 1:
                __ret, __msg, __info = upload_utils.upload_model_test_image(predict_dir=predict_dir, file=file)
            elif file_type == 2:
                __ret, __msg, __info = upload_utils.upload_model_test_video(predict_dir=predict_dir, file=file)
            else:
                raise Exception("不支持的文件类型")

            if not __ret:
                raise Exception(__msg)

            test_filepath = __info["test_filepath"]
            file_name = __info["file_name"]
            file_size = __info["file_size"]

            predict_log_filepath = os.path.join(predict_dir, "predict.log")  # 训练日志

            __calcu_state = False
            calcu_start_time = time.time()

            algorithm = g_config.trainAlgorithmDict.get(train.algorithm_code)
            if algorithm:
                yoloInstallDir = algorithm["install_dir"]
                yoloVenv = algorithm["venv"]
                yoloProcessName = algorithm["processName"]
                # yoloDefaultWeight = os.path.join(yoloInstallDir, algorithm["defaultWeight"])

                osSystem = OSSystem()
                if osSystem.getSystemName() == "Windows":
                    # Windows系统，需要执行下切换盘符的步骤
                    dirve, tail = os.path.splitdrive(yoloInstallDir)
                    cd_dirve = "%s &&" % dirve
                else:
                    cd_dirve = ""

                __command_run = "{yoloProcessName} detect predict model={model} source={source} device=cpu project={project} > {predict_log_filepath}".format(
                    yoloProcessName=yoloProcessName,
                    model=train_best_model_filepath,
                    source=test_filepath,
                    project=predict_dir,
                    predict_log_filepath=predict_log_filepath
                )
                __predict_command = "{cd_dirve} cd {yoloInstallDir} && {yoloVenv} && {command_run}".format(
                    cd_dirve=cd_dirve,
                    yoloInstallDir=yoloInstallDir,
                    yoloVenv=yoloVenv,
                    command_run=__command_run
                )
                print("__predict_command: %s" % __predict_command)
                g_logger.info("__predict_command: %s" % __predict_command)

                # proc = subprocess.Popen(__predict_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True, encoding='utf-8')
                proc = subprocess.Popen(__predict_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True)

                # print(type(proc),proc)
                # print("proc.pid=",proc.pid)
                stdout, stderr = proc.communicate()

            else:
                raise Exception("不支持的算法")


            calcu_end_time = time.time()
            calcu_seconds = calcu_end_time - calcu_start_time

            user = readUser(request)

            test = LabelTkPredictModel()
            test.sort = 0
            test.code = predict_code
            test.user_id = user.get("id")
            test.username = user.get("username")
            test.task_code = train.task_code
            test.train_code = train.code
            test.file_name = file_name
            test.file_size = file_size
            test.file_type = file_type
            test.calcu_seconds = round(calcu_seconds, 3)
            test.create_time = datetime.now()
            test.save()

            ret = True
            msg = "success"

        except Exception as e:
            msg = str(e)
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    return f_responseJson(res)

def api_getIndex(request):
    ret = False
    msg = "未知错误"
    data = []

    if request.method == 'GET':
        params = f_parseGetParams(request)
        train_code = params.get("train_code", "").strip()
        data = g_database.select("select * from xcnvs_labeltk_predict where train_code='%s' order by id desc" % train_code)
        for d in data:
            d["create_time"] = d["create_time"].strftime("%Y/%m/%d %H:%M")

        ret = True
        msg = "success"
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data
    }
    return f_responseJson(res)