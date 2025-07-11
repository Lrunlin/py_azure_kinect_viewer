from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import numpy as np
import global_vars
from modules.generate_point_cloud import generate_point_cloud

router = APIRouter()


@router.websocket("/ws/depth")
async def websocket_pointcloud(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await asyncio.sleep(0.05)
            with global_vars.frame_lock:
                frame = global_vars.latest_frame
            if frame is None or frame.color is None or frame.depth is None:
                continue
            fx, fy = 600.0, 600.0
            cx, cy = frame.depth.shape[1] / 2.0, frame.depth.shape[0] / 2.0
            points, _ = generate_point_cloud(
                frame.depth, fx, fy, cx, cy, frame.color)
            pc = points.astype(np.float32)
            await websocket.send_bytes(pc.tobytes())
    except WebSocketDisconnect:
        # 客户端主动断开，这里静默处理即可
        pass
    except Exception as e:
        # 可选：打印其他异常
        print(f"WebSocket异常: {e}")
    # 不需要 finally 里再 close 了，WebSocketDisconnect 时连接已关闭
