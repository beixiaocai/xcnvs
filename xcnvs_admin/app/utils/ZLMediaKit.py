import requests
import inspect
import json

class ZLMediaKit():
    def __init__(self, logger, config):
        self.__logger = logger
        self.__config = config
        self.timeout = 15
        self.ua = "xcnvs_admin"

    def __byteFormat(self, bytes, suffix="bps"):

        factor = 1024
        for unit in ["", "K", "M", "G"]:
            if bytes < factor:
                return f"{bytes:.2f}{unit}{suffix}"
            bytes /= factor

    def get_hlsUrl(self, app, name):
        __address = "http://" + self.__config.externalHost + ":" + str(self.__config.mediaHttpPort)
        return "%s/%s/%s.hls.m3u8" % (__address , app, name)

    def get_httpFlvUrl(self, app, name):
        __address = "http://" + self.__config.externalHost + ":" + str(self.__config.mediaHttpPort)
        return "%s/%s/%s.live.flv" % (__address, app, name)

    def get_rtspUrl(self, app, name):
        __address = "rtsp://" + self.__config.externalHost + ":" + str(self.__config.mediaRtspPort)
        return "%s/%s/%s" % (__address, app, name)

    def get_rtspHost(self):
        __address = "rtsp://" + self.__config.externalHost + ":" + str(self.__config.mediaRtspPort)
        return __address

    def get_wsHost(self):
        __address = "ws://" + self.__config.externalHost + ":" + str(self.__config.mediaHttpPort)
        return __address

    def get_wsMp4Url(self, app, name):
        __address = "ws://" + self.__config.externalHost + ":" + str(self.__config.mediaHttpPort)
        return "%s/%s/%s.live.mp4" % (__address, app, name)

    def get_wsFlvUrl(self, app, name):
        __address = "ws://" + self.__config.externalHost + ":" + str(self.__config.mediaHttpPort)
        return "%s/%s/%s.live.flv" % (__address, app, name)

    def get_httpMp4Url(self, app, name):
        __address = "http://" + self.__config.externalHost + ":" + str(self.__config.mediaHttpPort)
        return "%s/%s/%s.live.mp4" % (__address, app, name)

    def version(self):

        __ret = False
        __msg = "unknown error"
        is_online = False  # 流媒体服务器是否在线
        try:
            params = {
                "secret": self.__config.mediaSecret
            }
            address = "http://" + self.__config.internalHost + ":" + str(self.__config.mediaHttpPort)
            url = "{address}/index/api/version".format(address=address)
            res = requests.post(url, headers={
                "User-Agent": self.ua
            }, json=params, timeout=self.timeout)

            if res.status_code == 200:
                res_json = res.json()
                if 0 == res_json["code"]:
                    __ret = True
            else:
                raise Exception("status=%d" % res.status_code)

            is_online = True

        except Exception as e:
            __msg = str(e)
            self.__logger.error("version() error: %s" % str(e))

        return is_online

    def getMediaList(self):
        __data = []
        try:
            address = "http://" + self.__config.internalHost + ":" + str(self.__config.mediaHttpPort)
            url = "{address}/index/api/getMediaList?secret={secret}".format(
                address=address,
                secret=self.__config.mediaSecret
            )
            res = requests.get(url, headers={
                "User-Agent": self.ua
            }, timeout=self.timeout)

            if 200 == res.status_code:
                res_json = res.json()
                if 0 == res_json.get("code"):
                    data = res_json.get("data")
                    if data:
                        __data_group = {}  # 视频流按照流名称进行分组
                        for d in data:
                            app = d.get("app")  # 应用名
                            name = d.get("stream")  # 流id
                            schema = d.get("schema")  # 协议
                            an = "%s_%s" % (app, name)
                            v = __data_group.get(an)
                            if not v:
                                v = {}
                            v[schema] = d
                            __data_group[an] = v

                        for an, v in __data_group.items():
                            schema_clients = []
                            index = 0
                            d = None
                            for __schema, __d in v.items():
                                schema_clients.append({
                                    "schema": __schema,
                                    "readerCount": __d.get("readerCount")
                                })
                                if 0 == index:
                                    d = __d
                                index += 1
                            if d:
                                video_str = "无"
                                video_codec_name = None
                                video_width = 0
                                video_height = 0
                                audio_str = "无"
                                tracks = d.get("tracks", None)
                                if tracks:
                                    for track in tracks:
                                        # codec_id = track.get("codec_id","")
                                        codec_id_name = track.get("codec_id_name", "").lower()
                                        codec_type = track.get("codec_type", -1)  # Video = 0, Audio = 1
                                        # ready = track.get("ready","")

                                        if 0 == codec_type:  # 视频类型
                                            fps = track.get("fps")
                                            video_height = int(track.get("height", 0))
                                            video_width = int(track.get("width", 0))
                                            video_codec_name = codec_id_name

                                            video_str = "%s/%d/%dx%d" % (codec_id_name, fps, video_width, video_height)

                                        elif 1 == codec_type:  # 音频类型
                                            channels = track.get("channels")

                                            sample_bit = track.get("sample_bit")
                                            sample_rate = track.get("sample_rate")

                                            audio_str = "%s/%d/%d/%d" % (
                                                codec_id_name, channels, sample_rate, sample_bit)

                                produce_speed = self.__byteFormat(d.get("bytesSpeed"))  # 数据产生速度，单位byte/s

                                app = d.get("app")  # 应用名
                                name = d.get("stream")  # 流id
                                wsMp4Url = self.get_wsMp4Url(app, name)
                                __data.append({
                                    "is_online": 1,
                                    "code": an,
                                    "an": an,
                                    "app": app,
                                    "name": name,
                                    "produce_speed": produce_speed,
                                    "video": video_str,
                                    "video_codec_name": video_codec_name,
                                    "video_width": video_width,
                                    "video_height": video_height,
                                    "audio": audio_str,
                                    "originUrl": d.get("originUrl"),  # 推流地址
                                    "originType": d.get("originType"),  # 推流地址采用的推流协议类型
                                    "originTypeStr": d.get("originTypeStr"),  # 推流地址采用的推流协议类型（字符串）
                                    "clients": d.get("totalReaderCount"),  # 客户端总数量
                                    "schema_clients": schema_clients,
                                    "videoUrl": wsMp4Url,  # 默认播放地址(ws-fmp4)
                                    "wsHost": self.get_wsHost(),
                                    "wsMp4Url": wsMp4Url
                                })
            else:
                raise Exception("status=%d" % res.status_code)

        except Exception as e:
            self.__logger.error("getMediaList() error: %s" % str(e))

        return __data