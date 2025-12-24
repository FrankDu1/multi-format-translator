// 全局变量
let currentFileId = null;
let downloadUrl = null;
let currentTab = 'file'; // 当前激活的标签
let currentLanguage = 'zh'; // 当前界面语言
let currentPdfFile = null; // PDF文件相关变量
let pdfDownloadUrl = null;

// DOM元素
const fileInput = document.getElementById('fileInput');
const uploadArea = document.getElementById('uploadArea');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const uploadSection = document.getElementById('uploadSection');
const progressSection = document.getElementById('progressSection');
const resultSection = document.getElementById('resultSection');
const errorSection = document.getElementById('errorSection');
const translateBtn = document.getElementById('translateBtn');
const downloadBtn = document.getElementById('downloadBtn');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const translatedText = document.getElementById('translatedText');
const errorMessage = document.getElementById('errorMessage');

// 文本翻译相关元素
const textInput = document.getElementById('textInput');
const textInputSection = document.getElementById('textInputSection');
const textResultSection = document.getElementById('textResultSection');
const translateTextBtn = document.getElementById('translateTextBtn');
const charCount = document.getElementById('charCount');

// PDF翻译相关元素
const pdfFileInput = document.getElementById('pdfFileInput');
const pdfUploadArea = document.getElementById('pdfUploadArea');
const pdfFileInfo = document.getElementById('pdfFileInfo');
const pdfFileName = document.getElementById('pdfFileName');
const pdfFormatSection = document.getElementById('pdfFormatSection');
const pdfTranslateBtn = document.getElementById('pdfTranslateBtn');
const pdfPreviewContainer = document.getElementById('pdfPreviewContainer');
const downloadPdfBtn = document.getElementById('downloadPdfBtn');
const pdfFrame = document.getElementById('pdfFrame');

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeLanguage();
    setupEventListeners();
    checkSystemStatus();
});

// 设置事件监听器
function setupEventListeners() {
    // ✅ 安全检查：只对存在的元素添加监听器
    
    // 文件选择（如果存在）
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }
    
    // 拖拽功能（如果存在）
    if (uploadArea) {
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('dragleave', handleDragLeave);
        uploadArea.addEventListener('drop', handleDrop);
        uploadArea.addEventListener('click', () => {
            if (!currentFileId && fileInput) {
                fileInput.click();
            }
        });
    }
    
    // 下载按钮（如果存在）
    if (downloadBtn) {
        downloadBtn.addEventListener('click', handleDownload);
    }
    
    // PDF文件选择和事件
    if (pdfFileInput) {
        pdfFileInput.addEventListener('change', handlePdfFileSelect);
    }
    //if (pdfUploadArea) {
    //    pdfUploadArea.addEventListener('click', () => {
    //        if (!currentPdfFile && pdfFileInput) {
    //            pdfFileInput.click();
    //        }
    //    });
    //}
    if (downloadPdfBtn) {
        downloadPdfBtn.addEventListener('click', handlePdfDownload);
    }
    
    // 语言选择器事件
    const sourceLanguage = document.getElementById('sourceLanguage');
    const targetLanguage = document.getElementById('targetLanguage');
    
    if (sourceLanguage && targetLanguage) {
        sourceLanguage.addEventListener('change', function() {
            // 当源语言改变时，自动调整目标语言
            if (this.value === '中文') {
                targetLanguage.value = '英文';
            } else if (this.value === '英文') {
                targetLanguage.value = '中文';
            }
        });
    }
    
    // ✅ 文本输入相关事件
    if (textInput) {
        textInput.addEventListener('input', handleTextInput);
        console.log('✅ 文本输入监听器已绑定');
    } else {
        console.warn('⚠️ textInput 元素不存在');
    }
    
    // ✅ 翻译按钮点击事件
    if (translateTextBtn) {
        translateTextBtn.addEventListener('click', translateText);
        console.log('✅ 翻译按钮监听器已绑定');
    } else {
        console.warn('⚠️ translateTextBtn 元素不存在');
    }
}

