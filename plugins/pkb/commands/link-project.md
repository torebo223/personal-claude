---
description: 今の作業フォルダ（リポジトリ）を知識ベースのプロジェクトノートに紐づける
argument-hint: [プロジェクト名]
allowed-tools: mcp__plugin_pkb_basic-memory__*, Bash(python3:*), Bash(git:*), Read, Edit
---
1. `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/pkb.py" project-for` で既に紐づいているか確認。紐づいていれば、そのノートを伝えて終了。
2. プロジェクト名を決める: 引数「$ARGUMENTS」があればそれ。無ければ `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/pkb.py" projects` の既存一覧と、
   フォルダ名・README から候補を出してユーザーに選んでもらう（既存ノートへの紐づけも可）。
3. `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/pkb.py" link-project "<プロジェクト名>"` を実行（ノートが無ければ projects/ にひな形付きで作成される）。
4. 新規作成した場合は README・最近のコミット（`git log --oneline -15`）を読み、ノートの「概要」「現在の状況」「次の一手」の
   下書きを提示し、了承を得て `bm_edit`（project: "pkb"）で書き込む。
5. 以後このフォルダで Claude Code を開くと、前回の続きが自動で読み込まれ、終了時に作業ログが残ることを伝える。
