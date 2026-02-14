# ECI Pod Annotation 速查（只做导航，不硬背）

## 原则

- 以官方文档为准：不要凭印象写注解键名/取值。
- 先检索再输出：用 `$aliyun-eci-docs` 的索引查到“注解清单”对应页面，再抽取关键字段。

## 如何快速定位“注解清单”官方页面

1) 直接检索：
- `python3 ~/.codex/skills/aliyun-eci-docs/scripts/eci_docs.py search pod-annotations`
- `python3 ~/.codex/skills/aliyun-eci-docs/scripts/eci_docs.py search ECI Pod Annotation`

2) 进入命中文档后再拉取：
- `python3 ~/.codex/skills/aliyun-eci-docs/scripts/eci_docs.py fetch <URL> --format md`

## 注解常见分类（按排障/设计思路分组）

提示：下面是“分类维度”，不是具体键名清单。

- 调度类：让 Pod/工作负载被调度到 ECI/VNode、以及亲和/反亲和/可用区分布等
- 规格与资源类：CPU/内存/临时存储/GPU 等与资源调度相关的开关
- 网络类：公网访问、固定 IP、带宽限制、IPv6、DNS/hosts 等
- 存储类：NAS/OSS/云盘/`emptyDir`/`shm` 等挂载策略与参数
- 镜像加速类：ImageCache 自动匹配/指定、镜像仓库鉴权相关
- 数据加速类：DataCache 使用与调度策略（如按 profile 自动使用）
- 日志与可观测类：日志采集方式、STDOUT/日志服务、监控指标相关
- 安全类：RAM 角色、SecurityContext、最小权限等

## 输出时的“最小必要字段”策略

- 首先给最小可用配置：只保留必需注解/字段，确保能跑起来
- 再按目标逐项加注解：每增加一项都解释“作用/风险/如何验证”
- 最后附上依据链接：必须包含对应官方文档 URL

