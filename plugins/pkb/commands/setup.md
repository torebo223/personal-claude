---
description: 知識ベースの初期設定 — 保管庫を作成し、Basic Memory にプロジェクト「pkb」として登録・索引する
allowed-tools: Bash(python3:*), Bash(uvx:*), Bash(which:*), Bash(echo:*)
---
次を順に実行し、各ステップの結果を短く報告する。失敗したら原因と対処を示して止まる。

1. `which uvx` — 無ければ uv のインストール（https://docs.astral.sh/uv/ ）を案内して終了。
2. 保管庫の場所を `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/pkb.py" path` で確認する。クラウド（claude.ai/code）では、
   セッションに追加された `pkb-vault` リポジトリ（例: /home/user/pkb-vault）が自動で選ばれる。
   クラウドなのに ~/pkb になっている場合は、作ってもセッション終了で消えるので、pkb-vault リポジトリをセッションに追加するよう案内して止まる。
   ローカルなら `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/pkb.py" init` で保管庫を作成（既存なら何も壊さない）。出力されたパスを VAULT とする。
3. `uvx basic-memory project list` で「pkb」があるか確認。
   - 無ければ `uvx basic-memory project add pkb "<VAULT>"`（既存のノートが多いと索引に時間がかかる）。
   - あるがパスが VAULT と違う場合は、ユーザーに確認してから `uvx basic-memory project move pkb "<VAULT>"`。
4. `uvx basic-memory doctor` で問題が無いか確認。意味検索用の埋め込みモデルが取得できない環境では
   `uvx basic-memory config set default_search_type text` でキーワード検索に切り替えられることを伝える。
5. Basic Memory の MCP ツール（bm_search など）を使うには Claude Code の再起動、または `/mcp` での再接続が必要なことを伝える。
