from fastapi import APIRouter
from fastapi import Query
from fastapi.responses import StreamingResponse
import time
import cv2
import global_vars

router = APIRouter()

# 只能是根据变量判断是否断开 前端注销组件没用


def generate_video_stream(stream_id: str):
    try:
        while True:
            # 检查自己是否需要断开
            if global_vars.stream_stop_flags.get(stream_id, False):
                break
            with global_vars.frame_lock:
                frame = global_vars.latest_frame
            if frame is None:
                time.sleep(0.01)
                continue
            rgb_image = cv2.cvtColor(frame.color, cv2.COLOR_BGRA2BGR)
            _, encoded_image = cv2.imencode(".jpg", rgb_image)
            frame_bytes = encoded_image.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')
    finally:
        # 流断开后删除标记
        global_vars.stream_stop_flags.pop(stream_id, None)

@router.get("/video_stream")
def video_stream(stream_id: str = Query(...)):
    global_vars.stream_stop_flags[stream_id] = False  # 新连接
    return StreamingResponse(generate_video_stream(stream_id), media_type="multipart/x-mixed-replace; boundary=frame")
