document.addEventListener('DOMContentLoaded', function() {
    const addQuestionBtn = document.getElementById('add-question-btn');
    const questionsContainer = document.getElementById('questions-container');

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

    if (addQuestionBtn) {
        addQuestionBtn.addEventListener('click', () => {
            const questionCount = questionsContainer.querySelectorAll('.question-pair').length + 1;
            const newPair = document.createElement('div');
            newPair.classList.add('question-pair'); // スタイルはCSSで統一

            newPair.innerHTML = `
                <div class="form-group">
                    <label class="question-label">質問${questionCount}</label>
                    <textarea name="questions[]" rows="2" required></textarea>
                </div>
                <div class="form-group">
                    <label class="answer-label">回答${questionCount}</label>
                    <textarea name="answers[]" rows="4"></textarea>
                </div>
                <button type="button" class="btn-delete-question">×</button>
            `;
            
            questionsContainer.appendChild(newPair);

            // 追加した質問の削除ボタンにイベントリスナーを設定
            newPair.querySelector('.btn-delete-question').addEventListener('click', function() {
                this.parentElement.remove();
                renumberQuestions();
            });
        });
    }

    // 既存の削除ボタンにもイベントリスナーを設定
    questionsContainer.querySelectorAll('.btn-delete-question').forEach(button => {
        button.addEventListener('click', function() {
            this.parentElement.remove();
            renumberQuestions();
        });
    });
});
