import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { existsSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, "..");
const cliPath = path.join(projectRoot, "bin", "install.mjs");

const SKILLS = [
  "aliyun-eci-docs",
  "aliyun-eci-k8s",
  "aliyun-eci-openapi",
  "aliyun-eci-ops",
];

function runCli(args) {
  return spawnSync(process.execPath, [cliPath, ...args], {
    encoding: "utf8",
    cwd: projectRoot,
  });
}

test("CLI 帮助信息可正常输出", () => {
  const result = runCli(["--help"]);
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /npx eci-skills/);
  assert.match(result.stdout, /--target <目录>/);
});

test("CLI 可将四个技能安装到目标目录", () => {
  const targetDir = mkdtempSync(path.join(tmpdir(), "eci-skills-test-"));
  try {
    const result = runCli(["--target", targetDir, "--no-backup"]);
    assert.equal(result.status, 0, result.stderr);

    for (const skill of SKILLS) {
      const skillMdPath = path.join(targetDir, skill, "SKILL.md");
      assert.equal(existsSync(skillMdPath), true, `缺少 ${skillMdPath}`);
      const content = readFileSync(skillMdPath, "utf8");
      assert.match(content, /^---\n[\s\S]*\n---\n/m, `${skill} frontmatter 缺失`);
      assert.match(content, /^name:\s*.+$/m, `${skill} name 缺失`);
      assert.match(content, /^description:\s*.+$/m, `${skill} description 缺失`);
    }
  } finally {
    rmSync(targetDir, { recursive: true, force: true });
  }
});
