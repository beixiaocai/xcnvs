from django.db import models
# from pgvector.django import VectorField

class AiInterfaceModel(models.Model):
    user_id = models.IntegerField(verbose_name='user_id')
    sort = models.IntegerField(verbose_name='sort')
    code = models.CharField(max_length=50, verbose_name='code')
    address = models.TextField(verbose_name='address')
    api_key = models.CharField(max_length=100, verbose_name='api_key')
    state = models.IntegerField(verbose_name='状态')  # 0:未处理 1:已处理（正常报警） 2:已处理（误报） 5:逻辑删除
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='create_time')
    last_update_time = models.DateTimeField(verbose_name='last_update_time')
    model_name = models.CharField(max_length=100, verbose_name='model_name')

    def __repr__(self):
        return self.code

    def __str__(self):
        return self.code

    class Meta:
        db_table = 'xcnvs_ai_interface'
        verbose_name = 'xcnvs_ai_interface'
        verbose_name_plural = 'xcnvs_ai_interface'

class NodeModel(models.Model):
    # id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(verbose_name='user_id')
    sort = models.IntegerField(verbose_name='sort')
    code = models.CharField(max_length=50, verbose_name='code')
    nickname = models.CharField(max_length=100, verbose_name='昵称')
    version = models.FloatField(verbose_name='version')
    flag = models.CharField(max_length=50, verbose_name='flag')
    system_name = models.CharField(max_length=100, verbose_name='system_name')
    machine_node = models.CharField(max_length=100, verbose_name='machine_node')
    address = models.CharField(max_length=200, verbose_name='address')
    xcms_safe = models.CharField(max_length=100, verbose_name='xcms_safe')
    media_secret = models.CharField(max_length=100, verbose_name='media_secret')
    machine_mac = models.CharField(max_length=50, verbose_name='machine_mac')
    is_auth = models.IntegerField(verbose_name='is_auth')
    is_multi_process = models.IntegerField(verbose_name='is_multi_process')
    max_count = models.IntegerField(verbose_name='max_count')
    desc = models.CharField(max_length=200, verbose_name='desc')
    auth_info = models.TextField(verbose_name='auth_info')
    state = models.IntegerField(verbose_name='state')  # 默认0   0:未同步 1:在线 2:掉线 3:版本不支持 4:读取节点信息失败

    image_path = models.CharField(max_length=200, verbose_name='image_path')
    expand1 = models.CharField(max_length=200, verbose_name='expand1')
    expand2 = models.CharField(max_length=200, verbose_name='expand2')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='create_time')
    last_update_time = models.DateTimeField(auto_now_add=True, verbose_name='last_update_time')

    node_code = models.CharField(max_length=100, verbose_name='node_code')
    node_host = models.CharField(max_length=100, verbose_name='node_host')

    def __repr__(self):
        return self.code

    def __str__(self):
        return self.code

    class Meta:
        db_table = 'xcnvs_node'
        verbose_name = 'xcnvs_node'
        verbose_name_plural = 'xcnvs_node'
class NodeAlarmModel(models.Model):
    sort = models.IntegerField(verbose_name='sort')
    code = models.CharField(max_length=50, verbose_name='code')
    draw_type = models.IntegerField(verbose_name='合成报警视频画框类型')  # 1:画框 0:未画框
    flag = models.CharField(max_length=50, verbose_name='合成报警视频标记')
    node_code = models.CharField(max_length=100, verbose_name='node_code')
    control_code = models.CharField(max_length=50, verbose_name='布控编号')
    desc = models.CharField(max_length=200, verbose_name='描述')
    video_path = models.TextField(verbose_name='视频存储路径')
    video_count = models.IntegerField(verbose_name='视频总数量')
    image_path = models.TextField(verbose_name='主图存储路径')
    image_count = models.IntegerField(verbose_name='图片总数量')
    other_image_count = models.IntegerField(verbose_name='其他图片数量')
    level = models.IntegerField(verbose_name='报警级别')  # 0:普通 1:警告 2:严重
    state = models.IntegerField(verbose_name='状态')  # 0:未处理 1:已处理（正常报警） 2:已处理（误报） 5:逻辑删除
    is_check = models.IntegerField(verbose_name='是否检测')  # 0 未被检测到报警 1 已被页面检测到报警


    review_remark = models.CharField(max_length=200, verbose_name='审核备注')
    stream_app = models.CharField(max_length=50, verbose_name='视频流应用')
    stream_name = models.CharField(max_length=100, verbose_name='视频流名称')
    stream_code = models.CharField(max_length=50, verbose_name='视频流编号')
    flow_mode = models.IntegerField(verbose_name='业务算法模式')
    flow_code = models.CharField(max_length=50, verbose_name='业务算法编号')
    flow_name = models.CharField(max_length=100, verbose_name='业务算法名称')
    # v4.610新增
    main_plate_color = models.IntegerField(verbose_name='关键帧车牌颜色')
    main_plate_type = models.IntegerField(verbose_name='关键帧车牌类型')
    main_plate_no = models.CharField(max_length=100, verbose_name='关键帧车牌号')
    main_track_max_code = models.CharField(max_length=50, verbose_name='特征最大匹配编号')
    main_track_max_custom_code = models.CharField(max_length=50, verbose_name='特征最大匹配自定义编号')
    main_track_max_similary = models.IntegerField(verbose_name='特征最大相似度')
    expand1 = models.CharField(max_length=200, verbose_name='expand1')
    expand2 = models.CharField(max_length=200, verbose_name='expand2')

    create_time = models.DateTimeField(auto_now_add=True, verbose_name='create_time')
    create_timestamp = models.IntegerField(verbose_name='create_timestamp')  # 秒级时间戳
    last_update_time = models.DateTimeField(verbose_name='last_update_time')

    def __repr__(self):
        return self.desc

    def __str__(self):
        return self.desc
    def delete(self, using=None, keep_parents=False):
        ret = super(NodeAlarmModel, self).delete(using, keep_parents)
        return ret
    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        ret = super(NodeAlarmModel, self).save(force_insert, force_update, using, update_fields)
        return ret

    class Meta:
        db_table = 'xcnvs_node_alarm'
        verbose_name = 'xcnvs_node_alarm'
        verbose_name_plural = 'xcnvs_node_alarm'

