/**
 * 用途：在 chrome-devtools MCP 的 evaluate_script 中执行，自动展开 ECI 文档左侧目录树并抓取全部 URL。
 *
 * 使用方式：
 * 1) 打开任意 ECI 文档页（https://help.aliyun.com/zh/eci/...）
 * 2) 在 evaluate_script 执行：把本文件内容粘贴进去运行
 * 3) 返回值中包含 urls 数组；可将其保存为本地 urls.txt/urls.json 供索引脚本使用
 */

async () => {
  const normalize = (u) => {
    try {
      const url = new URL(u);
      url.hash = "";
      url.search = "";
      return url.toString();
    } catch {
      return u.split("#")[0].split("?")[0];
    }
  };

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const root = document.querySelector("#common-menu-container");
  if (!root) return { error: "common-menu-container not found" };

  const isOpen = (li) => (li.className || "").includes("Menu--open--");
  const hasChevron = (li) =>
    !!li.querySelector('svg[data-icon^="chevron"]');

  let expanded = 0;
  for (let iter = 0; iter < 120; iter++) {
    const toExpand = Array.from(root.querySelectorAll("li")).filter(
      (li) => hasChevron(li) && !isOpen(li),
    );
    if (toExpand.length === 0) break;

    for (const li of toExpand.slice(0, 16)) {
      const span = li.querySelector("span.Menu--menuItemText--oK3zD0t");
      if (!span) continue;
      span.click();
      expanded += 1;
      await sleep(80);
    }

    await sleep(160);
  }

  const urls = new Set();
  for (const a of root.querySelectorAll("a")) {
    if (!a.href) continue;
    if (!a.href.includes("help.aliyun.com/zh/eci/")) continue;
    urls.add(normalize(a.href));
  }

  const list = Array.from(urls).sort();
  return { expanded, urlCount: list.length, urls: list };
};

