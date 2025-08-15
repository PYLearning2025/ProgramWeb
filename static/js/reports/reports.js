$(document).ready(function () {
  // 表單驗證初始化
  validateForm();

  // 檔案上傳驗證
  initFileValidation();
});

/**
 * 表單驗證
 */
function validateForm() {
  const $form = $('#reportForm');

  if ($form.length === 0) return;

  $form.on('submit', function (event) {
    event.preventDefault(); // 阻止預設提交

    let isValid = true;

    // 檢查必填字段
    const requiredFields = [
      'id_category',
      'id_content'
    ];

    $.each(requiredFields, function (index, fieldId) {
      const $field = $('#' + fieldId);
      if ($field.length && !$field.val().trim()) {
        isValid = false;
        highlightInvalidField($field);
      } else {
        clearInvalidField($field);
      }
    });

    // 驗證檔案
    if (!validateFile()) {
      isValid = false;
    }

    // 如果表單無效，顯示錯誤
    if (!isValid) {
      showFormError('表單中存在錯誤，請修正後再提交。');
      $('html, body').animate({ scrollTop: 0 }, 'smooth');
      return;
    }

    // 表單有效，顯示確認 Modal
    showConfirmModal();
  });
}

/**
 * 初始化檔案驗證
 */
function initFileValidation() {
  const $fileInput = $('#id_attachment');

  if ($fileInput.length === 0) return;

  $fileInput.on('change', function () {
    const file = this.files[0];
    if (file) {
      validateSingleFile(file);
    }
  });
}

/**
 * 驗證單個檔案
 */
function validateSingleFile(file) {
  const maxSize = 5 * 1024 * 1024; // 5MB
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png'];

  // 檢查檔案類型
  if (!allowedTypes.includes(file.type)) {
    showFileError(`檔案「${file.name}」格式不支援，請上傳 JPG、JPEG 或 PNG 格式的圖片`);
    clearFileInput();
    return false;
  }

  // 檢查檔案大小
  if (file.size > maxSize) {
    const sizeInMB = (file.size / (1024 * 1024)).toFixed(2);
    showFileError(`檔案「${file.name}」大小為 ${sizeInMB}MB，超過 5MB 限制`);
    clearFileInput();
    return false;
  }

  clearFileError();
  return true;
}

/**
 * 驗證檔案（用於表單提交）
 */
function validateFile() {
  const $fileInput = $('#id_attachment');
  const file = $fileInput[0].files[0];

  if (!file) {
    return true; // 檔案是可選的
  }

  return validateSingleFile(file);
}

/**
 * 清除檔案輸入
 */
function clearFileInput() {
  const $fileInput = $('#id_attachment');
  $fileInput.val('');
}

/**
 * 高亮顯示無效的字段
 */
function highlightInvalidField($field) {
  $field.addClass('is-invalid');
  $field.on('input change', function () {
    if ($(this).val().trim()) {
      clearInvalidField($(this));
    }
  });
}

/**
 * 清除字段的無效狀態
 */
function clearInvalidField($field) {
  $field.removeClass('is-invalid');
}

/**
 * 顯示表單錯誤
 */
function showFormError(message) {
  let $errorAlert = $('.form-error-alert');
  if ($errorAlert.length === 0) {
    $errorAlert = $('<div>', {
      'class': 'alert alert-danger mt-3 form-error-alert',
      'html': `<i class="bi bi-exclamation-triangle-fill me-1"></i>${message}`
    });
    $('.bg-primary.bg-gradient.text-white.rounded-3.p-4').after($errorAlert);
  } else {
    $errorAlert.html(`<i class="bi bi-exclamation-triangle-fill me-1"></i>${message}`);
  }
  $errorAlert.removeClass('d-none');
}

/**
 * 顯示檔案錯誤
 */
function showFileError(message) {
  let $fileError = $('.file-error-alert');
  if ($fileError.length === 0) {
    $fileError = $('<div>', {
      'class': 'alert alert-danger mt-2 file-error-alert',
      'html': `<i class="bi bi-exclamation-triangle-fill me-1"></i>${message}`
    });
    $('#id_attachment').closest('.mb-4').after($fileError);
  } else {
    $fileError.html(`<i class="bi bi-exclamation-triangle-fill me-1"></i>${message}`);
  }
  $fileError.removeClass('d-none');
}

