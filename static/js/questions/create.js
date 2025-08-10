let aiAnalyzed = false;
let monacoEditor;

$(document).ready(function () {
    // 一開始就禁用提交按鈕
    $("button[type='submit']").prop("disabled", true).text("請先進行AI分析");

    // 設定主題和標籤的選項限制
    setupCheckboxLimit("id_topics", 3, "主題");
    setupCheckboxLimit("id_tags", 5, "標籤");

    // 綁定AI分析按鈕
    $("#ai-analysis-button").on("click", aiAnalysis);

    // 表單驗證
    validateForm();

    // Monaco Editor 初始化
    require(["vs/editor/editor.main"], function () {
        monacoEditor = monaco.editor.create($("#monaco-editor")[0], {
            value: $("#id_answer").val() || "",
            language: "python",
            roundedSelection: true,
            scrollBeyondLastLine: false,
            readOnly: false,
            theme: "vs-dark",
            automaticLayout: true,
        });

        $("#questionForm").on("submit", function () {
            $("#id_answer").val(monacoEditor.getValue());
        });
    });
});

/**
 * 設定多選框的選擇數量限制
 * @param {string} fieldId - 字段的ID
 * @param {number} maxCount - 最大可選數量
 * @param {string} fieldName - 字段名稱（用於顯示錯誤消息）
 */
function setupCheckboxLimit(fieldId, maxCount, fieldName) {
	const $checkboxes = $(`#${fieldId} input[type="checkbox"]`);
	const $checkboxContainer = $(`#${fieldId}`);

	if ($checkboxContainer.length === 0) return;

	// 創建警告消息元素
	const $warningElement = $("<div>", {
		class: "text-danger validation-warning mt-2 d-none",
		text: `最多只能選擇${maxCount}個${fieldName}`,
	});

	// 將警告消息插入到複選框容器後面
	$checkboxContainer.parent().append($warningElement);

	// 添加事件監聽器到每個複選框
	$checkboxes.on("change", function () {
		const checkedCount = $(`#${fieldId} input[type="checkbox"]:checked`).length;

		// 如果選擇超過最大數量，取消勾選該複選框並顯示警告
		if (checkedCount > maxCount) {
			$(this).prop("checked", false);
			$warningElement.removeClass("d-none");

			// 3秒後隱藏警告
			setTimeout(() => {
				$warningElement.addClass("d-none");
			}, 3000);
		}
	});
}

/**
 * 表單驗證
 */
function validateForm() {
    const $form = $("#questionForm");

    if ($form.length === 0) return;

    $form.on("submit", function (event) {
        // 檢查是否已經進行AI分析
        if (!aiAnalyzed) {
            event.preventDefault();
            // 顯示提示
            let $aiAlert = $(".ai-analyze-alert");
            if ($aiAlert.length === 0) {
                $aiAlert = $("<div>", {
                    class: "alert alert-warning mt-3 ai-analyze-alert",
                    text: "請先點擊『AI分析』並完成分析後才能提交問題。",
                });
                $("#ai-analysis-button").after($aiAlert);
            }
            $aiAlert.removeClass("d-none");
            // 滾動到AI分析按鈕
            $("html, body").animate({ scrollTop: $("#ai-analysis-button").offset().top - 100 }, "smooth");
            return;
        }

        // ...existing code (原本的驗證流程)...
        let isValid = true;
        const requiredFields = [
            "id_title",
            "id_content",
            "id_level",
            "id_input_format",
            "id_output_format",
            "id_input_example",
            "id_output_example",
        ];

        $.each(requiredFields, function (index, fieldId) {
            const $field = $("#" + fieldId);
            if ($field.length && !$field.val().trim()) {
                isValid = false;
                highlightInvalidField($field);
            }
        });

        // 特別處理 answer 字段 - 從 Monaco Editor 獲取值
        if (monacoEditor) {
            const answerValue = monacoEditor.getValue().trim();
            if (!answerValue) {
                isValid = false;
                // 為 Monaco Editor 添加視覺錯誤提示
                const $monacoContainer = $("#monaco-editor");
                $monacoContainer.css("border-color", "#dc3545");
                
                // 添加錯誤消息
                const $parentElement = $monacoContainer.parent();
                let $feedbackElement = $parentElement.find(".monaco-invalid-feedback");
                if ($feedbackElement.length === 0) {
                    $feedbackElement = $("<div>", {
                        class: "text-danger monaco-invalid-feedback mt-2",
                        text: "此字段為必填項",
                    });
                    $parentElement.append($feedbackElement);
                }
                $feedbackElement.show();

                				// 聚焦時移除錯誤狀態 - 檢查是否已經綁定過
				if (!monacoEditor._focusListenerBound) {
					monacoEditor.onDidFocusEditorText(() => {
						$monacoContainer.css("border-color", "#DDD");
						$feedbackElement.hide();
					});
					monacoEditor._focusListenerBound = true;
				}
            }
        }

        // 檢查主題選擇
        const topicsChecked = $('#id_topics input[type="checkbox"]:checked').length;
        if (topicsChecked === 0) {
            isValid = false;
            const $topicsContainer = $("#id_topics").parent();
            $topicsContainer.addClass("border-danger");

            // 添加警告消息
            let $warningElement = $topicsContainer.find(".validation-warning");
            if ($warningElement.length === 0) {
                $warningElement = $("<div>", {
                    class: "text-danger validation-warning mt-2",
                    text: "請至少選擇一個主題",
                });
                $topicsContainer.append($warningElement);
            }
            $warningElement.removeClass("d-none");
        }

        // 檢查標籤選擇
        const tagsChecked = $('#id_tags input[type="checkbox"]:checked').length;
        if (tagsChecked === 0) {
            isValid = false;
            const $tagsContainer = $("#id_tags").parent();
            $tagsContainer.addClass("border-danger");

            // 添加警告消息
            let $warningElement = $tagsContainer.find(".validation-warning");
            if ($warningElement.length === 0) {
                $warningElement = $("<div>", {
                    class: "text-danger validation-warning mt-2",
                    text: "請至少選擇一個標籤",
                });
                $tagsContainer.append($warningElement);
            }
            $warningElement.removeClass("d-none");
        }

        // 如果表單無效，阻止提交
        if (!isValid) {
            event.preventDefault();

            // 顯示一般錯誤消息
            const $formTop = $(".gradient-bg").length ? $(".gradient-bg") : $form;
            let $errorAlert = $(".form-error-alert");
            if ($errorAlert.length === 0) {
                $errorAlert = $("<div>", {
                    class: "alert alert-danger mt-3 form-error-alert",
                    text: "表單中存在錯誤，請修正後再提交。",
                });
                $formTop.after($errorAlert);
            }

            // 滾動到頂部
            $("html, body").animate({ scrollTop: 0 }, "smooth");
        }
    });
}

