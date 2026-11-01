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
| | `/pkb:link-project [名前]` | 今の作業フォルダをプロジェクトノートに紐づけ |
| | `/pkb:wrap` | 作業セッションのまとめ（状況・決定・ハマった点・次の一手）をノートに記録 |
| | `/pkb:capture <内容>` | 即記録（重複確認・リンク・デイリーへの痕跡） |
| | `/pkb:ask <質問>` | 知識ベースだけを根拠に出典付きで回答 |
| | `/pkb:daily [内容]` | デイリー追記 / 1日の振り返り |
| | `/pkb:process-inbox` | inbox の整理（承認制） |
| | `/pkb:review [日数]` | 週次レビュー＋孤立ノート・タグ揺れ点検 |
| | `/pkb:research <トピック>` | 既存ノート＋Web調査で参照ノート作成 |
| エージェント | librarian | 読み取り専用の横断検索（haiku、コンテキスト節約） |
| フック | SessionStart | 保管庫の状況に加え、紐づいたプロジェクトの「現在の状況・次の一手・未完了・直近ログ」を注入 |
| | SessionEnd | 紐づいたプロジェクトの作業ログに時間・ブランチ・コミットを自動追記（5分未満でコミット0なら記録しない） |
| スクリプト | scripts/pkb.py | デイリー追記・保管庫初期化・状況表示。MCP が使えないときの検索の代替 |

## プロジェクト連携

1. アプリ・ゲームなどの作業フォルダで Claude Code を開き、`/pkb:link-project やることアプリ`
   → `projects/やることアプリ.md` が作られ、frontmatter の `repos:` にフォルダ名が入る（`owner/repo` やフルパスでも可。1ノートに複数フォルダ可）。
2. 次からそのフォルダで開くと、前回の続きを Claude が最初から知っている状態で始まる。
3. 区切りで `/pkb:wrap` → 要約・決定事項・ハマった点をノートに保存。終了時のコミット記録は自動。

紐づけ一覧は `python3 scripts/pkb.py projects`。
