function addQA() {
  const container = document.getElementById('qa-container');  // 質問コンテナ取得
  const div = document.createElement('div');                  // 新しい質問エリアを作成
  div.className = 'qa';
  div.innerHTML = `
    <input type="text" name="questions[]" placeholder="質問" required>
    <textarea name="answers[]" placeholder="回答" required></textarea>
  `;
  container.appendChild(div);  // 既存のフォームに追加
}