class NodeMediaModel(models.Model):
    code = models.CharField(max_length=50, verbose_name='code')
    media_type = models.IntegerField(verbose_name='media_type')  # 1:图片 2:视频
    media_duration = models.IntegerField(verbose_name='media_duration')
    media_path = models.CharField(max_length=200, verbose_name='media_path')
    node_code = models.CharField(max_length=100, verbose_name='node_code')
    control_code = models.CharField(max_length=50, verbose_name='control_code')
    stream_code = models.CharField(max_length=50, verbose_name='stream_code')
    stream_app = models.CharField(max_length=50, verbose_name='stream_app')
    stream_name = models.CharField(max_length=100, verbose_name='stream_name')
    flow_mode = models.IntegerField(verbose_name='flow_mode')
    flow_code = models.CharField(max_length=50, verbose_name='flow_code')
    flow_name = models.CharField(max_length=100, verbose_name='flow_name')
    content = models.TextField(verbose_name='content')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='create_time')
    create_timestamp = models.IntegerField(verbose_name='create_timestamp')  # 秒级时间戳
    last_update_time = models.DateTimeField(verbose_name='last_update_time')

    class Meta:
        db_table = 'xcnvs_node_media'
        verbose_name = 'xcnvs_node_media'
        verbose_name_plural = 'xcnvs_node_media'

class NodeStreamModel(models.Model):
    sort = models.IntegerField(verbose_name='排序')
    stream_code = models.CharField(max_length=50, verbose_name='stream_code')
    stream_nickname = models.CharField(max_length=100, verbose_name='stream_nickname')
    node_codes = models.TextField(verbose_name='节点编号列表')
    state = models.IntegerField(verbose_name='状态')  # 0:默认状态 该参数暂未使用
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='create_time')
    last_update_time = models.DateTimeField(verbose_name='last_update_time')
    def __repr__(self):
        return self.stream_code

    def __str__(self):
        return self.stream_code

    class Meta:
        db_table = 'xcnvs_node_stream'
        verbose_name = 'xcnvs_node_stream'
        verbose_name_plural = 'xcnvs_node_stream'

class NodeAlgorithmFlowModel(models.Model):
    sort = models.IntegerField(verbose_name='排序')
    flow_code = models.CharField(max_length=50, verbose_name='flow_code')
    flow_name = models.CharField(max_length=100, verbose_name='flow_name')
    node_codes = models.TextField(verbose_name='节点编号列表')
    state = models.IntegerField(verbose_name='状态')  # 0:默认状态 该参数暂未使用
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='create_time')
    last_update_time = models.DateTimeField(verbose_name='last_update_time')
    def __repr__(self):
        return self.flow_code

    def __str__(self):
        return self.flow_code

    class Meta:
        db_table = 'xcnvs_node_algorithm_flow'
        verbose_name = 'xcnvs_node_algorithm_flow'
        verbose_name_plural = 'xcnvs_node_algorithm_flow'

class LabelTaskModel(models.Model):
    sort = models.IntegerField(verbose_name='sort')
    code = models.CharField(max_length=50, verbose_name='code')
    user_id = models.IntegerField(verbose_name='user_id')
    username = models.CharField(max_length=100, verbose_name='username')
    name = models.CharField(max_length=50, verbose_name='name')
    task_type = models.IntegerField(verbose_name='task_type') # 1:图片 2:视频 3:音频
    remark = models.TextField(verbose_name='remark')

    sample_annotation_count = models.IntegerField(verbose_name='sample_annotation_count')
    sample_count = models.IntegerField(verbose_name='sample_count')

    tags = models.CharField(max_length=500, verbose_name='tags')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='create_time')
    create_timestamp = models.IntegerField(verbose_name='create_timestamp')
    last_update_time = models.DateTimeField(auto_now_add=True, verbose_name='last_update_time')
    state = models.IntegerField(verbose_name='state')

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'xcnvs_label_task'
        verbose_name = '任务'
        verbose_name_plural = '任务'

