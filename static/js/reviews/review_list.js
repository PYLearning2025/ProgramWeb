// 顯示 toast
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

$(document).ready(function () {
  // 分頁設定
  const itemsPerPage = 6; // 每頁顯示6個題目
  let currentPage = 1;
  let filteredItems = []; // 存儲篩選後的項目

  // 篩選和搜尋功能初始化
  initializeFilters();
  initializePagination();

  // 評分狀態篩選
  $('.status-filter').on('click', function () {
    const status = $(this).data('status');

    // 更新按鈕狀態
    $('.status-filter').removeClass('active');
    $(this).addClass('active');

    // 重置到第一頁
    currentPage = 1;

    // 執行篩選
    filterQuestions(status, getCurrentSearchTerm());
  });

  // 搜尋功能
  $('#search-btn').on('click', function () {
    performSearch();
  });

  $('#search-input').on('keypress', function (e) {
    if (e.which === 13) { // Enter 鍵
      performSearch();
    }
  });

  // 實時搜尋 (延遲執行)
  let searchTimeout;
  $('#search-input').on('input', function () {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      performSearch();
    }, 300);
  });

  function performSearch() {
    const searchTerm = $('#search-input').val().trim();
    const status = getCurrentStatus();

    // 重置到第一頁
    currentPage = 1;
    filterQuestions(status, searchTerm);
  }

  // 重置篩選
  $('#reset-filters').on('click', function () {
    resetFilters();
  });

  // 卡片懸停效果
  $(document).on('mouseenter', '.question-card', function () {
    $(this).find('.question-title a').addClass('text-primary');
  });

  $(document).on('mouseleave', '.question-card', function () {
    $(this).find('.question-title a').removeClass('text-primary');
  });

  // 分頁點擊事件
  $(document).on('click', '.pagination .page-link', function (e) {
    e.preventDefault();
    const $this = $(this);
    const $parent = $this.parent();

    if ($parent.hasClass('disabled') || $parent.hasClass('active')) {
      return;
    }

    const action = $this.data('action');

    if (action === 'prev') {
      if (currentPage > 1) {
        currentPage--;
        updatePagination();
      }
    } else if (action === 'next') {
      const totalPages = Math.ceil(filteredItems.length / itemsPerPage);
      if (currentPage < totalPages) {
        currentPage++;
        updatePagination();
      }
    } else {
      const page = parseInt($this.text());
      if (!isNaN(page)) {
        currentPage = page;
        updatePagination();
      }
    }
  });

  function initializeFilters() {
    // 使用 Bootstrap 的列選擇器，排除空狀態和無結果狀態
    const $questionColumns = $('#questions-container > .col-12.col-md-6.col-xl-4');
    filteredItems = $questionColumns.toArray();



    updateFilterStats();
    updatePagination();
  }

  function initializePagination() {
    updatePagination();
  }

  function filterQuestions(status, searchTerm) {
    const $questionColumns = $('#questions-container > .col-12.col-md-6.col-xl-4');
    const $noResults = $('#no-results');
    const $questionsContainer = $('#questions-container');
    const $paginationWrapper = $('#pagination-wrapper');

    // 添加加載效果
    $questionsContainer.addClass('loading');

    setTimeout(() => {
      filteredItems = [];

      $questionColumns.each(function () {
        const $column = $(this);
        const itemStatus = $column.data('status');
        const itemReviewed = $column.data('reviewed') === 'true'; // 正確處理布林值
        const itemTitle = $column.data('title') || '';
        const itemContent = $column.data('content') || '';

        // 檢查狀態篩選
        const statusMatch = status === 'all' || itemStatus === status;

        // 檢查搜尋條件
        const searchMatch = !searchTerm ||
          itemTitle.includes(searchTerm.toLowerCase()) ||
          itemContent.includes(searchTerm.toLowerCase());

        if (statusMatch && searchMatch) {
          filteredItems.push(this);

          // 高亮搜尋結果
          if (searchTerm) {
            highlightSearchTerm($column, searchTerm);
          } else {
            removeHighlight($column);
          }
        } else {
          $column.hide();
        }
      });

      // 顯示/隱藏無結果提示
      if (filteredItems.length === 0) {
        $questionsContainer.hide();
        $noResults.show();
        $paginationWrapper.hide();
      } else {
        $questionsContainer.show();
        $noResults.hide();
        $paginationWrapper.show();

        // 更新分頁
        updatePagination();
      }

      // 更新統計信息
      updateFilterStats(filteredItems.length, status, searchTerm);

      // 移除加載效果
      $questionsContainer.removeClass('loading');

      // 滾動到結果區域
      if (searchTerm || status !== 'all') {
        $('html, body').animate({
          scrollTop: $('#questions-container').offset().top - 100
        }, 500);
      }
    }, 100);
  }

  function updatePagination() {
    const totalItems = filteredItems.length;
    const totalPages = Math.ceil(totalItems / itemsPerPage);

    // 隱藏所有題目列
    $('#questions-container > .col-12.col-md-6.col-xl-4').hide();

    // 計算當前頁要顯示的項目
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = Math.min(startIndex + itemsPerPage, totalItems);

    // 顯示當前頁的項目
    for (let i = startIndex; i < endIndex; i++) {
      $(filteredItems[i]).show();
    }

    // 更新分頁控件
    updatePaginationControls(totalPages);

    // 更新統計信息
    updateFilterStats(filteredItems.length, getCurrentStatus(), getCurrentSearchTerm());

    // 滾動到頂部
    if (totalPages > 1) {
      $('html, body').animate({
        scrollTop: $('#questions-container').offset().top - 100
      }, 300);
    }
  }

  function updatePaginationControls(totalPages) {
    const $paginationWrapper = $('#pagination-wrapper');

    if (totalPages <= 1) {
      $paginationWrapper.hide();
      return;
    }

    $paginationWrapper.show();

    let paginationHtml = '';

    // 上一頁按鈕
    paginationHtml += `
            <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" data-action="prev" aria-label="Previous">
                    <i class="bi bi-chevron-left"></i>
                </a>
            </li>
        `;

    // 頁碼按鈕邏輯
    const maxVisiblePages = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

    // 調整起始頁
    if (endPage - startPage + 1 < maxVisiblePages) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }

    // 如果不是從第1頁開始，添加第1頁和省略號
    if (startPage > 1) {
      paginationHtml += `<li class="page-item"><a class="page-link" href="#">1</a></li>`;
      if (startPage > 2) {
        paginationHtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
      }
    }

    // 添加頁碼
    for (let i = startPage; i <= endPage; i++) {
      paginationHtml += `
                <li class="page-item ${i === currentPage ? 'active' : ''}">
                    <a class="page-link" href="#">${i}</a>
                </li>
            `;
    }

    // 如果不是到最後一頁，添加省略號和最後一頁
    if (endPage < totalPages) {
      if (endPage < totalPages - 1) {
        paginationHtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
      }
      paginationHtml += `<li class="page-item"><a class="page-link" href="#">${totalPages}</a></li>`;
    }

    // 下一頁按鈕
    paginationHtml += `
            <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" data-action="next" aria-label="Next">
                    <i class="bi bi-chevron-right"></i>
                </a>
            </li>
        `;

    $('.pagination').html(paginationHtml);
  }

  function highlightSearchTerm($item, searchTerm) {
    if (!searchTerm) return;

    const $title = $item.find('.question-title a');
    const $content = $item.find('.question-content');

    const regex = new RegExp(`(${escapeRegExp(searchTerm)})`, 'gi');

    // 高亮標題
    const originalTitle = $title.text();
    const highlightedTitle = originalTitle.replace(regex, '<span class="highlight">$1</span>');
    $title.html(highlightedTitle);

    // 高亮內容
    const originalContent = $content.text();
    const highlightedContent = originalContent.replace(regex, '<span class="highlight">$1</span>');
    $content.html(highlightedContent);
  }

  function removeHighlight($item) {
    const $title = $item.find('.question-title a');
    const $content = $item.find('.question-content');

    $title.html($title.text());
    $content.html($content.text());
  }

  function updateFilterStats(visibleCount, status, searchTerm) {
    const totalCount = $('#questions-container > .col-12.col-md-6.col-xl-4').length;
    let statsText = '';

    if (visibleCount === undefined) {
      visibleCount = totalCount;
    }

    if (status === 'all' && !searchTerm) {
      statsText = `顯示全部 ${totalCount} 道題目`;
    } else {
      const statusText = getStatusText(status);
      const searchText = searchTerm ? `包含 "${searchTerm}" 的` : '';
      statsText = `顯示 ${searchText}${statusText}題目：${visibleCount} / ${totalCount} 道`;
    }

    // 添加分頁信息
    if (visibleCount > itemsPerPage) {
      const totalPages = Math.ceil(visibleCount / itemsPerPage);
      statsText += ` (第 ${currentPage} 頁，共 ${totalPages} 頁)`;
    }

    $('#filter-stats').text(statsText);
  }

  function getStatusText(status) {
    switch (status) {
      case 'pending': return '待評分';
      case 'reviewed': return '已評分';
      default: return '';
    }
  }

  function getCurrentStatus() {
    return $('.status-filter.active').data('status') || 'all';
  }

  function getCurrentSearchTerm() {
    return $('#search-input').val().trim();
  }

  function resetFilters() {
    // 重置狀態篩選
    $('.status-filter').removeClass('active');
    $('.status-filter[data-status="all"]').addClass('active');

    // 清除搜尋
    $('#search-input').val('');

    // 重置頁碼
    currentPage = 1;

    // 移除高亮
    $('#questions-container > .col-12.col-md-6.col-xl-4').each(function () {
      removeHighlight($(this));
    });

    // 重新篩選
    filterQuestions('all', '');
  }

  function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }
});

// 頁面加載完成後的動畫效果
$(window).on('load', function () {
  $('#questions-container > .col-12.col-md-6.col-xl-4').each(function (index) {
    $(this).css('animation-delay', `${index * 0.1}s`);
  });
});