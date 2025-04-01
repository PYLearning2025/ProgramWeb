$(document).ready(function(){
    $('form[id^="deleteForm_"]').on('submit', function(e){
        console.log('submit event triggered');
        e.preventDefault();
        var questionId = $(this).data('question-id');
        console.log("Form ID:", $(this).attr('id'), "對應的 Question ID:", questionId);
        if (confirm('確定要刪除這個題目嗎？')) {
            console.log('User confirmed deletion');
            $(this).off('submit').submit();
        } else {
            console.log('User cancelled deletion');
        }
    });
});