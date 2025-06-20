import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')


# ========== 参数解析部分 ==========
parser = argparse.ArgumentParser(description='npy文件读取与展示')
parser.add_argument('--path', type=str, help='npy文件路径')
args = parser.parse_args()

# ========== 路径选择逻辑 ==========
if args.path:
    file_path = args.path
    print(f"使用命令行参数路径: {file_path}")
else:
    file_path = input("请输入npy文件路径：")
    # file_path = 'E:\\DeskTop\\Py_Demo\data\\2025-06-17\\1750148745730\\1750148745730_depth.npy'
    print(f"使用默认路径: {file_path}")

# ========== 读取与展示部分 ==========
arr = np.load(file_path, allow_pickle=True)
data = arr.item()  # 假设npy里是dict

print("keys:", data.keys())

# 提取深度图
depth = data.get("depth")
if depth is not None:
    print("depth shape:", depth.shape, "dtype:", depth.dtype)
    plt.imshow(depth, cmap='gray')
    plt.title("Depth")
    plt.colorbar()
    plt.show()
else:
    print("未找到'depth'键")

# # 提取彩色图（如果需要）
# color = data.get("color")
# if color is not None:
#     print("color shape:", color.shape, "dtype:", color.dtype)
#     plt.imshow(color)
#     plt.title("Color")
#     plt.show()
