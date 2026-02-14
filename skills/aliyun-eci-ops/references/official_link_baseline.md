# ECI 运维排障官方链接基线（交付优先引用）

> 最近复核：2026-02-13（通过 Chrome DevTools 会话调用 `document_detail.json` 抽检）

## 总览与边界

- 使用限制：`https://help.aliyun.com/zh/eci/product-overview/limits`
- 地域和可用区：`https://help.aliyun.com/zh/eci/product-overview/regions-and-zones`
- 常见问题：`https://help.aliyun.com/zh/eci/user-guide/faq`

## 事件 / 状态 / 日志 / 监控

- 查看事件、日志和监控（入门）：`https://help.aliyun.com/zh/eci/getting-started/view-events-and-logs-of-an-elastic-container-instance`
- 查询容器组状态：`https://help.aliyun.com/zh/eci/developer-reference/api-eci-2018-08-08-describecontainergroupstatus`
- 查询容器组事件：`https://help.aliyun.com/zh/eci/developer-reference/api-eci-2018-08-08-describecontainergroupevents`
- 获取容器日志：`https://help.aliyun.com/zh/eci/developer-reference/api-eci-2018-08-08-describecontainerlog`
- 查看监控指标：`https://help.aliyun.com/zh/eci/user-guide/view-the-monitoring-metrics-of-an-elastic-container-instance`
- 云监控接入：`https://help.aliyun.com/zh/eci/user-guide/use-cloud-monitoring-to-monitor-eci-instances`

## 网络与安全组

- 为 ECI 实例配置公网连接：`https://help.aliyun.com/zh/eci/user-guide/enable-internet-access`
- 为 ECI Pod 配置公网连接：`https://help.aliyun.com/zh/eci/user-guide/enable-internet-access-1`
- 配置 ECI 实例所属安全组：`https://help.aliyun.com/zh/eci/user-guide/assign-a-security-group-2`
- 配置 IPv6 地址：`https://help.aliyun.com/zh/eci/user-guide/assign-an-ipv6-address-to-an-elastic-container-instance-2`

## 存储与日志采集

- 数据卷概述：`https://help.aliyun.com/zh/eci/user-guide/overview-of-volumes`
- 云存储概述：`https://help.aliyun.com/zh/eci/user-guide/cloud-storage-overview`
- 挂载 NAS 数据卷：`https://help.aliyun.com/zh/eci/user-guide/mount-a-nas-volume`
- 挂载云盘数据卷：`https://help.aliyun.com/zh/eci/user-guide/mount-a-disk-volume`
- 挂载 OSS 数据卷：`https://help.aliyun.com/zh/eci/user-guide/mount-an-oss-bucket-to-an-elastic-container-instance-as-a-volume`
- 自定义配置日志采集：`https://help.aliyun.com/zh/eci/user-guide/configure-log-collection-for-an-elastic-container-instance`
- 通过 SLS CRD 采集日志：`https://help.aliyun.com/zh/eci/user-guide/collect-logs-by-using-log-service-crds`

## 资源可用性与配额

- 查询可用规格：`https://help.aliyun.com/zh/eci/developer-reference/api-eci-2018-08-08-describeavailableresource`
- 创建实例 API（用于参数与错误码回查）：`https://help.aliyun.com/zh/eci/developer-reference/api-eci-2018-08-08-createcontainergroup`
