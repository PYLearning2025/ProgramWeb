$(document).ready(function () {
  $(".option-btn").on("click", function () {
    // 禁用所有按鈕
    $(".option-btn").prop("disabled", true);

    // 取得被點擊按鈕的值
    var clickedValue = $(this).val();

    $.ajax({
      url: "/game/check_answer/",
      type: "POST",
      data: {
        selected_option: clickedValue,
        question_id: question_id
      },
      headers: {
        "X-CSRFToken": csrf_token
      },
      success: function (response) {
        if (response.result === "correct") {
          // 答案正確，跳轉到 draw 頁面
          window.location.href = "/game/draw/";
        } else {
          // 答案錯誤，跳轉到 wrong 頁面
          window.location.href = "/game/wrong/";
        }
      },
      error: function (xhr, status, error) {
        console.error("AJAX 錯誤:", status, error);
      }
    });
  });
});