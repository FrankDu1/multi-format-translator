# 贡献指南 / Contributing Guide

感谢您对本项目感兴趣！我们欢迎各种形式的贡献。

Thank you for your interest in this project! We welcome all forms of contributions.

## 如何贡献 / How to Contribute

### 报告 Bug / Report Bugs

如果您发现了 Bug，请：
1. 检查 [Issues](https://github.com/FrankDu1/multi-format-translator/issues) 确认问题尚未被报告
2. 创建新 Issue，提供以下信息：
   - 问题描述
   - 复现步骤
   - 期望行为
   - 实际行为
   - 运行环境（OS、Python版本等）
   - 相关日志或截图

### 建议新功能 / Suggest Features

如果您有新功能建议：
1. 在 Issues 中描述您的想法
2. 说明为什么这个功能有用
3. 如果可能，提供实现思路

### 提交代码 / Submit Code

1. **Fork 项目**
   ```bash
   git clone https://github.com/FrankDu1/multi-format-translator.git
   cd multi-format-translator
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/bug-description
   ```

3. **进行开发**
   - 遵循现有代码风格
   - 添加必要的注释
   - 更新相关文档
   - 如果可能，添加测试

4. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   # 或
   git commit -m "fix: 修复Bug描述"
   ```

5. **推送到 GitHub**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **创建 Pull Request**
   - 在 GitHub 上创建 PR
   - 清晰描述您的更改
   - 关联相关 Issue

## 代码规范 / Code Standards

### Python 代码规范

- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 风格指南
- 使用有意义的变量和函数名
- 添加必要的文档字符串（docstrings）
- 保持函数简洁，单一职责

示例：
```python
def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """
    翻译文本
    
    Args:
        text: 要翻译的文本
        source_lang: 源语言代码
        target_lang: 目标语言代码
        
    Returns:
        翻译后的文本
    """
    # 实现代码
    pass
```

### JavaScript 代码规范

- 使用 ES6+ 语法
- 使用 const/let 替代 var
- 使用有意义的变量和函数名
- 添加必要的注释

示例：
```javascript
/**
 * 翻译文本
 * @param {string} text - 要翻译的文本
 * @param {string} sourceLang - 源语言
 * @param {string} targetLang - 目标语言
 * @returns {Promise<string>} 翻译结果
 */
async function translateText(text, sourceLang, targetLang) {
    // 实现代码
}
```

### 提交信息规范 / Commit Message Convention

使用语义化提交信息：

- `feat:` 新功能
- `fix:` 修复Bug
- `docs:` 文档更新
- `style:` 代码格式调整（不影响功能）
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具相关

示例：
```
feat: 添加德语翻译支持
fix: 修复PDF翻译格式错误
docs: 更新API文档
```

## 测试 / Testing

在提交 PR 前，请确保：

1. **运行现有测试**
   ```bash
   pytest
   ```

2. **添加新测试**（如果添加了新功能）
   ```python
   def test_new_feature():
       # 测试代码
       assert True
   ```

3. **手动测试**
   - 启动所有服务
   - 测试相关功能
   - 检查日志无错误

## 文档 / Documentation

- 更新 README.md（如果添加新功能）
- 更新 API 文档
- 添加代码注释
- 如果需要，创建专门的文档文件

## 代码审查 / Code Review

所有 PR 都需要经过审查：

- 保持耐心，审查需要时间
- 积极响应审查意见
- 根据反馈修改代码
- 保持友好和专业的态度

## 开发环境设置 / Development Setup

### 基本要求

- Python 3.8+
- Git
- 文本编辑器（推荐 VS Code）

### 推荐工具

- **Python 格式化**: `black`, `isort`
- **代码检查**: `pylint`, `flake8`
- **类型检查**: `mypy`

安装开发依赖：
```bash
pip install black isort pylint flake8 mypy pytest
```

格式化代码：
```bash
black .
isort .
```

检查代码：
```bash
pylint translator_api/
flake8 translator_api/
```

## 问题 / Questions

如果您有任何问题：

1. 查看 [文档](README.md)
2. 搜索现有 [Issues](https://github.com/yourusername/translator/issues)
3. 创建新 Issue 询问

## 行为准则 / Code of Conduct

- 尊重所有贡献者
- 建设性地提出意见
- 专注于改进项目
- 保持友好和包容的态度

## 许可 / License

通过贡献代码，您同意您的贡献将按照项目的 MIT 许可证进行许可。

---

再次感谢您的贡献！🎉

Thank you again for your contribution! 🎉
