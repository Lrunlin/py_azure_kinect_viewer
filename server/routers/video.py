from fastapi import APIRouter
from fastapi.responses import JSONResponse
import time
import os
import cv2
from datetime import datetime
import config
import global_vars
from routers import video_ws

router = APIRouter()


def get_video_save_dir():
    today = datetime.now().strftime("%Y-%m-%d")
    save_dir = os.path.join(config.VIDEO_SAVE_PATH, today)
    os.makedirs(save_dir, exist_ok=True)
    return save_dir


def get_video_save_path():
    save_dir = get_video_save_dir()
    ts = int(time.time() * 1000)
    filename = f"{ts}.mp4"
    return os.path.join(save_dir, filename)


def get_h264_writer(save_path, width, height, fps=25):
    """
    尝试多种H.264 FourCC，找到可用的VideoWriter。
    """
    for fourcc_str in ['mp4v', 'avc1', 'H264', 'X264']:
        fourcc = cv2.VideoWriter_fourcc(*fourcc_str)
        writer = cv2.VideoWriter(save_path, fourcc, fps, (width, height))
        if writer.isOpened():
            print(f"[INFO] 使用FourCC: {fourcc_str} (H.264)")
            return writer
    return None


@router.post("/start_record")
def start_record():
    if global_vars.recording_flag:
        return JSONResponse({"success": False, "msg": "已经在录制"}, status_code=400)
    with global_vars.frame_lock:
        frame = global_vars.latest_frame
    if frame is None:
        return JSONResponse({"success": False, "msg": "没有可用帧"}, status_code=400)
    rgb_image = cv2.cvtColor(frame.color, cv2.COLOR_BGRA2BGR)
    height, width, _ = rgb_image.shape
    save_path = get_video_save_path()
    writer = get_h264_writer(save_path, width, height, fps=25)
    if writer is None:
        return JSONResponse({"success": False, "msg": "无法打开VideoWriter，H.264尝试均失败"}, status_code=500)
    global_vars.recording_flag = True
    global_vars.recording_writer = writer
    global_vars.recording_path = save_path
    video_ws.notify_recording_status_change(True)  # 通知WebSocket客户端
    return JSONResponse({"success": True, "msg": "开始录制", "path": save_path})


@router.post("/stop_record")
def stop_record():
    if not global_vars.recording_flag:
        return JSONResponse({"success": False, "msg": "当前未录制"}, status_code=400)
    global_vars.recording_flag = False
    if global_vars.recording_writer is not None:
        global_vars.recording_writer.release()
    path = global_vars.recording_path
    global_vars.recording_writer = None
    global_vars.recording_path = None
    video_ws.notify_recording_status_change(False)  # 通知WebSocket客户端
    return JSONResponse({"success": True, "msg": "录制结束", "path": path})
