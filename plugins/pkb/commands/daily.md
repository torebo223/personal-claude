---
description: 今日のデイリーノートを開き、ログ追記または1日の振り返りを行う
argument-hint: [追記する内容 | 空なら振り返り]
allowed-tools: mcp__plugin_pkb_basic-memory__*, Bash(python3:*), Read, Edit
---
- 引数あり: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/pkb.py" daily --append "$ARGUMENTS"` を実行し、完了を1行で報告。
- 引数なし: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/pkb.py" daily` でパスを得て Read し、`bm_project`（最近の活動）または `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/pkb.py" recent --days 1` で今日触れたノートも確認。
  「今日やったこと / 学び / 未完了TODO / 明日の一手」を3〜6行でまとめ、ユーザーの了承を得てデイリーの「学び」「TODO」節に書き込む。
  学びのうち再利用価値の高いものは、恒久ノート化（[idea]/[decision] の Observation として）を提案する。
