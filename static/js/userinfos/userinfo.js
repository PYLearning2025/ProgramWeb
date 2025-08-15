$(document).ready(function () {
  const $form = $('#userinfo-form');
  const $editBtn = $('#edit-btn');
  const $saveBtn = $('#save-btn');
  const $cancelBtn = $('#cancel-btn');
  const $fields = $form.find('input, select, textarea').not('[type=hidden], #id_profile_img');
  const $profileImgInput = $('#id_profile_img');
  const $profileImg = $('#profile-img');

  let editing = false;

  // 編輯模式切換
  function toggleEditMode(isEditing) {
    editing = isEditing;
    $fields.prop('disabled', !isEditing);
    $editBtn.toggleClass('d-none', isEditing);
    $saveBtn.toggleClass('d-none', !isEditing);
    $cancelBtn.toggleClass('d-none', !isEditing);
  }

  toggleEditMode(false); // 初始不允許編輯欄位（除了頭像）

  // 編輯按鈕
  $editBtn.on('click', function () {
    toggleEditMode(true);
  });

  // 取消按鈕
  $cancelBtn.on('click', function () {
    toggleEditMode(false);
    $form[0].reset();
  });

  // 表單送出（含一般儲存與頭像變更）
  function submitForm(formData) {
    $saveBtn.prop('disabled', true).text('儲存中...');
    $.ajax({
      url: '',
      method: 'POST',
      data: formData,
      processData: false,
      contentType: false,
      headers: {
        'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
      },
      success: function (resp) {
        if (resp.success) {
          showToast('儲存成功', 'success');
          setTimeout(function () {
            window.location.reload();
          }, 1000);
        } else {
          showToast('儲存失敗', 'danger');
          $saveBtn.prop('disabled', false).text('儲存');
        }
      },
      error: function (xhr, status, error) {
        console.error('AJAX Error:', xhr.responseText);
        showToast('儲存失敗', 'danger');
        $saveBtn.prop('disabled', false).text('儲存');
      }
    });
  }

  // 儲存按鈕送出
  $form.on('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(this);
    submitForm(formData);
  });

  $profileImgInput.on('change', function () {
    if (this.files && this.files[0]) {
      const reader = new FileReader();
      reader.onload = function (e) {
        $profileImg.attr('src', e.target.result);
      };
      reader.readAsDataURL(this.files[0]);

      // 只送 profile_img 到新 API
      const formData = new FormData();
      formData.append('profile_img', this.files[0]);
      formData.append('csrfmiddlewaretoken', $('[name=csrfmiddlewaretoken]').val());

      $.ajax({
        url: '/userinfo/updateimg/',
        method: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        headers: {
          'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
        },
        success: function (resp) {
          if (resp.success) {
            showToast('頭像已更新', 'success');
            // 可選：直接更新 img src，不 reload
            if (resp.img_url) {
              $profileImg.attr('src', resp.img_url + '?t=' + Date.now());
            }
          } else {
            showToast('頭像更新失敗', 'danger');
          }
        },
        error: function (xhr, status, error) {
          console.error('AJAX Error:', xhr.responseText);
          showToast('頭像更新失敗', 'danger');
        }
      });
    }
  });
});

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