---
description: この作業セッションをまとめて、プロジェクトノートとデイリーに記録する
argument-hint: [補足メモ]
allowed-tools: mcp__plugin_pkb_basic-memory__*, Bash(python3:*), Bash(git:*), Read, Edit
---
1. `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/pkb.py" project-for` で紐づくプロジェクトノートを特定。無ければ `/pkb:link-project` を提案して終了。
2. このセッションの会話、`git status`、`git log --oneline`（このセッション中のコミット）、補足「$ARGUMENTS」から次をまとめる:
   - やったこと（2〜5行）
   - 決定事項とその理由
   - ハマった点と解決方法（エラー文・原因・直し方。次に同じ問題に当たったとき検索で見つかるように具体的に）
   - 次の一手 / 未完了
3. 内容をユーザーに見せて了承を得てから、`bm_edit`（project: "pkb"）でプロジェクトノートを更新:
   - 「現在の状況」「次の一手」節を最新に置き換える（find_replace / 節の置換）
   - 「決定事項」に追記、ハマった点は Observations に `- [problem] ... → [solution] ...` 形式で追記
   - 「作業ログ」に `- YYYY-MM-DD 要約` を1行追記
   - 他のプロジェクトにも関係する学び（例: 部品・ライブラリの癖）は、別の恒久ノートにして Relations でつなぐことを提案
4. `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/pkb.py" daily --append "[[プロジェクト名]] 要約1行"` でデイリーにも残す。
