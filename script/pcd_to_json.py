import os
import json
import numpy as np
import open3d as o3d
import time
import concurrent.futures
import traceback

def debug_log(msg):
    timestamp = time.strftime('%H:%M:%S')
    print(f"[{timestamp}] {msg}")

def convert_pcd_file(pcd_path):
    try:
        folder_path = os.path.dirname(pcd_path)
        folder_name = os.path.basename(folder_path)
        output_json = os.path.join(folder_path, f"{folder_name}_pcd.json")

        merged_data = []
        t_start = time.time()
        pcd = o3d.io.read_point_cloud(pcd_path)
        points = np.asarray(pcd.points)
        colors = (np.asarray(pcd.colors) * 255).astype(np.uint8)
        for i in range(points.shape[0]):
            x, y, z = points[i]
            r, g, b = colors[i]
            merged_data.append({
                "x": float(x),
                "y": float(y),
                "z": float(z),
                "r": int(r),
                "g": int(g),
                "b": int(b)
            })
        t_end = time.time()
        debug_log(f"[PCD → JSON] {os.path.basename(pcd_path)} 转换完成，用时 {t_end - t_start:.3f} 秒")
        return output_json, merged_data, True
    except Exception as e:
        debug_log(f"[错误] 处理文件 {pcd_path} 出错: {e}")
        traceback.print_exc()
        return None, None, False

def convert_pcd_to_json(folder_path):
    folder_name = os.path.basename(os.path.normpath(folder_path))
    output_json = os.path.join(folder_path, f"{folder_name}_pcd.json")

    if os.path.exists(output_json):
        debug_log(f"[跳过] {output_json} 已存在，跳过转换。")
        return 0, 0

    pcd_files = [os.path.join(folder_path, f)
                 for f in os.listdir(folder_path) if f.endswith(".pcd")]

    if not pcd_files:
        return 0, 0

    merged_data = []
    success_count = 0
    failure_count = 0

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(convert_pcd_file, pcd) for pcd in pcd_files]
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
        debug_log(f"[PCD → JSON] 所有文件保存: {output_json}")

    return success_count, failure_count

def process_all_subfolders(root_folder):
    total_success = 0
    total_failure = 0
    overall_start = time.time()

    for dirpath, _, filenames in os.walk(root_folder):
        if any(f.endswith('.pcd') for f in filenames):
            debug_log(f"处理文件夹: {dirpath}")
            success, failure = convert_pcd_to_json(dirpath)
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
