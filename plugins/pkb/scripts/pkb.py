#!/usr/bin/env python3
"""pkb.py — パーソナルナレッジベース用ヘルパー（標準ライブラリのみ）

保管場所: 環境変数 PKB_DIR（未設定なら ~/pkb）

サブコマンド:
  init                      保管庫のフォルダ構成を作成
  path                      保管庫のパスを表示
  status                    ノート数・inbox件数・最近の更新を表示
  new <type> <title> [--tags a,b] [--body TEXT]   ノートを作成しパスを表示
  daily [--append TEXT]     今日のデイリーノートを作成/追記しパスを表示
  search <query> [--tag T] [--limit N]           全文検索（スコア順）
  tags                      タグ一覧と件数
  backlinks <note-title>    [[note-title]] へリンクしているノート
  orphans                   どこからもリンクされていないノート
  recent [--days N]         最近更新されたノート

プロジェクト連携（Claude Code の作業フォルダ ⇔ projects/ のノート）:
  link-project <title> [--repo PATH]   作業フォルダをプロジェクトノートに紐づけ（無ければ作成）
  project-for [--cwd PATH]             作業フォルダに紐づくプロジェクトノートのパス
  projects                             紐づけ一覧
  session-start / session-end          Claude Code フック用（stdin に JSON）
  sync                                 保管庫が Git リポジトリなら commit・pull・push（クラウド用）
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

TYPES = {
    "inbox": "inbox",
    "note": "notes",
    "project": "projects",
    "person": "people",
    "ref": "references",
    "daily": "daily",
}
LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")
TAG_RE = re.compile(r"(?<![\w/#])#([\w\-/]+)", re.UNICODE)


VAULT_NAMES = ("pkb-vault", "pkb")


def vault() -> Path:
    """保管庫の場所: $PKB_DIR → ~/pkb → 作業フォルダの隣・ホーム・/home/user にある pkb-vault / pkb（クラウド用）"""
    if os.environ.get("PKB_DIR"):
        return Path(os.environ["PKB_DIR"]).expanduser()
    home = Path("~/pkb").expanduser()
    if home.exists():
        return home
    bases = [Path.cwd().parent, Path.cwd(), Path.home(), Path("/home/user")]
    for base in bases:
        for name in VAULT_NAMES:
            c = base / name
            if (c / "index.md").exists() or (c / ".git").exists():
                return c
    return home


def all_notes(v: Path):
    if not v.exists():
        return []
    return sorted(p for p in v.rglob("*.md") if not any(part.startswith(".") for part in p.relative_to(v).parts))


def parse(p: Path):
    text = p.read_text(encoding="utf-8", errors="replace")
    meta, body = {}, text
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            for line in text[4:end].splitlines():
                if ":" in line:
                    k, val = line.split(":", 1)
                    meta[k.strip()] = val.strip()
            body = text[end + 4:]
    tags = set()
    raw = meta.get("tags", "").strip("[]")
    tags.update(t.strip().strip("'\"#") for t in raw.split(",") if t.strip())
    tags.update(TAG_RE.findall(body))
    return meta, body, tags


def slugify(title: str) -> str:
    s = re.sub(r"[\\/:*?\"<>|]+", "", title).strip()
    s = re.sub(r"\s+", "-", s)
    return s or dt.datetime.now().strftime("%Y%m%d%H%M%S")


def cmd_init(a):
    v = vault()
    for d in set(TYPES.values()) | {"templates", "attachments"}:
        (v / d).mkdir(parents=True, exist_ok=True)
    idx = v / "index.md"
    if not idx.exists():
        idx.write_text(
            "---\ntitle: index\ntype: moc\n---\n# Index\n\n"
            "知識ベースの入口。主要なトピック・プロジェクトへのリンクをここに置く。\n\n"
            "## Projects\n\n## Topics\n\n## People\n",
            encoding="utf-8",
        )
    print(v)


def cmd_path(a):
    print(vault())


def cmd_status(a):
    v = vault()
    if not v.exists():
        print(f"PKB vault not found: {v} (run: pkb.py init)")
        return
    notes = all_notes(v)
    inbox = [n for n in notes if n.relative_to(v).parts[0] == "inbox"]
    recent = sorted(notes, key=lambda p: p.stat().st_mtime, reverse=True)[:5]
    print(f"vault: {v}")
    print(f"notes: {len(notes)}  inbox(未整理): {len(inbox)}")
    print("recent: " + ", ".join(str(r.relative_to(v)) for r in recent))


def write_note(path: Path, title: str, ntype: str, tags, body: str):
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    fm = f"---\ntitle: {title}\ntype: {ntype}\ncreated: {now}\nupdated: {now}\ntags: [{', '.join(tags)}]\n---\n"
    path.write_text(f"{fm}# {title}\n\n{body}\n", encoding="utf-8")


def cmd_new(a):
    v = vault()
    if a.type not in TYPES:
        sys.exit(f"type must be one of: {', '.join(TYPES)}")
    d = v / TYPES[a.type]
    d.mkdir(parents=True, exist_ok=True)
    base = slugify(a.title)
    if a.type == "inbox":
        base = dt.datetime.now().strftime("%Y%m%d-%H%M-") + base
    p = d / f"{base}.md"
    i = 2
    while p.exists():
        p = d / f"{base}-{i}.md"
        i += 1
    tags = [t.strip() for t in (a.tags or "").split(",") if t.strip()]
    write_note(p, a.title, a.type, tags, a.body or "")
    print(p)


def cmd_daily(a):
    v = vault()
    today = dt.date.today().isoformat()
    p = v / "daily" / f"{today}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        write_note(p, today, "daily", ["daily"], "## ログ\n\n## 学び\n\n## TODO\n")
    if a.append:
        t = dt.datetime.now().strftime("%H:%M")
        with p.open("a", encoding="utf-8") as f:
            f.write(f"- {t} {a.append}\n")
    print(p)


def cmd_search(a):
    v = vault()
    terms = [t.lower() for t in a.query.split() if t]
    results = []
    for p in all_notes(v):
        meta, body, tags = parse(p)
        if a.tag and a.tag.lstrip("#") not in tags:
            continue
        title = meta.get("title", p.stem).lower()
        low = body.lower()
        score = 0
        for t in terms:
            c = low.count(t)
            if c == 0 and t not in title and t not in {x.lower() for x in tags}:
                score = -1
                break
            score += c + (5 if t in title else 0) + (3 if t in {x.lower() for x in tags} else 0)
        if not terms:
            score = 1
        if score > 0:
            snippet = ""
            for line in body.splitlines():
                if any(t in line.lower() for t in terms):
                    snippet = line.strip()[:160]
                    break
            results.append((score, p, snippet))
    results.sort(key=lambda r: (-r[0], str(r[1])))
    for score, p, snip in results[: a.limit]:
        print(f"{score:>3}  {p.relative_to(v)}  |  {snip}")
    if not results:
        print("(no matches)")


def cmd_tags(a):
    counts = {}
    for p in all_notes(vault()):
        for t in parse(p)[2]:
            counts[t] = counts.get(t, 0) + 1
    for t, c in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
        print(f"{c:>4}  #{t}")


def link_graph(v):
    notes = all_notes(v)
    names = {p.stem: p for p in notes}
    for p in notes:
        t = parse(p)[0].get("title")
        if t:
            names.setdefault(t, p)
    inbound = {p: set() for p in notes}
    for p in notes:
        for target in LINK_RE.findall(p.read_text(encoding="utf-8", errors="replace")):
            tp = names.get(target.strip())
            if tp and tp != p:
                inbound[tp].add(p)
    return names, inbound


def cmd_backlinks(a):
    v = vault()
    names, inbound = link_graph(v)
    tp = names.get(a.title)
    if not tp:
        print(f"(note not found: {a.title})")
        return
    for p in sorted(inbound[tp]):
        print(p.relative_to(v))


def cmd_orphans(a):
    v = vault()
    _, inbound = link_graph(v)
    for p, src in sorted(inbound.items()):
        rel = p.relative_to(v)
        if not src and rel.parts[0] not in ("daily", "templates") and rel.name != "index.md":
            print(rel)


def cmd_recent(a):
    v = vault()
    cutoff = dt.datetime.now().timestamp() - a.days * 86400
    notes = [p for p in all_notes(v) if p.stat().st_mtime >= cutoff]
    for p in sorted(notes, key=lambda p: p.stat().st_mtime, reverse=True):
        ts = dt.datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        print(f"{ts}  {p.relative_to(v)}")


# ---------------------------------------------------------------- プロジェクト連携

PROJECT_TEMPLATE = """## 概要
（このプロジェクトは何か・ゴール）

