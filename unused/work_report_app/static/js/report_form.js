document.addEventListener('DOMContentLoaded', function() {
    // 「タスクを追加」ボタンの処理
    document.querySelectorAll('.add-task-btn').forEach(button => {
        button.addEventListener('click', function() {
            const containerId = this.dataset.container;
            const namePrefix = this.dataset.namePrefix;
            const container = document.getElementById(containerId);

            // 新しいタスク入力フィールドのコンテナを作成
            const newTaskEntry = document.createElement('div');
            newTaskEntry.classList.add('task-entry');
            
            // is_requiredフラグをチェックしてrequired属性を設定
            const isRequired = namePrefix === 'start_';

            // HTMLを生成
            newTaskEntry.innerHTML = `
                <input type="text" name="${namePrefix}task_descriptions[]" placeholder="タスク内容" ${isRequired ? 'required' : ''}>
                <input type="number" name="${namePrefix}task_durations[]" placeholder="所要時間(分)" ${isRequired ? 'required' : ''}>
                <button type="button" class="btn btn-danger btn-sm btn-delete-task">削除</button>
            `;
            
            container.appendChild(newTaskEntry);
        });
    });

    // 「削除」ボタンの処理（イベントデリゲーション）
    document.body.addEventListener('click', function(event) {
        if (event.target.classList.contains('btn-delete-task')) {
            const taskEntry = event.target.closest('.task-entry');
            // コンテナ内に複数のタスクエントリーがある場合のみ削除
            if (taskEntry.parentElement.querySelectorAll('.task-entry').length > 0) {
                taskEntry.remove();
            } else {
                // 最後の1つの場合は中身を空にする
                const inputs = taskEntry.querySelectorAll('input');
                inputs.forEach(input => input.value = '');
            }
        }
    });

    // 新規追加：前回のレポート表示トグル
    const toggleHeader = document.getElementById('toggle-previous-report');
    const toggleContent = document.getElementById('previous-report-content');
    if (toggleHeader && toggleContent) {
        toggleHeader.addEventListener('click', function() {
            const isHidden = toggleContent.style.display === 'none';
            toggleContent.style.display = isHidden ? 'block' : 'none';
            this.querySelector('.toggle-icon').style.transform = isHidden ? 'rotate(180deg)' : 'rotate(0deg)';
        });
        // CSSでスタイルを追加
        toggleHeader.style.cursor = 'pointer';
        toggleHeader.style.display = 'flex';
        toggleHeader.style.justifyContent = 'space-between';
        toggleHeader.style.alignItems = 'center';
        const icon = toggleHeader.querySelector('.toggle-icon');
        if (icon) {
            icon.style.transition = 'transform 0.3s ease';
        }
    }

    // 新規追加：コンテナにタスクが一つもない場合に、空の入力欄を一つ追加する
    function ensureFirstTaskEntry(containerId, namePrefix) {
        const container = document.getElementById(containerId);
        if (container && container.children.length === 0) {
            const addButton = document.querySelector(`.add-task-btn[data-container='${containerId}']`);
            if(addButton) {
                addButton.click();
            }
        }
    }
    ensureFirstTaskEntry('start-tasks-container', 'start_');
    ensureFirstTaskEntry('end-tasks-container', 'end_');

});
