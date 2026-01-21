# 🎨 Ubuntu 服务器中文字体安装指南

## 问题现象
```
⚠️ 系统中未找到中文字体
❌ 字体下载失败: HTTP Error 404: Not Found
⚠️ 没有 sudo 权限，无法自动安装字体
⚠️ 无法加载中文字体，使用默认字体（可能显示乱码）
```

图片翻译后中文显示为乱码或方框。

---

## 🚀 快速解决方案

### 方案 1：一键安装脚本（推荐）

**在服务器上执行：**
```bash
# 1. 赋予执行权限
chmod +x install-fonts.sh

# 2. 运行安装脚本
sudo ./install-fonts.sh

# 3. 重启 Docker 容器
docker-compose restart translator-api
```

---

### 方案 2：手动安装字体

#### Ubuntu/Debian 系统：
```bash
# 更新软件包列表
sudo apt-get update

# 安装中文字体包
sudo apt-get install -y \
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    fonts-wqy-zenhei \
    fonts-wqy-microhei

# 刷新字体缓存
sudo fc-cache -fv

# 验证字体安装
fc-list :lang=zh
```

#### CentOS/RHEL 系统：
```bash
# 安装字体
sudo yum install -y \
    google-noto-sans-cjk-sc-fonts \
    wqy-zenhei-fonts \
    wqy-microhei-fonts

# 刷新字体缓存
sudo fc-cache -fv

# 验证字体安装
fc-list :lang=zh
```

---

### 方案 3：Docker 容器内安装（临时方案）

**进入容器安装：**
```bash
# 1. 进入容器
docker exec -it translator-api bash

# 2. 安装字体
apt-get update
apt-get install -y fonts-noto-cjk fonts-wqy-zenhei
fc-cache -fv

# 3. 退出容器
exit

# 注意：容器重启后需要重新安装！
```

---

### 方案 4：重新构建 Docker 镜像（永久方案）

**Dockerfile 已更新，包含中文字体：**
```bash
# 1. 重新构建镜像
docker-compose build translator-api

# 2. 启动容器
docker-compose up -d translator-api

# 3. 验证字体
docker exec translator-api fc-list :lang=zh
```

---

## 📋 验证字体是否安装成功

### 方法 1：查看系统字体列表
```bash
# 在服务器上
fc-list :lang=zh

# 在 Docker 容器内
docker exec translator-api fc-list :lang=zh
```

**应该看到类似输出：**
```
/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc: Noto Sans CJK SC:style=Regular
/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc: WenQuanYi Zen Hei:style=Regular
/usr/share/fonts/truetype/wqy/wqy-microhei.ttc: WenQuanYi Micro Hei:style=Regular
```

### 方法 2：测试图片翻译
1. 上传一张包含中文的图片
2. 执行翻译
3. 检查翻译后的图片中文是否正常显示

### 方法 3：查看日志
```bash
# 查看 API 日志
docker logs translator-api | grep "字体"

# 应该看到成功信息：
# ✓ 使用字体: /usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc
```

---

## 🔧 代码改进说明

### 1. 修复字体下载 URL
**原 URL（已失效）：**
```
https://github.com/notofonts/noto-cjk/raw/main/...
```

**新 URL（有效）：**
```python
# 主源
https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansSC-Regular.otf

# CDN 备用（国内访问更快）
https://cdn.jsdelivr.net/gh/googlefonts/noto-cjk@main/Sans/OTF/SimplifiedChinese/NotoSansSC-Regular.otf
```

### 2. 增强字体搜索路径
代码已支持以下字体路径（按优先级）：
```python
fonts/NotoSansSC-Regular.otf                           # 本地字体目录
/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc # Ubuntu Noto Sans
/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc          # 文泉驿正黑
/usr/share/fonts/truetype/wqy/wqy-microhei.ttc        # 文泉驿微米黑
C:/Windows/Fonts/msyh.ttc                               # Windows 微软雅黑
/System/Library/Fonts/PingFang.ttc                      # macOS 苹方
```

### 3. Dockerfile 自动安装字体
新的 Dockerfile 会在构建镜像时自动安装中文字体：
```dockerfile
RUN apt-get install -y \
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    fontconfig \
    && fc-cache -fv
```

---

## 📦 推荐字体包

### Noto Sans CJK（推荐）
- **优点：** Google 开源，支持全面，显示效果好
- **大小：** ~130MB
- **包名：** `fonts-noto-cjk`, `fonts-noto-cjk-extra`

### 文泉驿正黑（备用）
- **优点：** 轻量级，国内常用
- **大小：** ~4MB
- **包名：** `fonts-wqy-zenhei`

### 文泉驿微米黑（备用）
- **优点：** 极小体积，适合嵌入式
- **大小：** ~1.8MB
- **包名：** `fonts-wqy-microhei`

---

## ❓ 常见问题

### Q1: 为什么字体下载失败？
**A:** GitHub 原始仓库路径变更导致。已更新为正确路径，并添加 CDN 备用源。

### Q2: 没有 sudo 权限怎么办？
**A:** 
1. 联系服务器管理员安装字体
2. 或使用 Docker 方式重新构建镜像（推荐）

### Q3: 字体安装后仍然乱码？
**A:** 检查以下几点：
1. 确认字体已刷新缓存：`fc-cache -fv`
2. 重启 Docker 容器：`docker-compose restart translator-api`
3. 查看日志确认字体加载：`docker logs translator-api | grep "字体"`

### Q4: 如何选择字体？
**A:** 推荐顺序：
1. **Noto Sans CJK** - 最佳显示效果
2. **WenQuanYi Zen Hei** - 轻量级备选
3. **WenQuanYi Micro Hei** - 极简方案

---

## 🎯 最佳实践

### 生产环境部署：
1. **方案 1（推荐）：** 在宿主机安装字体
   ```bash
   sudo apt-get install fonts-noto-cjk fonts-wqy-zenhei
   docker-compose restart translator-api
   ```

2. **方案 2：** 重新构建包含字体的 Docker 镜像
   ```bash
   docker-compose build translator-api
   docker-compose up -d
   ```

3. **方案 3：** 挂载字体目录到容器
   ```yaml
   # docker-compose.yml
   services:
     translator-api:
       volumes:
         - /usr/share/fonts:/usr/share/fonts:ro
   ```

---

## 📝 更新日志

- **2026-01-14:** 修复字体下载 URL 404 错误
- **2026-01-14:** 添加 jsDelivr CDN 备用源
- **2026-01-14:** Dockerfile 集成字体自动安装
- **2026-01-14:** 创建一键安装脚本

---

## 🔗 相关资源

- [Google Noto Fonts](https://github.com/googlefonts/noto-cjk)
- [文泉驿字体](http://wenq.org/)
- [Ubuntu 字体配置](https://wiki.ubuntu.com/Fonts)
- [Docker 字体支持](https://docs.docker.com/engine/reference/builder/)
