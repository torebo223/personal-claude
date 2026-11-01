# pkb — パーソナルナレッジベース × パーソナルエージェント（Claude Code プラグイン）

ローカルのMarkdown保管庫（Obsidian互換）を知識ベースにして、Claude Code を専属の司書・秘書として使うプラグイン。

## インストール
```bash
claude plugin marketplace add torebo223/personal-claude
claude plugin install pkb@personal-claude
```
保管庫の場所は環境変数 `PKB_DIR`（既定 `~/pkb`）。既存のObsidian保管庫も指定可能。

### Basic Memory（検索・知識グラフ）
- 前提: [uv](https://docs.astral.sh/uv/)（`uvx` コマンド）。MCP サーバー `uvx basic-memory mcp` はプラグインが自動で起動する。
- 初回はセッション内で **`/pkb:setup`** を実行 → 保管庫を作成し、Basic Memory にプロジェクト `pkb` として登録・索引する。
- その後 Claude Code を再起動（または `/mcp` で再接続）すると `bm_search` などのツールが使える。
- 意味検索（言い換えに強い検索）は初回に埋め込みモデル（約100MB, HuggingFace）を取得する。ネットワーク制限で取得できない環境では
  `uvx basic-memory config set default_search_type text` でキーワード検索のみに切り替える。
- データはすべてローカル。Basic Memory Cloud への同期は明示的に設定しない限り行われない。

## 構成
| 種類 | 名前 | 役割 |
|---|---|---|
| MCP | basic-memory | 全文/意味検索・知識グラフ（Observations / Relations）・ノートの読み書き・リンクを保った移動 |
| スキル | knowledge-base | 保管庫の構成・Basic Memory 形式のノート規約・振る舞いルール。「メモして」「前に何て書いた？」で自動発動 |
| コマンド | `/pkb:setup` | 保管庫作成と Basic Memory への登録 |
| | `/pkb:capture <内容>` | 即記録（重複確認・リンク・デイリーへの痕跡） |
| | `/pkb:ask <質問>` | 知識ベースだけを根拠に出典付きで回答 |
| | `/pkb:daily [内容]` | デイリー追記 / 1日の振り返り |
| | `/pkb:process-inbox` | inbox の整理（承認制） |
| | `/pkb:review [日数]` | 週次レビュー＋孤立ノート・タグ揺れ点検 |
| | `/pkb:research <トピック>` | 既存ノート＋Web調査で参照ノート作成 |
| エージェント | librarian | 読み取り専用の横断検索（haiku、コンテキスト節約） |
| フック | SessionStart | 起動時に保管庫の状況（件数・inbox・最近の更新）を注入 |
| スクリプト | scripts/pkb.py | デイリー追記・保管庫初期化・状況表示。MCP が使えないときの検索の代替 |
