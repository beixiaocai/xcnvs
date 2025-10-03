## xcnvs_admin

### 介绍
* xcnvs_admin是集群管理平台的后台管理模块，基于Python开发

## 依赖环境

| 程序         | 版本               |
| ---------- |------------------|
| python     | 3.8+             |
| 依赖库      | requirements.txt |


### 运行说明
- 首先安装Python和依赖库环境，推荐通过虚拟环境安装，可以参考下面的安装方法
- 环境安装完成后，启动服务： python manage.py runserver 0.0.0.0:9824
- 访问服务：在浏览器输入 http://127.0.0.1:9824 就可以开始了，默认账号 admin admin888



## windows 创建虚拟环境
~~~
//创建虚拟环境
python -m venv venv

//切换到虚拟环境
venv\Scripts\activate

//更新pip
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

//安装requirements
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

~~~


## linux 创建虚拟环境
~~~

//创建虚拟环境
python -m venv venv

//切换到虚拟环境
source venv/bin/activate

//更新pip
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

//安装requirements
python -m pip install -r requirements-linux.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

~~~