// 处理文件选择
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        processFile(file);
    }
}

// 处理拖拽悬停
function handleDragOver(event) {
    event.preventDefault();
    uploadArea.classList.add('dragover');
}

// 处理拖拽离开
function handleDragLeave(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
}

// 处理文件拖拽放置
function handleDrop(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        processFile(files[0]);
    }
}

// 处理文件
function processFile(file) {
    // 检查文件类型
    const allowedTypes = ['text/plain', 'application/pdf', 
                         'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                         'application/msword'];
    const allowedExtensions = ['.txt', '.pdf', '.docx', '.doc'];
    
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
        showError(t('error_file_type'));
        return;
    }
    
    // 检查文件大小 (16MB)
    if (file.size > 16 * 1024 * 1024) {
        showError(t('error_file_size'));
        return;
    }
    
    // 显示文件信息并直接开始上传翻译
    fileName.textContent = file.name;
    fileInfo.style.display = 'block';
    uploadArea.style.display = 'none';
    
    // 显示准备翻译状态
    translateBtn.disabled = true;
    translateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 准备翻译...';
    
    // 直接开始上传和翻译
    uploadFile(file);
}

// 上传文件并开始翻译（一体化接口）
async function uploadFile(file) {
    try {
        // 获取用户选择的语言
        const sourceLanguage = document.getElementById('sourceLanguage').value;
        const targetLanguage = document.getElementById('targetLanguage').value;
        
        // 隐藏上传区域，显示进度界面
        uploadSection.style.display = 'none';
        progressSection.style.display = 'block';
        resultSection.style.display = 'none';
        errorSection.style.display = 'none';
        
        // 开始进度动画
        animateProgress();
        
        const formData = new FormData();
        formData.append('file', file);
        
        // 添加语言选择参数
        if (sourceLanguage !== 'auto') {
            formData.append('source_language', sourceLanguage);
        }
        formData.append('target_language', targetLanguage);
        
        const response = await fetch(`${ENV_CONFIG.getApiUrl()}/upload`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        // 清除进度动画
        if (window.progressInterval) {
            clearInterval(window.progressInterval);
            window.progressInterval = null;
        }
        
        if (result.success) {
            // 翻译成功，直接显示结果
            downloadUrl = result.download_url;
            
            // 获取翻译结果预览
            try {
                const dlResponse = await fetch(downloadUrl);
                if (dlResponse.ok) {
                    const translatedContent = await dlResponse.text();
                    translatedText.textContent = translatedContent.substring(0, 500) + (translatedContent.length > 500 ? '...' : '');
                } else {
                    translatedText.textContent = '翻译完成，点击下载查看完整结果';
                }
            } catch (e) {
                translatedText.textContent = '翻译完成，点击下载查看完整结果';
            }
            
            // 显示结果界面
            progressSection.style.display = 'none';
            resultSection.style.display = 'block';
            resultSection.classList.add('fade-in');
            
            // 显示详细信息
            const detailInfo = `翻译完成！
处理时间：${result.processing_time || '未知'}
检测语言：${result.detected_language || '未知'} (置信度：${result.language_confidence || '未知'})
翻译方向：${result.translation_direction || '中文 → 英文'}
原文长度：${result.original_length || 0} 字符
译文长度：${result.translated_length || 0} 字符`;
            
            showNotification(detailInfo, 'success');
        } else {
            throw new Error(result.error || '上传和翻译失败');
        }
    } catch (error) {
        // 清除进度动画
        if (window.progressInterval) {
            clearInterval(window.progressInterval);
            window.progressInterval = null;
        }
        
        progressSection.style.display = 'none';
        showError('上传和翻译失败: ' + error.message);
    }
}

// 进度动画
function animateProgress() {
    let progress = 0;
    const steps = [
        t('uploading'),
        t('parsing'),
        t('connecting'),
        t('translating_doc'),
        t('generating')
    ];
    
    const interval = setInterval(() => {
        progress += Math.random() * 15 + 5;
        if (progress > 95) progress = 95;
        
        progressFill.style.width = progress + '%';
        
        const stepIndex = Math.floor((progress / 100) * steps.length);
        if (stepIndex < steps.length) {
            progressText.textContent = steps[stepIndex];
        }
    }, 500);
    
    // 清理定时器的引用，以便在翻译完成时清除
    window.progressInterval = interval;
}

// 处理下载
function handleDownload() {
    if (downloadUrl) {
        window.open(downloadUrl, '_blank');
    }
}

// 清除文件选择
function clearFile() {
    resetFileSelection();
    resetApp();
}

// 重置文件选择
function resetFileSelection() {
    // ✅ 修复：添加安全检查，避免操作不存在的元素
    if (fileInput) fileInput.value = '';
    currentFileId = null;
    if (fileInfo) fileInfo.style.display = 'none';
    if (uploadArea) uploadArea.style.display = 'block';
}

// 重置应用状态
function resetApp() {
    // 清除进度定时器
    if (window.progressInterval) {
        clearInterval(window.progressInterval);
        window.progressInterval = null;
    }
    
    // 重置UI状态
    resetFileSelection();
    if (uploadSection) uploadSection.style.display = 'block';
    if (progressSection) progressSection.style.display = 'none';
    if (resultSection) resultSection.style.display = 'none';
    if (errorSection) errorSection.style.display = 'none';
    
    // 重置进度
    if (progressFill) progressFill.style.width = '0%';
    if (progressText) progressText.textContent = '正在处理文档...';
    
    // 清除数据
    downloadUrl = null;
    if (translatedText) translatedText.textContent = '';
}

// 显示错误
function showError(message) {
    if (errorMessage) errorMessage.textContent = message;
    
    // ✅ 修复：添加安全检查
    if (uploadSection) uploadSection.style.display = 'none';
    if (progressSection) progressSection.style.display = 'none';
    if (resultSection) resultSection.style.display = 'none';
    if (errorSection) {
        errorSection.style.display = 'block';
        errorSection.classList.add('fade-in');
    }
    
    // 清除进度定时器
    if (window.progressInterval) {
        clearInterval(window.progressInterval);
        window.progressInterval = null;
    }
}

// 显示通知（支持多语言）
function showNotification(message, type = 'info') {
    // 如果message是一个key，尝试翻译
    const translatedMessage = i18nResources[currentLanguage]?.[message] || message;
    
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check' : type === 'error' ? 'fa-exclamation' : 'fa-info'}"></i>
        <span>${translatedMessage}</span>
    `;
    
    // 添加样式
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#d4edda' : type === 'error' ? '#f8d7da' : '#d1ecf1'};
        color: ${type === 'success' ? '#155724' : type === 'error' ? '#721c24' : '#0c5460'};
        border: 1px solid ${type === 'success' ? '#c3e6cb' : type === 'error' ? '#f5c6cb' : '#bee5eb'};
        border-radius: 8px;
        padding: 12px 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1000;
        display: flex;
        align-items: center;
        gap: 10px;
        max-width: 300px;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    // 3秒后自动移除
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// 安全的系统状态检查
async function checkSystemStatus() {
    const statusIndicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    const statusIcon = document.getElementById('statusIcon');
    
    // 如果元素不存在，直接返回（因为我们已经移除了状态显示）
    if (!statusIndicator || !statusText || !statusIcon) {
        console.log('状态指示器已移除，跳过检查');
        return;
    }
    
    try {
        // 检查后端API状态
        const response = await fetch('/api/health', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            statusText.textContent = '系统运行正常';
            statusIcon.classList.add('online');
            statusIcon.classList.remove('offline');
        } else {
            throw new Error('服务异常');
        }
    } catch (error) {
        console.warn('系统状态检查失败:', error);
        if (statusText) statusText.textContent = '服务连接异常';
        if (statusIcon) {
            statusIcon.classList.add('offline');
            statusIcon.classList.remove('online');
        }
    }
}

// 添加CSS动画样式
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// 定期检查系统状态
setInterval(checkSystemStatus, 30000); // 每30秒检查一次

// ===== 新增功能：标签切换 =====

// 切换标签
function switchTab(tabName) {
    currentTab = tabName;
    
    // 更新标签按钮状态（添加安全检查）
    const fileTab = document.getElementById('fileTab');
    const textTab = document.getElementById('textTab');
    const pdfTab = document.getElementById('pdfTab');
    
    if (fileTab) fileTab.classList.toggle('active', tabName === 'file');
    if (textTab) textTab.classList.toggle('active', tabName === 'text');
    if (pdfTab) pdfTab.classList.toggle('active', tabName === 'pdf');
    
    // 显示/隐藏对应区域
    if (uploadSection) uploadSection.style.display = tabName === 'file' ? 'block' : 'none';
    if (textInputSection) textInputSection.style.display = tabName === 'text' ? 'block' : 'none';
    if (pdfFormatSection) pdfFormatSection.style.display = tabName === 'pdf' ? 'block' : 'none';
    
    // 隐藏结果区域
    resultSection.style.display = 'none';
    textResultSection.style.display = 'none';
    progressSection.style.display = 'none';
    errorSection.style.display = 'none';
    if (pdfPreviewContainer) {
        pdfPreviewContainer.style.display = 'none';
    }
    
    // 重置状态
    if (tabName === 'file') {
        resetApp();
    } else if (tabName === 'text') {
        resetTextTranslation();
    } else if (tabName === 'pdf') {
        resetPdfTranslation();
    }
}

// ===== 新增功能：文本翻译 =====

// 处理文本输入
function handleTextInput() {
    const text = textInput.value;
    const count = text.length;
    
    // 更新字符计数
    if (charCount) {
        charCount.textContent = count;
    }
    
    // 启用/禁用翻译按钮
    if (translateTextBtn) {
        translateTextBtn.disabled = count < 1;
        
        if (count >= 1) {
            translateTextBtn.innerHTML = '<i class="fas fa-language"></i> 开始翻译';
        } else {
            translateTextBtn.innerHTML = '<i class="fas fa-language"></i> 开始翻译';
        }
    }
}

// 翻译文本
async function translateText() {
    const text = textInput.value.trim();
    
    if (!text) {
        showError(t('error_no_text'));
        return;
    }
    
    try {
        // 隐藏之前的总结
        hideAISummary();
        
        const sourceLanguage = document.getElementById('sourceLanguage').value;
        const targetLanguage = document.getElementById('targetLanguage').value;
        
        // 获取AI总结开关状态
        const aiSummarySwitch = document.getElementById('aiSummarySwitch');
        const enableSummary = aiSummarySwitch ? aiSummarySwitch.checked : false;
        
        const langMap = {
            '中文': 'zh',
            '英文': 'en',
            'auto': 'auto',
            'zh': 'zh',
            'en': 'en'
        };
        
        const srcLangCode = langMap[sourceLanguage] || sourceLanguage || 'auto';
        const tgtLangCode = langMap[targetLanguage] || targetLanguage || 'zh';
        
        console.log('🌐 语言映射:', {
            原始: { source: sourceLanguage, target: targetLanguage },
            转换后: { source: srcLangCode, target: tgtLangCode },
            AI总结: enableSummary ? '✓ 启用' : '✗ 禁用'
        });
        
        translateTextBtn.disabled = true;
        translateTextBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 翻译中...';
        
        progressSection.style.display = 'block';
        textResultSection.style.display = 'none';
        errorSection.style.display = 'none';
        
        animateProgress();
        
        const requestData = {
            text: text,
            target_lang: tgtLangCode,
            enable_summary: enableSummary
        };
        
        if (srcLangCode !== 'auto') {
            requestData.source_lang = srcLangCode;
        }
        
        console.log('📤 发送文本翻译请求:', requestData);
        
        const response = await fetch(`${ENV_CONFIG.getApiUrl()}/translate/translate-text`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });
        
        const result = await response.json();
        console.log('📥 收到翻译结果:', result);
        
        if (window.progressInterval) {
            clearInterval(window.progressInterval);
            window.progressInterval = null;
        }
        
        if (result.success) {
            progressSection.style.display = 'none';
            
            // 显示翻译结果 (原有逻辑不变)
            const translatedTextDisplay = document.getElementById('translatedTextDisplay');
            if (translatedTextDisplay) {
                translatedTextDisplay.textContent = result.translated_text;
            }
            
            textResultSection.style.display = 'block';
            
            // 🔥 显示AI总结 (通用函数)
            if (result.summary) {
                displayAISummary(result.summary);
            }
            
            showNotification('翻译完成！', 'success');
        } else {
            throw new Error(result.error || '翻译失败');
        }
    } catch (error) {
        if (window.progressInterval) {
            clearInterval(window.progressInterval);
            window.progressInterval = null;
        }
        
        progressSection.style.display = 'none';
        hideAISummary();
        showError('翻译失败: ' + error.message);
        
        translateTextBtn.disabled = false;
        translateTextBtn.innerHTML = '<i class="fas fa-language"></i> 开始翻译';
    }
}

// 显示文本翻译结果
function displayTextResult(result) {
    // ✅ 不要隐藏输入区域
    // textInputSection.style.display = 'none';  // ❌ 删除这行
    
    // ✅ 只显示结果区域
    progressSection.style.display = 'none';
    textResultSection.style.display = 'block';
    textResultSection.classList.add('fade-in');
    
    // 填充原文
    const originalTextDisplay = document.getElementById('originalTextDisplay');
    if (originalTextDisplay) {
        originalTextDisplay.textContent = result.original_text || '';
    }
    
    // 填充译文
    const translatedTextDisplay = document.getElementById('translatedTextDisplay');
    if (translatedTextDisplay) {
        translatedTextDisplay.textContent = result.translated_text || '';
    }
    
    // ✅ 安全地显示详细信息
    const originalInfo = document.getElementById('originalInfo');
    if (originalInfo) {
        const originalLength = result.original_text?.length || 0;
        const sourceLang = result.source_lang || 'auto';
        originalInfo.textContent = `${originalLength} 字符 | ${sourceLang}`;
    }
    
    const translatedInfo = document.getElementById('translatedInfo');
    if (translatedInfo) {
        const translatedLength = result.translated_text?.length || 0;
        const targetLang = result.target_lang || '未知';
        const processingTime = result.processing_time || '未知';
        translatedInfo.textContent = `${translatedLength} 字符 | ${targetLang} | ${processingTime}`;
    }
    
    // 启用重新翻译按钮
    if (translateTextBtn) {
        translateTextBtn.disabled = false;
        translateTextBtn.innerHTML = '<i class="fas fa-language"></i> 开始翻译';
    }
}

// 清空文本输入
function clearTextInput() {
    textInput.value = '';
    handleTextInput();
    textResultSection.style.display = 'none';
}

// 重置文本翻译
function resetTextTranslation() {
    clearTextInput();
    textInputSection.style.display = 'block';
    textResultSection.style.display = 'none';
    progressSection.style.display = 'none';
    errorSection.style.display = 'none';
    
    // 重置按钮状态
    if (translateTextBtn) {
        translateTextBtn.disabled = true;
        translateTextBtn.innerHTML = '<i class="fas fa-language"></i> 开始翻译';
    }
}

// 复制翻译结果到剪贴板
async function copyToClipboard() {
    const translatedTextElement = document.getElementById('translatedTextDisplay');
    const text = translatedTextElement.textContent;
    
    try {
        await navigator.clipboard.writeText(text);
        showNotification(t('copy_success'), 'success');
    } catch (err) {
        // 兼容性处理
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            showNotification(t('copy_success'), 'success');
        } catch (e) {
            showNotification('Copy failed, please copy manually', 'error');
        }
        
        document.body.removeChild(textArea);
    }
}

// 下载文本翻译结果
function downloadTextResult() {
    //const originalText = document.getElementById('originalTextDisplay').textContent;
    const translatedText = document.getElementById('translatedTextDisplay').textContent;
    
    //const content = `原文：\n${originalText}\n\n译文：\n${translatedText}`;
    const content = `译文：\n${translatedText}`;
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `trans_result_${new Date().toLocaleString().replace(/[:/]/g, '-')}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    URL.revokeObjectURL(url);
    showNotification(t('download_success'), 'success');
}

// ===== 多语言功能 =====

// 初始化语言功能
function initializeLanguage() {
    // 从localStorage读取用户的语言偏好
    const savedLanguage = localStorage.getItem('preferred-language') || 'zh';
    currentLanguage = savedLanguage;
    
    // 应用语言设置
    applyLanguage(currentLanguage);
    
    // 更新语言按钮状态
    updateLanguageButtons();
}

// 切换语言
function switchLanguage(language) {
    if (language === currentLanguage) return;
    
    currentLanguage = language;
    
    // 保存用户偏好
    localStorage.setItem('preferred-language', language);
    
    // 应用新语言
    applyLanguage(language);
    
    // 更新按钮状态
    updateLanguageButtons();
    
    // 显示切换成功通知
    const message = language === 'zh' ? '已切换到中文' : 'Switched to English';
    showNotification(message, 'success');
}

// 应用语言设置
function applyLanguage(language) {
    const translations = i18nResources[language];
    if (!translations) return;
    
    // 更新HTML lang属性
    document.documentElement.lang = language === 'zh' ? 'zh-CN' : 'en';
    
    // 更新页面标题
    document.title = translations.title;
    
    // 更新所有带有data-i18n属性的元素
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[key]) {
            element.textContent = translations[key];
        }
    });
    
    // 更新placeholder文本
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        const key = element.getAttribute('data-i18n-placeholder');
        if (translations[key]) {
            element.placeholder = translations[key];
        }
    });
    
    // 更新字符计数显示
    updateCharCountDisplay();
}

