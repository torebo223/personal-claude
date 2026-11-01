---
description: 思いつき・情報・決定事項を知識ベースに素早く記録する
argument-hint: <メモしたい内容>
allowed-tools: mcp__plugin_pkb_basic-memory__*, Bash(python3:*), Read, Edit, Write, Grep, Glob
---
knowledge-base スキルの規約に従い、次の内容を知識ベースに記録する:

$ARGUMENTS

手順（Basic Memory の bm_* ツールには常に project: "pkb"）:
1. 内容から種類（note / project / person / ref / inbox）・タイトル・タグを決める。迷ったら inbox。
2. `bm_search` で既存ノートを確認。該当があれば `bm_edit`（append）で Observations に追記、なければ `bm_write` で
   Basic Memory 形式（frontmatter + 本文 + Observations + Relations）の新規ノートを作る。inbox は `inbox/YYYYMMDD-HHMM-タイトル.md`。
3. Relations に関連ノートを1つ以上つなぐ（検索で見つけた既存ノート、関係するプロジェクトや人物）。
4. 今日のデイリーに `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/pkb.py" daily --append "[[タイトル]] を記録"` で痕跡を残す。
5. 保存先パスを1行で報告。引数が空なら、何を記録したいか尋ねる。
bm_* ツールが使えなければ `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/pkb.py" new` / Edit で代替し、`/pkb:setup` を案内する。
