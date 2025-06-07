import os
import time
import threading
import numpy as np
import cv2
from pyk4a import PyK4A, Config, ColorResolution, DepthMode
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import datetime

DEBUG_MODE = True  # 是否打印文件操作和Http请求日志
local_ip = "127.0.0.1"
OUTPUT_DIR = "../data"  # 数据存储地址


def debug_log(msg):
    if DEBUG_MODE:
        timestamp = time.strftime('%H:%M:%S')
        print(f"[{timestamp}] {msg}")


'''
【彩色相机分辨率（ColorResolution）】
16:9 比例：
ColorResolution.RES_720P    # 720p（1280x720）
ColorResolution.RES_1080P   # 1080p（1920x1080）
ColorResolution.RES_1440P   # 1440p（2560x1440）
ColorResolution.RES_2160P   # 2160p（3840x2160）

4:3 比例：
ColorResolution.RES_1536P   # 1536p（2048x1536）
ColorResolution.RES_3072P   # 3072p（4096x3072）

关闭彩色相机：
ColorResolution.OFF

【深度相机分辨率/模式（DepthMode）】
DepthMode.NFOV_BINNED       # 窄视角，降采样
DepthMode.NFOV_UNBINNED     # 窄视角，非降采样
DepthMode.WFOV_BINNED       # 广视角，降采样
DepthMode.WFOV_UNBINNED     # 广视角，非降采样
DepthMode.PASSIVE_IR        # 仅红外模式

 camera_fps=pyk4a.FrameRate.FPS_5 帧率
'''


k4a = PyK4A(Config(
    color_resolution=ColorResolution.RES_2160P,
    depth_mode=DepthMode.NFOV_UNBINNED,
    synchronized_images_only=True
))
k4a.start()
debug_log("Azure Kinect已启动")


def generate_point_cloud(depth_image, fx, fy, cx, cy, color_image=None):
    t_start = time.time()
    height, width = depth_image.shape
    xx, yy = np.meshgrid(np.arange(width), np.arange(height))
    valid = (depth_image > 0)
    z = depth_image[valid] / 1000.0
    x = (xx[valid] - cx) * z / fx
    y = (yy[valid] - cy) * z / fy
    points = np.vstack((x, y, z)).T
    if color_image is not None:
        colors = color_image[yy[valid], xx[valid], :]
    else:
        colors = np.zeros((points.shape[0], 3), dtype=np.uint8)
    t_end = time.time()
    debug_log(f"生成点云完成，用时 {t_end - t_start:.3f} 秒")
    return points, colors


def save_depth_images(base_dir, timestamp, depth_image):
    t_start = time.time()
    # 1️⃣ 保存16位PNG
    depth_16bit_path = os.path.join(base_dir, f"{timestamp}_depth16.png")
    cv2.imwrite(depth_16bit_path, depth_image)
    debug_log(f"保存深度图16位完成: {depth_16bit_path}")

    # 2️⃣ 保存8位PNG（缩放到0~255）
    depth_8bit = cv2.convertScaleAbs(depth_image, alpha=255.0 / 5000.0)
    depth_8bit_path = os.path.join(base_dir, f"{timestamp}_depth8.png")
    cv2.imwrite(depth_8bit_path, depth_8bit)
    debug_log(f"保存深度图8位完成: {depth_8bit_path}")

    # 3️⃣ 保存npy文件
    depth_npy_path = os.path.join(base_dir, f"{timestamp}_depth.npy")
    np.save(depth_npy_path, depth_image)
    debug_log(f"保存深度图npy完成: {depth_npy_path}")

    t_end = time.time()
    debug_log(f"深度图保存全部完成, 总用时 {t_end - t_start:.3f} 秒")

    return depth_16bit_path, depth_8bit_path, depth_npy_path


def save_point_cloud_ply(filename, points, colors):
    t_start = time.time()
    with open(filename, 'w') as f:
        f.write("ply\n")
        f.write("format ascii 1.0\n")
        f.write(f"element vertex {points.shape[0]}\n")
        f.write("property float x\n")
        f.write("property float y\n")
        f.write("property float z\n")
        f.write("property uchar red\n")
        f.write("property uchar green\n")
        f.write("property uchar blue\n")
        f.write("end_header\n")
        for i in range(points.shape[0]):
            x, y, z = points[i]
            r, g, b = colors[i]
            f.write(f"{x} {y} {z} {r} {g} {b}\n")
    t_end = time.time()
    debug_log(f"保存PLY完成，用时 {t_end - t_start:.3f} 秒")


def save_point_cloud_pcd(filename, points, colors):
    t_start = time.time()
    with open(filename, 'w') as f:
        f.write("VERSION .7\n")
        f.write("FIELDS x y z rgb\n")
        f.write("SIZE 4 4 4 4\n")
        f.write("TYPE F F F U\n")
        f.write("COUNT 1 1 1 1\n")
        f.write(f"WIDTH {points.shape[0]}\n")
        f.write("HEIGHT 1\n")
        f.write("VIEWPOINT 0 0 0 1 0 0 0\n")
        f.write(f"POINTS {points.shape[0]}\n")
        f.write("DATA ascii\n")
        for i in range(points.shape[0]):
            x, y, z = points[i]
            r, g, b = colors[i]
            rgb = (int(r) << 16) | (int(g) << 8) | int(b)
            f.write(f"{x} {y} {z} {rgb}\n")
    t_end = time.time()
    debug_log(f"保存PCD完成，用时 {t_end - t_start:.3f} 秒")


def save_point_cloud_json(points, colors):
    data = []
    for i in range(points.shape[0]):
        x, y, z = points[i]
        r, g, b = colors[i]
        data.append({
            "x": float(x),
            "y": float(y),
            "z": float(z),
            "r": int(r),
            "g": int(g),
            "b": int(b)
        })
    return data

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

    host_url = f"http://{local_ip}:3000"

    def to_url_path(path):
        rel_path = path.replace(OUTPUT_DIR, "/data")
        rel_path = rel_path.replace("\\", "/")
        return f"{host_url}{rel_path}"
    #

    if preview_mode == 0:
        def background_save():
            try:
                depth_image = frame.depth
                save_depth_images(base_dir, timestamp, depth_image)
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
    save_depth_images(base_dir, timestamp, depth_image)
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
        "json_data": save_point_cloud_json( points, colors)
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
