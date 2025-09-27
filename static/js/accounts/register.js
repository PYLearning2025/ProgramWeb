// 簡單的Toast通知功能
function showLoading() {
  $('#register-form').find('input').prop('disabled', true);
  $('#register-submit-btn').prop('disabled', true);
  $('#register-submit-btn').text('註冊中...');
}

function showOriginal() {
  $('#register-form').find('input').prop('disabled', false);
  $('#register-submit-btn').prop('disabled', false);
  $('#register-submit-btn').text('註冊');
}

function handleRegisterSubmit(e) {
  e.preventDefault();
  showLoading();
  const formData = new FormData();
  const csrfToken = $('[name=csrfmiddlewaretoken]').val();
  formData.append('csrfmiddlewaretoken', csrfToken);
  const form = $('#register-form');
  form.find('input, select, textarea').each(function () {
    const field = $(this);
    const name = field.attr('name');
    const value = field.val();
    if (name && value !== undefined && value !== null) {
      formData.append(name, value);
    }
  });
  const serializedData = new URLSearchParams(formData).toString();
  $.ajax({
    url: window.location.pathname,
    type: 'POST',
    data: serializedData,
    headers: {
      'X-CSRFToken': csrfToken,
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    dataType: 'json',
    success: function (res) {
      if (res.success) {
        showToast(res.message, 'success');
        setTimeout(() => {
          window.location.href = '/login';
        }, 1500);
      } else {
        showToast(res.message, 'error');
        showOriginal();
      }
    },
    error: function (xhr, status, error) {
      try {
        const response = JSON.parse(xhr.responseText);
        if (response.message) {
          showToast(response.message, 'error');
          showOriginal();
        } else {
          showToast('註冊失敗，請稍後再試', 'error');
          showOriginal();
        }
      } catch (e) {
        showToast('伺服器錯誤，請稍後再試', 'error');
        showOriginal();
      }
    }
  });
}

function handleCategoryChange() {
  var val = $('#category').val();
  if (val && parseInt(val) <= 5) {
    // 學生
    $('.student-field').removeClass('d-none');
    $('.social-field').addClass('d-none');
    $('#id_username').attr('required', true);
    $('#id_company, #id_job').removeAttr('required');
  } else if (val == '6') {
    // 社會人士
    $('.student-field').addClass('d-none');
    $('.social-field').removeClass('d-none');
    $('#id_company, #id_job').attr('required', true);
  } else {
    $('.student-field, .social-field').addClass('d-none');
    $('#id_username, #id_company, #id_job').removeAttr('required');
  }
}

// 設定username label
function setUsernameLabel() {
  var val = $('#category').val();
  if (val && parseInt(val) <= 5) {
    $('label[for="id_username"]').text('學號');
  } else {
    $('label[for="id_username"]').text('帳號');
  }
}

$(function () {
  $('#register-form').on('submit', handleRegisterSubmit);
  $('#category').on('change', handleCategoryChange);
  $('#category').on('change', setUsernameLabel);
  handleCategoryChange();
});

$(document).ready(function () {
  $('#category').change(setUsernameLabel);
  setUsernameLabel(); // 頁面載入時也執行一次
});

// Toast
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
