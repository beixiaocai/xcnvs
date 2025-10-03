from app.views.ViewsBase import *
from django.utils.encoding import escape_uri_path
import os


def download(request):
    params = f_parseGetParams(request)
    g_logger.info("StorageView.download() params:%s" % str(params))

    filename = params.get("filename")
    try:
        if filename:
            if filename.endswith(".mp4") \
                    or filename.endswith(".avi") \
                    or filename.endswith(".wav") \
                    or filename.endswith(".jpg") \
                    or filename.endswith(".png") \
                    or filename.endswith(".tar") \
                    or filename.endswith(".xclogs") \
                    or filename.endswith(".xcsettings") \
                    or filename.endswith(".xcflow"):

                filepath = os.path.join(g_config.storageTempDir, filename)

                if os.path.exists(filepath):
                    f = open(filepath, mode="rb")
                    data = f.read()
                    f.close()
                    response = HttpResponse(data, content_type="application/octet-stream")
                    response['Access-Control-Allow-Origin'] = "*"
                    response['Access-Control-Allow-Headers'] = "*"
                    response['Access-Control-Allow-Methods'] = "POST, GET, OPTIONS, DELETE"
                    response['Content-Disposition'] = "attachment;filename={};".format(escape_uri_path(filename))
                    try:
                        os.remove(filepath)
                    except Exception as e:
                        g_logger.error("storage/download completed, but delete error,filepath=%s : %s" % (filepath, str(e)))
                    return response
                else:
                    raise Exception("storage/download filepath not found")
            else:
                raise Exception("storage/download unsupported filename format")
        else:
            raise Exception("storage/download filename not found")

    except Exception as e:
        return f_responseJson({"msg": str(e)})

def access(request):
    params = f_parseGetParams(request)
    filename = params.get("filename")
    try:
        if filename:
            if (filename.endswith(".mp4") or
                    filename.endswith(".avi") or
                    filename.endswith(".wav") or
                    filename.endswith(".jpg") or
                    filename.endswith(".png")):

                filepath = os.path.join(g_config.storageDir, filename)

                if os.path.exists(filepath):
                    f = open(filepath, mode="rb")
                    data = f.read()
                    f.close()

                    if filename.endswith(".mp4"):
                        fs = os.path.getsize(filepath)
                        response = HttpResponse(data, content_type="video/mp4")
                        response['Accept-Ranges'] = "bytes"
                        response['Access-Control-Allow-Origin'] = "*"
                        response['Access-Control-Allow-Headers'] = "*"
                        response['Access-Control-Allow-Methods'] = "POST, GET, OPTIONS, DELETE"
                        response['Content-Length'] = fs
                        # response['Content-Range'] = "bytes 32768-188720863/188720864"
                        # response['Etag'] = "66dc3116-b3fa6e0"
                        # response['Content-Disposition'] = "attachment;filename={};".format(escape_uri_path(filename))
                    elif filename.endswith(".jpg") or filename.endswith(".png"):
                        response = HttpResponse(data, content_type="image/jpeg")
                        response['Access-Control-Allow-Origin'] = "*"
                        response['Access-Control-Allow-Headers'] = "*"
                        response['Access-Control-Allow-Methods'] = "POST, GET, OPTIONS, DELETE"
                    else:
                        response = HttpResponse(data, content_type="application/octet-stream")
                        response['Access-Control-Allow-Origin'] = "*"
                        response['Access-Control-Allow-Headers'] = "*"
                        response['Access-Control-Allow-Methods'] = "POST, GET, OPTIONS, DELETE"
                        response['Content-Disposition'] = "attachment;filename={};".format(escape_uri_path(filename))

                    return response
                else:
                    raise Exception("storage/access filepath not found")
            else:
                raise Exception("storage/access unsupported filename format")
        else:
            raise Exception("storage/access filename not exist")

    except Exception as e:
        return f_responseJson({"msg": str(e)})