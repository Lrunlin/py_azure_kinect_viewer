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
    print(f"使用输入路径: {file_path}")

# ========== 读取与展示部分 ==========
arr = np.load(file_path, allow_pickle=True)

# 处理多种格式
if isinstance(arr, dict):
    data = arr
elif isinstance(arr, np.ndarray) and arr.dtype == 'O' and arr.size == 1:
    # 典型的np.save(dict)方式
    data = arr.item()
elif isinstance(arr, np.ndarray) and arr.ndim >= 2:
    # 纯数组格式
    data = None
    depth = arr
    print("本npy文件为数组格式，shape:", depth.shape, "dtype:", depth.dtype)
    plt.imshow(depth, cmap='gray')
    plt.title("Depth (array直接存储)")
    plt.colorbar()
    plt.show()
else:
    print("无法识别的数据结构！")
    data = None

if data is not None:
    print("keys:", data.keys())
    depth = data.get("depth")
    if depth is not None:
        print("depth shape:", depth.shape, "dtype:", depth.dtype)
        plt.imshow(depth, cmap='gray')
        plt.title("Depth")
        plt.colorbar()
        plt.show()
    else:
        print("未找到'depth'键")
