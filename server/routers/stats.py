import os
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import datetime

from config import OUTPUT_DIR

router = APIRouter()


@router.get("/stats")
def stats():
    # 获取今天的日期（格式：yyyy-mm-dd）
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    today_dir = os.path.join(OUTPUT_DIR, today_str)

    # 检查目录是否存在
    if not os.path.exists(today_dir):
        folder_count = 0
    else:
        # 统计子文件夹数量
        folder_count = sum(os.path.isdir(os.path.join(today_dir, name))
                           for name in os.listdir(today_dir))

    return JSONResponse(content={
        "status": "success",
        "date": today_str,
        "folder_count": folder_count
    })
