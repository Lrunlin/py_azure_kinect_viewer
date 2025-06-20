from fastapi import APIRouter
import threading
from fastapi.responses import JSONResponse
import time
import datetime
import os
import cv2

from modules.log import log as debug_log
from modules.save.to_ply import save_point_cloud_ply
from modules.save.to_pcd import save_point_cloud_pcd
from modules.save.to_npy import save_point_cloud_npy
from modules.save.to_png import save_rgb_images
from modules.generate_point_cloud import generate_point_cloud
from config import OUTPUT_DIR, LOCAL_IP, STATIC_PORT
import global_vars


router = APIRouter()


@router.get("/capture")
def capture():
    with global_vars.frame_lock:
        frame = global_vars.latest_frame
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
    save_rgb_images(rgb_path, color_image)
    debug_log(f"保存RGB完成，用时 {time.time() - t_start:.3f} 秒")

    host_url = f"http://{LOCAL_IP}:{STATIC_PORT}"

    def to_url_path(path):
        rel_path = path.replace(OUTPUT_DIR, "/data")
        rel_path = rel_path.replace("\\", "/")
        return f"{host_url}{rel_path}"

    def background_save():
        try:
            depth_image = frame.depth
            save_point_cloud_npy(base_dir, timestamp,
                                 depth_image, color_image)
            fx, fy = 600.0, 600.0
            cx, cy = depth_image.shape[1] / 2.0, depth_image.shape[0] / 2.0
            points, colors = generate_point_cloud(
                depth_image, fx, fy, cx, cy, color_image)
            save_point_cloud_ply(os.path.join(
                base_dir, f"{timestamp}.ply"), points, colors)
            save_point_cloud_pcd(os.path.join(
                base_dir, f"{timestamp}.pcd"), points, colors)
            debug_log("后台保存完毕")
        except Exception as e:
            debug_log(f"后台保存失败: {e}")
    threading.Thread(target=background_save, daemon=True).start()  # 多线程保存
    return JSONResponse(content={
        "status": "success",
        "timestamp": timestamp,
        "rgb_image": to_url_path(rgb_path)
    })
