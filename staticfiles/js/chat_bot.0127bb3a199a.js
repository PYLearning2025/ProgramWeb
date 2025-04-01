$(function () {
    // 切換側邊欄顯示狀態
    $("#sidebarIcon").on("click", function () {
        $("#chatbot, #sidebarIcon").toggleClass("active");

        // 當 #chatbot 顯示時滾動到底部
        if ($("#chatbot").hasClass("active")) {
            setTimeout(() => {
                scrollToBottom($("#chatbot"));
            }, 200);
        }
    });

    // 滾動到指定元素最底部函式
    function scrollToBottom(element) {
        element.scrollTop(element.prop("scrollHeight"));
    }

    // DOM 元素
    const $chatForm = $('#chat-form');
    const $messageInput = $('#message-input');
    const $messagesList = $('#messages-list');
    const $chatbotElement = $('#chatbot');
    const $messagesBox = $('#messages-box');
    const csrfToken = $('meta[name="csrf-token"]').attr('content');
    const chatUrl = $chatForm.attr('action');

    // 初始化時滾動到底部
    scrollToBottom($messagesBox);

    // 建立 Showdown Markdown 轉換器
    const converter = new showdown.Converter({
        tables: true,
        ghCodeBlocks: true,
        omitExtraWLInCodeBlocks: true,
        noHeaderId: true,
        parseImgDimensions: true
    });

    /**
     * 處理 AI 回覆訊息的 Markdown 與程式碼高亮效果
     */
    function processMessageElement($messageElement) {
        let originalHTML = $messageElement.html().trim();
        let markdownText = originalHTML.replace(/&gt;/g, ">").replace(/&lt;/g, "<").replace(/<br\s*\/?>/g, "\n");
        let htmlOutput = converter.makeHtml(markdownText).trim();

        $messageElement.html(htmlOutput);

        $messageElement.find("pre code").each(function () {
            hljs.highlightElement(this);
            let langClass = $(this).attr("class").match(/language-(\w+)/);
            let lang = langClass ? langClass[1] : 'Code';
            $(this).attr("data-lang", lang.toUpperCase());
        });

        $messageElement.find("p").css("margin-bottom", "0");
    }

    // 首次載入處理現有AI回覆
    $(".message-received").each(function () {
        processMessageElement($(this));
    });

    // 訊息送出事件
    $chatForm.on('submit', function (e) {
        e.preventDefault();

        const message = $messageInput.val().trim();
        if (message === '') return;

        // 新增使用者訊息
        const $userMessage = $('<div/>', { class: 'message-pair' })
            .append($('<p/>', { class: 'message-sent', text: message }));
        $messagesList.append($userMessage);

        scrollToBottom($chatbotElement);
        $messageInput.val('');

        // 打字動畫
        const $typingIndicator = $(`
            <div class="message-pair">
                <div class="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `);
        $messagesList.append($typingIndicator);

        $.ajax({
            type: 'POST',
            url: chatUrl,
            data: { question: message },
            headers: { 'X-CSRFToken': csrfToken },
            success: function (data) {
                let parsedData;
                try {
                    parsedData = typeof data === "object" ? data : JSON.parse(data);
                } catch (error) {
                    console.error('JSON Parse Error:', error);
                    alert('發生錯誤，請稍後再試！');
                    $typingIndicator.remove();
                    return;
                }

                if (!parsedData.success) {
                    console.error('Error:', parsedData.errors);
                    alert('發生錯誤：' + JSON.stringify(parsedData.errors));
                    $typingIndicator.remove();
                    return;
                }

                $typingIndicator.remove();

                // AI回應訊息
                const $aiMessage = $('<div/>', { class: 'message-pair' })
                    .append($('<p/>', { class: 'message-received', text: parsedData.response }));
                $messagesList.append($aiMessage);

                processMessageElement($aiMessage.find('.message-received'));
                scrollToBottom($chatbotElement);
            },
            error: function (xhr, status, error) {
                console.error('Fetch Error:', error);
                alert('發生錯誤，請稍後再試');
                $typingIndicator.remove();
            }
        });
    });

    // 新節點自動滾動到底部
    const observer = new MutationObserver(() => {
        scrollToBottom($chatbotElement);
    });
    observer.observe($messagesList[0], { childList: true });
});