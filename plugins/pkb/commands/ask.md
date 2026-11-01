---
description: 知識ベースの内容だけを根拠に質問へ答える（出典付き）
argument-hint: <質問>
allowed-tools: mcp__plugin_pkb_basic-memory__*, Bash(python3:*), Read, Grep, Glob, Agent
---
質問: $ARGUMENTS

1. 質問からキーワード・同義語・表記揺れ（日本語/英語）を抽出し、`bm_search`（project: "pkb"）を数回投げる。
   広範囲の調査が必要なら librarian サブエージェントに委任する。
2. 上位ノートを `bm_read` し、`bm_context` で Relations・リンク元を1〜2段たどって文脈を補う。
3. 回答形式:
   - **回答**: 簡潔に。
   - **根拠**: 引用したノートのパスと該当箇所（Observation など）の短い抜粋。
   - **知識ベースにないこと**: 不足情報。一般知識で補った部分は明示的に分ける。
4. 回答が新しい洞察になった場合、ノート化するか提案する（保存はしない）。