## 現在の状況
（未記入）

## 次の一手
- （未記入）

## 決定事項

## Observations

## Relations

## 作業ログ
"""
LOG_HEADING = "## 作業ログ"


def git(cwd, *args, timeout=5):
    try:
        r = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def repo_keys(cwd: Path):
    """作業フォルダを識別するキーの集合（フルパス・フォルダ名・リモートの owner/repo と repo）"""
    cwd = Path(cwd).expanduser().resolve()
    top = Path(git(cwd, "rev-parse", "--show-toplevel") or cwd)
    keys = {str(top), top.name}
    remote = git(top, "remote", "get-url", "origin")
    m = re.search(r"[:/]([^/:]+)/([^/]+?)(?:\.git)?$", remote)
    if m:
        keys |= {f"{m.group(1)}/{m.group(2)}", m.group(2)}
    return top, {k.lower() for k in keys}


def parse_list(val: str):
    return [x.strip().strip("'\"") for x in val.strip().strip("[]").split(",") if x.strip()]


def find_project(cwd):
    v = vault()
    top, keys = repo_keys(cwd)
    for p in sorted((v / "projects").glob("*.md")):
        repos = parse_list(parse(p)[0].get("repos", ""))
        if any(r.lower() in keys or str(Path(r).expanduser()).lower() in keys for r in repos):
            return p, top
    return None, top


def set_frontmatter(p: Path, key: str, value: str):
    text = p.read_text(encoding="utf-8")
    if text.startswith("---\n") and (end := text.find("\n---", 4)) != -1:
        fm, rest = text[4:end], text[end:]
        if re.search(rf"^{key}:", fm, re.M):
            fm = re.sub(rf"^{key}:.*$", f"{key}: {value}", fm, flags=re.M)
        else:
            fm += f"\n{key}: {value}"
        p.write_text(f"---\n{fm}{rest}", encoding="utf-8")


def cmd_link_project(a):
    v = vault()
    top, _ = repo_keys(a.repo or os.getcwd())
    d = v / "projects"
    d.mkdir(parents=True, exist_ok=True)
    p = next((q for q in d.glob("*.md") if parse(q)[0].get("title", q.stem) == a.title or q.stem == slugify(a.title)), None)
    if p is None:
        p = d / f"{slugify(a.title)}.md"
        write_note(p, a.title, "project", ["project"], PROJECT_TEMPLATE)
        set_frontmatter(p, "status", "active")
    repos = parse_list(parse(p)[0].get("repos", ""))
    if top.name not in repos:
        repos.append(top.name)
    set_frontmatter(p, "repos", "[" + ", ".join(repos) + "]")
    print(f"{p}  <=  {top}  (repos: {', '.join(repos)})")


def cmd_project_for(a):
    p, _ = find_project(a.cwd or os.getcwd())
    if p:
        print(p)
    else:
        sys.exit(1)


def cmd_projects(a):
    v = vault()
    for p in sorted((v / "projects").glob("*.md")):
        meta = parse(p)[0]
        print(f"{meta.get('title', p.stem)}  [{meta.get('status', '-')}]  repos: {meta.get('repos', '-')}  ({p.relative_to(v)})")


def sections(body: str):
    out, cur = {}, None
    for line in body.splitlines():
        if line.startswith("## "):
            cur = line[3:].strip()
            out[cur] = []
        elif cur:
            out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def state_file(session_id: str) -> Path:
    d = Path(os.environ.get("XDG_CACHE_HOME", "~/.cache")).expanduser() / "pkb" / "sessions"
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{re.sub(r'[^A-Za-z0-9_-]', '_', session_id or 'unknown')}.json"


def hook_input():
    try:
        return json.loads(sys.stdin.read() or "{}")
    except Exception:
        return {}


def is_git_vault(v: Path) -> bool:
    return (v / ".git").exists()


def sync_vault(v: Path, pull_only=False) -> str:
    """保管庫が Git リポジトリなら commit → pull --rebase → push する。結果を1行で返す"""
    if not is_git_vault(v):
        return "保管庫は Git 管理されていません（同期不要）"
    msg = []
    if not pull_only and git(v, "status", "--porcelain"):
        git(v, "add", "-A")
        git(v, "commit", "-q", "-m", f"pkb: sync {dt.datetime.now():%Y-%m-%d %H:%M}")
        msg.append("commit")
    if git(v, "remote"):
        r = subprocess.run(["git", "-C", str(v), "pull", "-q", "--rebase", "--autostash"],
                           capture_output=True, text=True, timeout=60)
        msg.append("pull" if r.returncode == 0 else f"pull失敗: {r.stderr.strip()[:200]}")
        if not pull_only and git(v, "rev-list", "--count", "@{u}..HEAD", timeout=10) not in ("", "0"):
            r = subprocess.run(["git", "-C", str(v), "push", "-q"], capture_output=True, text=True, timeout=90)
            msg.append("push" if r.returncode == 0 else f"push失敗: {r.stderr.strip()[:200]}")
    return "同期: " + (", ".join(msg) or "変更なし")


def cmd_sync(a):
    print(sync_vault(vault()))


def ensure_basic_memory(v: Path):
    """Basic Memory にプロジェクト pkb が未登録なら、バックグラウンドで登録・索引する（クラウドの毎回まっさらな環境向け）"""
    cfg = Path("~/.basic-memory/config.json").expanduser()
    try:
        projects = json.loads(cfg.read_text(encoding="utf-8")).get("projects", {}) if cfg.exists() else {}
    except Exception:
        projects = {}
    if Path(projects.get("pkb", {}).get("path", "")).expanduser() == v:
        return False
    from shutil import which
    if not which("uvx"):
        return False
    sub = ["project", "move", "pkb", str(v)] if "pkb" in projects else ["project", "add", "pkb", str(v)]
    subprocess.Popen(["uvx", "basic-memory", *sub], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL, start_new_session=True)
    return True


def cmd_session_start(a):
    """SessionStart フック: 保管庫の状況と、紐づくプロジェクトの「前回の続き」を Claude の文脈に出力する"""
    data = hook_input()
    v = vault()
    if not v.exists():
        print(f"[pkb] 知識ベース未作成（{v}）。/pkb:setup で初期設定できます。")
        return
    cwd = data.get("cwd") or os.getcwd()
    git_vault = is_git_vault(v)
    if git_vault:
        pulled = sync_vault(v, pull_only=True)
    registering = ensure_basic_memory(v)
    p, top = find_project(cwd)
    notes = all_notes(v)
    inbox = sum(1 for n in notes if n.relative_to(v).parts[0] == "inbox")
    print(f"[pkb] 知識ベース: {v}（ノート {len(notes)} 件 / inbox 未整理 {inbox} 件）")
    if git_vault:
        print(f"[pkb] 保管庫は Git で同期しています（{pulled}）。ノートを書いたら、区切りごとに "
              f"`python3 \"${{CLAUDE_PLUGIN_ROOT}}/scripts/pkb.py\" sync` で commit・push してください"
              "（クラウドでは終了時の自動同期が動かないことがあるため）。")
    if registering:
        print("[pkb] Basic Memory への登録・索引をバックグラウンドで開始しました。bm_* ツールが失敗する間は pkb.py search / Grep を使ってください。")
    if not p:
        return
    meta, body, _ = parse(p)
    title = meta.get("title", p.stem)
    sec = sections(body)
    open_items = [l.strip() for l in body.splitlines() if re.match(r"\s*- \[(todo|question)\]", l)]
    log = [l for l in sec.get("作業ログ", "").splitlines() if l.strip()][-3:]
    parts = [
        f"[pkb] この作業フォルダ（{top.name}）はプロジェクト「{title}」に紐づいています: {p}",
        "このセッションでは、作業内容・決定事項・ハマった点をこのプロジェクトノートに記録する前提で動いてください（Basic Memory の project は \"pkb\"）。",
        "作業の区切りや終了時には /pkb:wrap でのまとめをユーザーに提案してください。",
    ]
    for name in ("現在の状況", "次の一手"):
        if sec.get(name) and "未記入" not in sec[name]:
            parts.append(f"■ {name}\n{sec[name][:800]}")
    if open_items:
        parts.append("■ 未完了・未解決\n" + "\n".join(open_items[:10]))
    if log:
        parts.append("■ 直近の作業ログ\n" + "\n".join(log))
    print("\n\n".join(parts)[:3500])
    state_file(data.get("session_id", "")).write_text(
        json.dumps({"start": dt.datetime.now().isoformat(), "project": str(p), "repo": str(top)}), encoding="utf-8")


def cmd_session_end(a):
    """SessionEnd フック: 紐づくプロジェクトのノートに、時間・ブランチ・コミットを機械的に記録する"""
    data = hook_input()
    sf = state_file(data.get("session_id", ""))
    if not sf.exists():
        return
    st = json.loads(sf.read_text(encoding="utf-8"))
    sf.unlink()
    p, repo = Path(st["project"]), Path(st["repo"])
    if not p.exists():
        return
    start = dt.datetime.fromisoformat(st["start"])
    end = dt.datetime.now()
    commits = [c for c in git(repo, "log", f"--since={start.isoformat()}", "--pretty=format:%h %s").splitlines() if c]
    if not commits and (end - start).total_seconds() < 300:
        return  # 短く何も起きなかったセッションは記録しない
    branch = git(repo, "rev-parse", "--abbrev-ref", "HEAD") or "-"
    entry = f"- {start:%Y-%m-%d %H:%M}–{end:%H:%M} Claude Code セッション（{repo.name} / {branch}）"
    entry += f" コミット {len(commits)} 件" + "".join(f"\n  - {c}" for c in commits[:10])
    text = p.read_text(encoding="utf-8")
    if LOG_HEADING not in text:
        text = text.rstrip() + f"\n\n{LOG_HEADING}\n"
    p.write_text(text.rstrip() + "\n" + entry + "\n", encoding="utf-8")
    set_frontmatter(p, "updated", end.strftime("%Y-%m-%d %H:%M"))
    title = parse(p)[0].get("title", p.stem)
    a.append = f"[[{title}]] で作業（コミット {len(commits)} 件）"
    with open(os.devnull, "w") as null:
        old, sys.stdout = sys.stdout, null
        try:
            cmd_daily(a)
        finally:
            sys.stdout = old


def cmd_session_end_sync(a):
    cmd_session_end(a)
    v = vault()
    if is_git_vault(v):
        sync_vault(v)


def safe(f):
    def run(a):
        try:
            f(a)
        except Exception as e:  # フックは Claude Code の動作を妨げない
            print(f"[pkb] hook error: {e}", file=sys.stderr)
    return run


def main():
    ap = argparse.ArgumentParser(description="Personal knowledge base helper")
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("init").set_defaults(f=cmd_init)
    sp.add_parser("path").set_defaults(f=cmd_path)
    sp.add_parser("status").set_defaults(f=cmd_status)
    n = sp.add_parser("new")
    n.add_argument("type")
    n.add_argument("title")
    n.add_argument("--tags")
    n.add_argument("--body")
    n.set_defaults(f=cmd_new)
    d = sp.add_parser("daily")
    d.add_argument("--append")
    d.set_defaults(f=cmd_daily)
    s = sp.add_parser("search")
    s.add_argument("query", nargs="?", default="")
    s.add_argument("--tag")
    s.add_argument("--limit", type=int, default=20)
    s.set_defaults(f=cmd_search)
    sp.add_parser("tags").set_defaults(f=cmd_tags)
    b = sp.add_parser("backlinks")
    b.add_argument("title")
    b.set_defaults(f=cmd_backlinks)
    sp.add_parser("orphans").set_defaults(f=cmd_orphans)
    r = sp.add_parser("recent")
    r.add_argument("--days", type=int, default=7)
    r.set_defaults(f=cmd_recent)
    lp = sp.add_parser("link-project")
    lp.add_argument("title")
    lp.add_argument("--repo")
    lp.set_defaults(f=cmd_link_project)
    pf = sp.add_parser("project-for")
    pf.add_argument("--cwd")
    pf.set_defaults(f=cmd_project_for)
    sp.add_parser("projects").set_defaults(f=cmd_projects)
    sp.add_parser("session-start").set_defaults(f=safe(cmd_session_start))
    sp.add_parser("session-end").set_defaults(f=safe(cmd_session_end_sync))
    sp.add_parser("sync").set_defaults(f=cmd_sync)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
