# Security Policy / 安全政策

## Supported Versions / 支持的版本

We release patches for security vulnerabilities for the following versions:

我们为以下版本发布安全漏洞补丁：

| Version / 版本 | Supported / 支持 |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability / 报告漏洞

If you discover a security vulnerability, please follow these steps:

如果你发现安全漏洞，请遵循以下步骤：

### 1. Do Not Disclose Publicly / 不要公开披露
Please **do not** create a public GitHub issue for security vulnerabilities.

请**不要**为安全漏洞创建公开的 GitHub Issue。

### 2. Email Us / 发送邮件
Send an email to: **offerupup@offerupup.cn**

发送邮件至：**offerupup@offerupup.cn**

Include the following information / 请包含以下信息：

- Type of vulnerability / 漏洞类型
- Full paths of source file(s) related to the vulnerability / 与漏洞相关的源文件完整路径
- Location of the affected code (tag/branch/commit) / 受影响代码的位置（标签/分支/提交）
- Step-by-step instructions to reproduce the issue / 重现问题的分步说明
- Proof-of-concept or exploit code (if possible) / 概念验证或利用代码（如果可能）
- Impact of the vulnerability / 漏洞的影响

### 3. Response Timeline / 响应时间

- **Within 48 hours**: We will acknowledge receipt of your vulnerability report
- **Within 7 days**: We will provide a more detailed response indicating next steps
- **Within 30 days**: We will work to release a fix

- **48 小时内**：我们将确认收到你的漏洞报告
- **7 天内**：我们将提供更详细的响应，说明后续步骤
- **30 天内**：我们将努力发布修复程序

### 4. Disclosure Policy / 披露政策

- Please give us reasonable time to address the vulnerability before public disclosure
- We will credit you in the security advisory (unless you prefer to remain anonymous)

- 请在公开披露之前给我们合理的时间来解决漏洞
- 我们会在安全公告中注明你的贡献（除非你希望保持匿名）

## Security Best Practices / 安全最佳实践

When using this project, please follow these security recommendations:

使用本项目时，请遵循以下安全建议：

### For Developers / 开发者

- Always use environment variables for sensitive information (API keys, passwords)
- Never commit `.env` files with real credentials
- Keep dependencies up to date
- Use HTTPS in production environments
- Implement proper input validation and sanitization

- 始终使用环境变量存储敏感信息（API 密钥、密码）
- 永远不要提交包含真实凭据的 `.env` 文件
- 保持依赖项最新
- 在生产环境中使用 HTTPS
- 实施适当的输入验证和清理

### For Users / 用户

- Keep your installation up to date
- Use strong passwords for monitoring dashboard
- Regularly review access logs
- Deploy behind a firewall when possible

- 保持安装最新
- 为监控面板使用强密码
- 定期审查访问日志
- 尽可能部署在防火墙后面

## Known Security Considerations / 已知安全考虑

### File Upload / 文件上传
- Maximum file size is enforced (`MAX_FILE_SIZE` in config)
- Supported file types are validated
- Uploaded files are stored temporarily and cleaned up

- 强制执行最大文件大小（配置中的 `MAX_FILE_SIZE`）
- 验证支持的文件类型
- 上传的文件临时存储并清理

### API Authentication / API 认证
- Monitoring dashboard requires password authentication
- Consider implementing rate limiting for public deployments

- 监控面板需要密码认证
- 考虑为公开部署实施速率限制

## Security Updates / 安全更新

Security updates will be released as:
- Patch versions (e.g., 1.0.1) for minor vulnerabilities
- Minor versions (e.g., 1.1.0) for moderate vulnerabilities
- Major versions (e.g., 2.0.0) for critical vulnerabilities requiring breaking changes

安全更新将作为以下版本发布：
- 补丁版本（例如 1.0.1）用于轻微漏洞
- 次要版本（例如 1.1.0）用于中等漏洞
- 主要版本（例如 2.0.0）用于需要破坏性更改的严重漏洞

---

**Thank you for helping keep our project and users safe!**

**感谢你帮助保护我们的项目和用户的安全！**
