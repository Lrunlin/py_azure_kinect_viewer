import os
import cv2
import imageio
import re


def contains_chinese(string):
    # 检查是否包含中文或其他非ASCII字符
    return re.search(r'[^\x00-\x7F]', string) is not None


'''
根据路径自动选择保存文件的模块
'''


def save_rgb_images(path, image):
    try:
        if contains_chinese(path):
            imageio.imwrite(path, image)
            if os.path.exists(path):
                return True
            else:
                print(f"[警告] imageio 保存失败: {path}")
                return False
        else:
            result = cv2.imwrite(path, image)
            if result and os.path.exists(path):
                return True
            else:
                print(f"[警告] cv2.imwrite 保存失败: {path}")
                return False
    except Exception as e:
        print(f"[错误] 保存图片时发生异常: {e}")
        return False
