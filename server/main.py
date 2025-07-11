import time
import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import webbrowser
import subprocess
import cv2

import global_vars
from modules.K4A import K4A
from modules.log import log as debug_log
from config import OUTPUT_DIR
from routers import stats, resource, video_stream, close_stream, capture, websocket_depth, video, video_ws

k4a = K4A()
k4a.start()
debug_log("Azure Kinect已启动")


def background_capture():
    frame_count = 0
    while True:
        try:
            frame = k4a.get_capture()
            if frame.color is not None and frame.depth is not None:
                with global_vars.frame_lock:
                    global_vars.latest_frame = frame
                    if global_vars.recording_flag and global_vars.recording_writer is not None:
                        frame_count += 1
                        if frame_count % 3 == 0:
                            rgb_image = cv2.cvtColor(
                                frame.color, cv2.COLOR_BGRA2BGR)
                            global_vars.recording_writer.write(rgb_image)
        except Exception as e:
            debug_log(f"后台采集失败: {e}")
            # 这里判断是否在录制，如果是，主动stop_record
            if global_vars.recording_flag:
                debug_log("检测到相机断开，自动停止录制")
                try:
                    video.stop_record()  # 调用接口函数即可
                except Exception as ex:
                    debug_log(f"自动停止录制失败: {ex}")
        time.sleep(0.01)


threading.Thread(target=background_capture, daemon=True).start()
debug_log("后台线程已启动")

app = FastAPI()
app.include_router(resource.router)
app.include_router(stats.router)
app.include_router(video_stream.router)
app.include_router(close_stream.router)
app.include_router(capture.router)
app.include_router(websocket_depth.router)
app.include_router(video.router)
app.include_router(video_ws.router)


app.mount("/data", StaticFiles(directory=OUTPUT_DIR), name="data")
# 挂载静态文件目录

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')
index_path = os.path.join(PUBLIC_DIR, 'index.html')
node_server_path = os.path.join(PUBLIC_DIR, 'static-server.cjs')
app.mount("/", StaticFiles(directory=PUBLIC_DIR, html=True), name="html")

if os.path.exists(index_path):
    # 打开默认浏览器
    webbrowser.open("http://localhost:3000")
    subprocess.Popen(['node', node_server_path], cwd=PUBLIC_DIR)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
