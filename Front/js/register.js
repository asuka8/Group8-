document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    registerForm.addEventListener('submit', function(event) {
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        // パスワードと確認パスワードが一致するか確認
        if (password !== confirmPassword) {
            alert('パスワードが一致しません。もう一度確認してください。');
            event.preventDefault(); // フォームの送信を止める
        }
    });
});