import time
import numpy as np
from modules.log import log as debug_log
import os


def save_depth_images(base_dir, timestamp, depth_image, color_image):
    t_start = time.time()
    # 保存npy文件
    depth_npy_path = os.path.join(base_dir, f"{timestamp}_depth.npy")
    np.save(depth_npy_path, {"depth": depth_image, "color": color_image})
    debug_log(f"保存深度图npy完成: {depth_npy_path}")

    t_end = time.time()
    debug_log(f"深度图保存全部完成, 总用时 {t_end - t_start:.3f} 秒")

    return depth_npy_path
