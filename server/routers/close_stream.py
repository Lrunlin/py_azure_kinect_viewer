from fastapi import APIRouter
import global_vars
from fastapi import Query
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/close_stream")
def close_stream(stream_id: str = Query(...)):
    global_vars.stream_stop_flags[stream_id] = True
    return JSONResponse({"status": "ok"})
