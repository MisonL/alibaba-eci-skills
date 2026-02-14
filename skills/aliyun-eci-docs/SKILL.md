---
name: aliyun-eci-docs
description: "阿里云 ECI 官方文档抓取、索引、检索与事实复核。Use when 需要基于 https://help.aliyun.com/zh/eci 确认功能、参数、计费、限制、排障结论，或需要更新本地索引/覆盖清单并输出可追溯依据链接。"
---

# 阿里云 ECI 文档助手

## 快速开始

1)（推荐）一键刷新索引与覆盖差异（discover + merge + index + stats）
- `bash scripts/refresh_eci_docs.sh`
- 若遇到官网风控（验证码拦截）导致索引质量下降，可将浏览器 `help.aliyun.com` 的 Cookie（单行）写入 `references/help_cookie.txt` 后重试
- `references/help_cookie.txt` 仅临时使用，不要长期保存或提交真实会话 Cookie
- 脚本会自动备份旧索引到 `references/eci_docs_index.jsonl.bak`
- `discover` 阶段若命中风控会自动降级，不中断整体刷新流程

2)（可选）更新 ECI 文档目录 URL 列表（chrome-devtools）
- 打开任意 ECI 文档页（`https://help.aliyun.com/zh/eci/...`）
- 在 `evaluate_script` 执行 `references/extract_eci_menu_urls.js`
- 将返回结果中的 `urls` 保存为 `references/eci_menu_urls.txt`（一行一个 URL）

3)（可选）发现“官网首页存在但左侧目录缺失”的入口 URL（用于维护补充列表）
- `python3 scripts/eci_docs.py discover --menu-file references/eci_menu_urls.txt`
- 将输出结果中你认为需要保留的 URL 追加到 `references/eci_extra_urls.txt`

4)（推荐）生成综合 URL 列表（补齐首页入口/旧链接）
- `cat references/eci_menu_urls.txt references/eci_extra_urls.txt | sort -u > references/eci_all_urls.txt`

5)（推荐）构建本地索引（便于离线检索）
- `python3 scripts/eci_docs.py index --urls-file references/eci_all_urls.txt`
- 如遇大量 `unknown`，可提高重试并放慢节奏：`python3 scripts/eci_docs.py index --urls-file references/eci_all_urls.txt --retry 4 --sleep 0.5`
- 默认输出：`references/eci_docs_index.jsonl`

5.1)（推荐）对 `unknown` 条目做二次修复
- `python3 scripts/eci_docs.py repair --index references/eci_docs_index.jsonl`
- 可限制样本：`python3 scripts/eci_docs.py repair --index references/eci_docs_index.jsonl --max 30`

6) 按关键字检索
- `python3 scripts/eci_docs.py search 公网 --show-excerpt`
- `python3 scripts/eci_docs.py search 镜像缓存`
- `python3 scripts/eci_docs.py search CreateContainerGroup`

7) 拉取单篇文档并转为 Markdown/Text
- `python3 scripts/eci_docs.py fetch <URL> --format md --out /tmp/eci_doc.md`
- `python3 scripts/eci_docs.py fetch <URL> --format text`

7.1)（推荐）命令行抓取遇到风控时，改用浏览器会话抓取单篇
- 打开任意 ECI 文档页（保证同域会话有效）
- 在 `evaluate_script` 执行 `references/fetch_eci_doc_via_browser.js`
- 将脚本中的 `targetUrl` 改成目标页面 URL，返回 `title/excerpt/lastModifiedTime` 作为权威依据

7.2)（推荐）批量修复 unknown（浏览器会话 + 合并）
- 在 `evaluate_script` 执行 `references/repair_unknown_via_browser.js`（每批建议 10~30 条 URL）
- 将返回 JSON 保存到本地（如 `/tmp/eci_repaired_rows.json`）
- 执行：`python3 scripts/merge_repaired_rows.py --index references/eci_docs_index.jsonl --rows-file /tmp/eci_repaired_rows.json --backup`

8)（可选）检查索引质量（是否有 error、空摘要、aliases）
- `python3 scripts/eci_docs.py stats --show-errors --show-empty`

## 工作流（用官方文档回答问题）

- 先用 `search` 找到最相关的官方页面（优先看标题命中与最近更新时间）
- 对关键页面用 `fetch --format md` 拉取，提炼“前提/限制/参数定义/计费项/排障步骤”
- 按“结论 -> 操作步骤 -> 注意事项/限制 -> 依据链接（URL 列表）”输出
- 避免大段粘贴原文；只引用必要的字段名/错误码/硬性限制

## 脚本与数据

- `scripts/eci_docs.py`: 抓取/索引/检索（`fetch/index/search`）
- `scripts/merge_repaired_rows.py`: 将浏览器批量修复结果合并回索引
- `scripts/refresh_eci_docs.sh`: 一键执行 discover + merge + index + repair + stats
- `references/extract_eci_menu_urls.js`: 在 chrome-devtools 展开左侧目录并抓取 URL
- `references/fetch_eci_doc_via_browser.js`: 通过浏览器同域会话直接调用 `document_detail.json` 拉取单篇文档
- `references/repair_unknown_via_browser.js`: 通过浏览器同域会话批量拉取 unknown URL 的修复结果
- `references/eci_menu_urls.txt`: ECI 文档目录 URL 列表（可手工维护或用脚本更新）
- `references/eci_extra_urls.txt`: 官网首页学习路径/旧链接中未出现在左侧目录的补充 URL（手工维护，小而精）
- `references/eci_discovered_missing_urls.txt`: `discover` 输出的“首页存在但菜单缺失”候选 URL
- `references/eci_all_urls.txt`: 综合 URL 列表（菜单 + 补充；用于构建索引）
- `references/eci_docs_index.jsonl`: 本地索引（运行 `index` 生成）
- `references/eci_full_skill_routing.json`: 306 篇文档到 4 个 ECI skills 的主技能路由清单
- `references/eci_full_skill_coverage.md`: 全量覆盖矩阵（按 skill 分组，含 URL/更新时间）
- `references/full_scope_urls.md`: `aliyun-eci-docs` 主路由文档全量清单（148 篇）

## 备注

- 对于目录/聚合节点：脚本会尽量通过官方 `document_detail.json` 自动跟随重定向并抽取正文；Markdown 输出会同时展示“请求URL”和“最终URL”。索引构建时会按最终 URL 去重，并在 `aliases` 字段记录旧入口。
- 若页面 `类型=unknown`：可能是目录页，也可能是官网风控导致；先重试，再用 `references/fetch_eci_doc_via_browser.js` 复核。
