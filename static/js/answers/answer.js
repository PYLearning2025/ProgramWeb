$(document).ready(function() {    
    // 表單驗證
    validateForm();
    
    // Monaco Editor 初始化
    let monacoEditor;
    require(['vs/editor/editor.main'], function () {
        monacoEditor = monaco.editor.create($('#monaco-editor')[0], {
            value: '',
            language: 'python',
            roundedSelection: true,
            scrollBeyondLastLine: false,
            readOnly: false,
            theme: 'vs',
            automaticLayout: true
        });
    });

    // 攔截 submit，先顯示 modal
    $('#answerForm').on('submit', function(e) {
        e.preventDefault();
        const code = monacoEditor.getValue();
        if (!code.trim()) {
            showMessage('danger', '請輸入答案');
            return;
        }
        // 顯示 modal
        const modal = new bootstrap.Modal(document.getElementById('submitConfirmModal'));
        modal.show();
        // 記錄目前的 code 內容
        window._pendingSubmitCode = code;
    });

    // Modal 確定送出
    $('#modal-submit-btn').on('click', function() {
        const code = window._pendingSubmitCode;
        const csrfToken = $("input[name='csrfmiddlewaretoken']").val();
        const questionId = $("#question_id").val();
        // 關閉 modal
        const modalEl = document.getElementById('submitConfirmModal');
        const modal = bootstrap.Modal.getInstance(modalEl);
        modal.hide();
        // 送出 AJAX
        $.ajax({
            url: '/answers/submit/',
            type: 'POST',
            data: {
                'code': code,
                'question_id': questionId,
                'csrfmiddlewaretoken': csrfToken
            },
            success: function(response) {
                location.reload();
            }
        });
    });

    // Debug 按鈕 AJAX
    $('#debug-btn').on('click', function() {
        const code = monacoEditor.getValue();
        const csrfToken = $("input[name='csrfmiddlewaretoken']").val();
        const questionId = $("#question_id").val();
        $.ajax({
            url: '/answers/debug/',
            type: 'POST',
            data: {
                'code': code,
                'question_id': questionId,
                'csrfmiddlewaretoken': csrfToken
            },
            success: function(response) {
                showMessage('info', response.message || 'Debug 結果：' + (response.result || '')); 
            },
            error: function(xhr) {
                showMessage('danger', xhr.responseJSON?.message || 'Debug 失敗，請稍後再試。');
            }
        });
    });
});

function validateForm() {
    const $form = $('#answerForm');
    
    if ($form.length === 0) return;
    
    $form.on('submit', function(event) {
        // 檢查必填字段
        let isValid = true;
        const requiredFields = [
            'id_answer',
        ];
        
        $.each(requiredFields, function(index, fieldId) {
            const $field = $(`#${fieldId}`);
            if ($field.length && !$field.val().trim()) {
                isValid = false;
                highlightInvalidField($field);
            }
        });
        
        // 如果表單無效，阻止提交
        if (!isValid) {
            event.preventDefault();
            
            // 顯示一般錯誤消息
            const $formTop = $('.gradient-bg').length ? $('.gradient-bg') : $form;
            let $errorAlert = $('.form-error-alert');
            if ($errorAlert.length === 0) {
                $errorAlert = $('<div>', {
                    'class': 'alert alert-danger mt-3 form-error-alert',
                    'text': '表單中存在錯誤，請修正後再提交。'
                });
                $formTop.after($errorAlert);
            }
            
            // 滾動到頂部
            $('html, body').animate({ scrollTop: 0 }, 'smooth');
        }
    });
}

function showMessage(type, message) {
    // type: success, danger, info
    let $msg = $('.form-error-alert');
    if ($msg.length === 0) {
        $msg = $('<div>', {
            'class': `alert alert-${type} mt-3 form-error-alert`,
            'text': message
        });
        $('#answerForm').before($msg);
    } else {
        $msg.removeClass('alert-success alert-danger alert-info').addClass(`alert-${type}`);
        $msg.text(message);
    }
    $('html, body').animate({ scrollTop: 0 }, 'smooth');
}