// 更新语言按钮状态
function updateLanguageButtons() {
    const zhBtn = document.getElementById('langZh');
    const enBtn = document.getElementById('langEn');
    
    if (zhBtn && enBtn) {
        zhBtn.classList.toggle('active', currentLanguage === 'zh');
        enBtn.classList.toggle('active', currentLanguage === 'en');
    }
}

// 更新字符计数显示
function updateCharCountDisplay() {
    const charCount = document.getElementById('charCount');
    const charCountParent = charCount?.parentElement;
    
    if (charCountParent && charCount) {
        const count = charCount.textContent;
        const translations = i18nResources[currentLanguage];
        charCountParent.innerHTML = translations.char_count + `<span id="charCount">${count}</span>`;
    }
}

// 获取当前语言的翻译文本
function t(key) {
    return i18nResources[currentLanguage]?.[key] || key;
}

// 更新动态内容的多语言支持
function updateDynamicContent() {
    // 更新进度文本
    const progressText = document.getElementById('progressText');
    if (progressText && progressText.textContent.includes('正在处理') || progressText.textContent.includes('Processing')) {
        progressText.textContent = t('processing');
    }
    
    // 更新状态文本
    const statusText = document.getElementById('statusText');
    if (statusText && (statusText.textContent.includes('检查系统') || statusText.textContent.includes('Checking'))) {
        statusText.textContent = t('checking_status');
    }
}

