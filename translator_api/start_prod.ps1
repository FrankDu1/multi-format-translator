# Image Translator API - 生产环境启动脚本
# PowerShell 脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Image Translator API - 生产模式" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 生产环境配置
$env:FLASK_PORT = "29003"
$env:FLASK_DEBUG = "false"
$env:USE_INPAINT = "true"
$env:OCR_SERVICE_URL = "http://47.97.97.198:29001/ocr"
$env:INPAINT_SERVICE_URL = "http://localhost:29002/inpaint"

Write-Host "🔧 配置信息:" -ForegroundColor Yellow
Write-Host "  端口: $env:FLASK_PORT"
Write-Host "  调试模式: $env:FLASK_DEBUG"
Write-Host "  Inpaint: $env:USE_INPAINT"
Write-Host "  OCR 服务: $env:OCR_SERVICE_URL"
Write-Host "  Inpaint 服务: $env:INPAINT_SERVICE_URL"
Write-Host ""

Write-Host "⚠️  生产模式 - 请确保所有服务已正常运行" -ForegroundColor Red
Write-Host ""

Write-Host "🚀 启动服务..." -ForegroundColor Green
python app.py
