function handleRegisterSubmit(e) {
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
            if(res.success) {
                window.location.href = '/login';
            }
        },
        error: function() {
            alert('伺服器錯誤，請稍後再試');
        }
    });
}

function handleCategoryChange() {
    var val = $('#category').val();
    if(val && parseInt(val) <= 5) {
        // 學生
        $('.student-field').removeClass('d-none');
        $('.social-field').addClass('d-none');
        $('#id_username').attr('required', true);
        $('#id_company, #id_job').removeAttr('required');
    } else if(val == '6') {
        // 社會人士
        $('.student-field').addClass('d-none');
        $('.social-field').removeClass('d-none');
        $('#id_company, #id_job').attr('required', true);
    } else {
        $('.student-field, .social-field').addClass('d-none');
        $('#id_username, #id_company, #id_job').removeAttr('required');
    }
}

// 設定username label
function setUsernameLabel() {
    var val = $('#category').val();
    if(val && parseInt(val) <= 5) {
        $('label[for="id_username"]').text('學號');
    } else {
        $('label[for="id_username"]').text('帳號');
    }
}

$(function() {
    $('#register-form').on('submit', handleRegisterSubmit);
    $('#category').on('change', handleCategoryChange);
    $('#category').on('change', setUsernameLabel);
    handleCategoryChange();
});

$(document).ready(function() {
    $('#category').change(setUsernameLabel);
    setUsernameLabel(); // 頁面載入時也執行一次
});
