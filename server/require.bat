@REM 导出Python所需依赖
@echo off
start cmd /k "pip freeze > requirements.txt&& exit" 