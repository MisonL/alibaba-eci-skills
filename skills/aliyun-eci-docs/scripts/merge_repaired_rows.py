#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _normalize_url(url: str) -> str:
    return (url or "").strip().rstrip("/")


def _load_rows_file(path: Path) -> list[dict[str, Any]]:
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return []

    payload = json.loads(raw)
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict):
        rows = payload.get("repairedRows") or payload.get("rows") or []
    else:
        rows = []

    out: list[dict[str, Any]] = []
    for row in rows:
        if isinstance(row, dict):
            out.append(row)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="将浏览器批量修复结果合并回 eci_docs_index.jsonl")
    parser.add_argument("--index", required=True, help="现有索引文件（jsonl）")
    parser.add_argument("--rows-file", required=True, help="修复结果 JSON 文件（array 或 {repairedRows:[]}）")
    parser.add_argument("--out", help="输出索引文件（默认覆盖 index）")
    parser.add_argument("--backup", action="store_true", help="覆盖前备份为 <index>.bak")
    args = parser.parse_args()

    index_path = Path(args.index)
    out_path = Path(args.out) if args.out else index_path
    rows_file = Path(args.rows_file)

    if not index_path.exists():
        raise SystemExit(f"索引不存在: {index_path}")
    if not rows_file.exists():
        raise SystemExit(f"修复结果文件不存在: {rows_file}")

    if args.backup and out_path == index_path:
        bak = index_path.with_suffix(index_path.suffix + ".bak")
        bak.write_text(index_path.read_text(encoding="utf-8"), encoding="utf-8")

    index_rows: list[dict[str, Any]] = []
    url_to_pos: dict[str, int] = {}
    alias_to_pos: dict[str, int] = {}

    for line in index_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(row, dict):
            continue
        index_rows.append(row)

    for i, row in enumerate(index_rows):
        u = _normalize_url(str(row.get("url") or ""))
        if u:
            url_to_pos[u] = i
        for alias in row.get("aliases") or []:
            a = _normalize_url(str(alias or ""))
            if a:
                alias_to_pos[a] = i

    repaired_rows = _load_rows_file(rows_file)
    replaced = 0
    appended = 0
    skipped = 0

    for row in repaired_rows:
        u = _normalize_url(str(row.get("url") or ""))
        if not u:
            skipped += 1
            continue
        row = dict(row)
        row["url"] = u
        pos = url_to_pos.get(u)
        if pos is None:
            pos = alias_to_pos.get(u)
        if pos is None:
            index_rows.append(row)
            new_pos = len(index_rows) - 1
            url_to_pos[u] = new_pos
            appended += 1
        else:
            index_rows[pos] = row
            url_to_pos[u] = pos
            replaced += 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for row in index_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(
        f"merge done: replaced={replaced}, appended={appended}, skipped={skipped}, out={out_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
