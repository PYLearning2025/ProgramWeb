document.addEventListener('DOMContentLoaded', function() {
    // 行動裝置選單切換
    const menuBtn = document.getElementById('menuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    if (menuBtn && mobileMenu) {
        menuBtn.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // 登入彈窗
    const loginBtn = document.getElementById('loginBtn');
    const loginModal = document.getElementById('loginModal');
    const closeLoginBtn = document.getElementById('closeLoginBtn');

    if (loginBtn && loginModal) {
        loginBtn.addEventListener('click', function() {
            loginModal.classList.remove('hidden');
        });
    }

    if (closeLoginBtn && loginModal) {
        closeLoginBtn.addEventListener('click', function() {
            loginModal.classList.add('hidden');
        });
    }

    // 點擊彈窗外部關閉
    if (loginModal) {
        loginModal.addEventListener('click', function(e) {
            if (e.target === loginModal) {
                loginModal.classList.add('hidden');
            }
        });
    }
});
