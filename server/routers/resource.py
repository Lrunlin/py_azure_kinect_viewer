import os
from fastapi import APIRouter
import psutil

router = APIRouter()


@router.get("/resource")
def resource():
    pid = os.getpid()
    p = psutil.Process(pid)
    mem_info = p.memory_info()
    mem_usage_mb = mem_info.rss / 1024 / 1024

    cpu_percent = p.cpu_percent(interval=0.5)  # 获取总占比
    cpu_count = psutil.cpu_count(logical=True)  # 逻辑核心数

    # 平均到所有核心，最大不会超过 100%
    cpu_percent_normalized = cpu_percent / cpu_count

    return {
        "cpu_percent": round(cpu_percent_normalized, 2),
        "memory_mb": round(mem_usage_mb, 2),
    }
