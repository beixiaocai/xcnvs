import os
import shutil
import json
import base64
import io
from PIL import Image

class AlarmUtils():
    def __init__(self, logger, database, storageDir):
        self.logger = logger
        self.database = database
        self.storageDir = storageDir


    def export_labelme(self,alarm_id,control_code,image_path,out_dir):
        # v4.634新增，将报警数据导出到labelme格式的样本
        ret = False
        msg = "未知错误"

        try:
            image_filepath = os.path.join(self.storageDir, image_path)
            alarm_id_dir = os.path.dirname(image_filepath)  # 示例：D:\file\storage\alarm\control1153f79df4\20250528\20250528112326\0

            annotation_name = "%s_%d"%(control_code,alarm_id)
            annotation_filepath = os.path.join(alarm_id_dir,"%s.json"%annotation_name)

            if not os.path.exists(image_filepath):
                raise FileNotFoundError(f"image_filepath not found: {image_filepath}")

            if not os.path.exists(annotation_filepath):
                raise FileNotFoundError(f"annotation_filepath not found: {annotation_filepath}")

            # 获取图片尺寸和Base64编码
            with Image.open(image_filepath) as img:
                width, height = img.size

                # 转换图片为RGB模式（处理可能存在的Alpha通道）
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # 将图片保存到内存字节流
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG')  # 可根据需要改为PNG格式
                img_byte_arr = img_byte_arr.getvalue()

                # 进行Base64编码
                image_data = base64.b64encode(img_byte_arr).decode('utf-8')

            out_filename = annotation_name # 输出名称与原标注文件名称保持一致

            # 构建LabelMe数据结构
            labelme_data = {
                "version": "5.5.0",
                "flags": {},
                "shapes": [],
                "imagePath": out_filename + ".jpg",
                "imageData": image_data,
                "imageHeight": height,
                "imageWidth": width
            }

            # 解析标注文件
            annotation_data = None
            for encoding in ["utf-8", "gbk"]:
                try:
                    f = open(annotation_filepath, 'r', encoding=encoding)
                    content = f.read()
                    annotation_data = json.loads(content)
                    f.close()
                    break
                except Exception as e:
                    raise Exception("encoding=%s,annotation_filepath=%s,error=%s" % (encoding, str(annotation_filepath),str(e)))

            if annotation_data:
                image_count = annotation_data.get("image_count", 0)
                image_detects = annotation_data.get("image_detects")
                if len(image_detects) == image_count:
                    detects = image_detects[0]  # 第一张图片的所有检测目标
                    for detect in detects:
                        x1 = int(detect["x1"])
                        x2 = int(detect["x2"])
                        y1 = int(detect["y1"])
                        y2 = int(detect["y2"])
                        label = detect["class_name"]
                        if x1 >= 0 and y1 >= 0 and x2 <= width and y2 <= height:
                            # 创建LabelMe标注对象
                            shape = {
                                "label": str(label),  # 类别标签
                                "points": [[x1, y1], [x2, y2]],
                                "group_id": None,
                                "shape_type": "rectangle",
                                "flags": {}
                            }

                            labelme_data["shapes"].append(shape)

            # 创建输出目录
            os.makedirs(out_dir, exist_ok=True)

            # 生成输出路径
            out_image_filepath = os.path.join(out_dir, out_filename + ".jpg")
            out_json_filepath = os.path.join(out_dir, out_filename + ".json")

            # 写入JSON文件（关键修改点：UTF-8编码 + 禁用ASCII转义）
            with open(out_json_filepath, 'w', encoding='utf-8') as f:
                json.dump(labelme_data, f, indent=2, ensure_ascii=False)

            shutil.copyfile(image_filepath, out_image_filepath)

            ret = True
            msg = "success"

        except Exception as e:
            msg = str(e)
            self.logger.error("AlarmUtils.export_labelme() error: %s"%str(e))

        return ret,msg

    def clearAlarmFiles(self, media_path, clear_type=0):
        """
        @media_path 主图图片或视频的相对路径
            例1: alarm/control1204542df7/20240927/174909/1/20240927174909.jpg
            例2: alarm/control1204542df7/20240927/174919/1/20240927174919.mp4
        @clear_type 清理类型
            0: 清理文本+图片+视频+上一级所有同级文件夹文件
            1: 仅清理文本+图片文件
        """
        self.logger.info("AlarmUtils.clearAlarmFiles() media_path=%s,clear_type=%d" % (media_path, clear_type))
        try:
            if media_path.startswith("alarm/"):
                media_path_abs = os.path.join(self.storageDir,media_path)  # /xx/alarm/control5245985c64/20240927/20240927213756/1/20240927213756.jpg

                if os.path.exists(media_path_abs):
                    if clear_type == 0:  # 删除文件夹及其内部所有子文件
                        file_path_parent_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(media_path_abs)))
                        if os.path.exists(file_path_parent_parent_dir):
                            shutil.rmtree(file_path_parent_parent_dir)

                    elif clear_type == 1:  # 删除除视频以外的所有文件
                        file_path_parent_dir = os.path.dirname(os.path.abspath(media_path_abs))
                        filenames = os.listdir(file_path_parent_dir)
                        for __filename in filenames:
                            __filename = str(__filename)
                            if not __filename.endswith(".mp4"):
                                __filepath = os.path.join(file_path_parent_dir, __filename)
                                if os.path.exists(__filepath):
                                    os.remove(__filepath)
                else:
                    raise Exception("media_path_abs=%s not exist"%media_path_abs)
            else:
                raise Exception("media_path=%s format error" % media_path)
        except Exception as e:
            self.logger.error("AlarmUtils.clearAlarmFiles() error: %s"%str(e))

    def clearAlarm(self):
        ret = False
        msg = "未知错误"
        data = self.database.select("select video_count,video_path,image_count,image_path from xcnvs_node_alarm where state=5")
        if len(data) > 0:
            self.database.execute("delete from xcnvs_node_alarm where state=5")
            for d in data:
                video_count = d["video_count"]
                video_path = d["video_path"]
                image_count = d["image_count"]
                image_path = d["image_path"]

                if image_count > 0:
                    self.clearAlarmFiles(image_path, 0)
                elif video_count > 0:
                    self.clearAlarmFiles(video_path, 0)
            msg = "清理报警缓存成功"
            ret = True
        else:
            msg = "暂无待清理缓存"

        return ret, msg
