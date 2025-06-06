import os
import time
import numpy as np
import cv2
from pyk4a import PyK4A, Config, ColorResolution, DepthMode
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import datetime
import json
import socket

# 获取内网地址函数
def get_local_ip():
    """获取本机的局域网IP地址（如192.168.x.x）"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 连接到一个公网IP（不会真正连接），借此获得本机IP
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip
# local_ip = get_local_ip()
local_ip = '127.0.0.1'

# 1. 配置输出文件夹
OUTPUT_DIR = "/data"

# 2. 初始化Kinect
k4a = PyK4A(Config(
    color_resolution=ColorResolution.RES_720P,
    depth_mode=DepthMode.NFOV_UNBINNED,
    synchronized_images_only=True
))
k4a.start()
print("[INFO] Azure Kinect已启动")

# 3. 点云生成函数
def generate_point_cloud(depth_image, fx, fy, cx, cy, color_image=None):
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
    return points, colors

# 4. 保存PLY文件
def save_point_cloud_ply(filename, points, colors):
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

# 5. 保存PCD文件
def save_point_cloud_pcd(filename, points, colors):
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

# 6. 保存JSON文件
def save_point_cloud_json(filename, points, colors):
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
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

# 7. FastAPI 应用
app = FastAPI()
app.mount("/data", StaticFiles(directory=OUTPUT_DIR), name="data")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或者写具体的域名，如 ["http://localhost:8080"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/capture")
def capture():
    capture = k4a.get_capture()
    if capture.color is not None and capture.depth is not None:
        timestamp = str(int(time.time() * 1000))
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        base_dir = os.path.join(OUTPUT_DIR, date_str, timestamp)
        os.makedirs(base_dir, exist_ok=True)

        print(f"[INFO] 采集帧：{timestamp}")

        # 保存彩色图像
        color_image = cv2.cvtColor(capture.color, cv2.COLOR_BGRA2BGR)
        rgb_path = os.path.join(base_dir, f"{timestamp}.png")
        cv2.imwrite(rgb_path, color_image)

        # 保存深度图像
        depth_image = capture.depth
        depth_path = os.path.join(base_dir, f"{timestamp}_depth.png")
        cv2.imwrite(depth_path, depth_image)

        # 生成点云
        fx, fy = 600.0, 600.0
        cx, cy = depth_image.shape[1] / 2.0, depth_image.shape[0] / 2.0
        points, colors = generate_point_cloud(depth_image, fx, fy, cx, cy, color_image)

        # 保存 PLY
        ply_path = os.path.join(base_dir, f"{timestamp}.ply")
        save_point_cloud_ply(ply_path, points, colors)

        # 保存 PCD
        pcd_path = os.path.join(base_dir, f"{timestamp}.pcd")
        save_point_cloud_pcd(pcd_path, points, colors)

        # 保存 JSON
        json_path = os.path.join(base_dir, f"{timestamp}.json")
        save_point_cloud_json(json_path, points, colors)

        print(f"[INFO] 已保存所有数据")
        host_url = f"http://{local_ip}:3000"

        # 把 Windows 路径分隔符 \ 转成 /
        def to_url_path(path):
            rel_path = path.replace(OUTPUT_DIR, "/data")
            rel_path = rel_path.replace("\\", "/")
            return f"{host_url}{rel_path}"

        # # 读取JSON数据
        with open(json_path, "r", encoding="utf-8") as jf:
            point_cloud_data = json.load(jf)

        return JSONResponse(content={
            "status": "success",
            "timestamp": timestamp,
            "rgb_image": to_url_path(rgb_path),
            # "depth_image": to_url_path(depth_path),
            # "ply_file": to_url_path(ply_path),
            # "pcd_file": to_url_path(pcd_path),
            "json_file": to_url_path(json_path),
            "json_data": point_cloud_data
        })

        # return JSONResponse(content={
        #     "status": "success",
        #     "timestamp": timestamp,
        #     "rgb_image": to_url_path(rgb_path),
        #     "depth_image": to_url_path(depth_path),
        #     "ply_file": to_url_path(ply_path),
        #     "pcd_file": to_url_path(pcd_path),
        #     "json_file": to_url_path(json_path)
        # })
    else:
        return JSONResponse(content={"status": "fail", "message": "未获取到图像数据"}, status_code=500)

# 8. 关闭设备
@app.on_event("shutdown")
def shutdown_event():
    k4a.stop()
    print("[INFO] 设备已关闭")

# 9. 启动 FastAPI
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=3000)
