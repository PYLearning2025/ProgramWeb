// 錯誤頁面互動功能
$(document).ready(function () {

  // 添加淡入動畫
  $('.error-card').addClass('fade-in');

  // 按鈕點擊特效
  $('.error-btn').on('click', function (e) {
    const $this = $(this);
    const offset = $this.offset();
    const size = Math.max($this.outerWidth(), $this.outerHeight());
    const x = e.pageX - offset.left - size / 2;
    const y = e.pageY - offset.top - size / 2;

    // 創建波紋效果
    const $ripple = $('<span>', {
      css: {
        position: 'absolute',
        width: size + 'px',
        height: size + 'px',
        background: 'rgba(255, 255, 255, 0.5)',
        borderRadius: '50%',
        transform: 'scale(0)',
        animation: 'ripple 0.6s ease-out',
        left: x + 'px',
        top: y + 'px',
        pointerEvents: 'none'
      }
    });

    $this.css({
      position: 'relative',
      overflow: 'hidden'
    }).append($ripple);

    // 移除波紋元素
    setTimeout(function () {
      $ripple.remove();
    }, 600);
  });

  // 鍵盤快捷鍵 - 按 Enter 或 Space 返回首頁
  $(document).on('keydown', function (e) {
    if (e.key === 'Enter' || e.key === ' ') {
      const $active = $(document.activeElement);
      const isEditable = $active.is('input, textarea') || $active.prop('contentEditable') === 'true';

      if ((e.key === 'Enter' || e.key === ' ') && !isEditable) {
        e.preventDefault();

        const $errorBtn = $('.error-btn');
        if ($errorBtn.length) {
          // 先觸發波紋效果
          $errorBtn.trigger('click');

          const href = $errorBtn.attr('href');
          if (href) {
            setTimeout(function () {
              window.location.href = href;
            }, 200);
          }
        }
      }
    }
  });

});
