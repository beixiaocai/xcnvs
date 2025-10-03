## xcnvs
* 作者：北小菜 
* 作者主页：https://www.beixiaocai.com
* gitee开源地址：https://gitee.com/Vanishi/xcnvs
* github开源地址：https://github.com/beixiaocai/xcnvs

### 项目介绍
* 管理平台（简称xcnvs），是计算机视觉相关一套完全开源的软件，主要包含算法模型的标注+训练功能。视频文搜功能，万物搜功能，输入描述文本，即可搜索相关的视频图片等相关功能。也可以用来作为，管理视频行为分析系统v3/v4的集群管理软件。软件采用C++和Python开发，几乎支持所有常见的操作系统或芯片。
#### 相关项目
* 视频行为分析系统v4： https://gitee.com/Vanishi/xcms
* 视频行为分析系统v3： https://gitee.com/Vanishi/BXC_VideoAnalyzer_v3

### 更新记录
#### v2.4
* 更新时间：2025/10/3
* 新增样本标注+模型训练功能（样本标注+模型训练基础功能来自xclabel，并做了优化： xclabel是一款开源支持多人协作的，样本导入+样本标注+模型训练+模型管理+模型测试+模型导出的工具）
* 优化后台管理UI风格
* 优化视频文搜功能的配置

#### v2.3
* 更新时间：2025/9/26
* 新增视频文搜功能（万物搜功能，输入描述文本，即可搜索相关的视频图片等相关资料）
* 优化后台管理配置，规范代码，整合重复的封装函数
* 新增兼容视频行为分析系统v3（要求v3.52及其之后的版本）
* 优化兼容视频行为分析系统v4（要求v4.709及其之后的版本）
##### 技术栈
* 后台管理框架：Django
* 流媒体服务器：ZLMediaKit
* 数据库： MySQL
* 向量数据库： PostgreSQL + pgvector
* 向量模型： 采用本地部署模型bge-large-zh-v1.5进行向量计算（也接入了千问的API接口调用进行计算）
* 多模态大模型：采用本地安装LMStudio部署qwen/qwen2.5-vl-7b的API进行本地计算，用户也可以自行扩展vLLM创建的API进行本地计算（也接入了千问的API接口调用进行计算）

#### v2.0-2.2
* 更新时间：2025/9/17
* 首次发布管理平台2.x，v2.0-2.2处于预发布阶段，期间针对数据表结构有较大调整和改动
##### 技术栈
* 后台管理框架：Django
* 流媒体服务器：ZLMediaKit
* 数据库： SQLite

### 编译运行
* 关于软件如何编译运行的文档，后续会发布头条账号，[点击前往头条账号](https://www.toutiao.com/c/user/token/CiyVdRwMzsId6ogtcpNg-cG3FfZNM3g57VCMoA-QhrGBOHLUUc7N9Ona7hkAaRpJCjwAAAAAAAAAAAAAT4ycz5qrTnFi6pIKDVC020ZtCVHkHyEWsRhBwKsSX2i-Wv2PvlVQK9UNeN5wMfdWMAQQsOf9DRjDxYPqBCIBA1KSH1M=/?source=list&log_from=1a251d608c1628_1759457033748)
* 关于软件如何编译运行的视频，后续会发布抖音账号

### 软件相关截图
<img width="720" alt="v2.3-wensou" src="https://gitee.com/Vanishi/images/raw/master/xcnvs/wensou.png">
<img width="720" alt="v2.4" src="https://gitee.com/Vanishi/images/raw/master/xcnvs/v2.4/1.png">
<img width="720" alt="v2.4" src="https://gitee.com/Vanishi/images/raw/master/xcnvs/v2.4/2.png">
<img width="720" alt="v2.4" src="https://gitee.com/Vanishi/images/raw/master/xcnvs/v2.4/3.png">
<img width="720" alt="v2.4" src="https://gitee.com/Vanishi/images/raw/master/xcnvs/v2.4/4.png">
<img width="720" alt="v2.4" src="https://gitee.com/Vanishi/images/raw/master/xcnvs/v2.4/5.png">
<img width="720" alt="v2.4" src="https://gitee.com/Vanishi/images/raw/master/xcnvs/v2.4/6.png">
<img width="720" alt="v2.4" src="https://gitee.com/Vanishi/images/raw/master/xcnvs/v2.4/7.png">
<img width="720" alt="v2.4" src="https://gitee.com/Vanishi/images/raw/master/xcnvs/v2.4/8.png">


### 授权协议

- 本项目自有代码使用宽松的MIT协议，在保留版权信息的情况下可以自由应用于各自商用、非商业的项目。
但是本项目也零碎的使用了一些其他的第三方库，由于使用本项目而产生的商业纠纷或侵权行为一概与本项目及开发者无关，请自行承担法律风险。
在使用本项目代码时，也应该在授权协议中同时表明本项目依赖的第三方库的协议，以及遵循相应的规定。
