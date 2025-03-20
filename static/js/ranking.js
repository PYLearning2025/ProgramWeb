$(function(){
    function showTab(tabId) {
        const isQuestionTab = tabId === 'tab-questions';
        $('#rankingTitle').text(isQuestionTab ? '學生排行榜-出題數' : '學生排行榜-分數');
        $('.ranking-tab').hide();
        $('#' + tabId).show();
    }
    $('#questionRanking').on('click', function(){
        showTab('tab-questions');
    });
    $('#scoreRanking').on('click', function(){
        showTab('tab-scores');
    });
    // 預設顯示出題數排名
    showTab('tab-questions');
});