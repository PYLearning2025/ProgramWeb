$(document).ready(function() {
    $('form').on('submit', function(event) {
        event.preventDefault();

        // 將 CodeMirror 的內容同步回 textarea
        if (window.answerEditor) {
            window.answerEditor.save();
        }

        const isConfirmed = confirm("確定要提交答案嗎？\n提交答案之後就不可以修改了喔");
        
        if (isConfirmed) {
            const formData = new FormData(this);
            
            $.ajax({
                url: window.location.href,
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                success: function(data) {
                    if (data.error) {
                        alert(data.error);
                        window.location.href = '/question/assignment/';
                    } else if (data.success) {
                        alert(data.success);
                        window.location.href = '/question/assignment/';
                    }
                },
                error: function(xhr, status, error) {
                    console.error('Error:', error);
                }
            });
        }
    });
});