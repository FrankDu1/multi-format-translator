# Image Translator API - 本地开发启动脚本
# PowerShell 脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Image Translator API - 本地开发模式" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 本地开发环境配置
$env:FLASK_PORT = "29003"
$env:FLASK_DEBUG = "true"
$env:USE_INPAINT = "false"  # 本地开发可以关闭 Inpaint 加速测试
$env:OCR_SERVICE_URL = "http://47.97.97.198:29001/ocr"

Write-Host "🔧 配置信息:" -ForegroundColor Yellow
Write-Host "  端口: $env:FLASK_PORT"
Write-Host "  调试模式: $env:FLASK_DEBUG"
Write-Host "  Inpaint: $env:USE_INPAINT"
Write-Host "  OCR 服务: $env:OCR_SERVICE_URL"
Write-Host ""

Write-Host "🚀 启动服务..." -ForegroundColor Green
python app.py
