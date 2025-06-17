import numpy as np
import matplotlib.pyplot as plt

# 你的 .npy 路径
file_path = 'E:/DeskTop/Py_Demo/data/2025-06-16/1750069442751/1750069442751_depth.npy'

# 读取
arr = np.load(file_path, allow_pickle=True)
data = arr.item()  # 取出字典

# 查看有哪些key
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

# 提取彩色图（如果需要）
# color = data.get("color")
# if color is not None:
#     print("color shape:", color.shape, "dtype:", color.dtype)
#     plt.imshow(color)
#     plt.title("Color")
#     plt.show()
