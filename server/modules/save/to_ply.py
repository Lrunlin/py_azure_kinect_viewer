import time
from modules.log import log as debug_log

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
