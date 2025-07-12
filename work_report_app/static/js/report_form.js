document.addEventListener('DOMContentLoaded', function() {
    // タスク追加ボタンのイベントリスナーを設定
    const addTaskBtn = document.getElementById('add-task-btn');
    if (addTaskBtn) {
        addTaskBtn.addEventListener('click', function() {
            const container = this.previousElementSibling; // tasks-container
            const newTaskPair = document.createElement('div');
            newTaskPair.classList.add('form-grid', 'task-entry');

            // 新しい入力フィールドのHTMLを生成
            newTaskPair.innerHTML = `
                <div class="form-group task-description">
                    <input type="text" name="task_descriptions[]" placeholder="タスク内容" required>
                </div>
                <div class="form-group task-duration">
                    <input type="number" name="task_durations[]" placeholder="所要時間(分)" required>
                </div>
                <button type="button" class="btn btn-danger btn-sm btn-delete-task">削除</button>
            `;

            container.appendChild(newTaskPair);

            // 新しく追加した削除ボタンにイベントリスナーを設定
            newTaskPair.querySelector('.btn-delete-task').addEventListener('click', function() {
                this.parentElement.remove();
            });
        });
    }

    document.querySelectorAll('.btn-delete-task').forEach(button => {
        button.addEventListener('click', function() {
            this.parentElement.remove();
        });
    });
});