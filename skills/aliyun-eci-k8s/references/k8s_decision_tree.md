# ECI × Kubernetes 对接选型与前置条件（导航版）

## 选型决策树

1) 你是否“必须”使用 Kubernetes 作为控制面？
- 否：优先用 ECI 控制台或 OpenAPI（见 `$aliyun-eci-openapi`）
- 是：继续

2) 你是否还没有集群/希望全托管？
- 是：优先 ACK Serverless（天然以 ECI 承载 Pod）
- 否：继续

3) 你是否已有 ACK（托管集群）并希望弹性扩容到 ECI？
- 是：ACK + ECI（在 ACK 中配置调度到 ECI 的能力，例如 `eci-profile`、Pod 注解等）
- 否：继续

4) 你是否是自建 K8s（ECS/IDC）？
- 是：按官方流程接入 VNode/Virtual Kubelet，再将 Pod 调度到 VNode

## 配置前置条件清单（最小集）

- 明确地域/可用区：目标业务落在哪个 Region/Zone
- 明确网络：VPC、vSwitch、SecurityGroup、（需要公网则）公网出口方案
- 明确镜像：镜像地址（ACR/自建/公网）、鉴权方式、是否需要 ImageCache
- 明确存储：是否需要 NAS/OSS/云盘/临时存储扩容/`emptyDir`/`shm`
- 明确权限：是否需要 Pod/实例使用 RAM 角色（访问 OSS/日志/监控等）
- 明确资源：CPU/内存/临时存储/GPU、以及峰值弹性目标

## 官方文档检索关键词（建议用 `$aliyun-eci-docs`）

以下关键词用于快速命中文档（不要凭记忆硬写字段）：

- 调度：`scheduling`、`schedule-pods`、`affinity`、`zone`
- 配置：`eci-profile`、`pod-annotations`
- 自建集群：`vnode`、`virtual-kubelet`、`vnodectl`
- 网络：`enable-internet-access`、`security group`、`IPv6`
- 存储：`volumes`、`NAS`、`OSS`、`CSI`
- 日志/监控：`log`、`monitoring metrics`

## 交付物（默认输出结构）

- 最小可用 YAML：确保 Pod 能被调度到 ECI 并成功拉起
- 增强配置：网络/存储/日志/监控/加速（ImageCache/DataCache）
- 排障路径：常见 Pending/拉取失败/挂载失败 的定位步骤
- 依据链接：列出用到的官方文档 URL

