---
description: 週次レビュー — 最近のノート・プロジェクトを振り返り、知識ベースの健全性を点検する
argument-hint: [日数 (既定 7)]
allowed-tools: mcp__plugin_pkb_basic-memory__*, Bash(python3:*), Bash(uvx:*), Read, Edit, Write, Grep, Glob
---
対象期間: 直近 ${ARGUMENTS:-7} 日（bm_* ツールには常に project: "pkb"）

1. `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/pkb.py" recent --days <日数>` と期間内の daily/ を読む。projects/ の各ノートは `bm_context` で関連も含めて確認。
2. 以下をまとめる:
   - 期間のハイライトと繰り返し現れたテーマ
   - プロジェクトごとの進捗・停滞・次の一手
   - 未完了の [todo] と未解決の [question]（`bm_search` で `[todo]` `[question]` を検索）
   - 健全性: 孤立ノート（`uvx basic-memory orphans --project pkb`）、inbox 残数、タグの揺れとその修正案
3. ユーザーの了承を得て `bm_write` で `reviews/YYYY-Www.md` に保存し、index.md の Relations に追加する。
