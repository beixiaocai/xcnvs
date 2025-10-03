from django.urls import path
from .views import UserView
from .views import IndexView
from .views import NodeView
from .views import AlarmView
from .views import MediaView
from .views import StreamView
from .views import ControlView
from .views import OpenView
from .views import StorageView
from .views import InnerlView
from .views import LabelTaskView
from .views import LabelTkSampleView
from .views import LabelTkTrainView
from .views import LabelTkPredictView
app_name = 'app'

urlpatterns = [
    # 主页功能
    path('', IndexView.index),

    # 登陆退出
    path('captcha', UserView.captcha),
    path('login', UserView.login),
    path('logout', UserView.logout),

    # 用户管理
    path('user/index', UserView.index),
    path('user/add', UserView.add),
    path('user/edit', UserView.edit),
    path('user/postDel', UserView.api_postDel),


    # 节点管理
    path('node/index', NodeView.index),
    path('node/add', NodeView.add),
    path('node/edit', NodeView.edit),
    path('node/openDel', NodeView.api_openDel),
    path('node/openSync', NodeView.api_openSync),
    path('node/openInfo', NodeView.api_openInfo),
    path('node/openImportUpdate', NodeView.api_openImportUpdate),

    # 报警管理
    path('alarm/index', AlarmView.index),
    path('alarm/edit', AlarmView.edit),
    path('alarm/openHandle', AlarmView.api_openHandle),
    path('alarm/openExport', AlarmView.api_openExport),
    path('alarm/openAdd', AlarmView.api_openAdd),
    path('alarm/openIndex', AlarmView.api_openIndex),
    path('alarm/openInfo', AlarmView.api_openInfo),

    # 媒体资料管理（接收图片或视频转换为向量存储，用于文搜，图搜）
    path('media/index', MediaView.index),
    path('media/openIndex', MediaView.api_openIndex),
    path('media/openAdd', MediaView.api_openAdd),

    # 节点视频管理
    path('stream/index', StreamView.index),
    path('stream/openIndex', StreamView.api_openIndex),
    path('stream/openAddStreamProxy', StreamView.api_openAddStreamProxy),
    path('stream/openDelStreamProxy', StreamView.api_openDelStreamProxy),
    path('stream/openHandleAllStreamProxy', StreamView.api_openHandleAllStreamProxy),
    path('stream/openDel', StreamView.api_openDel),
    path('stream/player', StreamView.player),

    # 节点布控管理
    path('control/index', ControlView.index),
    path('control/openIndex', ControlView.api_openIndex),
    path('control/add', ControlView.add),
    path('control/openAdd', ControlView.api_openAdd),
    path('control/edit', ControlView.edit),
    path('control/openEdit', ControlView.api_openEdit),
    path('control/openLog', ControlView.api_openLog),
    path('control/openDel', ControlView.api_openDel),
    path('control/openCopy', ControlView.api_openCopy),
    path('control/openSettings', ControlView.api_openSettings),
    path('control/openHandleAllControl', ControlView.api_openHandleAllControl),
    path('control/openStartControl', ControlView.api_openStartControl),
    path('control/openStopControl', ControlView.api_openStopControl),

    # 标注任务
    path('labelTask/index', LabelTaskView.index),
    path('labelTask/add', LabelTaskView.add),
    path('labelTask/edit', LabelTaskView.edit),
    path('labelTask/sync', LabelTaskView.api_sync),
    path('labelTask/postDel', LabelTaskView.api_postDel),
    path('labelTask/sample', LabelTaskView.sample),
    path('labeltkSample/getInfo', LabelTkSampleView.api_getInfo),
    path('labeltkSample/postSaveAnnotation', LabelTkSampleView.api_postSaveAnnotation),
    path('labeltkSample/postDelAnnotation', LabelTkSampleView.api_postDelAnnotation),
    path('labeltkSample/getIndex', LabelTkSampleView.api_getIndex),
    path('labeltkSample/postAdd', LabelTkSampleView.api_postAdd),
    path('labeltkSample/postDel', LabelTkSampleView.api_postDel),
    path('labeltkTrain/index', LabelTkTrainView.index),
    path('labeltkTrain/add', LabelTkTrainView.add),
    path('labeltkTrain/train', LabelTkTrainView.train),
    path('labeltkTrain/postDel', LabelTkTrainView.api_postDel),
    path('labeltkTrain/postGenDatasets', LabelTkTrainView.api_postGenDatasets),
    path('labeltkTrain/postStartTrain', LabelTkTrainView.api_postStartTrain),
    path('labeltkTrain/postStopTrain', LabelTkTrainView.api_postStopTrain),
    path('labeltkTrain/getLog', LabelTkTrainView.api_getLog),
    path('labeltkPredict/postAdd', LabelTkPredictView.api_postAdd),
    path('labeltkPredict/postDel', LabelTkPredictView.api_postDel),
    path('labeltkPredict/getIndex', LabelTkPredictView.api_getIndex),

    # 内部接口
    path('inner/on_stream_not_found', InnerlView.api_on_stream_not_found),

    # 开放接口
    path('open/getIndex', OpenView.api_getIndex),
    path('open/getZlmProcessData', OpenView.api_getZlmProcessData),
    path('open/getAllCoreProcessData', OpenView.api_getAllCoreProcessData),
    path('open/getAllCoreProcessData2', OpenView.api_getAllCoreProcessData2),
    path('open/getAllStreamData', OpenView.api_getAllStreamData),
    path('open/getControl', OpenView.api_getControl),


    # 下载模块
    path('storage/download', StorageView.download),
    path('storage/access', StorageView.access)
]
