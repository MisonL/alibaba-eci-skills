# eci-skills

阿里云 ECI（弹性容器实例）Skills 一键安装包，用于把一整套 ECI 专业技能安装到 Codex 的技能目录。

- GitHub 仓库：https://github.com/MisonL/alibaba-eci-skills
- npm 包：https://www.npmjs.com/package/eci-skills

## 包含技能

- `aliyun-eci-docs`：ECI 官网文档抓取、索引、检索与事实复核
- `aliyun-eci-k8s`：ACK / ACK Serverless / 自建 K8s 对接 ECI
- `aliyun-eci-openapi`：ECI OpenAPI/SDK 调用设计与鉴权排障
- `aliyun-eci-ops`：ECI 运维故障定位与修复建议

## 快速安装

```bash
npx eci-skills
```

默认安装到：

```bash
${CODEX_HOME:-$HOME/.codex}/skills
```

## 常用参数

```bash
# 指定安装目录
npx eci-skills --target ~/.codex/skills

# 覆盖安装且不备份
npx eci-skills --no-backup

# 查看帮助
npx eci-skills --help
```

## 安装行为说明

- 安装前会校验每个 `SKILL.md` 的基础合法性（`name` / `description` / frontmatter）。
- 若目标目录已存在同名技能：
  - 默认会备份到安装包目录下的 `.backup/<timestamp>/`
  - `--no-backup` 模式会直接覆盖。
- 安装完成后会再次校验，确保技能可被正常加载。

## 本地打包与测试（维护者）

```bash
# 在项目目录打包
npm pack

# 运行测试与基础检查
npm run check

# 使用本地目录测试安装
npx --yes . --target /tmp/eci-skills-test --no-backup

# 使用本地 tgz 测试安装
npx --yes -p ./eci-skills-<version>.tgz eci-skills --target /tmp/eci-skills-test --no-backup
```

## 问题反馈

- Issues：https://github.com/MisonL/alibaba-eci-skills/issues
