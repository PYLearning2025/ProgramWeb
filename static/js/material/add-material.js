(function () {
  var $form = $('#addMaterialForm');
  if ($form.length === 0) return;
  
  function getCsrfToken() {
    var $el = $('[name=csrfmiddlewaretoken]');
    return $el.length ? $el.val() : '';
  }

  $form.on('submit', function (e) {
    e.preventDefault();
    var formData = new FormData(this);
    var actionUrl = $(this).attr('action') || window.location.href;

    formData.append('csrfmiddlewaretoken', getCsrfToken());
    
    $.ajax({
      url: actionUrl,
      type: 'POST',
      data: formData,
      processData: false,
      contentType: false,
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      },
      dataType: 'json',
      success: function(data) {
        if (data && data.success) {
          alert(data.message);
          if (data.redirect) {
            window.location.href = data.redirect;
          }
        } else {
          alert((data && data.message) || '發生錯誤，請稍後再試。');
        }
      },
      error: function(xhr, status, error) {
        console.error('Error:', error);
        var errorMessage = '發生錯誤，請稍後再試。';
        
        try {
          var response = JSON.parse(xhr.responseText);
          errorMessage = response.message || errorMessage;
        } catch (e) {
          if (xhr.responseText) {
            errorMessage = xhr.responseText;
          }
        }
        
        alert(errorMessage);
      }
    });
  });
})();
