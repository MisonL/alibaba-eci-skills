# ECI OpenAPI 最小流程模板

## 模板 A：创建实例（最小可用）

1. 结论：本场景调用 `CreateContainerGroup`，随后用 `DescribeContainerGroups` 轮询状态。
2. 必填参数：`RegionId`、容器组基础配置、镜像、网络最小配置（按官方页）。
3. 验证方式：返回 `RequestId`；状态从创建中进入运行中。
4. 依据链接：
- `api-eci-2018-08-08-createcontainergroup`
- `api-eci-2018-08-08-describecontainergroups`

## 模板 B：问题诊断（事件 + 状态 + 日志）

1. 先看状态：`DescribeContainerGroupStatus`
2. 再看事件：`DescribeContainerGroupEvents`
3. 最后看日志：`DescribeContainerLog`
4. 输出格式：
- 现象：错误码/状态/时间
- 推断：最可能原因（1~3 条）
- 修复：参数修改或资源调整建议
- 回链：对应 API 官方 URL

## 模板 C：权限与鉴权说明

1. 鉴权方式：优先 STS 临时凭证；长期 AK 仅用于受控场景。
2. 权限边界：仅授予当前调用链涉及 Action，避免一次性全量授权。
3. 依据链接：
- `api-eci-2018-08-08-ram`
- `api-eci-2018-08-08-overview`

## 模板 D：错误码交付格式

- 错误现象：`<HTTPCode>/<ErrorCode>`
- 请求上下文：`RegionId`、关键入参、RequestId
- 对应文档：Action 页面 + 版本说明页面
- 处理建议：先参数合法性，再权限，再配额/资源可用性
