# ECI OpenAPI/SDK 速用清单（导航版）

## 先做两件事

1) 明确资源对象与动作
- 实例：创建/查询/更新/删除/重启/扩容存储
- 诊断：事件/状态/日志/指标
- 加速：ImageCache / DataCache
- 集群对接：VirtualNode

2) 先定位官方 API 文档页（强制）
- `python3 ~/.codex/skills/aliyun-eci-docs/scripts/eci_docs.py search <ActionName>`
- `python3 ~/.codex/skills/aliyun-eci-docs/scripts/eci_docs.py fetch <URL> --format md`

## 常用 Action 导航（示例）

- `CreateContainerGroup`：创建实例
- `DescribeContainerGroups`：查询实例列表/详情
- `DeleteContainerGroup`：删除实例
- `ExecContainerCommand`：进入容器执行命令
- `DescribeContainerLog`：拉取容器日志
- `DescribeContainerGroupEvents`：事件
- `DescribeContainerGroupStatus`：状态
- `CreateImageCache` / `DescribeImageCaches` / `DeleteImageCache`
- `CreateDataCache` / `DescribeDataCaches` / `DeleteDataCache`
- `CreateVirtualNode` / `DescribeVirtualNodes` / `DeleteVirtualNode`

## 鉴权与权限（只给方法论）

- 优先使用 STS/临时凭证，避免长期 AccessKey 明文落地
- 按最小权限拆分策略：把“创建实例/查询/删除/日志/缓存/虚拟节点”分开授权
- 不臆造具体权限项：以官方 RAM 文档页为准（从索引检索 `ram`/`policy`/`service-linked role`）

## 错误码排查（路径）

1) 先看错误码是否为权限/参数/配额/资源不可用
2) 再按场景对照官方 `errorcodes` 页面与对应 Action 页的限制说明
3) 输出时必须包含：
- 错误码/请求 ID（如果有）
- 触发条件（哪些参数、在哪个地域/可用区）
- 对照的官方文档 URL

