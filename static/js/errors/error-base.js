// 錯誤頁面互動功能
document.addEventListener('DOMContentLoaded', function() {
    
    // 添加淡入動畫
    const errorCard = document.querySelector('.error-card');
    if (errorCard) {
        errorCard.classList.add('fade-in');
    }
    
    // 按鈕點擊特效
    const errorBtn = document.querySelector('.error-btn');
    if (errorBtn) {
        errorBtn.addEventListener('click', function(e) {
            // 創建波紋效果
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                background: rgba(255, 255, 255, 0.5);
                border-radius: 50%;
                transform: scale(0);
                animation: ripple 0.6s ease-out;
                left: ${x}px;
                top: ${y}px;
                pointer-events: none;
            `;
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            // 移除波紋元素
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    }
    
    // 鍵盤快捷鍵 - 按 Enter 或 Space 返回首頁
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
            const active = document.activeElement;
            const isEditable = active && (
                active.tagName === 'INPUT' ||
                active.tagName === 'TEXTAREA' ||
                active.isContentEditable
            );
            if ((e.key === 'Enter' || e.key === ' ') && !isEditable) {
                if (errorBtn) {
                    errorBtn.click();
                }
            }
        }
    });
    
}); // 添加波紋動畫的 CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(2);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
