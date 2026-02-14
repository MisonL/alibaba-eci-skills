/**
 * 在 chrome-devtools 的 evaluate_script 中执行。
 * 用浏览器会话拉取 ECI 文档详情（绕过命令行抓取时可能遇到的风控页）。
 */
(async () => {
  const targetUrl = "https://help.aliyun.com/zh/eci/user-guide/configure-an-eci-profile";

  function toAlias(url) {
    const parsed = new URL(url);
    let path = parsed.pathname;
    if (path.startsWith("/zh/")) path = path.slice(3);
    if (!path.startsWith("/")) path = `/${path}`;
    if (!path.endsWith("/")) path = `${path}/`;
    return path;
  }

  const alias = toAlias(targetUrl);
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

  const resp = await fetch(apiUrl, { credentials: "include" });
  const raw = await resp.text();

  let json = null;
  try {
    json = JSON.parse(raw);
  } catch {
    return {
      ok: false,
      targetUrl,
      alias,
      status: resp.status,
      message: "返回不是 JSON（可能触发了验证码拦截）",
      preview: raw.slice(0, 300),
    };
  }

  if (json?.code !== 200 || !json?.data) {
    return {
      ok: false,
      targetUrl,
      alias,
      status: resp.status,
      apiCode: json?.code ?? null,
      message: "document_detail 返回非 200",
      payload: json,
    };
  }

  const data = json.data;
  const html = data.content || "";
  const div = document.createElement("div");
  div.innerHTML = html;
  const text = (div.textContent || "").replace(/\s+/g, " ").trim();

  return {
    ok: true,
    targetUrl,
    alias,
    canonicalUrl: data.path || targetUrl,
    title: data.title || data.docTitle || data.seoTitle || null,
    keywords: data.keywords || null,
    lastModifiedTime: data.lastModifiedTime || null,
    excerpt: text.slice(0, 800),
    contentHtmlLength: html.length,
  };
})();
