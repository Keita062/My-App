document.addEventListener('DOMContentLoaded', function() {
    // 「タスクを追加」ボタンの処理
    document.querySelectorAll('.add-task-btn').forEach(button => {
        button.addEventListener('click', function() {
            const containerId = this.dataset.container;
            const namePrefix = this.dataset.namePrefix;
            const container = document.getElementById(containerId);

            const newTaskEntry = document.createElement('div');
            newTaskEntry.classList.add('task-entry');
            
            newTaskEntry.innerHTML = `
                <input type="text" name="${namePrefix}task_descriptions[]" placeholder="タスク内容" required>
                <input type="number" name="${namePrefix}task_durations[]" placeholder="所要時間(分)" required>
                <button type="button" class="btn btn-danger btn-sm btn-delete-task">削除</button>
            `;
            
            container.appendChild(newTaskEntry);
        });
    });

    // 「削除」ボタンの処理（イベントデリゲーション）
    document.body.addEventListener('click', function(event) {
        if (event.target.classList.contains('btn-delete-task')) {
            const taskContainer = event.target.closest('div[id$="-tasks-container"]');
            if (taskContainer && taskContainer.querySelectorAll('.task-entry').length > 1) {
                event.target.closest('.task-entry').remove();
            } else {
                console.log("最後のタスクは削除できません。");
            }
        }
    });
});