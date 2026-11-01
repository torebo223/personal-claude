---
description: inbox の未整理メモを恒久ノートへ整理する
allowed-tools: mcp__plugin_pkb_basic-memory__*, Bash(python3:*), Read, Edit, Write, Grep, Glob
---
（bm_* ツールには常に project: "pkb"）
1. `bm_list` で inbox/ を一覧し、各メモを `bm_read`。
2. 各メモについて `bm_search` で統合先候補を探し、提案を表で示す:
   「元ファイル / 行き先（既存ノートへ統合 or 新規ノート名と種類）/ Observations のカテゴリ / 張る Relations」。
3. ユーザーの承認後に実行:
   - 統合: 統合先へ `bm_edit` で追記し、元メモは `bm_delete`。
   - 昇格: 本文を Basic Memory 形式に整えて `bm_move` で notes/ 等へ移す（リンクが保たれる）。
   承認されなかったものは残す。
4. 最後に整理件数と残件数を報告。
