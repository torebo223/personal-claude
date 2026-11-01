---
description: トピックを既存ノートとWebで調べ、出典付きの参照ノートを作る
argument-hint: <トピック>
allowed-tools: mcp__plugin_pkb_basic-memory__*, Bash(python3:*), Read, Edit, Write, Grep, Glob, WebSearch, WebFetch
---
トピック: $ARGUMENTS

1. まず `bm_search` / `bm_context`（project: "pkb"）で、ユーザーが既に知っていること・書いていることを把握する。
2. 不足部分をWebで調査（検索クエリにユーザーの個人情報やノート本文を含めない）。
3. `bm_write` で `references/<トピック>.md` を作成: 要点 / 詳細 / Observations（[fact] に出典URLと取得日）/
   Relations（既存ノートへの relates_to など）。
4. 既存ノートと矛盾する点があれば指摘する（既存ノートは勝手に書き換えない）。
