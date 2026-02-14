# ECI 运维与排障 Playbook（导航版）

## 统一输出格式（建议）

- 现象与范围：影响哪些实例/Pod、是否可复现、开始时间
- 证据：事件/日志/状态/监控指标（能贴就贴关键行）
- 结论：按概率排序的 1～3 个原因
- 修复：可执行步骤（控制台/配置/YAML）
- 验证：怎么确认已恢复
- 依据：官方文档 URL 列表（必须）

## 症状 -> 首选排查方向（快速分流）

### 1) 创建失败 / Pending 很久

- 优先看：事件（Events）、配额、规格/地域/可用区可用性
- 其次看：网络依赖（vSwitch/SecurityGroup）、镜像拉取、存储挂载
- 建议检索：`scheduling`、`limits`、`regions-and-zones`、`DescribeAvailableResource`

### 2) ImagePullBackOff / 拉取镜像失败

- 优先看：镜像地址是否可达、仓库鉴权、网络出口
- 增强项：使用 ImageCache 加速/稳定拉取
- 建议检索：`configure-a-container-image`、`image cache`、`pull images`、`use-imagecache`

### 3) MountFailed / 存储挂载失败

- 优先看：存储类型选择（NAS/OSS/云盘/临时存储）、权限、网络连通性
- 建议检索：`overview-of-volumes`、`NAS`、`OSS`、`CSI`、`temporary storage`

### 4) 服务不可达 / 公网访问异常

- 优先看：是否开启公网、出入口路径、SLB/Ingress、SecurityGroup 端口放通
- 建议检索：`enable-internet-access`、`security group`、`SLB`、`bandwidth`

### 5) 日志缺失 / 监控指标缺失

- 优先看：采集方案（STDOUT/日志服务/Prometheus 等）与权限、网络
- 建议检索：`configure-log-collection`、`monitoring metrics`、`ARMS`、`cloud monitoring`

## 如何用官方文档“落锤”

- 先用 `$aliyun-eci-docs` 搜索命中文档页：`python3 ~/.codex/skills/aliyun-eci-docs/scripts/eci_docs.py search <keyword>`
- 再用 `fetch` 抽取“限制/参数/步骤/注意事项”并回链：`python3 ~/.codex/skills/aliyun-eci-docs/scripts/eci_docs.py fetch <URL> --format md`

