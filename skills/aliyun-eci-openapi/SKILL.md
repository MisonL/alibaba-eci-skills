---
name: aliyun-eci-openapi
description: "ECI OpenAPI/SDK 调用设计与故障定位。Use when 需要通过代码自动化创建、查询、更新、删除 ECI 资源（实例、镜像缓存、DataCache、虚拟节点等），并给出最小请求、鉴权（RAM/STS）与错误码排查路径。"
---

# 阿里云 ECI OpenAPI/SDK

## 快速工作流（按官方文档落地）

1) 先定位官方 API 文档页面
- 优先用 `$aliyun-eci-docs` 本地索引检索（更快、更稳）
  - `python3 ~/.codex/skills/aliyun-eci-docs/scripts/eci_docs.py search CreateContainerGroup`
  - `python3 ~/.codex/skills/aliyun-eci-docs/scripts/eci_docs.py search ExecContainerCommand`
- 命中后拉取并阅读关键段落（参数/示例/错误码/限制）
  - `python3 ~/.codex/skills/aliyun-eci-docs/scripts/eci_docs.py fetch <URL> --format md`

2) 明确鉴权与权限边界（RAM/STS）
- 确认调用方身份：主账号/子账号 RAM User/STS 临时凭证/实例 RAM 角色
- 按“最小权限”原则给出策略建议（具体 Action/Resource 以官方文档为准）

3) 形成“最小可用请求 + 可选增强项”
- 最小可用：只包含必填参数，确保能创建/查询成功
- 增强项：网络/存储/日志/安全/规格等按场景逐项加入
- 输出时必须带：参数解释、常见报错定位、依据链接（官方 URL）
- 输出结构优先按 `references/minimal_api_workflow_templates.md` 的模板组织

## 常见需求到 API 的映射（只作导航）

- 创建/删除/查询实例：`CreateContainerGroup` / `DeleteContainerGroup` / `DescribeContainerGroups`
- 查看事件/状态：`DescribeContainerGroupEvents` / `DescribeContainerGroupStatus`
- 进入容器执行命令：`ExecContainerCommand`
- 拉取容器日志：`DescribeContainerLog`
- 镜像缓存：`CreateImageCache` / `DescribeImageCaches` / `DeleteImageCache`
- DataCache：`CreateDataCache` / `DescribeDataCaches` / `DeleteDataCache`
- 虚拟节点：`CreateVirtualNode` / `DescribeVirtualNodes` / `DeleteVirtualNode`

## 输出模板（回答/交付时遵循）

- 结论：该场景需要调用哪些 API、建议的调用顺序
- 最小示例：请求参数清单（必填/选填分组），必要时给伪代码/请求体结构
- 参数解释：每个关键字段“从哪里来/如何获取/常见坑”
- 权限与鉴权：需要的 RAM 角色/策略方向（不直接臆造具体 Action 列表）
- 排障：常见错误码/现象 -> 定位路径 -> 可能原因
- 依据：列出官方文档 URL

## 参考资料（需要细节时再读）

- `references/openapi_cheatsheet.md`: 常见调用套路与排障导航
- `references/official_link_baseline.md`: OpenAPI 常用 Action 官方链接基线
- `references/minimal_api_workflow_templates.md`: 最小可用调用流程模板（含鉴权/排障结构）
- `references/full_scope_urls.md`: `aliyun-eci-openapi` 主路由文档全量清单（45 篇）
- `~/.codex/skills/aliyun-eci-docs/references/eci_full_skill_coverage.md`: 全量文档覆盖矩阵（先确认该问题属于 OpenAPI 路由）
- `~/.codex/skills/aliyun-eci-docs/references/eci_full_skill_routing.json`: URL -> 主技能路由明细（跨域问题先查）