/**
 * 高亮顯示無效的字段
 * @param {jQuery} $field - 無效的表單字段 jQuery 元素
 */
function highlightInvalidField($field) {
	$field.addClass("is-invalid");

	// 添加警告消息
	const $parentElement = $field.parent();
	let $feedbackElement = $parentElement.find(".invalid-feedback");

	if ($feedbackElement.length === 0) {
		$feedbackElement = $("<div>", {
			class: "invalid-feedback d-block",
			text: "此字段為必填項",
		});
		$parentElement.append($feedbackElement);
	}

	// 檢查是否已經綁定過 focus 事件監聽器
	if (!$field.data("focus-listener-bound")) {
		// 添加聚焦時移除錯誤狀態
		$field.on("focus", function () {
			$(this).removeClass("is-invalid");
			const $parent = $(this).parent();
			const $feedback = $parent.find(".invalid-feedback");
			if ($feedback.length) {
				$feedback.text("");
			}
		});
		
		// 標記已綁定事件監聽器
		$field.data("focus-listener-bound", true);
	}
}

// AI分析按鈕點擊事件
function aiAnalysis() {
    const $form = $("#questionForm");
    if ($form.length === 0) return;

    // 檢查必填字段是否已填寫
    const requiredFields = [
        "id_title",
        "id_content",
        "id_level",
        "id_input_format",
        "id_output_format",
        "id_input_example",
        "id_output_example",
    ];

    let isValid = true;
    $.each(requiredFields, function (index, fieldId) {
        const $field = $("#" + fieldId);
        if ($field.length && !$field.val().trim()) {
            isValid = false;
            highlightInvalidField($field);
        }
    });

    // 在 AI 分析時也需要同步 Monaco Editor 的值
    if (monacoEditor) {
        $("#id_answer").val(monacoEditor.getValue());
    }

    if (!isValid) {
        alert("請填寫所有必填字段後再進行 AI 分析。");
        return;
    }

    // 禁用提交按鈕
    $("button[type='submit']").prop("disabled", true).text("AI分析中...");

    // 顯示正在分析提示
    const $title = $("#ai-analysis-title");
    const $content = $("#ai-analysis-content");
    $title.text("AI分析中...");
    $content.html("<div class='text-center'><span class='text-info'>正在分析，請稍候...</span></div>");

    // 透過ajax指定API提交表單以獲取 AI 分析結果
    $.ajax({
        url: "/ai/questionanalysis/",
        method: "POST",
        data: $form.serialize(),
        success: function (response) {
            // 顯示AI分析結果在右側卡片區塊
            $title.text("AI分析結果");
            if ($content.length) {
                $content.html(response.result ? `<pre class=\"mb-0\" style=\"white-space: pre-wrap; word-break: break-all; font-size: 1.25rem;\">${response.result}</pre>` : "<span class='text-danger'>分析失敗</span>");
            }
            aiAnalyzed = true;
            $(".ai-analyze-alert").remove();

            // 恢復提交按鈕
            $("button[type='submit']").prop("disabled", false).text("提交問題");
        },
        error: function (xhr, status, error) {
            // 只console.log錯誤，不顯示在畫面
            console.log("AI分析失敗", error);
            aiAnalyzed = false;

            // 恢復提交按鈕和原始狀態
            $("button[type='submit']").prop("disabled", false).text("提交問題");
            $title.text("注意事項");
            $content.html(`
        <ul class="list-group list-group-flush">
          <li class="list-group-item">題目提交後需經過審核才會顯示</li>
          <li class="list-group-item">難度級別決定題目的分類和推薦順序</li>
          <li class="list-group-item">提供清晰的輸入輸出格式有助於學習</li>
          <li class="list-group-item">參考資料請提供有效的 URL</li>
        </ul>
      `);
        },
    });
}