// ===== PDF格式翻译功能 =====

// 处理PDF文件选择
function handlePdfFileSelect(event) {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
        processPdfFile(file);
    } else {
        showError(t('error_file_type'));
    }
}

// 处理PDF文件
function processPdfFile(file) {
    currentPdfFile = file;
    
    // 显示文件信息
    if (pdfFileName) {
        pdfFileName.textContent = file.name;
    }
    if (pdfFileInfo) {
        pdfFileInfo.style.display = 'block';
    }
    if (pdfUploadArea) {
        pdfUploadArea.style.display = 'none';
    }
    
    // 启用翻译按钮
    if (pdfTranslateBtn) {
        pdfTranslateBtn.disabled = false;
        pdfTranslateBtn.innerHTML = `<i class="fas fa-language"></i> ${t('start_translate')}`;
    }
}

// 翻译PDF文件（修复 API URL）
// async function translatePdfFile() {
//     if (!currentPdfFile) {
//         showError('没有选择PDF文件');
//         return;
//     }
    
//     try {
//         // ✅ 修复：隐藏PDF上传区域，而不是图片的uploadSection
//         if (pdfUploadArea) pdfUploadArea.style.display = 'none';
//         if (pdfFileInfo) pdfFileInfo.style.display = 'none';
        
//         // 显示进度界面
//         progressSection.style.display = 'block';
//         if (resultSection) resultSection.style.display = 'none';
//         errorSection.style.display = 'none';
        
