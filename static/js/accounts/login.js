function showLoading() {
  $('.login-form').find('input').prop('disabled', true);
  $('.login-submit-btn').prop('disabled', true);
  $('.login-submit-btn').text('登入中...');
}

function showOriginal() {
  $('.login-form').find('input').prop('disabled', false);
  $('.login-submit-btn').prop('disabled', false);
  $('.login-submit-btn').text('登入');
}

$(document).ready(function () {
  $('#login-form').on('submit', function (e) {
    e.preventDefault();
    showLoading();
    const form = $(this);
    const formData = form.serialize();
    $.ajax({
      url: window.location.pathname,
      type: 'POST',
      data: formData,
      dataType: 'json',
      success: function (res) {
        if (res.success) {
          showToast(res.message, 'success');
          if (res.redirect_url) {
            setTimeout(() => {
              window.location.href = res.redirect_url;
            }, 1500);
          }
        } else {
          showToast(res.message, 'error');
          showOriginal();
        }
      },
      error: function (xhr, status, error) {
        try {
          var response = JSON.parse(xhr.responseText);
          if (response.message) {
            showToast(response.message, 'error');
            showOriginal();
          } else {
            showToast('登入失敗，請稍後再試', 'error');
            showOriginal();
          }
        } catch (e) {
          showToast('登入失敗，請稍後再試', 'error');
          showOriginal();
        }
      }
    });
  });
});

// 簡化的toast函數
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