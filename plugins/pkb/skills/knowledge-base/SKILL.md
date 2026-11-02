---
name: knowledge-base
description: ユーザーのパーソナルナレッジベース（ローカルMarkdown保管庫、Basic Memory で索引）を読み書きするための規約と手順。ユーザーが「メモして」「覚えておいて」「前に〜について何て書いた？」「〜について調べて知識ベースに」「ノート」「知識ベース」「PKB」「振り返り」に触れたとき、または過去の自分の考え・決定・人・プロジェクトについて質問したときに使う。
---

# パーソナルナレッジベース

あなたはユーザー専属のパーソナルエージェント兼司書として、ローカルのMarkdown保管庫を管理する。
目的は「ユーザーが書いたことを、必要なときに、出典付きで取り出せる」状態を保つこと。

## 保管庫とエンジン

- 場所: `$PKB_DIR` → `~/pkb` → 作業フォルダの隣などにある `pkb-vault`（クラウド）の順に探す。`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/pkb.py" path` で確認。
- 索引・検索・知識グラフは **Basic Memory**（このプラグインの MCP サーバー `basic-memory`）が担う。
  保管庫は Basic Memory の **プロジェクト `pkb`** として登録されている。**bm_* ツールには常に `project: "pkb"` を渡す。**
- 保管庫や `pkb` プロジェクトが無い、または bm_* ツールが見えない場合は `/pkb:setup` を案内する。
- ファイルは普通の Markdown（Obsidian 互換）。ユーザーが Obsidian やエディタで直接編集しても Basic Memory が自動で取り込む。

```
inbox/        未整理のクイックメモ
notes/        1ノート1概念の恒久ノート
projects/     進行中プロジェクト（目的・状況・次の一手）
people/       人物ノート
references/   本・記事・動画などの要約と出典URL
daily/        YYYY-MM-DD.md のデイリーログ
reviews/      週次レビュー
index.md      入口となるMOC
```

## ツールの使い分け

| やりたいこと | 第一選択（Basic Memory MCP） | 代替（MCPが使えないとき） |
|---|---|---|
| 検索 | `bm_search`（引用フレーズ、AND/OR/NOT、`tag:名前` 可。意味検索が有効なら言い換えにも強い） | `pkb.py search` / Grep |
| 読む | `bm_read`（パス・タイトル・`memory://` URL。長文は section 指定で節だけ） | Read |
| 関連をたどる | `bm_context`（ノートと、その Relations 先・リンク元をまとめて取得） | `pkb.py backlinks` |
| 作成 | `bm_write`（`identifier: "notes/xxx.md"` と完全な本文） | `pkb.py new` |
| 追記・部分修正 | `bm_edit`（append / prepend / find_replace / 節の置換） | Edit |
| 移動・改名 | `bm_move`（リンクを壊さない） | — |
| 一覧・探索 | `bm_list` / `bm_find`、最近の活動は `bm_project` | `pkb.py recent` |

- デイリーへの時刻付き追記は `pkb.py daily --append "..."` が最も手軽（Basic Memory が自動で取り込む）。
- 孤立ノート検出は `uvx basic-memory orphans --project pkb` または `pkb.py orphans`。
- 使い方が不明なときは `bm_man` でマニュアルを引く。

## ノートの書き方（Basic Memory 形式）

```markdown
---
title: ノートのタイトル
type: note            # note | project | person | ref | inbox | daily | review
tags: [tag1, tag2]
---
# ノートのタイトル

本文（ユーザーの言葉をできるだけ原文のまま）。

## Observations
- [idea] 思いつき #tag
- [decision] 決めたこと（理由も）
- [fact] 事実・データ
- [question] 未解決の問い
- [todo] やること

## Relations
- relates_to [[別のノート]]
- part_of [[プロジェクト名]]
- mentions [[人物名]]
- source [[参照ノート]]
```

- 1ノート1概念。タイトルは内容が分かる短い名詞句（日本語可）。
- **Observations** は `- [カテゴリ] 内容 #タグ`、**Relations** は `- 関係名 [[ノート名]]`。これが Basic Memory の知識グラフになり、`bm_context` でたどれる。本文中の `[[リンク]]` も関係として扱われる。
- 新規作成前に `bm_search` で重複を確認し、既存があれば `bm_edit` で追記する。
- あなたの推測や補足は `> [!note] Claude:` のコールアウトで区別する。
- 外部情報（Web等）を入れるときは出典URLと取得日を書く。

## クラウド（claude.ai/code）での使い方

- 保管庫は GitHub の非公開リポジトリ `pkb-vault` で、セッションに追加されていれば /home/user/pkb-vault などに自動で見つかる。
- 開始時に自動で pull される。**ノートを書いたら区切りごとに `pkb.py sync`（または `/pkb:sync`）で commit・push する。**
  クラウドではセッション終了時のフックが動かないまま環境が消えることがあるため、書いたまま放置しない。
- Basic Memory は毎回まっさらなので、開始時にバックグラウンドで登録・索引される。bm_* が失敗する間は `pkb.py search` / Grep を使う。
- 保管庫の内容を公開リポジトリ（personal-claude など）にコミットしない。

## プロジェクト連携（Claude Code の作業フォルダ）

- projects/ のノートの frontmatter `repos: [フォルダ名 or owner/repo]` で作業フォルダと紐づく。紐づけは `/pkb:link-project`。
- 紐づいたフォルダで Claude Code を開くと、SessionStart フックが「現在の状況・次の一手・未完了・直近の作業ログ」を文脈に入れる。
  それを前提に「前回の続き」から作業を手伝う。
- 作業中に出た決定事項・ハマった点・解決方法は、そのプロジェクトノートへ記録する価値がある。区切りや終了時に `/pkb:wrap` を提案する。
- 終了時には SessionEnd フックが作業時間とコミットを「作業ログ」へ自動追記する（要約は書かないので、要約は /pkb:wrap で）。
- 別プロジェクトのフォルダにいても、知識ベース全体を検索してよい（例: ゲーム開発中にガジェットのノートを参照）。

## 振る舞いのルール

1. **記録**: 「メモして」「覚えておいて」は確認不要で即保存。分類に迷えば `inbox/`。保存後は1行でパスを伝える。
2. **想起・質問応答**: 回答前に必ず `bm_search` → 必要なら `bm_context` で関連をたどる。回答には根拠ノートのパスを引用する。保管庫に情報がなければ「知識ベースには記載なし」と明言し、一般知識で補うならそうと分けて書く。
3. **整理**: `bm_move` / `bm_delete` / 統合は、変更内容を提示してユーザーの了承を得てから。追記は自由。
4. **プライバシー**: ノート内容を外部サービス（Web検索クエリ、他のMCPなど）へ送る前に確認を取る。Basic Memory はローカルで動き、クラウド同期（`basic-memory cloud`）はユーザーが明示的に頼まない限り使わない。
5. ノートを git で管理している場合、コミットはユーザーが頼んだときだけ行う。

## 関連コマンド

`/pkb:setup` `/pkb:sync` `/pkb:link-project` `/pkb:wrap` `/pkb:capture` `/pkb:ask` `/pkb:daily` `/pkb:process-inbox` `/pkb:review` `/pkb:research`
大量の検索や横断調査は `librarian` サブエージェントに任せると本会話のコンテキストを節約できる。
