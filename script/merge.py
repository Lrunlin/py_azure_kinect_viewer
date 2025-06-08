'''
根据ply pcd npy将数据合并为一个JSON文件
数据包括RGB XYZ NXNYNZ faces数据
'''

import os
import numpy as np
import open3d as o3d
import json


def load_point_cloud(folder):
    """
    尝试加载 a.ply, a.pcd, 或 a_depth.npy，并返回Open3D点云
    """
    basename = os.path.basename(folder.rstrip("/\\"))
    ply_file = os.path.join(folder, f"{basename}.ply")
    pcd_file = os.path.join(folder, f"{basename}.pcd")
    npy_file = os.path.join(folder, f"{basename}_depth.npy")

    if os.path.exists(ply_file):
        print(f"加载PLY文件: {ply_file}")
        pcd = o3d.io.read_point_cloud(ply_file)
    elif os.path.exists(pcd_file):
        print(f"加载PCD文件: {pcd_file}")
        pcd = o3d.io.read_point_cloud(pcd_file)
    elif os.path.exists(npy_file):
        print(f"加载NPY文件: {npy_file}")
        npy_data = np.load(npy_file, allow_pickle=True).item()
        depth = npy_data.get("depth")
        color = npy_data.get("color")
        if depth is None:
            raise ValueError(f"{npy_file} 中未找到depth数据")

        height, width = depth.shape
        fx, fy = 600.0, 600.0
        cx, cy = width / 2.0, height / 2.0
        xx, yy = np.meshgrid(np.arange(width), np.arange(height))
        valid = (depth > 0)
        z = depth[valid] / 1000.0
        x = (xx[valid] - cx) * z / fx
        y = (yy[valid] - cy) * z / fy
        points = np.vstack((x, y, z)).T

        if color is not None:
            colors = color[yy[valid], xx[valid], :][:, :3] / 255.0
        else:
            colors = np.zeros((points.shape[0], 3))

        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        pcd.colors = o3d.utility.Vector3dVector(colors)
    else:
        print(f"未找到ply/pcd/npy文件: {folder}")
        return None
    return pcd


def estimate_normals(pcd, radius=0.02, max_nn=30):
    pcd.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=radius, max_nn=max_nn))
    pcd.orient_normals_consistent_tangent_plane(k=30)
    return pcd


def poisson_mesh(pcd, depth=8):
    mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
        pcd, depth=depth)
    return mesh


def save_json(points, colors, normals, faces, output_file):
    """
    保存点、颜色、法向量、三角面片到JSON
    """
    data = {
        "points": [],
        "faces": []
    }
    for i in range(points.shape[0]):
        point = {
            "x": float(points[i, 0]),
            "y": float(points[i, 1]),
            "z": float(points[i, 2]),
            "r": int(colors[i, 0]*255),
            "g": int(colors[i, 1]*255),
            "b": int(colors[i, 2]*255),
            "nx": float(normals[i, 0]),
            "ny": float(normals[i, 1]),
            "nz": float(normals[i, 2])
        }
        data["points"].append(point)

    for tri in faces:
        data["faces"].append([int(idx) for idx in tri])

    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)
    print(f"已保存JSON: {output_file}")


def process_folder(folder):
    pcd = load_point_cloud(folder)
    if pcd is None:
        return

    print("估计法向量...")
    pcd = estimate_normals(pcd)

    # 转换为三角网格
    print("尝试生成网格...")
    mesh = poisson_mesh(pcd)
    mesh.compute_vertex_normals()

    # 提取points, colors, normals
    points = np.asarray(mesh.vertices)
    normals = np.asarray(mesh.vertex_normals)
    try:
        colors = np.asarray(pcd.colors)
        if colors.shape[0] != points.shape[0]:
            # 如果点云和网格点数对不上，就用黑色
            colors = np.zeros((points.shape[0], 3))
    except:
        colors = np.zeros((points.shape[0], 3))

    # faces
    faces = np.asarray(mesh.triangles)

    # 保存
    basename = os.path.basename(folder.rstrip("/\\"))
    output_file = os.path.join(folder, f"{basename}_summary.json")
    save_json(points, colors, normals, faces, output_file)


def recursive_process(root_folder):
    for dirpath, dirnames, filenames in os.walk(root_folder):
        if any(fname.endswith(('.ply', '.pcd', '.npy')) for fname in filenames):
            print(f"处理文件夹: {dirpath}")
            process_folder(dirpath)


if __name__ == "__main__":
    root_folder = "./data/2025-06-07"  # 这里写上你的数据根目录
    recursive_process(root_folder)
