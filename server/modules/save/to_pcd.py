import time
from modules.log import log as debug_log

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
