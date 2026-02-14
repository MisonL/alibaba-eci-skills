# ECI K8s YAML 生成模板（骨架版）

用途：用于快速生成“最小可用”配置骨架。ECI 特有字段（Annotation、Profile 字段、网络与存储参数）必须在输出前按官方页逐项复核。

## 模板 A：最小可用 Pod（调度到 ECI）

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: <pod-name>
  labels:
    app: <app-name>
    alibabacloud.com/eci: "true"
  annotations:
    # 在这里按官方文档补充 ECI Annotation
    # 例如调度/网络/存储/镜像加速相关字段
spec:
  containers:
  - name: <container-name>
    image: <image>
    resources:
      requests:
        cpu: "<cpu>"
        memory: "<memory>"
```

## 模板 B：最小可用 Deployment（业务常用）

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: <deploy-name>
spec:
  replicas: <replicas>
  selector:
    matchLabels:
      app: <app-name>
  template:
    metadata:
      labels:
        app: <app-name>
        alibabacloud.com/eci: "true"
      annotations:
        # 按官方文档补充 ECI Annotation
    spec:
      containers:
      - name: <container-name>
        image: <image>
```

## 模板 C：交付时必须附带的验证项

- 调度验证：`kubectl get pod -o wide`，确认 Pod 运行位置符合预期。
- 事件验证：`kubectl describe pod <pod-name>`，确认无调度/镜像/存储错误事件。
- 链接验证：最终答案至少引用一条 `pod-annotations` 或 `eci-profile` 官方页面链接。
