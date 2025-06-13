import time
import numpy as np
from modules.log import log as debug_log


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
