$(function(){
    var textarea = $("#answer-editor");

    if (textarea.length) {
        var status = textarea.data("status") || "";

        // 初始化 CodeMirror
        var editor = CodeMirror.fromTextArea(textarea[0], {
            lineNumbers: true,
            mode: "python",
            indentUnit: 4,
            tabSize: 4,
            matchBrackets: true
        });

        // 若 status 為 "submitted"，設定唯讀模式
        if ($.trim(status).toLowerCase() === "submitted") {
            editor.setOption("readOnly", "nocursor"); // 禁用輸入 & 游標
        }

        // 存入全域變數
        window.answerEditor = editor;
    }
});
