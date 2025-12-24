// 多语言文本资源
const i18nResources = {
    zh: {
        // 页面标题和头部
        title: "文档翻译工具",
        subtitle: "支持PDF、Word、TXT文档翻译，或直接输入文本进行翻译",
        
        // 翻译设置
        translation_settings: "翻译设置",
        source_language: "源语言：",
        target_language: "目标语言：",
        auto_detect: "自动检测",
        chinese: "中文",
        english: "英文",
        german: "德语",
        
        // 标签切换
        file_upload: "文件上传",
        text_input: "文本输入",
        pdf_format: "PDF格式翻译",
        start_translate_img: "开始翻译图片",
        upload_tip: "选择图片文件，支持 JPG、PNG、BMP、TIFF、WebP 格式",

        // 文件上传
        upload_title: "拖拽文件到此处或点击选择文件",
        upload_subtitle: "支持格式：PDF、DOCX、TXT（最大16MB）",
        select_file: "选择文件",
        reselect: "重新选择",
        translating: "翻译中...",
        
        // PDF格式翻译
        pdf_upload_title: "上传PDF文档进行格式翻译",
        pdf_upload_subtitle: "翻译后将保持原文档的格式和样式",
        select_pdf: "选择PDF文件",
        pdf_preview: "PDF翻译预览",
        download_pdf: "下载PDF",
        translate_new_pdf: "翻译新PDF",
        
        // 文本输入
        input_text: "输入要翻译的文本",
        clear: "清空",
        start_translate: "开始翻译",
        input_placeholder: "请在此处输入或粘贴要翻译的文本内容...\n\n支持中文和英文文本，系统会自动检测语言并翻译。",
        char_count: "字符数: ",
        input_hint: "支持自动检测语言，也可手动选择源语言和目标语言",
        
        // 翻译结果
        translation_complete: "翻译完成",
        copy_result: "复制结果",
        download_text: "下载文本",
        retranslate: "重新翻译",
        original_text: "原文",
        translated_text: "译文",
        
        // 进度和结果
        translating_progress: "翻译进行中...",
        processing: "正在处理文档...",
        download_file: "下载翻译文件",
        translate_new: "翻译新文档",
        translation_preview: "翻译预览：",
        
        // 错误处理
        processing_failed: "处理失败",
        restart: "重新开始",
        
        // 状态和页脚
        checking_status: "检查系统状态...",
        footer: "© 2024 文档翻译工具 | 基于 Ollama 大语言模型",
        
        // 动态消息
        upload_success: "文件上传成功",
        translation_success: "翻译完成",
        copy_success: "已复制到剪贴板",
        download_success: "文件下载成功",
        error_file_type: "不支持的文件类型",
        error_file_size: "文件大小超出限制",
        error_no_text: "请输入要翻译的文本",
        error_network: "网络连接失败",
        
        // 进度步骤
        uploading: "正在上传文档...",
        parsing: "正在解析文档内容...",
        connecting: "正在连接翻译服务...",
        translating_doc: "正在翻译文档...",
        generating: "正在生成翻译结果...",
        
        // 新增的翻译键值
        pdf_translation: "PDF 翻译",
        ppt_translation: "PPT翻译",
        image_translation: "图片翻译",
        start_translate: "开始翻译",
        reselect: "重新选择",
        start_translate_img: "开始翻译图片",
        start_translate_ppt: "开始翻译PPT",
        
        // 图片翻译相关
        select_image: "选择图片文件",
        image_tip: "支持 JPG、PNG、BMP、TIFF、WebP 格式，自动识别图片中的文字，精准翻译。",
        
        // PPT翻译相关
        select_ppt: "选择PPT文件",
        ppt_support: "支持 PPTX、PPT 格式",
        ppt_translation_complete: "PPT翻译完成",
        
        // PDF翻译相关
        pdf_translation_complete: "PDF翻译完成",
        
        // 通用下载和翻译
        download_file: "下载翻译文件",
        translate_new: "翻译新文档"
    },
    
    en: {
        // 页面标题和头部
        title: "Document Translator",
        subtitle: "Support PDF, Word, TXT document translation, or direct text input translation",
        
        // 翻译设置
        translation_settings: "Translation Settings",
        source_language: "Source Language:",
        target_language: "Target Language:",
        auto_detect: "Auto Detect",
        chinese: "Chinese",
        english: "English",
        german: "German",
        
        // 标签切换
        file_upload: "File Upload",
        text_input: "Text Input",
        pdf_format: "PDF Format Translation",
        start_translate_img: "Translate Image",
        upload_tip: "Select an image file (JPG, PNG, BMP, TIFF, WebP supported)",
        
        // 文件上传
        upload_title: "Drag files here or click to select files",
        upload_subtitle: "Supported formats: PDF, DOCX, TXT (max 16MB)",
        select_file: "Select File",
        reselect: "Reselect",
        translating: "Translating...",
        
        // PDF格式翻译
        pdf_upload_title: "Upload PDF document for format translation",
        pdf_upload_subtitle: "The format and style of the original document will be preserved after translation",
        select_pdf: "Select PDF File",
        pdf_preview: "PDF Translation Preview",
        download_pdf: "Download PDF",
        translate_new_pdf: "Translate New PDF",
        
        // 文本输入
        input_text: "Enter text to translate",
        clear: "Clear",
        start_translate: "Start Translation",
        input_placeholder: "Please enter or paste the text content to be translated here...\n\nSupports Chinese and English text, the system will automatically detect the language and translate.",
        char_count: "Character count: ",
        input_hint: "Supports automatic language detection, or manually select source and target languages",
        
        // 翻译结果
        translation_complete: "Translation Complete",
        copy_result: "Copy Result",
        download_text: "Download Text",
        retranslate: "Translate New",
        original_text: "Original",
        translated_text: "Translation",
        
        // 进度和结果
        translating_progress: "Translation in Progress...",
        processing: "Processing document...",
        download_file: "Download Translated File",
        translate_new: "Translate New Document",
        translation_preview: "Translation Preview:",
        
        // 错误处理
        processing_failed: "Processing Failed",
        restart: "Restart",
        
        // 状态和页脚
        checking_status: "Checking system status...",
        footer: "© 2024 Document Translator | Powered by Ollama LLM",
        
        // 动态消息
        upload_success: "File uploaded successfully",
        translation_success: "Translation completed",
        copy_success: "Copied to clipboard",
        download_success: "File downloaded successfully",
        error_file_type: "Unsupported file type",
        error_file_size: "File size exceeds limit",
        error_no_text: "Please enter text to translate",
        error_network: "Network connection failed",
        
        // 进度步骤
        uploading: "Uploading document...",
        parsing: "Parsing document content...",
        connecting: "Connecting to translation service...",
        translating_doc: "Translating document...",
        generating: "Generating translation results...",
        
        // 新增的翻译键值
        pdf_translation: "PDF Translation",
        ppt_translation: "PPT Translation",
        image_translation: "Image Translation",
        start_translate: "Start Translation",
        reselect: "Reselect",
        start_translate_img: "Translate Image",
        start_translate_ppt: "Translate PPT",
        
        // 图片翻译相关
        select_image: "Select Image File",
        image_tip: "Supports JPG, PNG, BMP, TIFF, WebP formats. Automatically recognizes and translates text in images.",
        
        // PPT翻译相关
        select_ppt: "Select PPT File",
        ppt_support: "Supports PPTX, PPT formats",
        ppt_translation_complete: "PPT Translation Complete",
        
        // PDF翻译相关
        pdf_translation_complete: "PDF Translation Complete",
        
        // 通用下载和翻译
        download_file: "Download Translated File",
        translate_new: "Translate New Document",
        
        // 其他翻译键值
        download_translated_pdf: "Download Translated PDF",
        download_translated_image: "Download Translated Image",
        download_translated_ppt: "Download Translated PPT",
        original_image: "Original Image",
        translated_image: "Translated Image",
        original_ppt_label: "Original PPT",
        translated_ppt_label: "Translated Result",
        ppt_translation_stats_label: "Translation Stats",
        ai_summary: "AI Summary"
    }
};

// 导出语言资源
if (typeof module !== 'undefined' && module.exports) {
    module.exports = i18nResources;
}