@echo off
chcp 65001 >nul
cls
echo =========================================
echo   启动所有翻译服务 (开发模式)
echo =========================================
echo.

cd /d c:\trans_web_app

echo [1/4] 启动 OCR 服务 (端口 29001)...
start "OCR服务" cmd /k "cd ocr && python app.py"
timeout /t 2 >nul

echo [2/4] 启动 Inpaint 服务 (端口 29002)...
start "Inpaint服务" cmd /k "cd inpaint && python app.py"
timeout /t 2 >nul

echo [3/4] 启动 API 服务 (端口 29003)...
start "API服务" cmd /k "cd translator_api && python app.py"
timeout /t 2 >nul

echo [4/4] 启动前端服务 (端口 5001)...
start "前端服务" cmd /k "cd translator_frontend && python -m http.server 5001"
timeout /t 2 >nul

echo.
echo =========================================
echo ✅ 所有服务已在新窗口中启动！
echo =========================================
echo.
echo 📌 服务地址:
echo    OCR服务:    http://localhost:29001
echo    Inpaint服务: http://localhost:29002
echo    API服务:    http://localhost:29003
echo    前端界面:   http://localhost:5001
echo.
echo 💡 提示:
echo    - 每个服务在独立的命令窗口中运行
echo    - 关闭窗口即停止对应服务
echo    - 或运行 stop-all-dev.bat 停止所有服务
echo.
pause