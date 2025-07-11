import threading

# 全局流断开控制(判断实时相机是否断开)
stream_stop_flags = {}  # {stream_id: bool}
latest_frame = None  # 相机最后一帧
frame_lock = threading.Lock()  # 锁 实时捕获相机帧


recording_flag = False
recording_writer = None
recording_path = None
