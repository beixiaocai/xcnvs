import json
import os

class Config(object):
    def __init__(self, filepath):
        self.__filepath = filepath

        config_data = None
        for encoding in ["utf-8", "gbk"]:
            try:
                f = open(filepath, 'r', encoding=encoding)
                content = f.read()
                config_data = json.loads(content)
                f.close()
                break
            except Exception as e:
                print("Config.__init__() read error:%s,encoding=%s|%s" % (str(e), encoding, str(filepath)))


        if config_data:
            self.__config_data= config_data
            self.__config_data_str = str(config_data)
            # self.host = "127.0.0.1" # 功能和作用已完全被internalHost替代
            self.internalHost = "127.0.0.1"  # 内部端口为127.0.0.1,意味着后台管理只能调用同一台机器的启动器，分析器，流媒体服务器
            self.externalHost = config_data.get("host")  # 外部端口为从配置文件读取的host,例如 192.168.1.8,47.122.67.81,,,服务于非本机访问
            self.logDebug = bool(config_data.get("logDebug",False))
            self.adminPort = int(config_data.get("adminPort"))
            self.mediaRtspPort = int(config_data.get("mediaRtspPort")) # zlm 的rtsp端口
            self.mediaHttpPort = int(config_data.get("mediaHttpPort")) # zlm 的http端口
            self.mediaSecret = str(config_data.get("mediaSecret"))     # zlm 的安全校验值
            self.xcnvsSafe = str(config_data.get("xcnvsSafe"))     # xcnvs系统的安全校验值
            self.install = str(config_data.get("install"))

            self.isEnableLoginCaptcha = int(config_data.get("isEnableLoginCaptcha", 1))  # 是否开启登录验证码
            self.isEnableWenSou = int(config_data.get("isEnableWenSou", 0))  # 是否开启文搜功能
            self.checkInterval = 15

            self.fontPath = config_data.get("fontPath")
            self.embModelPath = config_data.get("embModelPath")
            self.uploadDir = config_data.get("uploadDir")
            self.storageDir = config_data.get("storageDir")

            if not os.path.exists(self.storageDir):
                os.makedirs(self.storageDir)
            self.storageTempDir = os.path.join(self.storageDir, "temp")  # 存储临时文件（在线录像，在线截屏，上传批量导入摄像头数据等等）
            self.storageAlarmDir = os.path.join(self.storageDir, "alarm") # 存储报警文件
            if not os.path.exists(self.storageTempDir):
                os.makedirs(self.storageTempDir)
            if not os.path.exists(self.storageAlarmDir):
                os.makedirs(self.storageAlarmDir)

            # self.storageDir_www = "http://%s:%d/storage/access?filename=" % (host, adminPort)
            self.storageDir_www = "/storage/access?filename="
            self.trainAlgorithms = config_data.get("trainAlgorithms",[])
            self.trainAlgorithmDict = {}
            for algorithm in self.trainAlgorithms:
                self.trainAlgorithmDict[algorithm["code"]] = algorithm

            print("Config.trainAlgorithms:",type(self.trainAlgorithms),self.trainAlgorithms)

        else:
            msg = "read Config %s error" % str(filepath)
            raise Exception(msg)

    def __del__(self):
        pass

    def getStr(self):
        return self.__config_data_str