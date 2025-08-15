$(document).ready(function () {
  // 處理現有評分資料
  handleExistingReviewData();

  // 表單驗證
  validateForm();
});

/**
 * 處理現有評分資料，自動填充表單
 */
function handleExistingReviewData() {
  // 檢查是否有現有的評分資料
  if (typeof existingReview !== 'undefined' && existingReview && existingReview !== "None" && existingReview !== "null" && existingReview !== "") {
    try {
      // 解析現有評分資料
      const reviewData = JSON.parse(existingReview);

      // 填充評分分數
      if (reviewData.question_accuracy_score !== undefined) {
        $('select[name="question_accuracy_score"]').val(reviewData.question_accuracy_score);
      }
      if (reviewData.complexity_score !== undefined) {
        $('select[name="complexity_score"]').val(reviewData.complexity_score);
      }
      if (reviewData.practice_score !== undefined) {
        $('select[name="practice_score"]').val(reviewData.practice_score);
      }
      if (reviewData.answer_accuracy_score !== undefined) {
        $('select[name="answer_accuracy_score"]').val(reviewData.answer_accuracy_score);
      }
      if (reviewData.readability_score !== undefined) {
        $('select[name="readability_score"]').val(reviewData.readability_score);
      }

      // 填充建議文字
      if (reviewData.question_advice) {
        $('textarea[name="question_advice"]').val(reviewData.question_advice);
      }
      if (reviewData.answer_advice) {
        $('textarea[name="answer_advice"]').val(reviewData.answer_advice);
      }

      // 如果已經評分過，顯示提示訊息並禁用表單
      if (typeof isAlreadyReviewed !== 'undefined' && isAlreadyReviewed === "True") {
        showToast('您已經評分過此題目，以下是您的評分內容', 'info');
        disableForm();
      }

    } catch (error) {
      console.error('解析現有評分資料時發生錯誤:', error);
    }
  }
}

/**
 * 禁用表單編輯
 */
function disableForm() {
  // 禁用所有表單元素
  $('#reviewForm select, #reviewForm textarea').prop('disabled', true);
  $('#submitButton').prop('disabled', true).text('已評分');

  // 添加視覺提示
  $('#reviewForm').addClass('disabled-form');
}

function showLoading() {
  $("#submitButton").prop("disabled", true).text("提交中...");
}

function showOriginal() {
  $("#submitButton").prop("disabled", false).text("送出評分");
}

function validateForm() {
  const $form = $("#reviewForm");

  if ($form.length === 0) return;

  $form.on("submit", function (event) {
    showLoading();

    let isValid = true;
    const requiredFields = [
      "question_accuracy_score",
      "complexity_score",
      "practice_score",
      "answer_accuracy_score",
      "readability_score",
      "question_advice",
      "answer_advice"
    ];

    // 清除之前的錯誤狀態
    $form.find(".is-invalid").removeClass("is-invalid");
    $form.find(".invalid-feedback").remove();

    $.each(requiredFields, function (index, fieldName) {
      const $field = $form.find(`[name="${fieldName}"]`);
      if ($field.length) {
        const value = $field.val();
        if (!value || value.trim() === "" || (fieldName.includes("score") && parseInt(value) === 0)) {
          isValid = false;
          highlightInvalidField($field, fieldName);
        }
      }
    });

    // 如果表單無效，阻止提交
    if (!isValid) {
      event.preventDefault();
      showToast("表單中存在錯誤，請修正後再提交。", 'error');
      showOriginal();
      return;
    } else {
      // 表單有效，阻止默認提交並使用AJAX提交
      event.preventDefault();
      submitForm($form);
    }
  });
}

/**
 * 提交表單到後端
 * @param {jQuery} $form - 表單 jQuery 元素
 */
function submitForm($form) {
  $('#submitButton').prop("disabled", true).text("提交中...");

  // 獲取當前題目ID
  const questionId = window.location.pathname.split('/').filter(Boolean).pop();

  $.ajax({
    url: `/reviews/submit/${questionId}/`,
    method: 'POST',
    data: $form.serialize(),
    headers: {
      'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val(),
      'X-Requested-With': 'XMLHttpRequest'
    },
    success: function (response) {
      if (response.success) {
        showToast(response.message, 'success');
        // 延遲跳轉，讓用戶看到成功消息
        setTimeout(() => {
          window.location.href = response.redirect_url;
        }, 1500);
      } else {
        $('#submitButton').prop("disabled", false).text("送出評分");
        showToast(response.message, 'error');
        showOriginal();
      }
    },
    error: function (xhr, status, error) {
      console.error('提交失敗:', error);
      $('#submitButton').prop("disabled", false).text("送出評分");

      // 處理後端返回的錯誤信息
      if (xhr.responseJSON && xhr.responseJSON.message) {
        showToast(xhr.responseJSON.message, 'error');
      } else {
        showToast('提交失敗，請稍後再試。', 'error');
      }
      showOriginal();
    }
  });
}

/**
 * 高亮顯示無效的字段
 * @param {jQuery} $field - 無效的表單字段 jQuery 元素
 * @param {string} fieldName - 字段名稱
 */
function highlightInvalidField($field, fieldName) {
  $field.addClass("is-invalid");

  // 添加警告消息
  const $parentElement = $field.parent();
  let $feedbackElement = $parentElement.find(".invalid-feedback");

  if ($feedbackElement.length === 0) {
    let errorMessage = "此欄位為必填";

    // 根據字段名稱提供具體的錯誤信息
    if (fieldName.includes("score")) {
      errorMessage = "此欄位必須大於0";
    } else if (fieldName.includes("advice")) {
      errorMessage = "建議內容不得為空";
    }

    $feedbackElement = $("<div>", {
      class: "invalid-feedback d-block",
      text: errorMessage,
    });
    $parentElement.append($feedbackElement);
  }

  // 檢查是否已經綁定過 focus 事件監聽器
  if (!$field.data("focus-listener-bound")) {
    // 添加聚焦時移除錯誤狀態
    $field.on("focus", function () {
      $(this).removeClass("is-invalid");
      const $parent = $(this).parent();
      const $feedback = $parent.find(".invalid-feedback");
      if ($feedback.length) {
        $feedback.remove();
      }
    });

    // 標記已綁定事件監聽器
    $field.data("focus-listener-bound", true);
  }
}

function showToast(message, type = 'info') {
  const toastElement = document.getElementById('liveToast');
  const messageElement = document.getElementById('toastMessage');

  if (!toastElement || !messageElement) {
    // 如果沒有 toast 元素，創建一個簡單的 alert
    alert(message);
    return;
  }

  // 設置消息內容
  messageElement.textContent = message;

  // 設置背景顏色
  toastElement.className = 'toast align-items-center text-white border-0';
  if (type === 'error') {
    toastElement.classList.add('bg-danger');
  } else if (type === 'success') {
    toastElement.classList.add('bg-success');
  } else if (type === 'warning') {
    toastElement.classList.add('bg-warning');
  } else {
    toastElement.classList.add('bg-info');
  }

  // 使用Bootstrap標準API
  const toastBootstrap = bootstrap.Toast.getOrCreateInstance(toastElement, { delay: 3000 });
  toastBootstrap.show();
}

