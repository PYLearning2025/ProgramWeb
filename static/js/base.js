$(document).ready(function () {
  const $header = $('header');
  const $toggleButton = $('.navbar-toggler');
  const $navMenu = $('nav ul');

  // 切換 navbar 的 active 狀態
  $toggleButton.on('click', function () {
    $navMenu.toggleClass('active');
  });

  // 滾動時處理 header 的透明度
  $(window).on('scroll', function () {
    if ($(window).scrollTop() > 50) {
      $header.addClass('scrolled');
    } else {
      $header.removeClass('scrolled');
    }
  });

  // 登出按鈕觸發確認框
  const $logoutButton = $('.logout-btn');
  const $modal = $('.logout-modal');
  const closeModal = function () {
    $modal.fadeOut(200);
  };

  const $yesButton = $('.yes-btn');
  const $noButton = $('.no-btn');

  // 顯示登出確認框
  $logoutButton.on('click', function (e) {
    e.preventDefault(); // 防止表單提交
    $modal.css('display', 'flex').fadeIn(200);
  });
  $yesButton.on('click', function () {
    $(this).closest('form').submit();
  });

  // 點擊 "否" 或關閉確認框
  $noButton.on('click', closeModal);

  // 點擊確認框外部區域也可以關閉確認框
  $modal.on('click', function (event) {
    if ($(event.target).is($modal)) {
      closeModal();
    }
  });
});