//         // 开始进度动画（与图片翻译相同）
//         animateProgress();
        
//         // 准备表单数据
//         const formData = new FormData();
//         formData.append('file', currentPdfFile);
//         formData.append('preserve_format', 'true');  // 关键：保持格式参数
        
//         // 获取语言设置
//         const sourceLanguage = document.getElementById('sourceLanguage').value;
//         const targetLanguage = document.getElementById('targetLanguage').value;
        
//         if (sourceLanguage !== 'auto') {
//             formData.append('source_language', sourceLanguage);
//         }
//         formData.append('target_language', targetLanguage);
        
//         console.log('发送PDF翻译请求...');
        
//         // ✅ 修复：移除 /api 前缀，确保调用 /upload
//         const apiUrl = ENV_CONFIG.getApiUrl().replace('/api', '');  // 移除 /api
//         const response = await fetch(`${apiUrl}/upload`, {
//             method: 'POST',
//             body: formData
//         });
        
//         // ✅ 检查响应状态
//         if (!response.ok) {
//             throw new Error(`HTTP ${response.status}: ${response.statusText}`);
//         }
        
//         const result = await response.json();
//         console.log('PDF翻译结果:', result);
        
//         // 清除进度动画
//         if (window.progressInterval) {
//             clearInterval(window.progressInterval);
//             window.progressInterval = null;
//         }
        
