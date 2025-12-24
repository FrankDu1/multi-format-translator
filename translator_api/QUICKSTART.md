# 🚀 快速开始 - 配置参考

## 最简单的启动方式

```powershell
# 使用默认配置，端口 29003
python app.py
```

访问: http://localhost:29003

**💡 说明**: 默认不需要 `.env` 文件，使用 `config.py` 中的默认值

---

## .env 文件说明

### 本地运行时
- ✅ **不需要 .env 文件** - 使用 `config.py` 默认值（推荐快速测试）
- ✅ **可选 .env 文件** - 如需频繁修改配置可创建（需安装 python-dotenv）
- ✅ **环境变量优先** - 手动设置的环境变量优先级最高

### Docker 运行时
- ✅ **推荐使用 .env 文件** - Docker Compose 自动读取

📖 **详细说明**: 查看 [ENV_FILE_GUIDE.md](ENV_FILE_GUIDE.md)

---

## 常用开发场景

### 1️⃣ 本地开发（快速测试，不需要 Inpaint）

```powershell
# 使用快捷脚本
.\start_dev.ps1

# 或手动设置
$env:USE_INPAINT="false"
python app.py
```

### 2️⃣ 更换端口

```powershell
$env:FLASK_PORT=8080
python app.py
```

### 3️⃣ 连接本地 OCR 服务

```powershell
$env:OCR_SERVICE_URL="http://localhost:29001/ocr"
python app.py
```

### 4️⃣ 关闭调试模式（生产环境）

```powershell
$env:FLASK_DEBUG="false"
python app.py
```

---

## 测试配置

```powershell
# 验证配置是否正确
python test_config.py
```

---

## 配置文件

| 文件 | 说明 |
|------|------|
| `config.py` | 主配置文件（支持环境变量） |
| `.env.example` | 环境变量示例 |
| `CONFIG_GUIDE.md` | 完整配置文档 |
| `start_dev.ps1` | 开发模式启动脚本 |
| `start_prod.ps1` | 生产模式启动脚本 |
| `test_config.py` | 配置测试脚本 |

---

## 核心配置项速查

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `FLASK_PORT` | 29003 | API 端口 |
| `USE_INPAINT` | true | 是否使用 Inpaint |
| `FLASK_DEBUG` | true | 调试模式 |
| `OCR_SERVICE_URL` | http://47.97.97.198:29001/ocr | OCR 服务 |
| `INPAINT_SERVICE_URL` | http://localhost:29002/inpaint | Inpaint 服务 |

---

## 🆘 快速故障排查

### 端口被占用？
```powershell
$env:FLASK_PORT=8080
python app.py
```

### 需要查看当前配置？
访问: http://localhost:29003/api/info

### 测试配置是否生效？
```powershell
python test_config.py
```

---

📖 **需要更多帮助？** 查看 [CONFIG_GUIDE.md](CONFIG_GUIDE.md)
