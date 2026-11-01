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
"""
import argparse
import datetime as dt
import os
import re
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


def vault() -> Path:
    return Path(os.environ.get("PKB_DIR", "~/pkb")).expanduser()


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
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
