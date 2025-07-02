// DOMが完全に読み込まれたら実行
document.addEventListener('DOMContentLoaded', function() {
    
    // 「質問を追加」ボタンの要素を取得
    const addQuestionBtn = document.getElementById('add-question-btn');
    // 質問フォームを格納するコンテナ要素を取得
    const questionsContainer = document.getElementById('questions-container');

    // 現在の質問数を追跡するカウンター
    let questionCount = 1;

    // ボタンがクリックされたときのイベントリスナーを設定
    addQuestionBtn.addEventListener('click', function() {
        // 質問番号をインクリメント
        questionCount++;

        // 新しい質問・回答ペアのコンテナを作成
        const newPair = document.createElement('div');
        newPair.classList.add('question-pair', 'mt-4', 'pt-4', 'border-t');

        // --- 新しい「質問」入力欄を作成 ---
        const newQuestionLabel = document.createElement('label');
        newQuestionLabel.classList.add('block', 'text-sm', 'font-medium', 'text-gray-700', 'mb-1');
        newQuestionLabel.textContent = `質問${questionCount}`;

        const newQuestionTextarea = document.createElement('textarea');
        newQuestionTextarea.name = 'questions[]'; // 配列としてデータを送信
        newQuestionTextarea.rows = '2';
        newQuestionTextarea.required = true;
        newQuestionTextarea.classList.add('w-full', 'px-3', 'py-2', 'border', 'border-gray-300', 'rounded-md', 'shadow-sm', 'focus:outline-none', 'focus:ring-indigo-500', 'focus:border-indigo-500');

        // --- 新しい「回答」入力欄を作成 ---
        const newAnswerLabel = document.createElement('label');
        newAnswerLabel.classList.add('block', 'text-sm', 'font-medium', 'text-gray-700', 'mt-2', 'mb-1');
        newAnswerLabel.textContent = `回答${questionCount}`;

        const newAnswerTextarea = document.createElement('textarea');
        newAnswerTextarea.name = 'answers[]'; // 配列としてデータを送信
        newAnswerTextarea.rows = '4';
        newAnswerTextarea.classList.add('w-full', 'px-3', 'py-2', 'border', 'border-gray-300', 'rounded-md', 'shadow-sm', 'focus:outline-none', 'focus:ring-indigo-500', 'focus:border-indigo-500');

        // 作成した要素をペアのコンテナに追加
        newPair.appendChild(newQuestionLabel);
        newPair.appendChild(newQuestionTextarea);
        newPair.appendChild(newAnswerLabel);
        newPair.appendChild(newAnswerTextarea);

        // ペアのコンテナをメインのコンテナに追加
        questionsContainer.appendChild(newPair);
    });
});
