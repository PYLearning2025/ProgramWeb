$(function () {
    const form = $('#peer-review-form');

    form.on('submit', function (event) {
        event.preventDefault(); // 防止表單默認提交行為

        // 收集所有分數欄位
        const scoreFields = [
            { id: 'id_question_accuracy_score', label: '題目正確性' },
            { id: 'id_complexity_score', label: '複雜度' },
            { id: 'id_practice_score', label: '實踐性' },
            { id: 'id_answer_accuracy_score', label: '答案正確性' },
            { id: 'id_readability_score', label: '可讀性' }
        ];

        let hasError = false;

        // 檢查是否有分數為零
        $.each(scoreFields, function (_, fieldData) {
            const field = $('#' + fieldData.id);
            if (field.length && parseInt(field.val()) === 0) {
                hasError = true;
                field.addClass('error'); // 加入錯誤樣式
                alert(`${fieldData.label} 的分數不可為 0，請修改後再提交！`); // 顯示對應錯誤訊息
                field.focus(); // 聚焦到有問題的欄位
                return false; // 終止檢查
            } else if (field.length) {
                field.removeClass('error'); // 移除錯誤樣式
            }
        });

        if (hasError) {
            return; // 如果有錯誤，停止提交
        }

        const userConfirmed = confirm("確定要提交您的評分嗎？\n提交後將無法修改。");
        if (!userConfirmed) {
            return;
        }

        // 發送表單資料到後端
        const formData = new FormData(form[0]);
        const url = form.attr('action'); // 獲取表單的 action URL

        fetch(url, {
            method: 'POST',
            body: new URLSearchParams(formData),
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.success);
                window.location.href = '/question/peer_assessment/';
            } else if (data.error) {
                let errorDiv = $('#error-message');
                if (!errorDiv.length) {
                    errorDiv = $('<div>', {
                        id: 'error-message',
                        class: 'alert alert-danger mt-3'
                    }).prependTo(form);
                }
                errorDiv.text(data.error);
            }
        })
        .catch(error => {
            let errorDiv = $('#error-message');
            if (!errorDiv.length) {
                errorDiv = $('<div>', {
                    id: 'error-message',
                    class: 'alert alert-danger mt-3'
                }).prependTo(form);
            }
            errorDiv.text("提交過程中發生錯誤，請稍後再試。");
        });
    });
});