//         if (result.success) {
//             pdfDownloadUrl = result.download_url;
            
//             // ✅ 显示PDF预览（启用预览功能）
//             showPdfPreview(result.download_url);
            
//             // 显示成功通知
//             const detailInfo = `PDF翻译完成！
//处理时间：${result.processing_time || '未知'}
//检测语言：${result.detected_language || '未知'} (置信度：${result.language_confidence || '未知'})
//翻译方向：${result.translation_direction || '中文 → 英文'}
//原文长度：${result.original_length || 0} 字符
//译文长度：${result.translated_length || 0} 字符`;
            
//             showNotification(detailInfo, 'success');
//         } else {
//             throw new Error(result.error || '翻译失败');
//         }
        
//     } catch (error) {
//         console.error('PDF翻译失败:', error);
        
//         // 清除进度动画
//         if (window.progressInterval) {
//             clearInterval(window.progressInterval);
//             window.progressInterval = null;
//         }
        
//         progressSection.style.display = 'none';
//         showError('PDF翻译失败: ' + error.message);
//     }
// }

// 显示PDF预览（确保 iframe 正确加载）
// function showPdfPreview(downloadUrl) {
//     if (pdfPreviewContainer && pdfFrame) {
//         // 设置PDF预览URL（使用浏览器内置PDF查看器）
//         pdfFrame.src = downloadUrl;
//         pdfPreviewContainer.style.display = 'block';
        
