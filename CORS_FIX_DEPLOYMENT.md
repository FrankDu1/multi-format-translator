# 修复 CORS 和 torch 依赖问题 - 部署指南

## 问题总结

1. **CORS 问题**: 跨域访问被阻止（从 5001 端口访问 5002 端口）
2. **torch 依赖问题**: 云翻译模式下不应该需要 torch，但代码在导入时就尝试加载

## 已修复的文件

### 后端修复（需要重新构建镜像）
1. `translator_api/config.py` - CORS 配置改为允许所有来源（`*`）
2. `translator_api/app.py` - 正确处理 CORS 通配符配置
3. `translator_api/services/nllb_translator_pipeline.py` - 条件导入 torch
4. `translator_api/services/torch_compat.py` - 优雅处理 torch 不存在
5. `translator_api/services/text_translator.py` - 条件导入 torch
6. `translator_api/services/local_translator.py` - 条件导入 torch
7. `translator_api/services/nllb_translator.py` - 条件导入 torch

### 前端修复（已完成）
1. `translator_frontend/index.html` - 修复 API URL 自动检测
2. `translator_frontend/static/js/env-config.js` - 支持 IP/域名/localhost
3. 禁用生产环境的 .env 文件加载

## 重新构建和部署步骤

### 方案 1: 本地构建并推送到 GitHub Container Registry

```bash
# 1. 进入 translator_api 目录
cd translator_api

# 2. 构建新镜像（使用新标签）
docker build -t ghcr.io/frankdu1/translator-api:fix-cors-torch .

# 3. 登录 GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u frankdu1 --password-stdin

# 4. 推送镜像
docker push ghcr.io/frankdu1/translator-api:fix-cors-torch

# 5. 更新 docker-compose.yml，修改镜像标签
# 将 image: ghcr.io/frankdu1/translator-api:main-bf53baa
# 改为 image: ghcr.io/frankdu1/translator-api:fix-cors-torch

# 6. 重新部署
docker-compose down
docker-compose pull
docker-compose up -d
```

### 方案 2: 在服务器上直接构建（推荐）

```bash
# 1. SSH 到服务器
ssh user@40.162.204.61

# 2. 进入项目目录
cd /path/to/multi-format-translator

# 3. 拉取最新代码
git pull origin main

# 4. 构建新镜像（本地标签）
docker build -t translator-api:latest translator_api/

# 5. 修改 docker-compose.yml
# 将 image: ghcr.io/frankdu1/translator-api:main-bf53baa
# 改为 image: translator-api:latest

# 6. 重启服务
docker-compose down
docker-compose up -d
```

### 方案 3: 快速测试（临时方案）

如果只是测试，可以不重新构建，直接在 docker-compose.yml 中覆盖环境变量：

```yaml
api:
  image: ghcr.io/frankdu1/translator-api:main-bf53baa
  environment:
    - ALLOWED_ORIGINS=*
    - USE_CLOUD_TRANSLATE=true
    # ... 其他环境变量
```

但这样不能解决 torch 依赖问题，只能解决 CORS 问题。

## 验证修复

### 1. 检查 CORS 配置
```bash
# 查看日志，确认 CORS 已启用
docker logs translator-api | grep CORS

# 应该看到：
# ✓ CORS 已启用（允许所有来源）
```

### 2. 测试翻译功能
- 访问 `http://40.162.204.61:5001`
- 尝试文本翻译
- 尝试 PDF 翻译
- 检查浏览器控制台是否还有 CORS 错误

### 3. 检查云翻译配置
```bash
# 查看日志，确认云翻译已启用
docker logs translator-api | grep "USE_CLOUD_TRANSLATE"

# 应该看到：
# [启动] USE_CLOUD_TRANSLATE 环境变量: true
# [启动] USE_CLOUD_TRANSLATE 解析结果: True
```

## 可能的问题和解决方案

### 问题 1: 仍然看到 "No module named 'torch'"
**原因**: 仍在使用旧镜像  
**解决**: 确保使用新构建的镜像，执行 `docker-compose down && docker-compose up -d`

### 问题 2: CORS 错误仍然存在
**原因**: Nginx 可能也有 CORS 配置  
**解决**: 检查 nginx 配置，添加 CORS 头：
```nginx
location /translator-api/ {
    add_header 'Access-Control-Allow-Origin' '*' always;
    add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
    add_header 'Access-Control-Allow-Headers' 'Content-Type' always;
    
    if ($request_method = 'OPTIONS') {
        return 204;
    }
    
    # ... 其他配置
}
```

### 问题 3: 翻译失败，显示 "translation failed"
**原因**: 阿里云翻译配置可能不正确  
**解决**: 检查 .env 文件中的阿里云密钥：
```bash
ALI_ACCESS_KEY_ID=your_key_id
ALI_ACCESS_KEY_SECRET=your_key_secret
```

## 生产环境建议

1. **CORS 配置**: 生产环境应该限制 ALLOWED_ORIGINS，而不是使用 `*`
   ```env
   ALLOWED_ORIGINS=https://offerupup.cn,https://www.offerupup.cn
   ```

2. **监控**: 添加日志监控，及时发现错误
   ```bash
   docker logs -f translator-api
   ```

3. **健康检查**: 添加健康检查端点
   ```python
   @app.route('/health')
   def health():
       return jsonify({'status': 'healthy'})
   ```

## 前端环境变量说明

前端会自动检测环境：
- **localhost** → `http://localhost:5002/api`
- **IP 地址** → `http://40.162.204.61:5002/api`
- **域名** → `/translator-api/api`（通过 nginx 代理）

无需手动配置！
