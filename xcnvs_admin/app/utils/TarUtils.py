import os
import tarfile
import time
from io import BytesIO
import shutil

class TarUtils():

    # 压缩文件夹->tar文件
    def compress_folder(self, folder_dir, output_filepath):
        # 创建一个tar文件 ->output_filepath
        with tarfile.open(output_filepath, 'w') as tar:
            # 获取文件夹路径
            top_root = None
            top_root_len = 0

            i = 0
            for root, dirs, files in os.walk(folder_dir):

                if i == 0 and top_root is None:
                    top_root = root
                    top_root_len = len(top_root)
                    relative_root = ""
                else:
                    relative_root = root[top_root_len+1:]

                # print("%d,relative_root=%s,dirs=%s,files=%s" % (i,relative_root, str(dirs), str(files)))

                # 遍历文件夹和文件，将它们添加到tar文件中
                for file in files:

                    # 读取绝对路径下的文件内容
                    filepath = os.path.join(root, file)  # 文件绝对路径
                    relative_filepath = os.path.join(relative_root, file)

                    f = open(filepath, 'rb')
                    content = f.read()
                    f.close()

                    # 构建相对路径的tarinfo

                    info = tarfile.TarInfo(name=relative_filepath)
                    info.size = len(content)
                    info.mtime = time.time()

                    # 添加tarinfo
                    tar.addfile(info,BytesIO(content))

                i += 1

    # 解压缩tar->文件夹
    def uncompress_folder(self,tar_filepath, output_folder_dir):
        if not os.path.exists(output_folder_dir):
            os.makedirs(output_folder_dir)

        with tarfile.open(tar_filepath, "r:") as tar:
            tar.extractall(path=output_folder_dir)

    # 复制文件夹->目标文件夹
    def copy_folder(self,src_folder_dir,dst_folder_dir,del_suffix=None):
        if os.path.exists(dst_folder_dir):
            shutil.rmtree(dst_folder_dir)

        shutil.copytree(src_folder_dir,dst_folder_dir)

        if del_suffix:
            filenames = os.listdir(dst_folder_dir)
            for filename in filenames:
                if filename.endswith(del_suffix):
                    filepath = os.path.join(dst_folder_dir,filename)
                    os.remove(filepath)


