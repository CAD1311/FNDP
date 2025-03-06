@echo off
REM 确保脚本在项目根目录执行（FNDP目录）
set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

REM 启动Redis服务（需配置环境变量）
start /b "Redis Server" cmd /k "redis-server"

REM 启动后端服务（强制定位到backend子目录）
start /b "ruoyi-fastapi-backend" cmd /k "cd /d %ROOT_DIR%ruoyi-fastapi-backend && python app.py"

REM 等待后端服务启动完成5秒
ping 127.0.0.1 -n 5 > nul

REM 启动前端服务（强制定位到frontend子目录）
start "ruoyi-fastapi-frontend" cmd /k "cd /d %ROOT_DIR%ruoyi-fastapi-frontend && npm run dev"
