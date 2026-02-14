#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REF_DIR="${SKILL_DIR}/references"

MENU_FILE="${REF_DIR}/eci_menu_urls.txt"
EXTRA_FILE="${REF_DIR}/eci_extra_urls.txt"
DISCOVERED_FILE="${REF_DIR}/eci_discovered_missing_urls.txt"
ALL_FILE="${REF_DIR}/eci_all_urls.txt"
INDEX_FILE="${REF_DIR}/eci_docs_index.jsonl"
INDEX_BAK_FILE="${REF_DIR}/eci_docs_index.jsonl.bak"
COOKIE_FILE="${REF_DIR}/help_cookie.txt"

if [[ -s "${COOKIE_FILE}" ]]; then
  export ALIYUN_HELP_COOKIE
  ALIYUN_HELP_COOKIE="$(cat "${COOKIE_FILE}")"
fi

if [[ -f "${INDEX_FILE}" ]]; then
  cp "${INDEX_FILE}" "${INDEX_BAK_FILE}"
fi

if ! python3 "${SCRIPT_DIR}/eci_docs.py" discover \
  --menu-file "${MENU_FILE}" \
  --out "${DISCOVERED_FILE}"; then
  echo "[WARN] discover 阶段失败（可能命中官网风控），继续使用已有 URL 清单" >&2
  : > "${DISCOVERED_FILE}"
fi

cat "${MENU_FILE}" "${EXTRA_FILE}" \
  | sed '/^#/d' \
  | sed '/^[[:space:]]*$/d' \
  | sort -u > "${ALL_FILE}"

python3 "${SCRIPT_DIR}/eci_docs.py" index \
  --urls-file "${ALL_FILE}" \
  --out "${INDEX_FILE}" \
  --retry 4 \
  --sleep 0.3

python3 "${SCRIPT_DIR}/eci_docs.py" repair \
  --index "${INDEX_FILE}" \
  --sleep 0.3 \
  --retry 3

python3 "${SCRIPT_DIR}/eci_docs.py" stats \
  --index "${INDEX_FILE}" \
  --show-errors \
  --show-empty
