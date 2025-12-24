# Docker 国内镜像源配置指南

## 问题
在中国大陆访问 Docker Hub (docker.io) 经常会遇到网络连接问题。

## 解决方案

### 方法 1: 配置 Docker Desktop (推荐)

1. 打开 Docker Desktop
2. 点击右上角的 **设置图标** (齿轮)
3. 选择 **Docker Engine**
4. 在 JSON 配置中添加或修改 `registry-mirrors`:

```json
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.nju.edu.cn",
    "https://dockerproxy.com"
  ]
}
```

5. 点击 **Apply & Restart** 重启 Docker

### 方法 2: 手动编辑配置文件

#### Windows (Docker Desktop)
编辑文件: `C:\Users\你的用户名\.docker\daemon.json`

如果文件不存在，创建它并添加以下内容:
```json
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.nju.edu.cn",
    "https://dockerproxy.com"
  ]
}
```

然后重启 Docker Desktop。

#### Linux
编辑文件: `/etc/docker/daemon.json`

```bash
sudo nano /etc/docker/daemon.json
```

添加相同的配置，然后重启:
```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

### 方法 3: 使用国内替代镜像 (临时方案)

如果你不想修改 Docker 配置，可以直接使用国内镜像仓库的镜像:

#### GPU 版本 (使用 DaoCloud 镜像)
修改 `Dockerfile` 第一行:
```dockerfile
FROM docker.m.daocloud.io/nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04
```

#### CPU 版本
修改 `Dockerfile.cpu` 第一行:
```dockerfile
FROM docker.m.daocloud.io/library/python:3.11-slim
```

### 可用的国内镜像源

1. **DaoCloud** (推荐)
   - `https://docker.m.daocloud.io`

2. **南京大学**
   - `https://docker.nju.edu.cn`

3. **Docker Proxy**
   - `https://dockerproxy.com`

4. **阿里云** (需要注册)
   - `https://[你的ID].mirror.aliyuncs.com`
   - 获取地址: https://cr.console.aliyun.com/cn-hangzhou/instances/mirrors

### 验证配置

配置完成后，验证是否生效:

```powershell
docker info | Select-String "Registry Mirrors"
```

应该能看到你配置的镜像源。

### 构建镜像

配置完成后，重新构建:

```powershell
# GPU 版本
cd inpaint
docker build -t inpaint-service:latest .

# 或 CPU 版本
docker build -f Dockerfile.cpu -t inpaint-service:cpu .
```

## 其他注意事项

### NVIDIA 镜像
NVIDIA 的 CUDA 镜像在国内访问也可能较慢。如果配置镜像源后仍然很慢，可以考虑:

1. 使用预先下载好的基础镜像
2. 使用国内的 GPU 云服务 (如阿里云、腾讯云的 GPU 实例)
3. 使用 CPU 版本进行开发测试

### 已配置的优化

Dockerfile 中已经配置了:
- ✅ Ubuntu/Debian APT 源 → 阿里云
- ✅ Python pip 源 → 清华大学镜像

这样可以加速系统包和 Python 包的下载。

## 推荐流程

1. **首先**: 配置 Docker Desktop 的 registry-mirrors
2. **重启**: Docker Desktop
3. **验证**: `docker info` 查看配置
4. **构建**: `docker build -t inpaint-service:latest .`

如果还是无法连接，尝试方法 3 直接修改 Dockerfile 使用国内镜像。
