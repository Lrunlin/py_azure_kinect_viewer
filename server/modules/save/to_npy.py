import time
import numpy as np
from modules.log import log as debug_log
import os


def save_point_cloud_npy(base_dir, timestamp, depth_image, color_image):
    t_start = time.time()
    # 保存npy文件
    depth_npy_path = os.path.join(base_dir, f"{timestamp}_depth.npy")
    np.save(depth_npy_path, {"depth": depth_image, "color": color_image})
    t_end = time.time()
    debug_log(f"保存NPY完成，用时 {t_end - t_start:.3f} 秒")

    return depth_npy_path
