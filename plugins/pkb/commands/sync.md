---
description: 知識ベースの保管庫（Git リポジトリ）を commit・pull・push して同期する（クラウド用）
allowed-tools: Bash(python3:*), Bash(git:*)
---
`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/pkb.py" sync` を実行し、結果を1行で報告する。
push が失敗した場合: 保管庫のリポジトリ（例: torebo223/pkb-vault）がこのセッションに追加されていない可能性が高い。
その旨と「セッション開始時に pkb-vault も選ぶ」ことを伝える。ノートはローカルには残っているが、セッション終了で消えることも伝える。
