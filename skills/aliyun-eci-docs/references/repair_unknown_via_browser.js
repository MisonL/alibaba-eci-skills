/**
 * 在 chrome-devtools 的 evaluate_script 中执行：
 * - 通过浏览器同域会话批量拉取 unknown URL 对应的 document_detail.json
 * - 结果可复制保存为 JSON，再用 scripts/merge_repaired_rows.py 合并回索引
 */
(async () => {
  const unknownUrls = [
    // 在这里填入 unknown URL（建议每次 10~30 条，避免执行超时）
    // "https://help.aliyun.com/zh/eci/user-guide/configure-an-eci-profile",
  ];
  const sleepMs = 150;

  const toAlias = (url) => {
    const parsed = new URL(url);
    let path = parsed.pathname;
    if (path.startsWith("/zh/")) path = path.slice(3);
    if (!path.startsWith("/")) path = `/${path}`;
    if (!path.endsWith("/")) path = `${path}/`;
    return path;
  };

  const toIso = (ms) => {
    if (!ms) return null;
    try {
      return new Date(ms).toISOString();
    } catch {
      return null;
    }
  };

  const toText = (html) => {
    const div = document.createElement("div");
    div.innerHTML = html || "";
    return (div.textContent || "").replace(/\s+/g, " ").trim();
  };

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  const repairedRows = [];
  const failed = [];

  for (const rawUrl of unknownUrls) {
    const url = (rawUrl || "").trim();
    if (!url) continue;

    const alias = toAlias(url);
    const apiUrl =
      "https://help.aliyun.com/help/json/document_detail.json?" +
      new URLSearchParams({
        alias,
        pageNum: "1",
        pageSize: "20",
        website: "cn",
        language: "zh",
        channel: "",
      }).toString();

    try {
      const resp = await fetch(apiUrl, { credentials: "include" });
      const text = await resp.text();
      let json = null;
      try {
        json = JSON.parse(text);
      } catch {
        json = null;
      }

      if (!json || json.code !== 200 || !json.data || !json.data.content) {
        failed.push({
          url,
          alias,
          status: resp.status,
          code: json?.code ?? null,
          reason: "document_detail 不可用或无正文",
        });
        await sleep(sleepMs);
        continue;
      }

      const data = json.data;
      const excerpt = toText(data.content).slice(0, 4000);
      repairedRows.push({
        url: (data.path || url).replace(/\/$/, ""),
        page_type: "doc",
        title: data.title || data.docTitle || data.seoTitle || null,
        keywords: data.keywords || null,
        last_modified_ms: data.lastModifiedTime || null,
        last_modified_iso: toIso(data.lastModifiedTime || null),
        excerpt,
      });
    } catch (error) {
      failed.push({
        url,
        alias,
        reason: String(error),
      });
    }

    await sleep(sleepMs);
  }

  return {
    totalInput: unknownUrls.length,
    repaired: repairedRows.length,
    failed: failed.length,
    repairedRows,
    failedRows: failed,
  };
})();
