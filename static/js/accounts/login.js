$(function() {
    $('#login-form').on('submit', function(e) {
        e.preventDefault();
        var form = $(this);
        var formData = form.serialize();
        $.ajax({
            url: window.location.pathname,
            type: 'POST',
            data: formData,
            dataType: 'json',
            success: function(res) {
                alert(res.message);
                if(res.success && res.redirect_url) {
                    window.location.href = res.redirect_url;
                }
            },
            error: function() {
                alert('伺服器錯誤，請稍後再試');
            }
        });
    });
});