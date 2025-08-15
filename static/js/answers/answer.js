$(document).ready(function () {
  // 表單驗證
  validateForm();

  // Monaco Editor 初始化
  let monacoEditor;
  require(['vs/editor/editor.main'], function () {
    // 設定初始值
    let initialValue = '';
    if (existingAnswerData) {
      initialValue = existingAnswerData;
    }

    monacoEditor = monaco.editor.create($('#monaco-editor')[0], {
      value: initialValue,
      language: 'python',
      roundedSelection: true,
      scrollBeyondLastLine: false,
      readOnly: isAlreadySubmitted === "True" ? true : false,
      theme: 'vs',
      automaticLayout: true
    });

    // 如果已提交，顯示提示訊息
    if (isAlreadySubmitted === "True") {
      isAlreadySubmitted = true;
      showToast('您已經提交過答案，無法再編輯', 'info');
    } else {
      isAlreadySubmitted = false;
    }
  });

  // 攔截 submit，先顯示 modal
  $('#answerForm').on('submit', function (e) {
    e.preventDefault();

    // 如果已經提交過，阻止再次提交
    if (isAlreadySubmitted) {
      showToast('您已經提交過答案，無法再次提交', 'error');
      return;
    }

    const code = monacoEditor.getValue();
    if (!code.trim()) {
      showToast('請輸入答案', 'error');
      return;
    }
    // 顯示 modal
    const modal = new bootstrap.Modal(document.getElementById('submitConfirmModal'));
    modal.show();
    // 記錄目前的 code 內容
    window._pendingSubmitCode = code;
  });

  // Modal 確定送出
  $('#modal-submit-btn').on('click', function () {
    $('button[type="submit"]').prop('disabled', true).text('Submitting...');
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
      success: function (response) {
        showToast(response.message || '送出成功', 'success');
        setTimeout(function () {
          window.location.href = response.redirect_url;
        }, 1000);
      },
      error: function (xhr) {
        showToast(xhr.responseJSON?.message || '送出失敗，請稍後再試。', 'error');
        $('button[type="submit"]').prop('disabled', false).text('Submit');
      }
    });
  });

  // Debug 按鈕 AJAX
  $('#debug-btn').on('click', function () {
    // 如果已經提交過，仍然可以 debug
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
      success: function (response) {
        showToast(response.message || 'Debug 結果：' + (response.result || ''), 'info');
      },
      error: function (xhr) {
        showToast(xhr.responseJSON?.message || 'Debug 失敗，請稍後再試。', 'error');
      }
    });
  });
});

function validateForm() {
  const $form = $('#answerForm');

  if ($form.length === 0) return;

  $form.on('submit', function (event) {
    // 檢查必填字段
    let isValid = true;
    const requiredFields = [
      'id_answer',
    ];

    $.each(requiredFields, function (index, fieldId) {
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
      showToast('表單中存在錯誤，請修正後再提交。', 'error');
    }
  });
}

function showToast(message, type = 'info') {
  const toastElement = document.getElementById('liveToast');
  const messageElement = document.getElementById('toastMessage');

  // 設置消息內容
  messageElement.textContent = message;

  // 設置背景顏色
  toastElement.className = 'toast align-items-center text-white border-0';
  if (type === 'error') {
    toastElement.classList.add('bg-danger');
  } else if (type === 'success') {
    toastElement.classList.add('bg-success');
  } else {
    toastElement.classList.add('bg-info');
  }

  // 使用Bootstrap標準API
  const toastBootstrap = bootstrap.Toast.getOrCreateInstance(toastElement, { delay: 3000 });
  toastBootstrap.show();
}