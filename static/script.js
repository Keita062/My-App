document.addEventListener('DOMContentLoaded', function() {
    const addQuestionBtn = document.getElementById('add-question-btn');
    const questionsContainer = document.getElementById('questions-container');
    const mainForm = document.getElementById('survey-form');
    const companyNameInput = document.getElementById('company_name');
    const confirmationModal = document.getElementById('confirmation-modal');
    const modalText = document.getElementById('modal-text');
    const confirmBtn = document.getElementById('confirm-btn');
    const cancelBtn = document.getElementById('cancel-btn');

    // --- 質問の動的な追加と削除 ---

    // 質問番号を振り直す関数
    const renumberQuestions = () => {
        const allPairs = questionsContainer.querySelectorAll('.question-pair');
        allPairs.forEach((pair, index) => {
            const questionLabel = pair.querySelector('.question-label');
            const answerLabel = pair.querySelector('.answer-label');
            const questionNumber = index + 1;
            if (questionLabel) questionLabel.textContent = `質問${questionNumber}`;
            if (answerLabel) answerLabel.textContent = `回答${questionNumber}`;
        });
    };

    // 質問を追加する関数
    const addQuestion = () => {
        const questionCount = questionsContainer.querySelectorAll('.question-pair').length + 1;
        
        const newPair = document.createElement('div');
        newPair.classList.add('question-pair', 'relative', 'mt-4', 'pt-6', 'border-t');

        // 削除ボタン
        const deleteBtn = document.createElement('button');
        deleteBtn.type = 'button';
        deleteBtn.textContent = '×';
        deleteBtn.classList.add('absolute', 'top-0', 'right-0', 'text-red-500', 'font-bold', 'hover:text-red-700', 'p-2');
        deleteBtn.onclick = () => {
            newPair.remove();
            renumberQuestions(); // 削除後に番号を振り直す
        };

        // 質問ラベルとテキストエリア
        const newQuestionLabel = document.createElement('label');
        newQuestionLabel.classList.add('question-label', 'block', 'text-sm', 'font-medium', 'text-gray-700', 'mb-1');
        newQuestionLabel.textContent = `質問${questionCount}`;

        const newQuestionTextarea = document.createElement('textarea');
        newQuestionTextarea.name = 'questions[]';
        newQuestionTextarea.rows = '2';
        newQuestionTextarea.required = true;
        newQuestionTextarea.classList.add('w-full', 'px-3', 'py-2', 'border', 'border-gray-300', 'rounded-md', 'shadow-sm');

        // 回答ラベルとテキストエリア
        const newAnswerLabel = document.createElement('label');
        newAnswerLabel.classList.add('answer-label', 'block', 'text-sm', 'font-medium', 'text-gray-700', 'mt-2', 'mb-1');
        newAnswerLabel.textContent = `回答${questionCount}`;

        const newAnswerTextarea = document.createElement('textarea');
        newAnswerTextarea.name = 'answers[]';
        newAnswerTextarea.rows = '4';
        newAnswerTextarea.classList.add('w-full', 'px-3', 'py-2', 'border', 'border-gray-300', 'rounded-md', 'shadow-sm');
        
        // 要素の組み立て
        newPair.appendChild(deleteBtn);
        newPair.appendChild(newQuestionLabel);
        newPair.appendChild(newQuestionTextarea);
        newPair.appendChild(newAnswerLabel);
        newPair.appendChild(newAnswerTextarea);
        
        questionsContainer.appendChild(newPair);
    };

    addQuestionBtn.addEventListener('click', addQuestion);

    // --- 企業名重複チェックとフォーム送信処理 ---
    mainForm.addEventListener('submit', async function(event) {
        event.preventDefault(); // まずフォームの自動送信を停止

        const companyName = companyNameInput.value.trim();
        if (!companyName) {
            mainForm.submit(); // 空の場合は通常通り送信（サーバー側でバリデーションされる）
            return;
        }

        // サーバーに重複チェックを問い合わせ
        try {
            const response = await fetch('/check_company', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ company_name: companyName })
            });
            const data = await response.json();

            if (data.exists) {
                // 重複がある場合、モーダルを表示
                modalText.textContent = `「${companyName}」は既に存在します。「${data.suggestion}」として登録しますか？`;
                confirmationModal.classList.remove('hidden');

                // モーダルの「OK」ボタンが押された時の処理
                confirmBtn.onclick = () => {
                    companyNameInput.value = data.suggestion; // 企業名を候補に書き換える
                    confirmationModal.classList.add('hidden');
                    mainForm.submit(); // フォームを送信
                };

                // モーダルの「キャンセル」ボタンが押された時の処理
                cancelBtn.onclick = () => {
                    confirmationModal.classList.add('hidden');
                };

            } else {
                // 重複がない場合、そのままフォームを送信
                mainForm.submit();
            }
        } catch (error) {
            console.error('Error checking company name:', error);
            alert('エラーが発生しました。コンソールを確認してください。');
        }
    });

    // 初期表示時に最初の質問フォームに削除ボタンを追加
    const firstPair = document.querySelector('.question-pair');
    if (firstPair) {
        const deleteBtn = document.createElement('button');
        deleteBtn.type = 'button';
        deleteBtn.textContent = '×';
        deleteBtn.classList.add('absolute', 'top-0', 'right-0', 'text-red-500', 'font-bold', 'hover:text-red-700', 'p-2');
        deleteBtn.onclick = () => {
            // 最初の1つは削除できないようにする（もしくは削除可能にする）
            // ここでは削除不可にする
            alert('最初の質問は削除できません。');
        };
        // 最初の質問を削除可能にしたい場合は、以下のコメントを外す
        // firstPair.classList.add('relative', 'pt-6');
        // firstPair.prepend(deleteBtn);
        // deleteBtn.onclick = () => {
        //     if (questionsContainer.querySelectorAll('.question-pair').length > 1) {
        //         firstPair.remove();
        //         renumberQuestions();
        //     } else {
        //         alert('最後の質問は削除できません。');
        //     }
        // };
    }
});
