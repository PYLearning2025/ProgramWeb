$(document).ready(function() {
    // 分頁設定
    const itemsPerPage = 6; // 每頁顯示6個題目
    let currentPage = 1;
    let filteredItems = []; // 存儲篩選後的項目
    
    // 篩選和搜尋功能初始化
    initializeFilters();
    initializePagination();
    
    // 難度篩選
    $('.level-filter').on('click', function() {
        const level = $(this).data('level');
        
        // 更新按鈕狀態
        $('.level-filter').removeClass('active');
        $(this).addClass('active');
        
        // 重置到第一頁
        currentPage = 1;
        
        // 執行篩選
        filterQuestions(level, getCurrentSearchTerm());
    });
    
    // 搜尋功能
    $('#search-btn').on('click', function() {
        performSearch();
    });
    
    $('#search-input').on('keypress', function(e) {
        if (e.which === 13) { // Enter 鍵
            performSearch();
        }
    });
    
    // 實時搜尋 (延遲執行)
    let searchTimeout;
    $('#search-input').on('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            performSearch();
        }, 300);
    });
    
    function performSearch() {
        const searchTerm = $('#search-input').val().trim();
        const level = getCurrentLevel();
        
        // 重置到第一頁
        currentPage = 1;
        filterQuestions(level, searchTerm);
    }

    // 重置篩選
    $('#reset-filters').on('click', function() {
        resetFilters();
    });
    
    // 卡片懸停效果
    $(document).on('mouseenter', '.question-card', function() {
        $(this).find('.question-title a').addClass('text-primary');
    });
    
    $(document).on('mouseleave', '.question-card', function() {
        $(this).find('.question-title a').removeClass('text-primary');
    });

    // 分頁點擊事件
    $(document).on('click', '.pagination .page-link', function(e) {
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

    function filterQuestions(level, searchTerm) {
        const $questionColumns = $('#questions-container > .col-12.col-md-6.col-xl-4');
        const $noResults = $('#no-results');
        const $questionsContainer = $('#questions-container');
        const $paginationWrapper = $('#pagination-wrapper');
        
        // 添加加載效果
        $questionsContainer.addClass('loading');
        
        setTimeout(() => {
            filteredItems = [];
            
            $questionColumns.each(function() {
                const $column = $(this);
                const itemLevel = $column.data('level');
                const itemTitle = $column.data('title') || '';
                const itemDescription = $column.data('description') || '';
                
                // 檢查難度篩選
                const levelMatch = level === 'all' || itemLevel === level;
                
                // 檢查搜尋條件
                const searchMatch = !searchTerm || 
                    itemTitle.includes(searchTerm.toLowerCase()) || 
                    itemDescription.includes(searchTerm.toLowerCase());
                
                if (levelMatch && searchMatch) {
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
            updateFilterStats(filteredItems.length, level, searchTerm);
            
            // 移除加載效果
            $questionsContainer.removeClass('loading');
            
            // 滾動到結果區域
            if (searchTerm || level !== 'all') {
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
        updateFilterStats(filteredItems.length, getCurrentLevel(), getCurrentSearchTerm());
        
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
        const $description = $item.find('.question-description');
        
        const regex = new RegExp(`(${escapeRegExp(searchTerm)})`, 'gi');
        
        // 高亮標題
        const originalTitle = $title.text();
        const highlightedTitle = originalTitle.replace(regex, '<span class="highlight">$1</span>');
        $title.html(highlightedTitle);
        
        // 高亮描述
        const originalDescription = $description.text();
        const highlightedDescription = originalDescription.replace(regex, '<span class="highlight">$1</span>');
        $description.html(highlightedDescription);
    }

    function removeHighlight($item) {
        const $title = $item.find('.question-title a');
        const $description = $item.find('.question-description');
        
        $title.html($title.text());
        $description.html($description.text());
    }

    function updateFilterStats(visibleCount, level, searchTerm) {
        const totalCount = $('#questions-container > .col-12.col-md-6.col-xl-4').length;
        let statsText = '';
        
        if (visibleCount === undefined) {
            visibleCount = totalCount;
        }
        
        if (level === 'all' && !searchTerm) {
            statsText = `顯示全部 ${totalCount} 道題目`;
        } else {
            const levelText = getLevelText(level);
            const searchText = searchTerm ? `包含 "${searchTerm}" 的` : '';
            statsText = `顯示 ${searchText}${levelText}題目：${visibleCount} / ${totalCount} 道`;
        }
        
        // 添加分頁信息
        if (visibleCount > itemsPerPage) {
            const totalPages = Math.ceil(visibleCount / itemsPerPage);
            statsText += ` (第 ${currentPage} 頁，共 ${totalPages} 頁)`;
        }
        
        $('#filter-stats').text(statsText);
    }

    function getLevelText(level) {
        switch(level) {
            case 'easy': return '簡單';
            case 'medium': return '中等';
            case 'hard': return '困難';
            default: return '';
        }
    }

    function getCurrentLevel() {
        return $('.level-filter.active').data('level') || 'all';
    }

    function getCurrentSearchTerm() {
        return $('#search-input').val().trim();
    }

    function resetFilters() {
        // 重置難度篩選
        $('.level-filter').removeClass('active');
        $('.level-filter[data-level="all"]').addClass('active');
        
        // 清除搜尋
        $('#search-input').val('');
        
        // 重置頁碼
        currentPage = 1;
        
        // 移除高亮
        $('#questions-container > .col-12.col-md-6.col-xl-4').each(function() {
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
$(window).on('load', function() {
    $('#questions-container > .col-12.col-md-6.col-xl-4').each(function(index) {
        $(this).css('animation-delay', `${index * 0.1}s`);
    });
});