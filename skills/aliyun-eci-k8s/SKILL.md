---
name: aliyun-eci-k8s
description: "ECI 与 Kubernetes（ACK、ACK Serverless、自建集群 + VNode/Virtual Kubelet）对接方案生成与排障。Use when 需要把 Pod 调度到 ECI、编写/修订 YAML 与 eci-profile、配置 Annotation，或定位调度/网络/存储/权限失败。"
---

# 阿里云 ECI K8s 对接

## 生成配置前先确认

- 集群类型：ACK Serverless / ACK（托管集群）/ 自建 K8s
- 目标 Workload：Deployment/StatefulSet/Job/CronJob/Argo 等
- 资源规格：CPU/内存/临时存储、GPU（如需）
- 网络：是否需要公网、VPC/安全组、SLB/Ingress、DNS
- 存储：NAS/OSS/云盘/emptyDir/shm
- 加速：ImageCache / DataCache
- 安全：RAM 角色、Secret、SecurityContext

## 输出要求（默认）

- 先给“最小可用”YAML（能跑起来、能被调度到 ECI）
- 再给“可选增强项”（网络/存储/日志/监控/成本）
- 最后给“关键限制/注意事项 + 依据链接”

## 快速工作流

1) 选对接方式（优先建议）
- 纯 Serverless：优先 ACK Serverless
- 需要保留 ACK 能力但扩容到 ECI：ACK + ECI
- 已有自建集群要接入：自建 K8s + VNode/Virtual Kubelet（按官方流程接入）

2) 生成 YAML
- 提供 Pod/Deployment/Job YAML（含关键注解/标签/资源/网络/存储）
- 如需要策略化调度，补充 `eci-profile`（按官方字段）
- 优先参考 `references/yaml_generation_templates.md` 的模板骨架，再按官方文档补字段

3) 排障（调度失败/长时间 Pending）
- 收集：Pod 事件、调度器信息、VNode 状态、镜像拉取错误、网络/存储错误
- 对照官方限制：地域/可用区、规格、配额、网络、镜像仓库访问、权限

## 参考资料（需要细节时再读）

- `references/k8s_decision_tree.md`: 选型与前置条件清单
- `references/pod_annotations_cheatsheet.md`: 注解/字段速查（只做导航与关键词，不硬背）
- `references/official_link_baseline.md`: K8s 对接场景的官方文档基线链接（交付时优先引用）
- `references/yaml_generation_templates.md`: 低风险 YAML 模板骨架（字段需按官方页复核后填充）
- `references/full_scope_urls.md`: `aliyun-eci-k8s` 主路由文档全量清单（62 篇）
- `~/.codex/skills/aliyun-eci-docs/references/eci_full_skill_coverage.md`: 全量文档覆盖矩阵（先确认该问题确实属于 K8s 路由）
- `~/.codex/skills/aliyun-eci-docs/references/eci_full_skill_routing.json`: URL -> 主技能路由明细（遇到边界问题先查）
