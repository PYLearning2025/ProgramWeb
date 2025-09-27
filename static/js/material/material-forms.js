// Material forms
(function ($, window) {
  'use strict';

  const MaterialForms = {
    init: function () {
      // 表單提交處理
      $('.material-form').on('submit', MaterialForms.handleFormSubmit);

      // 檔案上傳處理
      $('input[type="file"]').on('change', MaterialForms.handleFileSelect);

      // 表單驗證
      MaterialForms.setupFormValidation();
    },

    // 處理表單提交
    handleFormSubmit: function (e) {
      const $form = $(e.target);
      const $submitBtn = $form.find('button[type="submit"]');

      if (!MaterialForms.validateForm($form)) {
        e.preventDefault();
        return false;
      }

      // 如果是 AJAX 表單
      if ($form.hasClass('ajax-form')) {
        e.preventDefault();
        MaterialForms.submitFormAjax($form, $submitBtn);
      }
    },

    // AJAX 表單提交
    submitFormAjax: function ($form, $submitBtn) {
      const hideLoading = (window.MaterialBase && window.MaterialBase.showLoading)
        ? window.MaterialBase.showLoading($submitBtn)
        : function () { };

      const formData = new FormData($form[0]);

      $.ajax({
        url: $form.attr('action') || window.location.href,
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': MaterialForms.getCsrfToken()
        },
        success: function (data) {
          hideLoading();

          if (data.success) {
            if (window.MaterialBase && window.MaterialBase.showMessage) {
              window.MaterialBase.showMessage(data.message, 'success');
            }

            if (data.redirect) {
              setTimeout(() => {
                window.location.href = data.redirect;
              }, 1500);
            } else if (data.reset_form) {
              $form[0].reset();
            }
          } else {
            if (window.MaterialBase && window.MaterialBase.showMessage) {
              window.MaterialBase.showMessage(data.message || '操作失敗，請重試。', 'error');
            }

            // 顯示欄位錯誤
            if (data.errors) {
              MaterialForms.displayFieldErrors($form, data.errors);
            }
          }
        },
        error: function (xhr, status, error) {
          hideLoading();
          console.error('Error:', error);
          if (window.MaterialBase && window.MaterialBase.showMessage) {
            window.MaterialBase.showMessage('發生錯誤，請稍後再試。', 'error');
          }
        }
      });
    },

    // 表單驗證
    validateForm: function ($form) {
      let isValid = true;

      // 清除之前的錯誤
      MaterialForms.clearFormErrors($form);

      // 必填欄位驗證
      $form.find('[required]').each(function () {
        const $field = $(this);
        if (!$field.val().trim()) {
          MaterialForms.showFieldError($field, '此欄位為必填');
          isValid = false;
        }
      });

      // 檔案類型驗證
      $form.find('input[type="file"]').each(function () {
        const $input = $(this);
        const files = this.files;
        
        if (files.length > 0) {
          const file = files[0];
          const allowedTypes = $input.data('allowed-types');

          if (allowedTypes && !allowedTypes.split(',').includes(file.type)) {
            MaterialForms.showFieldError($input, '檔案類型不支援');
            isValid = false;
          }

          const maxSize = $input.data('max-size');
          if (maxSize && file.size > parseInt(maxSize)) {
            MaterialForms.showFieldError($input, '檔案大小超過限制');
            isValid = false;
          }
        }
      });

      return isValid;
    },

    // 設置表單驗證
    setupFormValidation: function () {
      $('.form-control, .form-select').on({
        blur: function () {
          MaterialForms.validateField($(this));
        },
        input: function () {
          MaterialForms.clearFieldError($(this));
        }
      });
    },

    // 驗證單一欄位
    validateField: function ($field) {
      let isValid = true;

      if ($field.prop('required') && !$field.val().trim()) {
        MaterialForms.showFieldError($field, '此欄位為必填');
        isValid = false;
      }

      if ($field.attr('type') === 'email' && $field.val() && !MaterialForms.isValidEmail($field.val())) {
        MaterialForms.showFieldError($field, '請輸入有效的電子郵件地址');
        isValid = false;
      }

      return isValid;
    },

    // 處理檔案選擇
    handleFileSelect: function (e) {
      const $input = $(e.target);
      const file = e.target.files[0];

      if (file) {
        const fileName = file.name;
        const fileSize = (file.size / 1024 / 1024).toFixed(2) + ' MB';

        // 更新檔案資訊顯示
        const $fileInfo = $input.parent().find('.file-info');
        if ($fileInfo.length) {
          $fileInfo.html(`
            <i class="bi bi-file-earmark me-2"></i>
            ${fileName} (${fileSize})
          `);
        }

        // 預覽圖片
        if (file.type.startsWith('image/')) {
          MaterialForms.showImagePreview($input, file);
        }
      }
    },

    // 顯示圖片預覽
    showImagePreview: function ($input, file) {
      const reader = new FileReader();
      reader.onload = function (e) {
        let $preview = $input.parent().find('.image-preview');
        if (!$preview.length) {
          $preview = $('<div>', {
            class: 'image-preview mt-2'
          });
          $input.parent().append($preview);
        }

        $preview.html(`
          <img src="${e.target.result}" alt="預覽" style="max-width: 200px; max-height: 200px; border-radius: 8px;">
        `);
      };
      reader.readAsDataURL(file);
    },

    // 顯示欄位錯誤
    showFieldError: function ($field, message) {
      MaterialForms.clearFieldError($field);

      $field.addClass('is-invalid');

      const $errorDiv = $('<div>', {
        class: 'error-message',
        text: message
      });

      $field.parent().append($errorDiv);
    },

    // 清除欄位錯誤
    clearFieldError: function ($field) {
      $field.removeClass('is-invalid');
      $field.parent().find('.error-message').remove();
    },

    // 清除所有表單錯誤
    clearFormErrors: function ($form) {
      $form.find('.is-invalid').each(function () {
        MaterialForms.clearFieldError($(this));
      });
    },

    // 顯示多個欄位錯誤
    displayFieldErrors: function ($form, errors) {
      $.each(errors, function (fieldName, errorMessages) {
        const $field = $form.find(`[name="${fieldName}"]`);
        if ($field.length) {
          MaterialForms.showFieldError($field, errorMessages[0]);
        }
      });
    },

    // 工具函數
    getCsrfToken: function () {
      return $('[name=csrfmiddlewaretoken]').val() || '';
    },

    isValidEmail: function (email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(email);
    }
  };

  $(document).ready(MaterialForms.init);

  // 暴露命名空間
  window.MaterialForms = MaterialForms;
})(jQuery, window);