/**
 * 清除檔案錯誤
 */
function clearFileError() {
  $('.file-error-alert').addClass('d-none');
}

/**
 * 清除所有錯誤訊息
 */
function clearAllErrors() {
  $('.form-error-alert, .file-error-alert').addClass('d-none');
}

/**
 * 顯示載入狀態
 */
function showLoadingState() {
  const $submitBtn = $('#submit-btn');
  const $returnBtn = $('button[onclick="history.back()"]');

  // 禁用按鈕並顯示載入文字
  $submitBtn.prop('disabled', true).html('<i class="bi bi-hourglass-split me-1"></i>提交中...');
  $returnBtn.prop('disabled', true);

  // 顯示載入提示
  showFormInfo('正在提交您的回報，請稍候...', 'info');
}

/**
 * 顯示表單資訊訊息
 */
function showFormInfo(message, type = 'info') {
  let $infoAlert = $('.form-info-alert');
  if ($infoAlert.length === 0) {
    $infoAlert = $('<div>', {
      'class': `alert alert-${type} mt-3 form-info-alert`,
      'html': `<i class="bi bi-info-circle-fill me-1"></i>${message}`
    });
    $('.bg-primary.bg-gradient.text-white.rounded-3.p-4').after($infoAlert);
  } else {
    $infoAlert.removeClass('alert-info alert-success alert-danger').addClass(`alert-${type}`);
    $infoAlert.html(`<i class="bi bi-info-circle-fill me-1"></i>${message}`);
  }
  $infoAlert.removeClass('d-none');
}

/**
 * 顯示確認 Modal
 */
function showConfirmModal() {
  // 移除之前的事件監聽器（避免重複綁定）
  $('#confirmModal').off('hidden.bs.modal');

  // 監聽確認 Modal 的確認按鈕點擊事件
  $('#confirmSubmitBtn').off('click').on('click', function () {
    // 關閉確認 Modal
    const confirmModal = bootstrap.Modal.getInstance(document.getElementById('confirmModal'));
    confirmModal.hide();

    // 提交表單到後端
    submitFormAjax();
  });

  // 顯示確認 Modal
  const confirmModal = new bootstrap.Modal(document.getElementById('confirmModal'));
  confirmModal.show();
}

/**
 * 處理表單提交成功
 */
function handleSubmitSuccess() {
  // 隱藏載入狀態
  $('.form-info-alert').addClass('d-none');

  // 重置表單
  $('#reportForm')[0].reset();

  // 移除之前的事件監聽器（避免重複綁定）
  $('#successModal').off('hidden.bs.modal');

  // 監聽 Modal 關閉事件，關閉後跳轉到首頁
  $('#successModal').on('hidden.bs.modal', function () {
    window.location.href = '/';
  });

  // 顯示成功 Modal
  const successModal = new bootstrap.Modal(document.getElementById('successModal'));
  successModal.show();
}

/**
 * 處理表單提交失敗
 */
function handleSubmitError(errorMessage) {
  // 隱藏載入狀態
  $('.form-info-alert').addClass('d-none');

  // 顯示錯誤訊息
  showFormInfo(errorMessage || '提交失敗，請稍後再試。', 'danger');

  // 恢復按鈕狀態
  const $submitBtn = $('#submit-btn');
  const $returnBtn = $('button[onclick="history.back()"]');

  $submitBtn.prop('disabled', false).html('<i class="bi bi-send me-1"></i>提交回報');
  $returnBtn.prop('disabled', false);

  // 滾動到頂部
  $('html, body').animate({ scrollTop: 0 }, 'smooth');
}

/**
 * AJAX 提交表單
 */
function submitFormAjax() {
  // 顯示載入狀態
  showLoadingState();

  // 獲取表單數據
  const formData = new FormData($('#reportForm')[0]);

  // 發送 AJAX 請求
  $.ajax({
    url: window.location.pathname,
    type: 'POST',
    data: formData,
    processData: false,
    contentType: false,
    headers: {
      'X-Requested-With': 'XMLHttpRequest'
    },
    success: function (response) {
      if (response.success) {
        handleSubmitSuccess();
      } else {
        handleSubmitError(response.message);
      }
    },
    error: function (xhr, status, error) {
      console.error('AJAX 錯誤:', error);
      handleSubmitError('網路錯誤，請稍後再試。');
    }
  });
}