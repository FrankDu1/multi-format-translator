# PDF翻译器代码说明

## 概述

`pdf_translator.py` 实现了保留原始排版的PDF翻译功能。核心策略是删除原文、保留图片，然后在相同位置插入翻译文本。

## 主要函数

### 1. `translate_pdf_file()` - 主入口函数

完整的PDF翻译流程：

```
提取文本 → 语言检测 → 批量翻译 → 重建PDF → 生成摘要(可选)
```

**参数：**
- `pdf_file_path`: PDF文件路径
- `src_lang`: 源语言（'auto'为自动检测）
- `tgt_lang`: 目标语言（'zh'/'en'/'de'等）
- `enable_summary`: 是否生成AI摘要

**返回：**
- `(翻译后的PDF路径, AI摘要结果)`

---

## 核心辅助函数

### 文本提取阶段

#### `_extract_text_with_positions(doc)`
从PDF提取文本及其精确坐标

**策略：**
1. 使用 `get_text("words")` 获取所有单词
2. 按Y坐标分组（`round(y0, 1)`）识别文本行
3. 每行内按X坐标排序保持阅读顺序
4. 计算每行的边界矩形

**返回：** `(文本列表, 位置信息列表)`

#### `_detect_language(texts)`
基于中英文字符比例自动检测语言

### 翻译阶段

#### `_log_text_preview()` / `_log_translation_preview()`
输出调试信息，显示文本和坐标对应关系

### PDF重建阶段

#### `_rebuild_pdf_with_translation()`
重建PDF的主控函数

**流程：**
1. 创建新PDF文档
2. 遍历每一页：
   - 标记原文区域（redaction）
   - 复制redacted页面（保留图片）
   - 插入翻译文本
3. 保存新PDF

#### `_redact_text_regions()`
在页面上标记文本区域为redaction（白色填充）

**扩展边界：** 左-3, 上-4, 右+20, 下+5（确保完全覆盖）

#### `_copy_redacted_page()`
通过临时文件复制页面

**为什么需要临时文件？**
- `show_pdf_page()` 需要从已保存的文件读取
- 否则会复制redaction前的内容

#### `_get_page_translations()`
收集指定页面的翻译并按Y坐标排序

#### `_calculate_safe_height()`
计算文本框安全高度（避免与下一行重叠）

**策略：**
```
间距 < 15pt  → max_height = max(12, gap - 2)
15pt ≤ 间距 < 25pt → max_height = max(18, gap - 3)
间距 ≥ 25pt  → max_height = min(60, gap - 5)
```

#### `_insert_translations()`
在新页面插入翻译文本

**策略：**
1. 计算动态高度（避免重叠）
2. 根据目标语言选择字体集
3. 尝试插入，失败则渐进式缩放

---

## 字体处理

### `_find_chinese_font()`
查找可用的外部中文字体

**搜索顺序：**
1. fonts目录：NotoSansSC, SourceHanSansSC, simhei, msyh
2. Windows字体目录：msyh, simhei, simsun

### `_get_font_list()`
根据目标语言返回合适的字体列表

- **CJK语言：** `["china-ss", "china-s", "cjk"]`
- **西文语言：** `["helv", "times", "cour"]`

### `_try_insert_text()`
尝试插入文本（支持多字体和渐进式缩放）

**流程：**
1. 原始字号尝试所有字体
2. 失败则缩放：80% → 70% → 60% → 50%
3. 每个缩放级别尝试所有字体

### `_try_fonts()`
遍历字体列表尝试插入

**返回码（rc）：**
- `rc >= 0`: 成功，返回剩余高度
- `rc < 0`: 失败，文本不适合

---

## 关键技术点

### 1. Redaction + show_pdf_page 组合
- `add_redact_annot()`: 标记删除区域
- `apply_redactions()`: 永久删除文本
- `show_pdf_page()`: 复制页面内容（图片、图表）

### 2. 临时文件保存
确保redaction对show_pdf_page可见

```python
doc.save(temp_path)
with fitz.open(temp_path) as redacted_doc:
    new_page.show_pdf_page(new_page.rect, redacted_doc, page_num)
```

### 3. 动态高度计算
根据实际行间距调整文本框高度，避免重叠

### 4. 渐进式字号缩放
5个尝试级别：100% → 80% → 70% → 60% → 50%

### 5. 多语言字体支持
- CJK语言：使用中文字体（china-ss等）
- 西文语言：使用西文字体（helv等，支持ä ö ü ß）

---

## 调试日志

### 重要日志点

1. **文本提取：** 显示前10行文本和坐标
2. **翻译对应：** 显示原文-译文-坐标对应关系
3. **插入详情：** 每行的坐标、高度、字号、字体选择
4. **字号缩放：** 显示缩放比例和成功的字体

### 日志级别

- `info`: 关键流程节点
- `debug`: 字号缩放尝试
- `warning`: 插入失败或异常情况

---

## 使用示例

```python
from services.pdf_translator import translate_pdf_file

# 基本翻译
output_path, _ = translate_pdf_file(
    pdf_file_path='test.pdf',
    src_lang='en',
    tgt_lang='zh'
)

# 带AI摘要的翻译
output_path, summary = translate_pdf_file(
    pdf_file_path='test.pdf',
    src_lang='auto',  # 自动检测
    tgt_lang='zh',
    enable_summary=True
)
```

---

## 已知限制

1. **复杂排版：** 多栏、表格、文本框可能位置不准确
2. **字体覆盖：** 内置字体不支持所有Unicode字符
3. **文本长度：** 翻译后文本过长可能被截断（已通过渐进缩放缓解）

---

## 备用函数

### `translate_pdf_preserve_layout()`
简化版本，创建纯文本PDF，不保留图片

**用途：** 仅供参考，主要使用 `translate_pdf_file()`
