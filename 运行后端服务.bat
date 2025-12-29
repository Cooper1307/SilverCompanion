@echo off
chcp 65001
echo [启动] 正在启动 SilverCompanion 后端服务 (端口 8001)...
echo [提示] 请不要关闭此窗口。
echo [提示] 启动成功后，请在浏览器打开 frontend/index.html 进行测试。
echo.

cd /d "%~dp0"
uvicorn project_code.backend.main:app --host 0.0.0.0 --port 8001 --reload

pause
