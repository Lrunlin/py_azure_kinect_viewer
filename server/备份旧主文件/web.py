import os
import time
import numpy as np
import cv2
from pyk4a import PyK4A, Config, ColorResolution, DepthMode
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

# 1. 配置输出文件夹
OUTPUT_DIR = "/data"
os.makedirs(os.path.join(OUTPUT_DIR, "rgb"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "depth"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "pointcloud_ply"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "pointcloud_pcd"), exist_ok=True)

# 2. 初始化Kinect
k4a = PyK4A(Config(
    color_resolution=ColorResolution.RES_720P,
    depth_mode=DepthMode.NFOV_UNBINNED,
    synchronized_images_only=True
))
k4a.start()
print("[INFO] Azure Kinect已启动")

# 3. 定义点云生成函数（示例内参）
def generate_point_cloud(depth_image, fx, fy, cx, cy, color_image=None):
    height, width = depth_image.shape
    xx, yy = np.meshgrid(np.arange(width), np.arange(height))
    valid = (depth_image > 0)
    z = depth_image[valid] / 1000.0  # 单位: 米
    x = (xx[valid] - cx) * z / fx
    y = (yy[valid] - cy) * z / fy
    points = np.vstack((x, y, z)).T
    if color_image is not None:
        colors = color_image[yy[valid], xx[valid], :]
    else:
        colors = np.zeros((points.shape[0], 3), dtype=np.uint8)
    return points, colors

# 4. 保存PLY
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

# 5. 保存PCD
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

# 6. FastAPI 应用
app = FastAPI()

@app.get("/capture")
def capture():
    capture = k4a.get_capture()
    if capture.color is not None and capture.depth is not None:
        timestamp = str(int(time.time() * 1000))
        print(f"[INFO] 采集帧：{timestamp}")

        # 保存彩色图像
        color_image = cv2.cvtColor(capture.color, cv2.COLOR_BGRA2BGR)
        cv2.imwrite(os.path.join(OUTPUT_DIR, "rgb", f"{timestamp}.png"), color_image)

        # 保存深度图像
        depth_image = capture.depth
        cv2.imwrite(os.path.join(OUTPUT_DIR, "depth", f"{timestamp}.png"), depth_image)

        # 生成点云（示例）
        fx = 600.0
        fy = 600.0
        cx = depth_image.shape[1] / 2.0
        cy = depth_image.shape[0] / 2.0
        points, colors = generate_point_cloud(depth_image, fx, fy, cx, cy, color_image)

        # 保存PLY
        ply_path = os.path.join(OUTPUT_DIR, "pointcloud_ply", f"{timestamp}.ply")
        save_point_cloud_ply(ply_path, points, colors)
        print(f"[INFO] 保存点云（PLY）：{ply_path}")

        # 保存PCD
        pcd_path = os.path.join(OUTPUT_DIR, "pointcloud_pcd", f"{timestamp}.pcd")
        save_point_cloud_pcd(pcd_path, points, colors)
        print(f"[INFO] 保存点云（PCD）：{pcd_path}")

        return JSONResponse(content={
            "status": "success",
            "timestamp": timestamp,
            "rgb_image": f"{timestamp}.png",
            "depth_image": f"{timestamp}.png",
            "ply_file": f"{timestamp}.ply",
            "pcd_file": f"{timestamp}.pcd"
        })
    else:
        return JSONResponse(content={"status": "fail", "message": "未获取到图像数据"}, status_code=500)

# 7. 关闭设备（可选）
@app.on_event("shutdown")
def shutdown_event():
    k4a.stop()
    print("[INFO] 设备已关闭")

# 8. 启动 FastAPI
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=3000)
