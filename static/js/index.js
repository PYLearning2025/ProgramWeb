$(document).ready(function () {
  // 行動裝置選單切換
  const $menuBtn = $('#menuBtn');
  const $mobileMenu = $('#mobileMenu');
  
  if ($menuBtn.length && $mobileMenu.length) {
    $menuBtn.on('click', function () {
      $mobileMenu.toggleClass('hidden');
    });
  }

  // 登入彈窗
  const $loginBtn = $('#loginBtn');
  const $loginModal = $('#loginModal');
  const $closeLoginBtn = $('#closeLoginBtn');

  if ($loginBtn.length && $loginModal.length) {
    $loginBtn.on('click', function () {
      $loginModal.removeClass('hidden');
    });
  }

  if ($closeLoginBtn.length && $loginModal.length) {
    $closeLoginBtn.on('click', function () {
      $loginModal.addClass('hidden');
    });
  }

  // 點擊彈窗外部關閉
  if ($loginModal.length) {
    $loginModal.on('click', function (e) {
      if (e.target === this) {
        $loginModal.addClass('hidden');
      }
    });
  }
});
