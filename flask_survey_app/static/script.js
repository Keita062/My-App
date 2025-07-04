document.addEventListener('DOMContentLoaded', function() {
    const addQuestionBtn = document.getElementById('add-question-btn');
    const questionsContainer = document.getElementById('questions-container');
    const mainForm = document.getElementById('survey-form');
    const companyNameInput = document.getElementById('company_name');
    const confirmationModal = document.getElementById('confirmation-modal');
    const modalText = document.getElementById('modal-text');
    const confirmBtn = document.getElementById('confirm-btn');
    const cancelBtn = document.getElementById('cancel-btn');

    // --- 質問の動的な追加と削除 --- (変更なし)
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
    const addQuestion = () => {
        const questionCount = questionsContainer.querySelectorAll('.question-pair').length + 1;
        const newPair = document.createElement('div');
        newPair.classList.add('question-pair', 'relative', 'mt-4', 'pt-6', 'border-t');
        const deleteBtn = document.createElement('button');
        deleteBtn.type = 'button';
        deleteBtn.textContent = '×';
        deleteBtn.classList.add('absolute', 'top-0', 'right-0', 'text-red-500', 'font-bold', 'hover:text-red-700', 'p-2');
        deleteBtn.onclick = () => {
            newPair.remove();
            renumberQuestions();
        };
        const newQuestionLabel = document.createElement('label');
        newQuestionLabel.classList.add('question-label', 'block', 'text-sm', 'font-medium', 'text-gray-700', 'mb-1');
        newQuestionLabel.textContent = `質問${questionCount}`;
        const newQuestionTextarea = document.createElement('textarea');
        newQuestionTextarea.name = 'questions[]';
        newQuestionTextarea.rows = '2';
        newQuestionTextarea.required = true;
        newQuestionTextarea.classList.add('w-full', 'px-3', 'py-2', 'border', 'border-gray-300', 'rounded-md', 'shadow-sm');
        const newAnswerLabel = document.createElement('label');
        newAnswerLabel.classList.add('answer-label', 'block', 'text-sm', 'font-medium', 'text-gray-700', 'mt-2', 'mb-1');
        newAnswerLabel.textContent = `回答${questionCount}`;
        const newAnswerTextarea = document.createElement('textarea');
        newAnswerTextarea.name = 'answers[]';
        newAnswerTextarea.rows = '4';
        newAnswerTextarea.classList.add('w-full', 'px-3', 'py-2', 'border', 'border-gray-300', 'rounded-md', 'shadow-sm');
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
        event.preventDefault(); 

        const companyName = companyNameInput.value.trim();
        if (!companyName) {
            mainForm.submit();
            return;
        }

        try {
            // 【変更】fetchのURLに '/survey' を追加
            const response = await fetch('/survey/check_company', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ company_name: companyName })
            });
            const data = await response.json();

            if (data.exists) {
                modalText.textContent = `「${companyName}」は既に存在します。「${data.suggestion}」として登録しますか？`;
                confirmationModal.classList.remove('hidden');

                confirmBtn.onclick = () => {
                    companyNameInput.value = data.suggestion;
                    confirmationModal.classList.add('hidden');
                    mainForm.submit();
                };

                cancelBtn.onclick = () => {
                    confirmationModal.classList.add('hidden');
                };

            } else {
                mainForm.submit();
            }
        } catch (error) {
            console.error('Error checking company name:', error);
            alert('エラーが発生しました。コンソールを確認してください。');
        }
    });
});
