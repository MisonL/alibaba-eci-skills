---
name: aliyun-eci-ops
description: "ECI 运行运维与故障处理。Use when 出现实例或 Pod 创建失败、长时间 Pending、镜像拉取失败、网络不可达、公网或 IPv6 问题、存储挂载异常、日志/监控缺失、弹性伸缩与成本优化场景，并需要官方依据的定位与修复步骤。"
---

# 阿里云 ECI 运维与排障

## 统一排障入口（先收集再下结论）

1) 明确问题形态
- 资源形态：ECI 实例（控制台/OpenAPI）或 Pod（ACK/自建 K8s）
- 阶段：创建中/运行中/重启中/销毁中
- 症状：Pending、CrashLoop、ImagePullBackOff、MountFailed、无法访问、无日志、无指标等

2) 收集最小证据集（按场景取用）
- K8s：`kubectl describe pod`、事件（Events）、`kubectl logs`、节点/VNode 状态
- OpenAPI：实例状态、事件、容器日志（对应 API/控制台入口）
- 网络：VPC/安全组/路由/公网 NAT/SLB/Ingress/DNS 解析
- 存储：挂载点/权限/存储类型（NAS/OSS/云盘/临时存储）
- 配额与限制：地域/可用区、规格、账号/资源配额

3) 对照官方文档给出定位与修复
- 优先用 `$aliyun-eci-docs` 搜索对应主题，拿到权威依据链接
  - `python3 ~/.codex/skills/aliyun-eci-docs/scripts/eci_docs.py search enable-internet-access`
  - `python3 ~/.codex/skills/aliyun-eci-docs/scripts/eci_docs.py search overview-of-volumes`
  - `python3 ~/.codex/skills/aliyun-eci-docs/scripts/eci_docs.py search configure-log-collection`
- 输出：检查项清单 -> 可能原因 -> 修复步骤 -> 依据链接
- 输出格式优先按 `references/incident_response_templates.md` 组织

## 常见症状的排障路径（导航版）

- 创建失败/长时间 Pending：优先看事件与配额/规格/网络依赖 -> 再看镜像/存储
- 镜像拉取失败：仓库可达性/鉴权/镜像地址/镜像缓存（ImageCache）
- 业务无法访问：公网/SLB/Ingress/安全组/端口/健康检查/DNS
- 存储挂载失败：存储类型选择、权限、挂载参数、网络连通性
- 日志缺失：采集方式（Log Service/STDOUT）、采集配置、权限与网络
- 指标缺失：监控组件、采集开关、指标口径与延迟

## 输出模板（回答/交付时遵循）

- 结论：最可能的 1～3 个原因（按概率排序）
- 定位步骤：每一步“看什么/怎么判断/下一步怎么分流”
- 修复建议：具体改动点（YAML/控制台/配置项）
- 风险提示：影响面、回滚方式、变更窗口建议
- 依据：对应官方文档 URL（必须给）

## 参考资料（需要细节时再读）

- `references/troubleshooting_playbook.md`: 症状 -> 定位 -> 解决（可扩展）
- `references/official_link_baseline.md`: 运维排障高频场景官方链接基线
- `references/incident_response_templates.md`: 标准化故障响应模板（证据/结论/修复/回链）
- `references/full_scope_urls.md`: `aliyun-eci-ops` 主路由文档全量清单（51 篇）
- `~/.codex/skills/aliyun-eci-docs/references/eci_full_skill_coverage.md`: 全量文档覆盖矩阵（确认问题是否应路由到 ops）
- `~/.codex/skills/aliyun-eci-docs/references/eci_full_skill_routing.json`: URL -> 主技能路由明细（边界场景优先查）
