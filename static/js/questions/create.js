$(document).ready(function() {
    // 設定主題和標籤的選項限制
    setupCheckboxLimit('id_topics', 3, '主題');
    setupCheckboxLimit('id_tags', 5, '標籤');
    
    // 表單驗證
    validateForm();
    
    // Monaco Editor 初始化
    let monacoEditor;
    require(['vs/editor/editor.main'], function () {
        monacoEditor = monaco.editor.create($('#monaco-editor')[0], {
            value: $('#id_answer').val() || '',
            language: 'python',
            roundedSelection: true,
            scrollBeyondLastLine: false,
            readOnly: false,
            theme: 'vs-dark',
            automaticLayout: true
        });

        $('#questionForm').on('submit', function () {
            $('#id_answer').val(monacoEditor.getValue());
        });
    });
});

/**
 * 設定多選框的選擇數量限制
 * @param {string} fieldId - 字段的ID
 * @param {number} maxCount - 最大可選數量
 * @param {string} fieldName - 字段名稱（用於顯示錯誤消息）
 */
function setupCheckboxLimit(fieldId, maxCount, fieldName) {
    const $checkboxes = $(`#${fieldId} input[type="checkbox"]`);
    const $checkboxContainer = $(`#${fieldId}`);
    
    if ($checkboxContainer.length === 0) return;
    
    // 創建警告消息元素
    const $warningElement = $('<div>', {
        'class': 'text-danger validation-warning mt-2 d-none',
        'text': `最多只能選擇${maxCount}個${fieldName}`
    });
    
    // 將警告消息插入到複選框容器後面
    $checkboxContainer.parent().append($warningElement);
    
    // 添加事件監聽器到每個複選框
    $checkboxes.on('change', function() {
        const checkedCount = $(`#${fieldId} input[type="checkbox"]:checked`).length;
        
        // 如果選擇超過最大數量，取消勾選該複選框並顯示警告
        if (checkedCount > maxCount) {
            $(this).prop('checked', false);
            $warningElement.removeClass('d-none');
            
            // 3秒後隱藏警告
            setTimeout(() => {
                $warningElement.addClass('d-none');
            }, 3000);
        }
    });
}

/**
 * 表單驗證
 */
function validateForm() {
    const $form = $('#questionForm');
    
    if ($form.length === 0) return;
    
    $form.on('submit', function(event) {
        // 檢查必填字段
        let isValid = true;
        const requiredFields = [
            'id_title', 
            'id_content', 
            'id_level', 
            'id_answer', 
            'id_input_format', 
            'id_output_format', 
            'id_input_example', 
            'id_output_example'
        ];
        
        $.each(requiredFields, function(index, fieldId) {
            const $field = $(`#${fieldId}`);
            if ($field.length && !$field.val().trim()) {
                isValid = false;
                highlightInvalidField($field);
            }
        });
        
        // 檢查主題選擇
        const topicsChecked = $('#id_topics input[type="checkbox"]:checked').length;
        if (topicsChecked === 0) {
            isValid = false;
            const $topicsContainer = $('#id_topics').parent();
            $topicsContainer.addClass('border-danger');
            
            // 添加警告消息
            let $warningElement = $topicsContainer.find('.validation-warning');
            if ($warningElement.length === 0) {
                $warningElement = $('<div>', {
                    'class': 'text-danger validation-warning mt-2',
                    'text': '請至少選擇一個主題'
                });
                $topicsContainer.append($warningElement);
            }
            $warningElement.removeClass('d-none');
        }
        
        // 檢查標籤選擇
        const tagsChecked = $('#id_tags input[type="checkbox"]:checked').length;
        if (tagsChecked === 0) {
            isValid = false;
            const $tagsContainer = $('#id_tags').parent();
            $tagsContainer.addClass('border-danger');
            
            // 添加警告消息
            let $warningElement = $tagsContainer.find('.validation-warning');
            if ($warningElement.length === 0) {
                $warningElement = $('<div>', {
                    'class': 'text-danger validation-warning mt-2',
                    'text': '請至少選擇一個標籤'
                });
                $tagsContainer.append($warningElement);
            }
            $warningElement.removeClass('d-none');
        }
        
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

/**
 * 高亮顯示無效的字段
 * @param {jQuery} $field - 無效的表單字段 jQuery 元素
 */
function highlightInvalidField($field) {
    $field.addClass('is-invalid');
    
    // 添加警告消息
    const $parentElement = $field.parent();
    let $feedbackElement = $parentElement.find('.invalid-feedback');
    
    if ($feedbackElement.length === 0) {
        $feedbackElement = $('<div>', {
            'class': 'invalid-feedback d-block',
            'text': '此字段為必填項'
        });
        $parentElement.append($feedbackElement);
    }
    
    // 添加聚焦時移除錯誤狀態
    $field.on('focus', function() {
        $(this).removeClass('is-invalid');
        if ($feedbackElement) {
            $feedbackElement.text('');
        }
    });
}