class LabelTkSampleModel(models.Model):
    sort = models.IntegerField(verbose_name='排序')
    code = models.CharField(max_length=50, verbose_name='编号')
    user_id = models.IntegerField(verbose_name='用户')
    username = models.CharField(max_length=100, verbose_name='用户名')
    task_type = models.IntegerField(verbose_name='任务类型')
    task_code = models.CharField(max_length=50, verbose_name='任务编号')
    old_filename = models.CharField(max_length=200, verbose_name='原名称')
    new_filename = models.CharField(max_length=200, verbose_name='新名称')
    remark = models.CharField(max_length=100, verbose_name='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    state = models.IntegerField(verbose_name='状态')  # 0:样本所属任务不存在 1:样本所属任务存在 默认0

    annotation_user_id = models.IntegerField(verbose_name='标注用户')
    annotation_username = models.CharField(max_length=100, verbose_name='标注用户名')
    annotation_time = models.DateTimeField(verbose_name='标注时间')
    annotation_content = models.TextField(verbose_name='标注内容')
    annotation_state = models.IntegerField(verbose_name='标注状态') # 0:未标注 1:已标注 默认0

    def __repr__(self):
        return self.code

    def __str__(self):
        return self.code

    class Meta:
        db_table = 'xcnvs_labeltk_sample'
        verbose_name = '样本'
        verbose_name_plural = '样本'

class LabelTkTrainModel(models.Model):
    sort = models.IntegerField(verbose_name='排序')
    code = models.CharField(max_length=50, verbose_name='编号')
    user_id = models.IntegerField(verbose_name='用户')
    username = models.CharField(max_length=100, verbose_name='用户名')
    task_code = models.CharField(max_length=50, verbose_name='任务编号')
    algorithm_code = models.CharField(max_length=50, verbose_name='算法编号')
    device = models.CharField(max_length=50, verbose_name='设备')
    imgsz = models.IntegerField(verbose_name='输入尺寸')
    epochs = models.IntegerField(verbose_name='训练周期')
    batch = models.IntegerField(verbose_name='训练批次')
    save_period = models.IntegerField(verbose_name='保存周期')
    sample_ratio = models.IntegerField(verbose_name='训练验证比例')
    extra = models.TextField(verbose_name='其他参数')
    create_time = models.DateTimeField(verbose_name='create_time')
    train_datasets = models.CharField(max_length=200, verbose_name='train_datasets')
    train_datasets_remark = models.CharField(max_length=200, verbose_name='train_datasets_remark')
    train_datasets_time = models.DateTimeField(verbose_name='train_datasets_time')
    train_command = models.TextField(verbose_name='train_command')
    train_process_name = models.CharField(max_length=100, verbose_name='train_process_name')
    train_pid = models.IntegerField(verbose_name='train_pid')
    train_count = models.IntegerField(verbose_name='train_count')
    train_state = models.IntegerField(verbose_name='train_state')  # 0:未开启训练 1:训练中 2:已完成
    train_start_time = models.DateTimeField(verbose_name='train_start_time')
    train_stop_time = models.DateTimeField(verbose_name='train_stop_time')
    train_remark = models.CharField(max_length=200, verbose_name='train_remark')

    def __repr__(self):
        return self.code

    def __str__(self):
        return self.code

    class Meta:
        db_table = 'xcnvs_labeltk_train'
        verbose_name = '训练'
        verbose_name_plural = '训练'

class LabelTkPredictModel(models.Model):
    sort = models.IntegerField(verbose_name='排序')
    code = models.CharField(max_length=50, verbose_name='编号')
    user_id = models.IntegerField(verbose_name='用户')
    username = models.CharField(max_length=100, verbose_name='用户名')
    task_code = models.CharField(max_length=50, verbose_name='任务编号')
    train_code = models.CharField(max_length=50, verbose_name='训练编号')
    file_name = models.CharField(max_length=100, verbose_name='文件名称')
    file_size = models.IntegerField(verbose_name='文件大小')
    file_type = models.IntegerField(verbose_name='文件类型') # 0:未知 1:图片 2:视频
    calcu_seconds = models.FloatField(verbose_name='计算耗时') # 计算耗时
    create_time = models.DateTimeField(verbose_name='create_time')

    def __repr__(self):
        return self.code

    def __str__(self):
        return self.code

    class Meta:
        db_table = 'xcnvs_labeltk_predict'
        verbose_name = '测试记录'
        verbose_name_plural = '测试记录'

