import os
import json
import numpy as np
import time
import concurrent.futures
import traceback


def debug_log(msg):
    timestamp = time.strftime('%H:%M:%S')
    print(f"[{timestamp}] {msg}")


def convert_npy_file(npy_path, fx=600.0, fy=600.0):
    try:
        folder_path = os.path.dirname(npy_path)
        folder_name = os.path.basename(folder_path)
        output_json = os.path.join(folder_path, f"{folder_name}_npy.json")

        merged_data = []
        t_start = time.time()

        # 尝试解析npz文件或npy字典格式
        npy_data = np.load(npy_path, allow_pickle=True)
        if isinstance(npy_data, np.lib.npyio.NpzFile):
            npy_data = dict(npy_data)
        if isinstance(npy_data, dict) or isinstance(npy_data, np.ndarray) and npy_data.shape == ():  # 0维数组
            npy_data = npy_data.item()
            depth = npy_data.get("depth")
            color_image = npy_data.get("color")
        else:
            depth = npy_data
            color_image = None

        if depth is None:
            raise ValueError("NPY文件中缺少depth数据")

        height, width = depth.shape
        cx, cy = width / 2.0, height / 2.0
        xx, yy = np.meshgrid(np.arange(width), np.arange(height))
        valid = (depth > 0)
        z = depth[valid] / 1000.0
        x = (xx[valid] - cx) * z / fx
        y = (yy[valid] - cy) * z / fy
        points = np.vstack((x, y, z)).T

        if color_image is not None:
            colors = color_image[yy[valid], xx[valid], :]
        else:
            colors = np.zeros((points.shape[0], 3), dtype=np.uint8)

        for i in range(points.shape[0]):
            xi, yi, zi = points[i]
            r, g, b = colors[i]
            merged_data.append({
                "x": float(xi),
                "y": float(yi),
                "z": float(zi),
                "r": int(r),
                "g": int(g),
                "b": int(b)
            })

        t_end = time.time()
        debug_log(
            f"[NPY → JSON] {os.path.basename(npy_path)} 转换完成，用时 {t_end - t_start:.3f} 秒")
        return output_json, merged_data, True

    except Exception as e:
        debug_log(f"[错误] 处理文件 {npy_path} 出错: {e}")
        traceback.print_exc()
        return None, None, False


def convert_npy_to_json(folder_path):
    folder_name = os.path.basename(os.path.normpath(folder_path))
    output_json = os.path.join(folder_path, f"{folder_name}_npy.json")

    if os.path.exists(output_json):
        debug_log(f"[跳过] {output_json} 已存在，跳过转换。")
        return 0, 0

    npy_files = [os.path.join(folder_path, f)
                 for f in os.listdir(folder_path) if f.endswith(".npy")]

    if not npy_files:
        return 0, 0

    merged_data = []
    success_count = 0
    failure_count = 0

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(convert_npy_file, npy) for npy in npy_files]
        for future in concurrent.futures.as_completed(futures):
            output_json_tmp, data, success = future.result()
            if success:
                merged_data.extend(data)
                success_count += 1
            else:
                failure_count += 1

    if merged_data:
        with open(output_json, "w") as jf:
            json.dump(merged_data, jf, indent=2)
        debug_log(f"[NPY → JSON] 所有文件保存: {output_json}")

    return success_count, failure_count


def process_all_subfolders(root_folder):
    total_success = 0
    total_failure = 0
    overall_start = time.time()

    for dirpath, _, filenames in os.walk(root_folder):
        if any(f.endswith('.npy') for f in filenames):
            debug_log(f"处理文件夹: {dirpath}")
            success, failure = convert_npy_to_json(dirpath)
            total_success += success
            total_failure += failure

    overall_end = time.time()
    debug_log(f"=== 统计结果 ===")
    debug_log(f"总成功文件数: {total_success}")
    debug_log(f"总失败文件数: {total_failure}")
    debug_log(f"总耗时: {overall_end - overall_start:.2f} 秒")


if __name__ == "__main__":
    root_dir = "./data/2025-06-07"
    process_all_subfolders(root_dir)
