document.addEventListener('DOMContentLoaded', function () {
    // 取得特定的 textarea（只適用於 answer-editor）
    var textarea = document.getElementById("answer-editor");

    // 確保該 textarea 存在才初始化 CodeMirror
    if (textarea) {
        var editor = CodeMirror.fromTextArea(textarea, {
            lineNumbers: true,
            mode: "python",
            indentUnit: 4,
            tabSize: 4,
            matchBrackets: true
        });

        // 如果是 "/question/answer/" 頁面，才根據 status 決定是否鎖住輸入
        if (window.location.pathname.includes("/question/answer/")) {
            var status = "{{ status }}";  // Django 模板變數

            // 當 status 不是 "pending"，則鎖住 CodeMirror 輸入
            if (status !== "pending") {
                editor.setOption("readOnly", "nocursor");  // 設定唯讀並隱藏游標
            }
        }

        // 保存到全局變數
        window.answerEditor = editor;
    }
});