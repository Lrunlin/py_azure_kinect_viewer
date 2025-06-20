import asyncio
import numpy as np
import time
import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

import global_vars
from modules.K4A import K4A
from modules.log import log as debug_log
from config import OUTPUT_DIR
from routers import stats, resource, video_stream, close_stream, capture, websocket_pointcloud

k4a = K4A()
k4a.start()
debug_log("Azure Kinect已启动")


def background_capture():
    while True:
        try:
            frame = k4a.get_capture()
            if frame.color is not None and frame.depth is not None:
                with global_vars.frame_lock:
                    global_vars.latest_frame = frame
        except Exception as e:
            debug_log(f"后台采集失败: {e}")
        time.sleep(0.01)


threading.Thread(target=background_capture, daemon=True).start()
debug_log("后台线程已启动")

app = FastAPI()
app.include_router(resource.router)
app.include_router(stats.router)
app.include_router(video_stream.router)
app.include_router(close_stream.router)
app.include_router(capture.router)
app.include_router(websocket_pointcloud.router)


app.mount("/data", StaticFiles(directory=OUTPUT_DIR), name="data")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
