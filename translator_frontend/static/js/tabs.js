// Tab切换功能

// 切换Tab函数
function switchTab(tabName) {
    console.log('切换到标签:', tabName);
    
    // 移除所有Tab的active类
    const allTabs = document.querySelectorAll('.tab-btn-modern');
    allTabs.forEach(tab => {
        tab.classList.remove('active');
    });
    
    // 添加active类到当前Tab
    const tabButtonMap = {
        'file': 'fileTabBtn',
        'text': 'textTabBtn',
        'pdf': 'pdfTabBtn',
        'image': 'imageTabBtn',
        'ppt': 'pptTabBtn'
    };
    
    const currentTabBtn = document.getElementById(tabButtonMap[tabName]);
    if (currentTabBtn) {
        currentTabBtn.classList.add('active');
    }
    
    // 隐藏所有内容区域
    const allSections = [
        'uploadSection',
        'textInputSection',
        'pdfFormatSection',
        'imageTranslationSection',
        'pptTranslationSection'
    ];
    
    allSections.forEach(sectionId => {
        const section = document.getElementById(sectionId);
        if (section) {
            section.classList.add('hidden');
        }
    });
    
    // 显示对应的内容区域
    const sectionMap = {
        'file': 'uploadSection',
        'text': 'textInputSection',
        'pdf': 'pdfFormatSection',
        'image': 'imageTranslationSection',
        'ppt': 'pptTranslationSection'
    };
    
    const targetSectionId = sectionMap[tabName];
    const targetSection = document.getElementById(targetSectionId);
    
    if (targetSection) {
        targetSection.classList.remove('hidden');
        console.log('显示区域:', targetSectionId);
    } else {
        console.error('找不到目标区域:', targetSectionId);
    }
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('初始化Tab系统');
    
    // 确保第一个Tab默认激活
    const firstTab = document.getElementById('fileTabBtn');
    if (firstTab && !firstTab.classList.contains('active')) {
        firstTab.classList.add('active');
    }
    
    // 显示第一个Tab的内容
    switchTab('file');
});

// 导出函数供全局使用
window.switchTab = switchTab;