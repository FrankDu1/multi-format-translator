# AI 总结服务配置指南

## 📋 支持的 AI 提供商

本项目支持多种 AI 服务提供商，通过配置轻松切换：

| 提供商 | 说明 | 成本 | 速度 | 推荐场景 |
|-------|------|------|------|---------|
| **Ollama** | 本地部署 | 免费（需显卡） | 中等 | 隐私敏感、离线使用 |
| **通义千问** | 阿里云 DashScope | 按量付费 | 快 | 生产环境、高并发 |
| **OpenAI** | ChatGPT API | 按量付费 | 快 | 国际用户（需代理） |

---

## 🚀 快速配置

### 方法1：使用通义千问（阿里云）

#### 1. 获取 API Key
- 访问 [阿里云 DashScope](https://dashscope.console.aliyun.com/)
- 注册/登录后创建 API Key

#### 2. 配置环境变量
```bash
# 在 translator_api 目录下创建 .env 文件
cd translator_api
cp .env.example .env

# 编辑 .env 文件
AI_PROVIDER=qwen
QWEN_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx  # 替换为你的 API Key
QWEN_MODEL=qwen-plus                    # 或 qwen-turbo (更便宜)
```

#### 3. 重启服务
```bash
# 停止所有服务
.\manage-services.bat  # 选择 2

# 启动所有服务
.\manage-services.bat  # 选择 1
```

#### 4. 测试
访问 http://localhost:5001，翻译时勾选"AI 总结"，查看效果。

---

### 方法2：使用 Ollama（本地部署）

#### 1. 安装 Ollama
```bash
# Windows/Mac/Linux 安装
https://ollama.com/download

# 拉取模型
ollama pull qwen2.5:7b
```

#### 2. 配置环境变量
```bash
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
```

#### 3. 重启服务（同上）

---

### 方法3：使用 OpenAI（国际）

#### 1. 获取 API Key
- 访问 [OpenAI Platform](https://platform.openai.com/)
- 创建 API Key

#### 2. 配置环境变量
```bash
AI_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-3.5-turbo  # 或 gpt-4
```

#### 3. 配置代理（国内用户）
```bash
# 设置 HTTP 代理
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
```

---

## ⚙️ 完整配置说明

### 通用配置
```bash
# AI 总结最大字数（所有提供商通用）
SUMMARY_MAX_WORDS=200

# 超时时间（秒）
QWEN_TIMEOUT=60
OLLAMA_TIMEOUT=60
OPENAI_TIMEOUT=60

# Temperature（0.0-1.0，越高越随机）
QWEN_TEMPERATURE=0.7
OLLAMA_TEMPERATURE=0.7
OPENAI_TEMPERATURE=0.7
```

### Ollama 专属配置
```bash
OLLAMA_BASE_URL=http://localhost:11434  # Ollama 服务地址
OLLAMA_MODEL=qwen2.5:7b                 # 可选: llama3, mistral 等
```

### 通义千问专属配置
```bash
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-plus      # 或 qwen-turbo (更便宜), qwen-max (更强)
QWEN_API_KEY=sk-xxxxxxx  # 必填
```

### OpenAI 专属配置
```bash
OPENAI_BASE_URL=https://api.openai.com/v1  # 或其他兼容服务
OPENAI_MODEL=gpt-3.5-turbo                 # 或 gpt-4, gpt-4-turbo
OPENAI_API_KEY=sk-xxxxxxx                  # 必填
```

---

## 🔄 切换提供商

### 运行时切换（推荐）
修改 `.env` 文件中的 `AI_PROVIDER`，然后重启服务：
```bash
# 方法1: 修改 .env 文件
AI_PROVIDER=qwen  # 改为 ollama 或 openai

# 方法2: 命令行设置（Windows）
set AI_PROVIDER=qwen
.\manage-services.bat

# 方法3: 命令行设置（Linux/Mac）
export AI_PROVIDER=qwen
./manage-services.sh
```

---

## 💰 成本对比（参考）

### 通义千问（阿里云）
| 模型 | 输入价格 | 输出价格 | 适用场景 |
|------|---------|---------|----------|
| qwen-turbo | ¥0.0008/千tokens | ¥0.002/千tokens | 高频调用 |
| qwen-plus | ¥0.004/千tokens | ¥0.012/千tokens | 平衡性能 |
| qwen-max | ¥0.04/千tokens | ¥0.12/千tokens | 高质量 |

**示例**：翻译 1000 个文档（每个 200 字总结）
- qwen-turbo: ~¥5-10
- qwen-plus: ~¥25-50

### OpenAI
| 模型 | 输入价格 | 输出价格 |
|------|---------|---------|
| gpt-3.5-turbo | $0.0005/千tokens | $0.0015/千tokens |
| gpt-4-turbo | $0.01/千tokens | $0.03/千tokens |

### Ollama
- **免费**（需要本地 GPU/CPU 运行）
- 推荐显存：8GB+ (qwen2.5:7b)

---

## 🐛 常见问题

### 1. 提示"AI总结服务暂时不可用"
**原因**：服务未启动或配置错误

**解决方案**：
```bash
# Ollama 用户
ollama list          # 检查模型是否已下载
ollama serve         # 确保服务运行中

# Qwen 用户
# 检查 API Key 是否正确
curl -X POST https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions \
  -H "Authorization: Bearer $QWEN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen-plus","messages":[{"role":"user","content":"test"}]}'
```

### 2. Ollama 响应慢
**原因**：本地硬件性能限制

**解决方案**：
- 使用更小的模型：`ollama pull qwen2.5:3b`
- 切换到云服务（Qwen/OpenAI）

### 3. 通义千问报错 401
**原因**：API Key 无效或过期

**解决方案**：
- 重新生成 API Key
- 检查 `.env` 文件中 `QWEN_API_KEY` 是否正确

### 4. 切换提供商后无效果
**原因**：未重启服务

**解决方案**：
```bash
.\manage-services.bat  # 选择 3 (重启所有服务)
```

---

## 📊 性能对比

| 指标 | Ollama (本地) | 通义千问 | OpenAI |
|-----|--------------|---------|--------|
| 响应速度 | 5-15秒 | 2-5秒 | 2-5秒 |
| 并发能力 | 1-2 | 100+ | 100+ |
| 质量 | 中上 | 优秀 | 优秀 |
| 隐私性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 成本 | 免费 | 按量 | 按量 |

---

## 🔐 安全建议

### 1. 保护 API Key
```bash
# ❌ 不要提交到 Git
echo ".env" >> .gitignore

# ✅ 使用环境变量
export QWEN_API_KEY=sk-xxxxxxx
```

### 2. 设置请求限制
```python
# config.py 中添加
AI_MAX_REQUESTS_PER_MINUTE = 10
AI_MAX_TEXT_LENGTH = 5000
```

### 3. 监控使用量
- [阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/)
- [OpenAI Usage Dashboard](https://platform.openai.com/usage)

---

## 🎯 推荐配置

### 个人开发者
```bash
AI_PROVIDER=ollama  # 免费，隐私
OLLAMA_MODEL=qwen2.5:7b
```

### 小型企业
```bash
AI_PROVIDER=qwen    # 性价比高
QWEN_MODEL=qwen-turbo
```

### 大型企业/高并发
```bash
AI_PROVIDER=qwen    # 或 openai
QWEN_MODEL=qwen-plus
# 配合 Redis 缓存和负载均衡
```

---

## 📞 技术支持

遇到问题？
1. 查看日志：`translator_api/logs/api.log`
2. 提交 Issue：[GitHub Issues](https://github.com/your-repo/issues)
3. 邮件：offerupup@offerupup.cn
