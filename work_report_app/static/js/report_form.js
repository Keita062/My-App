document.addEventListener('DOMContentLoaded', function() {

    // タスク入力欄を囲むコンテナ要素を取得
    const tasksContainer = document.getElementById('tasks-container');
    // 「タスクを追加」ボタンを取得
    const addTaskBtn = document.getElementById('add-task-btn');

    // 新しいタスク入力欄を追加する関数
    function addTask() {
        const newTaskEntry = document.createElement('div');
        newTaskEntry.classList.add('task-entry');
        
        // 追加するHTML要素を定義
        newTaskEntry.innerHTML = `
            <input type="text" name="task_descriptions[]" placeholder="タスク内容" required>
            <input type="number" name="task_durations[]" placeholder="所要時間(分)" required>
            <button type="button" class="btn btn-danger btn-sm btn-delete-task">削除</button>
        `;
        
        // コンテナに新しいタスク入力欄を追加
        tasksContainer.appendChild(newTaskEntry);
    }

    // 「タスクを追加」ボタンがクリックされた時の処理
    if (addTaskBtn) {
        addTaskBtn.addEventListener('click', addTask);
    }

    // 削除ボタンの処理（イベントデリゲーション）
    // コンテナ全体でクリックを監視し、クリックされたのが削除ボタンの場合のみ処理を実行
    if (tasksContainer) {
        tasksContainer.addEventListener('click', function(event) {
            // クリックされた要素が削除ボタンかチェック
            if (event.target.classList.contains('btn-delete-task')) {
                
                // タスクが1つしかない場合は削除しない
                if (tasksContainer.querySelectorAll('.task-entry').length > 1) {
                    // ボタンの親要素である .task-entry を削除
                    event.target.parentElement.remove();
                } else {
                    // alert()は使えないため、何もしないか、もしくはコンソールにログを出す
                    console.log("最後のタスクは削除できません。");
                }
            }
        });
    }
});