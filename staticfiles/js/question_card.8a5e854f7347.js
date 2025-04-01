$(document).ready(function () {
    // 篩選科目功能
    const descriptions = document.querySelectorAll('.custom-text');
    descriptions.forEach(function(element) {
    // 取得原始文字內容
    const originalText = element.textContent;
    // 用 <br> 替換空格，這裡會把所有空格都轉換成換行，如果只想轉換部分請調整規則
    const newText = originalText.split(' ').join('\n');
    // 更新元素內容
    element.innerHTML = newText;
    });


    // 篩選難易度功能
    $('.difficulty-filter').on('click', function () {
        var selectedDifficulty = $(this).data('difficulty');

        $('.question-item').each(function () {
            var itemDifficulty = $(this).data('difficulty');

            if (selectedDifficulty === 'all' || itemDifficulty === selectedDifficulty) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    });
});