//         // 隐藏进度区域
//         hideProgress();
        
//         // 隐藏PDF上传区域
//         if (pdfFormatSection) {
//             const uploadArea = pdfFormatSection.querySelector('.pdf-upload-area');
//             if (uploadArea) {
//                 uploadArea.style.display = 'none';
//             }
//         }
        
//         console.log('PDF预览已显示，URL:', downloadUrl);
//     } else {
//         console.error('PDF预览元素未找到');
//     }
// }

// PDF下载处理
function handlePdfDownload() {
    if (pdfDownloadUrl) {
        window.open(pdfDownloadUrl, '_blank');
    }
}

// 重置PDF翻译
function resetPdfTranslation() {
    // 隐藏预览
    const previewContainer = document.getElementById('pdfPreviewContainer');
    if (previewContainer) {
        previewContainer.style.display = 'none';
    }
    
    // 清空iframe
    const pdfFrame = document.getElementById('pdfFrame');
    if (pdfFrame) {
        pdfFrame.src = '';
    }
    
    // ✅ 修复：直接重置文件选择，确保重新显示上传区域
    currentPdfFile = null;
    
    const pdfFileInput = document.getElementById('pdfFileInput');
    const pdfFileInfo = document.getElementById('pdfFileInfo');
    const pdfUploadArea = document.getElementById('pdfUploadArea');
    
    if (pdfFileInput) pdfFileInput.value = '';
    if (pdfFileInfo) pdfFileInfo.style.display = 'none';
    if (pdfUploadArea) pdfUploadArea.style.display = 'block';  // ✅ 确保重新显示
    
    console.log('PDF翻译已重置，上传区域已重新显示');
}

