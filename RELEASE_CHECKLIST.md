# 发布前检查清单 / Pre-release Checklist

在发布到 GitHub 之前，请确认以下事项：

## ✅ 代码清理 / Code Cleanup

- [ ] 删除所有调试代码和 console.log
- [ ] 删除所有注释掉的无用代码
- [ ] 删除所有临时文件和测试文件
- [ ] 确保没有硬编码的敏感信息（API密钥、密码等）
- [ ] 检查是否有遗留的 TODO/FIXME 注释

## ✅ 配置文件 / Configuration Files

- [x] .gitignore 已完善
- [x] .env.example 已创建
- [ ] 所有 .env 文件都在 .gitignore 中
- [ ] 配置文件中没有敏感信息
- [x] manage-services.bat 使用通用路径（%~dp0）

## ✅ 文档 / Documentation

- [x] README.md 已创建并完善
- [x] LICENSE 文件已添加
- [x] CONTRIBUTING.md 已创建
- [ ] API 文档已更新
- [ ] 所有配置选项都有说明
- [ ] 安装步骤清晰明确

## ✅ 依赖管理 / Dependencies

- [ ] 所有 requirements.txt 文件都是最新的
- [ ] 检查是否有未使用的依赖
- [ ] 版本号已固定（避免兼容性问题）
- [ ] 大型模型文件不在仓库中（通过下载脚本获取）

## ✅ 文件整理 / File Organization

- [ ] 删除 logs/ 目录中的所有日志文件
- [ ] 删除 uploads/ 目录中的所有上传文件
- [ ] 删除 __pycache__/ 目录
- [ ] 删除 .pyc 文件
- [ ] 删除临时文件和备份文件

## ✅ 功能测试 / Functional Testing

- [ ] 所有服务能正常启动
- [ ] 文本翻译功能正常
- [ ] 图片翻译功能正常
- [ ] PDF翻译功能正常
- [ ] PPT翻译功能正常
- [ ] 语言切换功能正常
- [ ] 错误处理正常工作

## ✅ Docker 支持 / Docker Support

- [x] docker-compose.yml 已创建
- [ ] 所有服务都有 Dockerfile
- [ ] Docker 镜像能正常构建
- [ ] Docker 容器能正常运行
- [ ] 容器间通信正常

## ✅ 安全检查 / Security Check

- [ ] 没有硬编码的密码或API密钥
- [ ] 没有个人信息（邮箱、真实姓名等）
- [ ] 上传文件有大小限制
- [ ] 文件类型验证完善
- [ ] SQL注入防护（如果使用数据库）
- [ ] XSS防护

## ✅ 性能优化 / Performance Optimization

- [ ] 静态文件已压缩
- [ ] 图片已优化
- [ ] 前端资源有版本号（缓存控制）
- [ ] API 响应时间合理
- [ ] 内存使用合理

## ✅ 兼容性 / Compatibility

- [ ] 测试 Windows 系统
- [ ] 测试 Linux 系统
- [ ] 测试 macOS 系统
- [ ] 测试不同 Python 版本（3.8+）
- [ ] 测试不同浏览器（Chrome, Firefox, Edge）

## ✅ Git 准备 / Git Preparation

- [ ] 确认当前分支是 main 或 master
- [ ] 所有更改已提交
- [ ] 提交信息清晰明确
- [ ] 没有遗留的 merge 冲突标记
- [ ] Git 历史记录干净（考虑 squash 多个小提交）

## ✅ GitHub 设置 / GitHub Setup

- [ ] 仓库名称清晰
- [ ] 仓库描述准确
- [ ] 选择了合适的开源许可证
- [ ] 添加了 topics/tags（如：translation, python, flask）
- [ ] 设置了仓库主页 URL（如果有）

## 📋 执行命令 / Commands to Run

### 1. 清理临时文件
```bash
# Windows
del /s /q __pycache__
del /s /q *.pyc
del /s /q *.log
rmdir /s /q logs
rmdir /s /q translator_api\uploads
rmdir /s /q translator_api\archives

# Linux/Mac
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.log" -delete
rm -rf logs/*
rm -rf translator_api/uploads/*
rm -rf translator_api/archives/*
```

### 2. 创建必要的空目录
```bash
mkdir -p logs
mkdir -p translator_api/uploads
mkdir -p translator_api/archives
echo "# Log files will be stored here" > logs/.gitkeep
echo "# Upload files will be stored here" > translator_api/uploads/.gitkeep
echo "# Archive files will be stored here" > translator_api/archives/.gitkeep
```

### 3. 检查 Git 状态
```bash
git status
git diff
```

### 4. 提交并推送
```bash
git add .
git commit -m "chore: prepare for GitHub release"
git push origin main
```

### 5. 创建 Release
在 GitHub 上：
1. 点击 "Releases" → "Create a new release"
2. 创建新标签（如 v1.0.0）
3. 填写发布说明
4. 上传构建产物（如果有）
5. 发布

## 🎯 最后检查 / Final Check

发布后：
- [ ] 克隆仓库到新目录测试
- [ ] 按照 README 说明安装和运行
- [ ] 确认所有链接正常工作
- [ ] 确认图片和资源正常显示
- [ ] 在 GitHub Issues 中回复已知问题

---

完成所有检查项后，您就可以放心发布到 GitHub 了！🎉
