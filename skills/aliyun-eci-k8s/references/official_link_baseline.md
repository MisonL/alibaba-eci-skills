# ECI × K8s 官方链接基线（交付优先引用）

> 最近复核：2026-02-13（通过 Chrome DevTools 会话调用 `document_detail.json` 抽检）

## 核心对接与调度

- ACK 对接概览：`https://help.aliyun.com/zh/eci/user-guide/connection-overview`
- 配置 `eci-profile`：`https://help.aliyun.com/zh/eci/user-guide/configure-an-eci-profile`
- 使用 `eci-profile` 调度到 VNode：`https://help.aliyun.com/zh/eci/user-guide/use-eci-profile-to-schedule-pods-to-a-vnode`
- 调度 Pod 到 x86 虚拟节点：`https://help.aliyun.com/zh/eci/user-guide/schedule-pods-to-virtual-kubelet`
- 调度 Pod 到 Arm 虚拟节点：`https://help.aliyun.com/zh/eci/user-guide/scheduling-pods-to-virtual-nodes-in-the-arm-architecture`
- ECI Pod Annotation：`https://help.aliyun.com/zh/eci/user-guide/pod-annotations`

## 自建集群接入

- 自建 K8s 对接 ECI 概览：`https://help.aliyun.com/zh/eci/user-guide/overview-3`
- 接入 VNode（VNodectl）：`https://help.aliyun.com/zh/eci/user-guide/use-vnodectl-to-connect-a-vnode-to-a-self-managed-kubernetes-cluster`
- 接入 VNode（手动）：`https://help.aliyun.com/zh/eci/user-guide/manually-connect-a-vnode-to-a-self-managed-kubernetes-cluster`

## 资源与网络

- 多可用区创建 Pod：`https://help.aliyun.com/zh/eci/user-guide/create-pods-in-multiple-zones`
- 多规格创建 Pod：`https://help.aliyun.com/zh/eci/user-guide/create-pods-by-specifying-multiple-specifications`
- 指定 x86 规格创建 Pod：`https://help.aliyun.com/zh/eci/user-guide/specifying-the-x86-specification-to-create-a-pod`
- 云存储概述：`https://help.aliyun.com/zh/eci/user-guide/cloud-storage-overview`
- 使用限制：`https://help.aliyun.com/zh/eci/product-overview/limits`
- 地域和可用区：`https://help.aliyun.com/zh/eci/product-overview/regions-and-zones`

## 交付约束

- 所有 Annotation、Label、`eci-profile` 字段必须回链到上述官方页面或其直接子页面。
- 如果命中多个版本页（例如同名 `-1` 页面），优先引用更新时间更近且与你场景一致的页面。
