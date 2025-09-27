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
    $('button[type="submit"]').prop('disabled', true).html('<i class="bi bi-upload"></i> Submitting...');
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
        $('#debug-btn').prop('disabled', true).html('<i class="bi bi-bug-fill"></i> Debug');
      },
      error: function (xhr) {
        let errorMessage = '送出失敗，請稍後再試。';
        
        // 嘗試從JSON response中獲取錯誤訊息
        if (xhr.responseJSON && xhr.responseJSON.message) {
          errorMessage = xhr.responseJSON.message;
        } else if (xhr.responseText) {
          // 如果不是JSON格式，嘗試解析responseText
          try {
            const response = JSON.parse(xhr.responseText);
            if (response.message) {
              errorMessage = response.message;
            }
          } catch (e) {
            // 如果解析失敗，使用預設訊息
            console.log('無法解析錯誤回應:', xhr.responseText);
          }
        }
        
        showToast(errorMessage, 'error');
        $('button[type="submit"]').prop('disabled', false).html('<i class="bi bi-upload"></i> Submit');
      }
    });
  });

  // Debug 按鈕 AJAX
  $('#debug-btn').on('click', function () {
    $('#debug-btn').prop('disabled', true).html('<i class="bi bi-bug-fill"></i> Debuging...');
    // 如果已經提交過，仍然可以 debug
    const code = monacoEditor.getValue();
    const csrfToken = $("input[name='csrfmiddlewaretoken']").val();
    const questionId = $("#question_id").val();
    
    // 顯示載入中訊息
    showToast('正在執行測試...', 'info');
    
    $.ajax({
      url: '/answers/debug/',
      type: 'POST',
      data: {
        'code': code,
        'question_id': questionId,
        'csrfmiddlewaretoken': csrfToken
      },
      success: function (response) {
        $('#debug-btn').prop('disabled', false).html('<i class="bi bi-bug-fill"></i> Debug');
        showToast('Debug 完成', 'success');
        // 顯示測試結果 modal
        showDebugResultModal(response);
      },
      error: function (xhr) {
        let errorMessage = 'Debug 失敗，請稍後再試。';
        
        // 嘗試從JSON response中獲取錯誤訊息
        if (xhr.responseJSON && xhr.responseJSON.message) {
          errorMessage = xhr.responseJSON.message;
        } else if (xhr.responseText) {
          // 如果不是JSON格式，嘗試解析responseText
          try {
            const response = JSON.parse(xhr.responseText);
            if (response.message) {
              errorMessage = response.message;
            }
          } catch (e) {
            // 如果解析失敗，使用預設訊息
            console.log('無法解析錯誤回應:', xhr.responseText);
          }
        }
        
        $('#debug-btn').prop('disabled', false).html('<i class="bi bi-bug-fill"></i> Debug');
        showToast(errorMessage, 'error');
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

function showDebugResultModal(response) {
  const statusElement = $('#debug-status');
  
  // 根據 result_code 設置對應的狀態
  const resultCode = response.result_code || 'WA';
  let statusText, icon, alertClass;
  
  switch (resultCode) {
    case 'AC':
      statusText = 'Accepted (AC)';
      icon = 'bi-check-circle-fill';
      alertClass = 'alert-success';
      break;
    case 'WA':
      statusText = 'Wrong Answer (WA)';
      icon = 'bi-x-circle-fill';
      alertClass = 'alert-danger';
      break;
    case 'CE':
      statusText = 'Compilation Error (CE)';
      icon = 'bi-exclamation-triangle-fill';
      alertClass = 'alert-warning';
      break;
    case 'TLE':
      statusText = 'Time Limit Exceeded (TLE)';
      icon = 'bi-clock-fill';
      alertClass = 'alert-warning';
      break;
    case 'MLE':
      statusText = 'Memory Limit Exceeded (MLE)';
      icon = 'bi-cpu-fill';
      alertClass = 'alert-warning';
      break;
    case 'RE':
      statusText = 'Runtime Error (RE)';
      icon = 'bi-exclamation-triangle-fill';
      alertClass = 'alert-warning';
      break;
    default:
      statusText = 'Unknown Error';
      icon = 'bi-question-circle-fill';
      alertClass = 'alert-secondary';
  }
  
  statusElement.removeClass('alert-success alert-danger alert-warning alert-secondary').addClass(alertClass);
  statusElement.html(`
    <i class="bi ${icon} me-2" style="font-size: 1.3rem;"></i>
    <span>${statusText}</span>
  `);

  // 設置輸入範例
  if (response.inputs && response.inputs.length > 0) {
    $('#debug-inputs').html(`<pre class="mb-0">${response.inputs.join('\n')}</pre>`);
  } else {
    $('#debug-inputs').html('<span class="text-muted">無輸入範例</span>');
  }

  // 設置期望輸出
  if (response.outputs && response.outputs.length > 0) {
    $('#debug-outputs').html(`<pre class="mb-0">${response.outputs.join('\n')}</pre>`);
  } else {
    $('#debug-outputs').html('<span class="text-muted">無期望輸出</span>');
  }

  // 設置執行結果 - 顯示簡潔的結果訊息
  let resultMessage = '';
  switch (resultCode) {
    case 'AC':
      resultMessage = '恭喜！所有測試案例都通過了。';
      break;
    case 'WA':
      resultMessage = '答案錯誤，請檢查程式邏輯。';
      break;
    case 'CE':
      resultMessage = '編譯錯誤，請檢查語法。';
      break;
    case 'TLE':
      resultMessage = '執行超時，請優化程式效率。';
      break;
    case 'MLE':
      resultMessage = '記憶體超限，請減少記憶體使用。';
      break;
    case 'RE':
      resultMessage = '執行時錯誤，請檢查程式邏輯。';
      break;
    default:
      resultMessage = '發生未知錯誤。';
  }
  
  $('#debug-result pre').text(resultMessage);

  // 顯示 modal
  const debugModal = new bootstrap.Modal(document.getElementById('debugResultModal'));
  debugModal.show();
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