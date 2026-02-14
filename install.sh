#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_SKILLS_DIR="${SCRIPT_DIR}/skills"
VALIDATOR="${SCRIPT_DIR}/scripts/quick_validate.py"

SKILLS=(
  "aliyun-eci-docs"
  "aliyun-eci-k8s"
  "aliyun-eci-openapi"
  "aliyun-eci-ops"
)

usage() {
  cat <<'EOF'
用法：
  bash install.sh [--target <技能目录>] [--no-backup]

示例：
  bash install.sh
  bash install.sh --target "$HOME/.codex/skills"

说明：
  - 默认安装到：${CODEX_HOME:-$HOME/.codex}/skills
  - 默认覆盖前先备份同名技能到：./.backup/<时间戳>/
EOF
}

TARGET_DIR="${CODEX_HOME:-$HOME/.codex}/skills"
NO_BACKUP="false"

while (($# > 0)); do
  case "$1" in
    --target)
      TARGET_DIR="${2:?--target 需要传入目录路径}"
      shift 2
      ;;
    --no-backup)
      NO_BACKUP="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "未知参数: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ ! -d "${SOURCE_SKILLS_DIR}" ]]; then
  echo "[ERROR] 未找到技能目录: ${SOURCE_SKILLS_DIR}" >&2
  exit 1
fi

if [[ ! -f "${VALIDATOR}" ]]; then
  echo "[ERROR] 未找到校验脚本: ${VALIDATOR}" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERROR] 未检测到 python3，无法执行 SKILL.md 校验" >&2
  exit 1
fi

for skill in "${SKILLS[@]}"; do
  python3 "${VALIDATOR}" "${SOURCE_SKILLS_DIR}/${skill}" >/dev/null
done

mkdir -p "${TARGET_DIR}"
BACKUP_DIR=""
if [[ "${NO_BACKUP}" != "true" ]]; then
  BACKUP_DIR="${SCRIPT_DIR}/.backup/$(date +%Y%m%d-%H%M%S)"
  mkdir -p "${BACKUP_DIR}"
fi

for skill in "${SKILLS[@]}"; do
  src="${SOURCE_SKILLS_DIR}/${skill}"
  dst="${TARGET_DIR}/${skill}"

  if [[ ! -d "${src}" ]]; then
    echo "[ERROR] 缺少技能目录: ${src}" >&2
    exit 1
  fi

  if [[ -e "${dst}" ]]; then
    if [[ "${NO_BACKUP}" == "true" ]]; then
      rm -rf "${dst}"
    else
      mv "${dst}" "${BACKUP_DIR}/${skill}"
    fi
  fi

  rsync -a "${src}/" "${dst}/"
  python3 "${VALIDATOR}" "${dst}" >/dev/null
  echo "[OK] 已安装 ${skill} -> ${dst}"
done

echo
echo "安装完成。"
echo "目标目录: ${TARGET_DIR}"
if [[ "${NO_BACKUP}" != "true" ]]; then
  echo "备份目录: ${BACKUP_DIR}"
fi
