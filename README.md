# eci-skills

[![npm version](https://img.shields.io/npm/v/eci-skills?logo=npm&color=CB3837)](https://www.npmjs.com/package/eci-skills)
[![npm downloads](https://img.shields.io/npm/dm/eci-skills?logo=npm)](https://www.npmjs.com/package/eci-skills)
[![license](https://img.shields.io/npm/l/eci-skills)](./LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/MisonL/alibaba-eci-skills?style=social)](https://github.com/MisonL/alibaba-eci-skills)

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

## npm 包说明与关联

- 包名：`eci-skills`
- npm 页面：https://www.npmjs.com/package/eci-skills
- GitHub 仓库：https://github.com/MisonL/alibaba-eci-skills
- 问题反馈：https://github.com/MisonL/alibaba-eci-skills/issues

常见命令：

```bash
# 安装并执行最新版本
npx eci-skills

# 指定版本执行
npx eci-skills@1.0.2 --help

# 查看包最新版本
npm view eci-skills version

# 查看所有已发布版本
npm view eci-skills versions
```

说明：

- `npx eci-skills` 会拉取 npm 上 `latest` 标签对应版本并执行 CLI。
- 若遇到本地缓存导致版本滞后，可加 `--yes` 或清理 npm 缓存后重试。

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
