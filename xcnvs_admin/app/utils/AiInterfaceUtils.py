import os
import time
import json
from openai import OpenAI
import cv2
import base64
from sentence_transformers import SentenceTransformer
import requests


class AiInterfaceUtils():
    def __init__(self,logger,config):
        self.logger = logger
        if config.isEnableWenSou:
            print("AiInterfaceUtils.__init__() 配置开启了文搜功能")
            self.logger.info("AiInterfaceUtils.__init__() 配置开启了文搜功能")
            embModelPath = config.embModelPath
            if os.path.exists(embModelPath):
                self.emb_model = SentenceTransformer(embModelPath)
                msg = 'AiInterfaceUtils() success, embModelPath: %s' % embModelPath
                print(msg)
                logger.info(msg)
            else:
                msg = 'AiInterfaceUtils() error, embModelPath does not exist: %s' % embModelPath
                print(msg)
                logger.error(msg)
        else:
            print("AiInterfaceUtils.__init__() 配置未开启文搜功能")
            self.logger.info("AiInterfaceUtils.__init__() 配置未开启文搜功能")
            self.emb_model = None

    def __local_calcu_image(self,image):
        """
        通过本地模型（调用本地LMStudio的API），分析图片获得文本描述
        """
        url = "http://localhost:1234/v1/chat/completions"  # 替换为你的实际API地址

        try:
            # 将图片编码为Base64
            # image->base64
            encoded_image_byte = cv2.imencode(".jpg", image)[1].tobytes()  # bytes类型
            image_base64 = base64.b64encode(encoded_image_byte) # byte类型
            image_base64 = image_base64.decode("utf-8")  # str类型

            headers = {
                "Content-Type": "application/json"
            }
            params = {
                "model": "qwen/qwen2.5-vl-7b",  # 替换为你的模型名称
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "图中描绘的是什么景象？"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 300
            }
            response = requests.post(url, json=params, headers=headers)
            response.raise_for_status()  # 检查请求是否成功
            res_json = response.json()
            content = res_json["choices"][0]["message"]["content"]

            return content
        except Exception as e:
            raise Exception("__local_calcu_image() error:%s"%str(e))
    def __local_calcu_content_embedding(self,content,dimensions=1024):
        """
        通过本地模型，计算文本的向量
        """
        try:
            contents = [content]
            embeddings = self.emb_model.encode(contents)
            embedding = embeddings[0]
            embedding = list(map(lambda x: float(x), embedding))

            # print("__local_calcu_content_embedding() embedding:", type(embedding), len(embedding), embedding)

            return embedding
        except Exception as e:
            raise Exception("__local_calcu_content_embedding() error:%s"%str(e))
    def __qw_calcu_image(self,image):
        """
        通过通义千问大模型API，分析图片获得文本描述
        """
        # 调用千问 qwen2.5-vl-7b-instruct 分析图片
        DASHSCOPE_API_KEY = "sk-xxx"  # 替换为你的 DashScope API Key
        EMBEDDING_MODEL = "qwen2.5-vl-7b-instruct"
        EMBEDDING_ENDPOINT = "https://dashscope.aliyuncs.com/compatible-mode/v1"

        try:
            # 将图片resize后转换base64
            IMAGE_SCALE_FACTOR = 2
            h, w, c = image.shape
            resize_h = int(h / IMAGE_SCALE_FACTOR)
            resize_w = int(w / IMAGE_SCALE_FACTOR)
            image = cv2.resize(image, (resize_w, resize_h), interpolation=cv2.INTER_NEAREST)
            # image->base64
            encoded_image_byte = cv2.imencode(".jpg", image)[1].tobytes()  # bytes类型
            image_base64 = base64.b64encode(encoded_image_byte) # byte类型
            image_base64 = image_base64.decode("utf-8")  # str类型

            messages = [
                # {
                #     "role": "system",
                #     "content": [{"type": "text", "text": "You are a helpful assistant."}]
                # },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "data:image/jpeg;base64,%s" % str(image_base64)
                            },
                        },
                        {"type": "text", "text": "图中描绘的是什么景象？"},
                        # {"type": "text", "text": "检测到图片中人推自行车的具体坐标？"},
                        # {"type": "text", "text": "检测到图片中有人打架的具体坐标？"},
                    ],
                }
            ]
            client = OpenAI(
                api_key=DASHSCOPE_API_KEY,
                base_url=EMBEDDING_ENDPOINT
            )
            completion = client.chat.completions.create(
                model=EMBEDDING_MODEL,
                messages=messages,
            )
            # print(completion)

            content = completion.choices[0].message.content

            # print("calcu_image() content:",content)
            return content
        except Exception as e:
            raise Exception("__qw_calcu_image() error:%s"%str(e))
    def __qw_calcu_content_embedding(self,content,dimensions=1024):
        """
        通过通义千问大模型API，计算文本的向量
        """
        # 通义千问 text-embedding-v4 生成向量
        DASHSCOPE_API_KEY = "sk-xxx"  # 替换为你的 DashScope API Key
        EMBEDDING_MODEL = "text-embedding-v4"
        EMBEDDING_ENDPOINT = "https://dashscope.aliyuncs.com/compatible-mode/v1"

        try:

            client = OpenAI(
                api_key=DASHSCOPE_API_KEY,
                base_url=EMBEDDING_ENDPOINT # 百炼服务的base_url
            )

            completion = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=content,
                dimensions=dimensions,  # 指定向量维度（仅 text-embedding-v3及 text-embedding-v4支持该参数）
                encoding_format="float"
            )
            res_text = completion.model_dump_json()
            res_json = json.loads(res_text)

            embedding = res_json["data"][0]["embedding"]  # 1024维度
            # print("__qw_calcu_content_embedding() embedding:", type(embedding), len(embedding), embedding)
            return embedding
        except Exception as e:
            raise Exception("__qw_calcu_content_embedding() error:%s"%str(e))

    def calcu_image(self,image):
        """
        分析图片获得文本描述
        """

        return self.__local_calcu_image(image)# 调用本地部署的LMStudio的API进行计算
        # return self.__qw_calcu_image(image) # 调用千问的API进行计算，需要自行购买千问的key
    def calcu_content_embedding(self,content):
        """
        计算文本的向量
        """
        return self.__local_calcu_content_embedding(content)# 调用本地的模型进行计算
        # return self.__qw_calcu_content_embedding(content) # 调用千问的API进行计算，需要自行购买千问的key
