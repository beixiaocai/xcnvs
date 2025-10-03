import json
import os

class Settings:
    def __init__(self, filepath):
        self.__filepath = filepath

        data = None
        for encoding in ["utf-8","gbk"]:
            try:
                f = open(self.__filepath, 'r', encoding=encoding)
                content = f.read()
                data = json.loads(content)
                f.close()
                break
            except Exception as e:
                print("Settings.__init__() error:%s,encoding=%s|%s" % (str(e), encoding, str(self.__filepath)))
        if data:
            self.__data_str = str(data)
            self.data = {
                "name": data.get("name"),
                "welcome": data.get("welcome"),
                "logo_url": data.get("logo_url"),
                "bottom_name": data.get("bottom_name"),
                "is_show_author": bool(data.get("is_show_author",True)),
                "author": data.get("author"),
                "author_link": data.get("author_link")
            }
        else:
            msg = "Settings.__init__() read %s error" % str(self.__filepath)
            raise Exception(msg)

    def __del__(self):
        pass

    def getStr(self):
        return self.__data_str

    def show(self):
        pass
