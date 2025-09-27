// Material Base
(function ($, window) {
  'use strict';
  
  const MaterialBase = {
    init: function () {
      // 搜尋框自動對焦
      const $searchInput = $('.search-box');
      if ($searchInput.length) {
        $searchInput.on('keypress', function (e) {
          if (e.key === 'Enter') {
            $(this).closest('form').submit();
          }
        });
      }

      // 卡片懸停效果增強
      $('.material-card').hover(
        function () {
          $(this).css('transform', 'translateY(-4px)');
        },
        function () {
          $(this).css('transform', 'translateY(0)');
        }
      );

      // 確認刪除對話框
      $('.btn-delete').on('click', function (e) {
        if (!confirm('確定要刪除此項目嗎？此操作無法復原。')) {
          e.preventDefault();
        }
      });

      // 表格排序功能
      $('.sortable').css('cursor', 'pointer').on('click', function () {
        MaterialBase.sortTable($(this));
      });

      // 批量操作功能
      const $selectAllCheckbox = $('#selectAll');
      if ($selectAllCheckbox.length) {
        $selectAllCheckbox.on('change', function () {
          const isChecked = $(this).is(':checked');
          $('.item-checkbox').prop('checked', isChecked);
          MaterialBase.updateBatchActions();
        });
      }

      $('.item-checkbox').on('change', MaterialBase.updateBatchActions);
    },

    // 表格排序函數
    sortTable: function ($header) {
      const $table = $header.closest('table');
      const $tbody = $table.find('tbody');
      const $rows = $tbody.find('tr');
      const columnIndex = $header.index();
      const isAscending = !$header.hasClass('sort-asc');

      // 清除其他列的排序標記
      $table.find('th').removeClass('sort-asc sort-desc');

      // 添加當前排序標記
      $header.addClass(isAscending ? 'sort-asc' : 'sort-desc');

      // 排序行
      const sortedRows = $rows.toArray().sort((a, b) => {
        const aValue = $(a).children().eq(columnIndex).text().trim();
        const bValue = $(b).children().eq(columnIndex).text().trim();

        if (isAscending) {
          return aValue.localeCompare(bValue);
        } else {
          return bValue.localeCompare(aValue);
        }
      });

      // 重新插入排序後的行
      $tbody.append(sortedRows);
    },

    // 更新批量操作按鈕狀態
    updateBatchActions: function () {
      const $checkedBoxes = $('.item-checkbox:checked');
      const $batchActions = $('.batch-actions');

      if ($batchActions.length) {
        if ($checkedBoxes.length > 0) {
          $batchActions.show();
        } else {
          $batchActions.hide();
        }
      }
    },

    // 顯示載入狀態
    showLoading: function ($element) {
      if (!$element || !$element.length) {
        return function () { };
      }
      const originalText = $element.text();
      $element.prop('disabled', true);
      $element.html('<i class="bi bi-spinner-border-sm me-2"></i>處理中...');

      return function () {
        $element.prop('disabled', false);
        $element.text(originalText);
      };
    },

    // 顯示提示訊息
    showMessage: function (message, type = 'info') {
      const alertClass = {
        'success': 'alert-success',
        'error': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info'
      };

      const $alertDiv = $('<div>', {
        class: `alert ${alertClass[type]} alert-dismissible fade show`,
        html: `
          ${message}
          <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `
      });

      const $container = $('.container-fluid').length ? $('.container-fluid') : $('body');
      $container.prepend($alertDiv);

      // 自動隱藏
      setTimeout(() => {
        $alertDiv.remove();
      }, 5000);
    }
  };

  $(document).ready(MaterialBase.init);

  // 暴露命名空間
  window.MaterialBase = MaterialBase;
})(jQuery, window);
