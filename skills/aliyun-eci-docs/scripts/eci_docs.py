#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import gzip
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable, Optional

try:
    import requests
except Exception:
    requests = None


USER_AGENT = (
    os.environ.get("ALIYUN_HELP_USER_AGENT")
    or "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)
HELP_COOKIE = (os.environ.get("ALIYUN_HELP_COOKIE") or "").strip()
HELP_REFERER = (os.environ.get("ALIYUN_HELP_REFERER") or "https://help.aliyun.com/zh/eci/").strip()
HELP_DOC_DETAIL_API = "https://help.aliyun.com/help/json/document_detail.json"
MAX_REDIRECTS = 5


@dataclass(frozen=True)
class DocPayload:
    url: str
    page_type: str  # doc | product | unknown
    title: Optional[str]
    keywords: Optional[str]
    last_modified_ms: Optional[int]
    content_html: Optional[str]


class _HtmlToMarkdown(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._out: list[str] = []
        self._list_stack: list[str] = []
        self._in_pre = False
        self._in_code = False
        self._pending_href: Optional[str] = None
        self._link_text_buf: list[str] = []

    def getvalue(self) -> str:
        text = "".join(self._out)
        # 压缩多余空行
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip() + "\n"

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        attrs_dict = dict(attrs)

        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = int(tag[1])
            self._out.append("\n" + ("#" * level) + " ")
            return

        if tag == "p":
            self._out.append("\n\n")
            return

        if tag == "br":
            self._out.append("\n")
            return

        if tag in {"ul", "ol"}:
            self._list_stack.append(tag)
            self._out.append("\n")
            return

        if tag == "li":
            self._out.append("\n- ")
            return

        if tag == "pre":
            self._in_pre = True
            self._out.append("\n\n```")
            return

        if tag == "code":
            self._in_code = True
            if not self._in_pre:
                self._out.append("`")
            return

        if tag == "a":
            self._pending_href = attrs_dict.get("href") or ""
            self._link_text_buf = []
            return

        if tag == "table":
            self._out.append("\n\n[表格]\n")
            return

        if tag in {"section", "main", "div"}:
            return

    def handle_endtag(self, tag: str) -> None:
        if tag in {"ul", "ol"}:
            if self._list_stack:
                self._list_stack.pop()
            self._out.append("\n")
            return

        if tag == "pre":
            self._in_pre = False
            self._out.append("\n```\n")
            return

        if tag == "code":
            if not self._in_pre:
                self._out.append("`")
            self._in_code = False
            return

        if tag == "a":
            text = "".join(self._link_text_buf).strip()
            href = (self._pending_href or "").strip()
            self._pending_href = None
            self._link_text_buf = []
            if not text:
                return
            if href:
                self._out.append(f"[{text}]({href})")
            else:
                self._out.append(text)
            return

    def handle_data(self, data: str) -> None:
        if not data:
            return
        s = html.unescape(data)
        if self._pending_href is not None:
            self._link_text_buf.append(s)
            return

        if self._in_pre:
            # pre 内保留原始换行/空格
            self._out.append(s)
            return

        # 普通文本：压缩多余空白
        s = re.sub(r"\s+", " ", s)
        self._out.append(s)


def _build_headers(accept: str) -> dict[str, str]:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": accept,
        "Accept-Encoding": "gzip",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    if HELP_REFERER:
        headers["Referer"] = HELP_REFERER
    if HELP_COOKIE:
        headers["Cookie"] = HELP_COOKIE
    return headers


def _fetch_url(url: str, timeout_s: int = 30) -> str:
    if requests is not None:
        try:
            resp = requests.get(
                url,
                headers=_build_headers("text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
                timeout=timeout_s,
                allow_redirects=True,
            )
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            raise RuntimeError(f"请求失败: {url} ({e})") from e

    req = urllib.request.Request(
        url,
        headers=_build_headers("text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read()
            if (resp.headers.get("Content-Encoding") or "").lower() == "gzip":
                raw = gzip.decompress(raw)
            charset = resp.headers.get_content_charset() or "utf-8"
            return raw.decode(charset, errors="replace")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {url}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"请求失败: {url} ({e})") from e


def _fetch_json(url: str, timeout_s: int = 30) -> Any:
    if requests is not None:
        try:
            resp = requests.get(
                url,
                headers=_build_headers("application/json, text/plain, */*"),
                timeout=timeout_s,
                allow_redirects=True,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise RuntimeError(f"请求失败: {url} ({e})") from e

    req = urllib.request.Request(
        url,
        headers=_build_headers("application/json, text/plain, */*"),
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read()
            if (resp.headers.get("Content-Encoding") or "").lower() == "gzip":
                raw = gzip.decompress(raw)
            charset = resp.headers.get_content_charset() or "utf-8"
            return json.loads(raw.decode(charset, errors="replace"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {url}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"请求失败: {url} ({e})") from e
    except json.JSONDecodeError as e:
        raise RuntimeError(f"解析 JSON 失败: {url} ({e})") from e


def _normalize_url(url: str) -> str:
    s = (url or "").strip()
    if not s:
        return ""
    if s.startswith("/"):
        s = "https://help.aliyun.com" + s
    try:
        p = urllib.parse.urlparse(s)
        p = p._replace(query="", fragment="")
        return p.geturl().rstrip("/")
    except Exception:
        return s.split("#")[0].split("?")[0].rstrip("/")


def _extract_assigned_json(html_text: str, marker: str) -> Optional[str]:
    """
    从类似 `window.__ICE_PAGE_PROPS__= {...};` 中抽取 JSON 字符串（不含分号）。
    使用括号配对扫描，避免正则在大页面上误匹配/超时。
    """
    idx = html_text.find(marker)
    if idx < 0:
        return None
    # 找到 '=' 后第一个 '{'
    eq = html_text.find("=", idx)
    if eq < 0:
        return None
    start = html_text.find("{", eq)
    if start < 0:
        return None

    brace = 0
    in_str = False
    esc = False
    for i in range(start, len(html_text)):
        ch = html_text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
            continue
        if ch == "{":
            brace += 1
            continue
        if ch == "}":
            brace -= 1
            if brace == 0:
                return html_text[start : i + 1]
            continue
    return None


def _help_url_to_alias(url: str) -> Optional[str]:
    """
    将 `https://help.aliyun.com/zh/eci/...` 转为 document_detail.json 所需的 alias：
    - 去掉 `/zh` 前缀
    - 确保以 `/` 开头、以 `/` 结尾
    """
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme and parsed.scheme not in {"http", "https"}:
        return None
    if parsed.netloc and parsed.netloc != "help.aliyun.com":
        return None

    path = parsed.path or "/"
    if path.startswith("/zh/"):
        path = path[len("/zh") :]
    if not path.startswith("/"):
        path = "/" + path
    if not path.endswith("/"):
        path = path + "/"

    # 只对 ECI 目录页尝试该 API；避免误伤其它 help 页面
    if not (path == "/eci/" or path.startswith("/eci/")):
        return None
    return path


def _build_doc_detail_api_url(alias: str) -> str:
    query = {
        "alias": alias,
        "pageNum": 1,
        "pageSize": 20,
        "website": "cn",
        "language": "zh",
        "channel": "",
    }
    return HELP_DOC_DETAIL_API + "?" + urllib.parse.urlencode(query)


def _try_fetch_via_doc_detail(url: str, timeout_s: int, redirect_depth: int) -> Optional[DocPayload]:
    alias = _help_url_to_alias(url)
    if not alias:
        return None

    api_url = _build_doc_detail_api_url(alias)
    try:
        data = _fetch_json(api_url, timeout_s=timeout_s)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None

    code = data.get("code")
    payload_data = data.get("data") if isinstance(data.get("data"), dict) else None

    if code == 302 and payload_data and redirect_depth < MAX_REDIRECTS:
        redirect_url = payload_data.get("redirectUrl")
        if isinstance(redirect_url, str) and redirect_url.strip():
            ru = redirect_url.strip()
            if ru.startswith("/"):
                ru = "https://help.aliyun.com" + ru
            elif not ru.startswith("http"):
                ru = "https://help.aliyun.com/" + ru.lstrip("/")
            return _try_fetch_via_doc_detail(ru, timeout_s=timeout_s, redirect_depth=redirect_depth + 1)
        return None

    if code != 200 or not payload_data:
        return None

    title = payload_data.get("title") or payload_data.get("docTitle") or payload_data.get("seoTitle")
    keywords = payload_data.get("keywords")
    last_modified_ms = payload_data.get("lastModifiedTime")
    content_html = payload_data.get("content")
    desc = payload_data.get("desc")

    canonical_url = payload_data.get("path") or url

    # doc 节点一般会包含 content；产品/聚合节点可能只有 desc
    if isinstance(content_html, str) and content_html.strip():
        page_type = "doc"
        content = content_html
    elif isinstance(desc, str) and desc.strip():
        page_type = "product"
        content = f"<p>{html.escape(desc.strip())}</p>"
    else:
        page_type = "unknown"
        content = None

    return DocPayload(
        url=str(canonical_url),
        page_type=page_type,
        title=str(title) if isinstance(title, str) and title.strip() else None,
        keywords=str(keywords) if isinstance(keywords, str) and keywords.strip() else None,
        last_modified_ms=int(last_modified_ms) if isinstance(last_modified_ms, int) else None,
        content_html=content if isinstance(content, str) else None,
    )


def _parse_doc_payload(url: str, html_text: str) -> DocPayload:
    json_text = _extract_assigned_json(html_text, "window.__ICE_PAGE_PROPS__")
    if not json_text:
        # 部分目录页/聚合页不是 ICE SSR，先尽力提取 <title>
        title = None
        m = re.search(r"<title>(.*?)</title>", html_text, flags=re.I | re.S)
        if m:
            title = re.sub(r"\s+", " ", html.unescape(m.group(1))).strip()
        return DocPayload(
            url=url,
            page_type="unknown",
            title=title,
            keywords=None,
            last_modified_ms=None,
            content_html=None,
        )

    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"解析 JSON 失败: {url} ({e})") from e

    if isinstance(data, dict) and "docDetailData" in data:
        store = (
            data.get("docDetailData", {})
            .get("storeData", {})
            .get("data", {})
        )
        canonical_url = store.get("path")
        out_url = canonical_url if isinstance(canonical_url, str) and canonical_url.startswith("http") else url
        title = store.get("title") or store.get("docTitle") or store.get("seoTitle")
        keywords = store.get("keywords")
        last_modified_ms = store.get("lastModifiedTime")
        content_html = store.get("content")
        return DocPayload(
            url=out_url,
            page_type="doc",
            title=title,
            keywords=keywords,
            last_modified_ms=last_modified_ms if isinstance(last_modified_ms, int) else None,
            content_html=content_html if isinstance(content_html, str) else None,
        )

    if isinstance(data, dict) and "productData" in data:
        store = (
            data.get("productData", {})
            .get("storeData", {})
            .get("data", {})
        )
        canonical_url = store.get("path")
        out_url = canonical_url if isinstance(canonical_url, str) and canonical_url.startswith("http") else url
        title = store.get("title") or store.get("seoTitle")
        keywords = store.get("keywords")
        last_modified_ms = store.get("lastModifiedTime")
        return DocPayload(
            url=out_url,
            page_type="product",
            title=title,
            keywords=keywords,
            last_modified_ms=last_modified_ms if isinstance(last_modified_ms, int) else None,
            content_html=None,
        )

    return DocPayload(
        url=url,
        page_type="unknown",
        title=None,
        keywords=None,
        last_modified_ms=None,
        content_html=None,
    )


def _ms_to_iso(ms: int) -> str:
    dt = datetime.fromtimestamp(ms / 1000, tz=timezone.utc).astimezone()
    return dt.isoformat(timespec="seconds")


def _to_markdown(payload: DocPayload, requested_url: Optional[str] = None) -> str:
    lines: list[str] = []
    title = payload.title or "(无标题)"
    lines.append(f"# {title}\n")
    meta: list[str] = []
    if requested_url:
        req_n = requested_url.strip()
        cur_n = payload.url.strip()
        if req_n and cur_n and req_n.rstrip("/") != cur_n.rstrip("/"):
            meta.append(f"- 请求URL: {requested_url}")
    meta.append(f"- URL: {payload.url}")
    meta.append(f"- 类型: {payload.page_type}")
    if payload.last_modified_ms is not None:
        meta.append(f"- 最近更新: {_ms_to_iso(payload.last_modified_ms)}")
    if payload.keywords:
        meta.append(f"- 关键词: {payload.keywords}")
    lines.append("\n".join(meta) + "\n")

    if payload.content_html:
        parser = _HtmlToMarkdown()
        parser.feed(payload.content_html)
        lines.append(parser.getvalue())
    else:
        lines.append("\n(该页面未包含可直接抽取的正文内容；可能是目录页/聚合页。)\n")
    return "\n".join(lines).rstrip() + "\n"


def _to_text(payload: DocPayload) -> str:
    if not payload.content_html:
        return ""
    parser = _HtmlToMarkdown()
    parser.feed(payload.content_html)
    md = parser.getvalue()
    # 粗略移除 markdown 标记，保留可搜索文本
    md = re.sub(r"`{1,3}", "", md)
    md = re.sub(r"^#{1,6}\\s+", "", md, flags=re.M)
    md = re.sub(r"\\[(.*?)\\]\\([^)]*\\)", r"\\1", md)
    return md.strip() + "\n"


def _payload_to_index_row(payload: DocPayload, requested_url: str, excerpt_chars: int) -> dict[str, Any]:
    canonical_url = _normalize_url(payload.url or requested_url)
    if not canonical_url:
        canonical_url = requested_url
    text = _to_text(payload) if payload.content_html else ""
    excerpt = text[:excerpt_chars] if text else ""
    row: dict[str, Any] = {
        "url": canonical_url,
        "page_type": payload.page_type,
        "title": payload.title,
        "keywords": payload.keywords,
        "last_modified_ms": payload.last_modified_ms,
        "last_modified_iso": _ms_to_iso(payload.last_modified_ms) if payload.last_modified_ms else None,
        "excerpt": excerpt,
    }
    if requested_url != canonical_url:
        row["aliases"] = [requested_url]
    return row


def _fetch_best_payload(
    requested_url: str,
    timeout_s: int,
    retry_n: int,
    sleep_s: float,
    prefer_api: bool = False,
) -> Optional[DocPayload]:
    payload: Optional[DocPayload] = None
    for attempt in range(retry_n + 1):
        payload = None
        if prefer_api:
            api_payload = _try_fetch_via_doc_detail(requested_url, timeout_s=timeout_s, redirect_depth=0)
            if api_payload is not None:
                payload = api_payload
            if payload is None or payload.page_type == "unknown":
                try:
                    html_text = _fetch_url(requested_url, timeout_s=timeout_s)
                    payload = _parse_doc_payload(requested_url, html_text)
                except Exception:
                    pass
        else:
            try:
                html_text = _fetch_url(requested_url, timeout_s=timeout_s)
                payload = _parse_doc_payload(requested_url, html_text)
            except Exception:
                payload = None
            if payload is None or payload.page_type == "unknown":
                api_payload = _try_fetch_via_doc_detail(requested_url, timeout_s=timeout_s, redirect_depth=0)
                if api_payload is not None:
                    payload = api_payload

        if payload is not None and payload.page_type != "unknown":
            return payload

        if attempt < retry_n:
            cooldown = max(1.0, sleep_s) * (attempt + 1)
            time.sleep(cooldown)

    return payload


def cmd_fetch(args: argparse.Namespace) -> int:
    url = args.url
    requested_url = url
    payload: Optional[DocPayload] = None

    html_err: Optional[Exception] = None
    try:
        html_text = _fetch_url(url, timeout_s=args.timeout)
        payload = _parse_doc_payload(url, html_text)
    except Exception as e:
        html_err = e

    if payload is None or payload.page_type == "unknown":
        api_payload = _try_fetch_via_doc_detail(url, timeout_s=args.timeout, redirect_depth=0)
        if api_payload is not None:
            payload = api_payload

    if payload is None:
        raise RuntimeError(f"抓取失败: {url} ({html_err})") from html_err

    if args.format == "json":
        out_obj: dict[str, Any] = {
            "url": payload.url,
            "requested_url": requested_url,
            "page_type": payload.page_type,
            "title": payload.title,
            "keywords": payload.keywords,
            "last_modified_ms": payload.last_modified_ms,
        }
        if args.include_html:
            out_obj["content_html"] = payload.content_html
        else:
            out_obj["content_html"] = None
        text = json.dumps(out_obj, ensure_ascii=False, indent=2) + "\n"
    elif args.format == "text":
        text = _to_text(payload)
    else:
        text = _to_markdown(payload, requested_url=requested_url)

    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        return 0
    sys.stdout.write(text)
    return 0


def _iter_urls_from_file(path: Path) -> Iterable[str]:
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        yield s


def cmd_index(args: argparse.Namespace) -> int:
    urls_file = Path(args.urls_file)
    out_path = Path(args.out) if args.out else _default_index_path()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    limit = args.limit
    sleep_s = args.sleep
    retry_n = max(0, int(args.retry))

    count = 0
    errors: list[dict[str, Any]] = []
    by_url: dict[str, dict[str, Any]] = {}
    aliases: dict[str, set[str]] = {}

    for url in _iter_urls_from_file(urls_file):
        count += 1
        if limit is not None and count > limit:
            break

        requested_url = _normalize_url(url)
        if not requested_url:
            continue

        try:
            payload = _fetch_best_payload(requested_url=requested_url, timeout_s=args.timeout, retry_n=retry_n, sleep_s=sleep_s)
            if payload is None:
                raise RuntimeError("抓取失败（HTML 与 API 均不可用）")

            new_row = _payload_to_index_row(payload=payload, requested_url=requested_url, excerpt_chars=args.excerpt_chars)
            canonical_url = str(new_row["url"])

            row = by_url.get(canonical_url)
            if row is None:
                row = {k: v for k, v in new_row.items() if k != "aliases"}
                by_url[canonical_url] = row
                aliases[canonical_url] = set()

            for alias in new_row.get("aliases") or []:
                aliases[canonical_url].add(alias)
        except Exception as e:
            errors.append(
                {
                    "url": requested_url,
                    "page_type": "error",
                    "error": str(e),
                }
            )

        if sleep_s > 0:
            time.sleep(sleep_s)

    with out_path.open("w", encoding="utf-8") as f:
        for canonical_url in sorted(by_url.keys()):
            row = by_url[canonical_url]
            alias_list = sorted(aliases.get(canonical_url) or [])
            if alias_list:
                row = dict(row)
                row["aliases"] = alias_list
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        for row in errors:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    sys.stdout.write(f"已写入索引: {out_path} (条数={len(by_url) + len(errors)})\n")
    return 0


def cmd_repair(args: argparse.Namespace) -> int:
    index_path = Path(args.index) if args.index else _default_index_path()
    out_path = Path(args.out) if args.out else index_path
    if not index_path.exists():
        raise SystemExit(f"索引不存在: {index_path}")

    rows: list[dict[str, Any]] = []
    for line in index_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)

    unknown_idx: list[int] = []
    for i, row in enumerate(rows):
        if str(row.get("page_type") or "") != "unknown":
            continue
        u = _normalize_url(str(row.get("url") or ""))
        if not u:
            continue
        unknown_idx.append(i)

    if args.max is not None:
        unknown_idx = unknown_idx[: max(0, int(args.max))]

    repaired = 0
    for i in unknown_idx:
        row = rows[i]
        requested_url = _normalize_url(str(row.get("url") or ""))
        if not requested_url:
            continue

        payload = _fetch_best_payload(
            requested_url=requested_url,
            timeout_s=args.timeout,
            retry_n=max(0, int(args.retry)),
            sleep_s=float(args.sleep),
            prefer_api=True,
        )
        if payload is None or payload.page_type == "unknown":
            continue

        new_row = _payload_to_index_row(payload=payload, requested_url=requested_url, excerpt_chars=args.excerpt_chars)
        rows[i] = new_row
        repaired += 1

        if args.sleep > 0:
            time.sleep(args.sleep)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    remaining_unknown = sum(1 for row in rows if str(row.get("page_type") or "") == "unknown")
    sys.stdout.write(
        f"修复完成: repaired={repaired}, remaining_unknown={remaining_unknown}, out={out_path}\n"
    )
    return 0


def _default_index_path() -> Path:
    skill_dir = Path(__file__).resolve().parent.parent
    return skill_dir / "references" / "eci_docs_index.jsonl"


def cmd_search(args: argparse.Namespace) -> int:
    index_path = Path(args.index) if args.index else _default_index_path()
    query = args.query.strip()
    if not query:
        raise SystemExit("query 不能为空")

    query_l = query.lower()
    results: list[dict[str, Any]] = []

    for line in index_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        hay = " ".join(
            [
                str(row.get("title") or ""),
                str(row.get("url") or ""),
                str(row.get("aliases") or ""),
                str(row.get("keywords") or ""),
                str(row.get("excerpt") or ""),
            ]
        ).lower()
        if query_l in hay:
            results.append(row)

    # 简单排序：标题匹配优先，其次按最近更新时间（新 -> 旧）
    def score(row: dict[str, Any]) -> tuple[int, int]:
        title = (row.get("title") or "").lower()
        in_title = 1 if query_l in title else 0
        lm = int(row.get("last_modified_ms") or 0)
        return (-in_title, -lm)

    results.sort(key=score)

    max_n = args.max
    shown = results[:max_n]
    for i, row in enumerate(shown, start=1):
        title = row.get("title") or "(无标题)"
        url = row.get("url")
        lm = row.get("last_modified_iso") or ""
        sys.stdout.write(f"{i}. {title}\n   {url}\n   {lm}\n")
        if args.show_excerpt and row.get("excerpt"):
            ex = str(row.get("excerpt") or "").strip().replace("\n", " ")
            sys.stdout.write(f"   摘要: {ex[:200]}{'…' if len(ex) > 200 else ''}\n")
    sys.stdout.write(f"\n命中 {len(results)} 条，展示 {len(shown)} 条。\n")
    return 0


def _fetch_product_json(alias: str, timeout_s: int = 30) -> dict[str, Any]:
    query = {
        "alias": alias,
        "website": "cn",
        "language": "zh",
        "channel": "",
    }
    url = "https://help.aliyun.com/help/json/product.json" + "?" + urllib.parse.urlencode(query)
    data = _fetch_json(url, timeout_s=timeout_s)
    if not isinstance(data, dict) or data.get("code") != 200:
        raise RuntimeError(f"product.json 拉取失败: alias={alias}")
    payload = data.get("data")
    if not isinstance(payload, dict):
        raise RuntimeError("product.json 返回 data 非对象")
    return payload


def _extract_urls_from_product_data(product_data: dict[str, Any]) -> list[str]:
    urls: set[str] = set()

    lp = product_data.get("learningPath")
    if isinstance(lp, dict):
        for ch in lp.get("chapters") or []:
            if not isinstance(ch, dict):
                continue
            for sec in ch.get("sections") or []:
                if not isinstance(sec, dict):
                    continue
                for it in sec.get("items") or []:
                    if not isinstance(it, dict):
                        continue
                    u = it.get("url")
                    if isinstance(u, str) and u.strip():
                        urls.add(u.strip())

    intro = product_data.get("introduction")
    if isinstance(intro, dict):
        for b in intro.get("mainBlockButtons") or []:
            if not isinstance(b, dict):
                continue
            u = b.get("url")
            if isinstance(u, str) and u.strip():
                urls.add(u.strip())

    el = product_data.get("experienceLab")
    if isinstance(el, dict):
        for it in el.get("courseList") or []:
            if not isinstance(it, dict):
                continue
            u = it.get("url")
            if isinstance(u, str) and u.strip():
                urls.add(u.strip())

    cp = product_data.get("commonProblem")
    if isinstance(cp, dict):
        for it in cp.get("linkList") or []:
            if not isinstance(it, dict):
                continue
            u = it.get("linkUrl") or it.get("url")
            if isinstance(u, str) and u.strip():
                urls.add(u.strip())

    out: list[str] = []
    for u in urls:
        nu = _normalize_url(u)
        if not nu:
            continue
        if urllib.parse.urlparse(nu).netloc != "help.aliyun.com":
            continue
        out.append(nu)
    return sorted(set(out))


def cmd_discover(args: argparse.Namespace) -> int:
    product_alias = args.alias
    product_data = _fetch_product_json(product_alias, timeout_s=args.timeout)
    home_urls = _extract_urls_from_product_data(product_data)

    out_urls = home_urls
    if args.menu_file:
        menu_set = set(_normalize_url(u) for u in _iter_urls_from_file(Path(args.menu_file)))
        out_urls = sorted([u for u in home_urls if u not in menu_set])

    text = "\n".join(out_urls) + ("\n" if out_urls else "")
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    index_path = Path(args.index) if args.index else _default_index_path()
    if not index_path.exists():
        raise SystemExit(f"索引不存在: {index_path}")

    total = 0
    types: Counter[str] = Counter()
    errors: list[dict[str, Any]] = []
    empty_excerpt: list[str] = []
    alias_rows = 0

    for line in index_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(row, dict):
            continue
        total += 1
        pt = str(row.get("page_type") or "unknown")
        types[pt] += 1
        if pt == "error":
            errors.append(row)
        if pt == "doc" and not str(row.get("excerpt") or "").strip():
            u = str(row.get("url") or "").strip()
            if u:
                empty_excerpt.append(u)
        if row.get("aliases"):
            alias_rows += 1

    sys.stdout.write(f"索引: {index_path}\n")
    sys.stdout.write(f"总条数: {total}\n")
    sys.stdout.write("类型统计:\n")
    for k, v in types.most_common():
        sys.stdout.write(f"- {k}: {v}\n")
    sys.stdout.write(f"包含 aliases 的条目: {alias_rows}\n")
    sys.stdout.write(f"doc 且 excerpt 为空: {len(empty_excerpt)}\n")
    if args.show_empty and empty_excerpt:
        for u in empty_excerpt[: args.max_show]:
            sys.stdout.write(f"  - {u}\n")
    sys.stdout.write(f"error 条目: {len(errors)}\n")
    if args.show_errors and errors:
        for row in errors[: args.max_show]:
            sys.stdout.write(f"  - {row.get('url')}: {row.get('error')}\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="eci_docs.py",
        description="阿里云 ECI 官方文档抓取/索引/检索（help.aliyun.com/zh/eci）",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    p_fetch = sub.add_parser("fetch", help="抓取单篇文档并输出为 Markdown/Text/JSON")
    p_fetch.add_argument("url", help="文档 URL（建议使用 help.aliyun.com/zh/eci/...）")
    p_fetch.add_argument("--format", choices=["md", "text", "json"], default="md")
    p_fetch.add_argument("--timeout", type=int, default=30)
    p_fetch.add_argument("--out", help="输出文件路径（缺省输出到 stdout）")
    p_fetch.add_argument("--include-html", action="store_true", help="JSON 输出时包含 content_html（可能很大）")
    p_fetch.set_defaults(func=cmd_fetch)

    p_index = sub.add_parser("index", help="根据 URL 列表构建本地索引（jsonl）")
    p_index.add_argument("--urls-file", required=True, help="URL 列表文件（每行一个 URL）")
    p_index.add_argument("--out", help="输出索引路径（默认写到 references/eci_docs_index.jsonl）")
    p_index.add_argument("--limit", type=int, default=None, help="只处理前 N 条 URL（调试用）")
    p_index.add_argument("--sleep", type=float, default=0.2, help="每次请求后 sleep 秒数，避免过快")
    p_index.add_argument("--retry", type=int, default=2, help="当页面解析为 unknown 时的重试次数")
    p_index.add_argument("--timeout", type=int, default=30)
    p_index.add_argument("--excerpt-chars", type=int, default=4000, help="保存可检索正文摘要长度")
    p_index.set_defaults(func=cmd_index)

    p_repair = sub.add_parser("repair", help="修复索引中的 unknown 条目")
    p_repair.add_argument("--index", help="输入索引路径（默认 references/eci_docs_index.jsonl）")
    p_repair.add_argument("--out", help="输出索引路径（默认覆盖输入）")
    p_repair.add_argument("--max", type=int, default=None, help="最多修复 N 条 unknown（调试用）")
    p_repair.add_argument("--sleep", type=float, default=0.3, help="每条修复后 sleep 秒数，避免过快")
    p_repair.add_argument("--retry", type=int, default=3, help="单条 unknown 的重试次数")
    p_repair.add_argument("--timeout", type=int, default=30)
    p_repair.add_argument("--excerpt-chars", type=int, default=4000, help="保存可检索正文摘要长度")
    p_repair.set_defaults(func=cmd_repair)

    p_search = sub.add_parser("search", help="在本地索引中按关键字检索")
    p_search.add_argument("query", help="关键字（大小写不敏感）")
    p_search.add_argument("--index", help="索引文件路径（默认 references/eci_docs_index.jsonl）")
    p_search.add_argument("--max", type=int, default=20)
    p_search.add_argument("--show-excerpt", action="store_true")
    p_search.set_defaults(func=cmd_search)

    p_discover = sub.add_parser("discover", help="从 ECI 官网首页产品数据发现入口 URL（可选对比菜单缺失项）")
    p_discover.add_argument("--alias", default="/eci/", help="产品别名（默认 /eci/）")
    p_discover.add_argument("--menu-file", help="可选：菜单 URL 列表文件，用于输出“首页存在但菜单缺失”的 URL")
    p_discover.add_argument("--out", help="输出文件路径（缺省输出到 stdout）")
    p_discover.add_argument("--timeout", type=int, default=30)
    p_discover.set_defaults(func=cmd_discover)

    p_stats = sub.add_parser("stats", help="统计索引质量（类型/错误/空摘要/aliases）")
    p_stats.add_argument("--index", help="索引文件路径（默认 references/eci_docs_index.jsonl）")
    p_stats.add_argument("--show-errors", action="store_true")
    p_stats.add_argument("--show-empty", action="store_true")
    p_stats.add_argument("--max-show", type=int, default=20, help="最多展示 N 条明细")
    p_stats.set_defaults(func=cmd_stats)

    return p


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
