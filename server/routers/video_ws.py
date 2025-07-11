from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import global_vars
import threading
import asyncio

router = APIRouter()

ws_clients = set()
ws_clients_lock = threading.Lock()


@router.websocket("/ws/recording_status")
async def recording_status_ws(websocket: WebSocket):
    await websocket.accept()
    with ws_clients_lock:
        ws_clients.add(websocket)
    try:
        # 连接后立即推送当前状态
        await websocket.send_json({"recording": global_vars.recording_flag})
        while True:
            # 接收任意消息，客户端可用作心跳或主动查询
            await websocket.receive_text()
            await websocket.send_json({"recording": global_vars.recording_flag})
    except WebSocketDisconnect:
        pass
    finally:
        with ws_clients_lock:
            ws_clients.discard(websocket)


def notify_recording_status_change(new_status: bool):
    import asyncio

    async def broadcast():
        remove_set = set()
        for ws in list(ws_clients):
            try:
                await ws.send_json({"recording": new_status})
            except Exception as e:
                print("WS推送异常：", e)
                remove_set.add(ws)
        # 移除异常连接
        with ws_clients_lock:
            for ws in remove_set:
                ws_clients.discard(ws)
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(broadcast())
        print(f"【通知WS】广播录制状态：{new_status}，客户端数量：{len(ws_clients)}")
    except Exception as ex:
        print(f"【通知WS】广播失败：{ex}")
