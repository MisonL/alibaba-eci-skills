#!/usr/bin/env node
import { cpSync, existsSync, mkdirSync, readFileSync, renameSync, rmSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { parseArgs } from "node:util";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const SKILLS = [
  "aliyun-eci-docs",
  "aliyun-eci-k8s",
  "aliyun-eci-openapi",
  "aliyun-eci-ops",
];

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const packageRoot = path.resolve(__dirname, "..");
const sourceSkillsDir = path.join(packageRoot, "skills");
const pythonValidator = path.join(packageRoot, "scripts", "quick_validate.py");

function usage() {
  console.log(`用法：
  npx eci-skills
  npx eci-skills --target ~/.codex/skills
  npx eci-skills --no-backup

参数：
  --target <目录>   指定安装目标目录（默认：\${CODEX_HOME:-~/.codex}/skills）
  --no-backup       覆盖安装时不备份目标目录下的同名技能
  -h, --help        显示帮助
`);
}

function getDefaultTargetDir() {
  const home = process.env.HOME;
  const codexHome = process.env.CODEX_HOME || (home ? path.join(home, ".codex") : ".codex");
  return path.join(codexHome, "skills");
}

function readFrontmatter(skillMdPath) {
  const content = readFileSync(skillMdPath, "utf8");
  const match = content.match(/^---\n([\s\S]*?)\n---\n?/);
  if (!match) {
    throw new Error(`缺少或损坏 frontmatter: ${skillMdPath}`);
  }
  return match[1];
}

function hasPythonValidator() {
  if (!existsSync(pythonValidator)) return false;
  try {
    execFileSync("python3", ["--version"], { stdio: "ignore" });
    return true;
  } catch {
    return false;
  }
}

function validateSkillWithFallback(skillDir) {
  const skillMdPath = path.join(skillDir, "SKILL.md");
  if (!existsSync(skillMdPath)) {
    throw new Error(`缺少 SKILL.md: ${skillMdPath}`);
  }

  const frontmatter = readFrontmatter(skillMdPath);
  const nameMatch = frontmatter.match(/^name:\s*(.+)\s*$/m);
  const descLineMatch = frontmatter.match(/^description:\s*(.*)$/m);
  if (!nameMatch || !nameMatch[1].trim()) {
    throw new Error(`name 非法: ${skillMdPath}`);
  }
  if (!descLineMatch) {
    throw new Error(`description 非法: ${skillMdPath}`);
  }
  const descRaw = descLineMatch[1].trim();
  if (descRaw.length === 0) {
    const rest = frontmatter
      .split(/\r?\n/)
      .slice(frontmatter.split(/\r?\n/).findIndex((line) => line.startsWith("description:")) + 1)
      .find((line) => line.trim().length > 0);
    if (rest && rest.trim().startsWith("-")) {
      throw new Error(`description 不能是 YAML 数组: ${skillMdPath}`);
    }
    throw new Error(`description 不能为空: ${skillMdPath}`);
  }
}

function validateSkill(skillDir) {
  if (hasPythonValidator()) {
    try {
      execFileSync("python3", [pythonValidator, skillDir], { stdio: "ignore" });
      return;
    } catch {
      throw new Error(`官方 quick_validate 校验失败: ${skillDir}`);
    }
  }
  validateSkillWithFallback(skillDir);
}

function timestamp() {
  const now = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  return `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}-${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
}

function main() {
  const rawArgs = process.argv.slice(2);
  const normalizedArgs = rawArgs[0] === "--" ? rawArgs.slice(1) : rawArgs;
  const { values, positionals } = parseArgs({
    args: normalizedArgs,
    options: {
      target: { type: "string" },
      "no-backup": { type: "boolean", default: false },
      help: { type: "boolean", short: "h", default: false },
    },
    allowPositionals: true,
  });

  if (values.help) {
    usage();
    return;
  }
  if (positionals.length > 0) {
    throw new Error(`不支持的位置参数: ${positionals.join(" ")}`);
  }
  if (!existsSync(sourceSkillsDir)) {
    throw new Error(`未找到 skills 目录: ${sourceSkillsDir}`);
  }

  const targetDir = path.resolve(values.target || getDefaultTargetDir());
  mkdirSync(targetDir, { recursive: true });

  for (const skill of SKILLS) {
    const src = path.join(sourceSkillsDir, skill);
    validateSkill(src);
  }

  const noBackup = Boolean(values["no-backup"]);
  const backupDir = noBackup ? null : path.join(packageRoot, ".backup", timestamp());
  if (backupDir) {
    mkdirSync(backupDir, { recursive: true });
  }

  for (const skill of SKILLS) {
    const src = path.join(sourceSkillsDir, skill);
    const dst = path.join(targetDir, skill);

    if (existsSync(dst)) {
      if (noBackup) {
        rmSync(dst, { recursive: true, force: true });
      } else {
        renameSync(dst, path.join(backupDir, skill));
      }
    }

    cpSync(src, dst, { recursive: true, force: true });
    validateSkill(dst);
    console.log(`[OK] ${skill} -> ${dst}`);
  }

  console.log("");
  console.log("安装完成。");
  console.log(`目标目录: ${targetDir}`);
  if (backupDir) {
    console.log(`备份目录: ${backupDir}`);
  }
}

try {
  main();
} catch (error) {
  const message = error instanceof Error ? error.message : String(error);
  console.error(`[ERROR] ${message}`);
  process.exit(1);
}
