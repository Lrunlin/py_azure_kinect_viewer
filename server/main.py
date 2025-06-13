import os
import time
import threading
import cv2
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import datetime

from modules.K4A import K4A
from modules.save.ply import save_point_cloud_ply
from modules.save.pcd import save_point_cloud_pcd
from modules.save.npy import save_depth_images
from modules.save.json import save_point_cloud_json
from modules.generate_point_cloud import generate_point_cloud
from modules.log import log as debug_log
from config import OUTPUT_DIR, LOCAL_IP


k4a = K4A()
k4a.start()
debug_log("Azure Kinect已启动")


latest_frame = None
frame_lock = threading.Lock()


def background_capture():
    global latest_frame
    while True:
        try:
            frame = k4a.get_capture()
            if frame.color is not None and frame.depth is not None:
                with frame_lock:
                    latest_frame = frame
        except Exception as e:
            debug_log(f"后台采集失败: {e}")
        time.sleep(0.01)


threading.Thread(target=background_capture, daemon=True).start()
debug_log("后台线程已启动")

app = FastAPI()
app.mount("/data", StaticFiles(directory=OUTPUT_DIR), name="data")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


def generate_video_stream():
    while True:
        with frame_lock:
            frame = latest_frame
        if frame is None:
            continue

        # 获取当前帧的RGB图像
        rgb_image = cv2.cvtColor(frame.color, cv2.COLOR_BGRA2BGR)

        # 将图片编码为JPEG格式
        _, encoded_image = cv2.imencode(".jpg", rgb_image)
        frame_bytes = encoded_image.tobytes()

        # 返回一个帧，保持持续流
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')


@app.get("/video_stream")
def video_stream():
    return StreamingResponse(generate_video_stream(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.get("/capture")
def capture(preview_mode: int = Query(1, description="预览模式: 1=正常，0=极速模式")):
    with frame_lock:
        frame = latest_frame
    if frame is None:
        return JSONResponse(content={"status": "fail", "message": "暂无可用帧"}, status_code=500)

    timestamp = str(int(time.time() * 1000))
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    base_dir = os.path.join(OUTPUT_DIR, date_str, timestamp)
    os.makedirs(base_dir, exist_ok=True)

    debug_log(f"开始保存数据：{timestamp}")

    t_start = time.time()
    color_image = cv2.cvtColor(frame.color, cv2.COLOR_BGRA2BGR)
    rgb_path = os.path.join(base_dir, f"{timestamp}.png")
    cv2.imwrite(rgb_path, color_image)
    debug_log(f"保存RGB完成，用时 {time.time() - t_start:.3f} 秒")

    host_url = f"http://{LOCAL_IP}:3000"

    def to_url_path(path):
        rel_path = path.replace(OUTPUT_DIR, "/data")
        rel_path = rel_path.replace("\\", "/")
        return f"{host_url}{rel_path}"

    if preview_mode == 0:
        def background_save():
            try:
                depth_image = frame.depth
                save_depth_images(base_dir, timestamp,
                                  depth_image, color_image)
                fx, fy = 600.0, 600.0
                cx, cy = depth_image.shape[1] / 2.0, depth_image.shape[0] / 2.0
                points, colors = generate_point_cloud(
                    depth_image, fx, fy, cx, cy, color_image)
                save_point_cloud_ply(os.path.join(
                    base_dir, f"{timestamp}.ply"), points, colors)
                save_point_cloud_pcd(os.path.join(
                    base_dir, f"{timestamp}.pcd"), points, colors)
                debug_log("极速模式：后台保存完毕")
            except Exception as e:
                debug_log(f"极速模式后台保存失败: {e}")
        threading.Thread(target=background_save, daemon=True).start()  # 多线程保存
        return JSONResponse(content={
            "status": "success",
            "timestamp": timestamp,
            "rgb_image": to_url_path(rgb_path)
        })

    depth_image = frame.depth
    save_depth_images(base_dir, timestamp, depth_image, color_image)
    fx, fy = 600.0, 600.0
    cx, cy = depth_image.shape[1] / 2.0, depth_image.shape[0] / 2.0
    points, colors = generate_point_cloud(
        depth_image, fx, fy, cx, cy, color_image)
    save_point_cloud_ply(os.path.join(
        base_dir, f"{timestamp}.ply"), points, colors)
    save_point_cloud_pcd(os.path.join(
        base_dir, f"{timestamp}.pcd"), points, colors)

    debug_log("预览模式：所有数据保存完成")
    return JSONResponse(content={
        "status": "success",
        "timestamp": timestamp,
        "rgb_image": to_url_path(rgb_path),
        "json_data": save_point_cloud_json(points, colors)
    })


@app.get("/stats")
def get_today_stats():
    # 获取今天的日期（格式：yyyy-mm-dd）
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    today_dir = os.path.join(OUTPUT_DIR, today_str)

    # 检查目录是否存在
    if not os.path.exists(today_dir):
        folder_count = 0
    else:
        # 统计子文件夹数量
        folder_count = sum(os.path.isdir(os.path.join(today_dir, name))
                           for name in os.listdir(today_dir))

    return JSONResponse(content={
        "status": "success",
        "date": today_str,
        "folder_count": folder_count
    })


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
