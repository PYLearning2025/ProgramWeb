document.addEventListener('DOMContentLoaded', function () {
    // 取得 DOM 元素
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const messagesList = document.getElementById('messages-list');
    const messagesBox = document.getElementById('messages-box'); // 訊息區域
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content'); // CSRF Token

    // 初始化時滾動到底部
    const initialScroll = () => {
        messagesBox.scrollTop = messagesBox.scrollHeight;
    };
    initialScroll();

    // 建立 Showdown Markdown 轉換器（全局只建立一次）
    const converter = new showdown.Converter({ 
        tables: true, 
        ghCodeBlocks: true, 
        omitExtraWLInCodeBlocks: true,
        noHeaderId: true,
        parseImgDimensions: true
    });

    /**
     * 處理 AI 回覆訊息的 Markdown 與程式碼高亮效果。
     * @param {HTMLElement} messageElement - 要處理的 .message-received 元素
     */
    function processMessageElement(messageElement) {
        // 取得原始內容，並將 <br> 換行標籤轉成 \n（保留換行）
        let originalHTML = messageElement.innerHTML.trim();
        let markdownText = originalHTML.replace(/&gt;/g, ">").replace(/&lt;/g, "<").replace(/<br\s*\/?\>/g, "\n");

        // 利用 showdown 轉換 Markdown 成 HTML
        let htmlOutput = converter.makeHtml(markdownText).trim();
        messageElement.innerHTML = htmlOutput;

        // 使用 highlight.js 處理 <pre><code> 區塊
        messageElement.querySelectorAll("pre code").forEach((block) => {
            hljs.highlightElement(block);

            // 取得語言名稱（例如 language-javascript），若無則預設為 'Code'
            let langClass = block.className.match(/language-(\w+)/);
            let lang = langClass ? langClass[1] : 'Code';
            block.setAttribute("data-lang", lang.toUpperCase());
        });

        // 確保內部所有 <p> 標籤的 margin-bottom 設為 0
        messageElement.querySelectorAll("p").forEach(p => {
            p.style.marginBottom = "0";
        });
    }

    // 首次載入時，處理所有已存在的 AI 回覆
    document.querySelectorAll(".message-received").forEach(el => {
        processMessageElement(el);
    });

    // 訊息送出表單提交事件
    chatForm.addEventListener('submit', function (e) {
        e.preventDefault(); // 防止表單預設送出導致頁面刷新

        const message = messageInput.value.trim();
        if (message === '') return; // 避免空訊息

        // 新增使用者訊息到畫面
        const userMessage = document.createElement('div');
        userMessage.className = 'message-pair';
        const userMessageText = document.createElement('p');
        userMessageText.className = 'message-sent';
        userMessageText.textContent = message;
        userMessage.appendChild(userMessageText);
        messagesList.appendChild(userMessage);

        // 清空輸入框
        messageInput.value = '';

        // 新增「打字動畫」效果
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'message-pair';
        typingIndicator.innerHTML = `
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        `;
        messagesList.appendChild(typingIndicator);

        // 滾動到底部
        messagesBox.scrollTop = messagesBox.scrollHeight;

        // 使用 Fetch API 送出 POST 請求
        fetch('', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: new URLSearchParams({
                'question': message
            })
        })
        .then(response => response.text())
        .then(text => {
            let data;
            try {
                data = JSON.parse(text);
            } catch (error) {
                console.error('JSON Parse Error:', error);
                alert('發生錯誤，請稍後再試！');
                return;
            }

            if (!data.success) {
                console.error('Error:', data.errors);
                alert('發生錯誤：' + JSON.stringify(data.errors));
                return;
            }

            // 移除「打字動畫」
            if (typingIndicator.parentNode) {
                messagesList.removeChild(typingIndicator);
            }

            // 新增 AI 回應訊息
            const aiMessage = document.createElement('div');
            aiMessage.className = 'message-pair';
            const aiMessageText = document.createElement('p');
            aiMessageText.className = 'message-received';
            aiMessageText.textContent = data.response;
            aiMessage.appendChild(aiMessageText);
            messagesList.appendChild(aiMessage);

            // 處理新加入的 AI 訊息（Markdown 轉換與程式碼高亮）
            processMessageElement(aiMessageText);

            // 滾動到底部
            messagesBox.scrollTop = messagesBox.scrollHeight;
        })
        .catch(error => {
            console.error('Fetch Error:', error);
            alert('發生錯誤，請稍後再試');
            if (typingIndicator.parentNode) {
                messagesList.removeChild(typingIndicator);
            }
        });
    });

    // 當訊息區域有新節點加入時自動滾動到底部
    const observer = new MutationObserver(() => {
        messagesBox.scrollTop = messagesBox.scrollHeight;
    });
    observer.observe(messagesList, { childList: true });
});