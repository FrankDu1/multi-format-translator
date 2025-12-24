@echo off
chcp 65001 >nul
cls
echo =========================================
echo   停止所有翻译服务
echo =========================================
echo.

echo 正在停止所有服务...
echo.

taskkill /FI "WINDOWTITLE eq OCR服务*" /F >nul 2>&1
if %ERRORLEVEL% EQU 0 (echo ✅ OCR服务已停止) else (echo ⚠️  OCR服务未运行)

taskkill /FI "WINDOWTITLE eq Inpaint服务*" /F >nul 2>&1
if %ERRORLEVEL% EQU 0 (echo ✅ Inpaint服务已停止) else (echo ⚠️  Inpaint服务未运行)

taskkill /FI "WINDOWTITLE eq API服务*" /F >nul 2>&1
if %ERRORLEVEL% EQU 0 (echo ✅ API服务已停止) else (echo ⚠️  API服务未运行)

taskkill /FI "WINDOWTITLE eq 前端服务*" /F >nul 2>&1
if %ERRORLEVEL% EQU 0 (echo ✅ 前端服务已停止) else (echo ⚠️  前端服务未运行)

echo.
echo =========================================
echo ✅ 操作完成！
echo =========================================
echo.
pause