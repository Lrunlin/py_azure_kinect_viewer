from pyk4a import PyK4A, Config, ColorResolution, DepthMode, FPS

# 帧数:4K就是30 2k就是15


'''
【彩色相机分辨率（ColorResolution）】
16:9 比例：
ColorResolution.RES_720P    # 720p（1280x720）
ColorResolution.RES_1080P   # 1080p（1920x1080）
ColorResolution.RES_1440P   # 1440p（2560x1440）
ColorResolution.RES_2160P   # 2160p（3840x2160）

4:3 比例：
ColorResolution.RES_1536P   # 1536p（2048x1536）
ColorResolution.RES_3072P   # 3072p（4096x3072）

关闭彩色相机：
ColorResolution.OFF

【深度相机分辨率/模式（DepthMode）】
DepthMode.NFOV_BINNED       # 窄视角，降采样
DepthMode.NFOV_UNBINNED     # 窄视角，非降采样
DepthMode.WFOV_BINNED       # 广视角，降采样
DepthMode.WFOV_UNBINNED     # 广视角，非降采样
DepthMode.PASSIVE_IR        # 仅红外模式

 camera_fps=FPS.FPS_5 帧率
 
 
 
     RES_720P = 1
    RES_1080P = 2
    RES_1440P = 3
    RES_1536P = 4
    RES_2160P = 5
    RES_3072P = 6
    
    
    FPS_5 = 0
    FPS_15 = 1
    FPS_30 = 2
'''


def K4A():
    return PyK4A(Config(
        color_resolution=ColorResolution.RES_1080P,
        camera_fps=FPS.FPS_30,
        depth_mode=DepthMode.NFOV_UNBINNED,
        synchronized_images_only=True
    ))