// 清除PDF文件
function clearPdfFile() {
    resetPdfTranslation();
}

// 🔥 新增: 通用的AI总结显示函数 (所有tab调用)
function displayAISummary(summaryResult) {
    const summaryCard = document.getElementById('aiSummaryCard');
    const summarySuccess = document.getElementById('aiSummarySuccess');
    const summaryError = document.getElementById('aiSummaryError');
    const summaryContent = document.getElementById('aiSummaryContent');
    const summaryErrorText = document.getElementById('aiSummaryErrorText');
    
    if (!summaryCard) {
        console.warn('⚠️ AI总结显示区域未找到');
        return;
    }
    
    // 先隐藏所有内容
    summarySuccess.style.display = 'none';
    summaryError.style.display = 'none';
    
    if (!summaryResult) {
        // 没有总结数据,隐藏整个卡片
        summaryCard.style.display = 'none';
        return;
    }
    
    if (summaryResult.success && summaryResult.content) {
        // 总结成功
        summaryContent.textContent = summaryResult.content;
        summarySuccess.style.display = 'block';
        summaryCard.style.display = 'block';
        console.log('✅ AI总结显示成功');
    } else if (summaryResult.error) {
        // 总结失败
        summaryErrorText.textContent = summaryResult.error;
        summaryError.style.display = 'block';
        summaryCard.style.display = 'block';
        console.log('⚠️ AI总结失败:', summaryResult.error);
    } else {
        // 无效数据,隐藏
        summaryCard.style.display = 'none';
    }
}

// 🔥 新增: 隐藏AI总结的函数
function hideAISummary() {
    const summaryCard = document.getElementById('aiSummaryCard');
    if (summaryCard) {
        summaryCard.style.display = 'none';
    }
}