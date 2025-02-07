document.addEventListener('DOMContentLoaded', function () {
    var textarea = document.getElementById("answer-editor");

    if (textarea) {
        var status = textarea.getAttribute("data-status") || "";

        // 初始化 CodeMirror
        var editor = CodeMirror.fromTextArea(textarea, {
            lineNumbers: true,
            mode: "python",
            indentUnit: 4,
            tabSize: 4,
            matchBrackets: true
        });

        // 若 status 為 "submitted"，設定唯讀模式
        if (status.trim().toLowerCase() === "submitted") {
            editor.setOption("readOnly", "nocursor"); // 禁用輸入 & 游標
        }

        // 存入全域變數
        window.answerEditor = editor;
    }
});