document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    loginForm.addEventListener('submit', function(event) {
        // ここに必要に応じて追加のバリデーションやアクションを書けます。
        // 例: フィールドの値をチェックする
        var userId = document.getElementById('userId').value;
        var password = document.getElementById('password').value;

        if (!userId || !password) {
            alert('ユーザーIDとパスワードを入力してください。');
            event.preventDefault(); // フォームの送信を止める
        }
    });
});