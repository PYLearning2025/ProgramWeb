$(document).ready(function () {
  $("#draw-button").on("click", function () {
    // 禁用所有按鈕
    $("#draw-button").prop("disabled", true);
    $.ajax({
      url: "/game/draw_card/",
      type: "POST",
      headers: {
        "X-CSRFToken": csrf_token,
      },
      success: function (response) {
        window.location.href = response.redirect_url;
      },
      error: function (xhr, status, error) {
        console.error("AJAX 錯誤:", status, error);
      },
    });
  });
});
