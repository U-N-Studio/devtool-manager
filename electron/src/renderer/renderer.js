const PAGE_SIZE = 50;

const TOOL_CATEGORIES = ["Java", "Python", "Android", "Node.js", "Go", "Rust"];

let envData = {};
let pkgAllItems = [];
let pkgPage = 0;

document.addEventListener("DOMContentLoaded", async () => {
  initTabs();
  await initEnvTab();
  await initPackagesTab();
});

function initTabs() {
  document.querySelectorAll(".tab").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(`tab-${btn.dataset.tab}`).classList.add("active");
    });
  });
}

async function initEnvTab() {
  const catSel = document.getElementById("env-category");
  catSel.addEventListener("change", onEnvCategoryChange);
  document.getElementById("env-add").addEventListener("click", onEnvAdd);
  document.getElementById("env-refresh").addEventListener("click", () => loadEnvData());

  await loadEnvData();
}

async function loadEnvData() {
  document.getElementById("env-msg").textContent = "Loading...";
  try {
    envData = await window.api.env.getCategorized();
    const catSel = document.getElementById("env-category");
    const cats = Object.keys(envData);
    catSel.innerHTML = cats.map((c) => `<option value="${c}">${c}</option>`).join("");
    if (cats.length) onEnvCategoryChange();
  } finally {
    document.getElementById("env-msg").textContent = "";
  }
}

async function onEnvCategoryChange() {
  const cat = document.getElementById("env-category").value;
  renderEnvList(envData[cat] || []);
  await renderToolInfo(cat);
}

function renderEnvList(items) {
  const list = document.getElementById("env-list");
  list.innerHTML = items
    .map(
      (item) => `
    <div class="env-row">
      <span class="env-name" title="${esc(item.name)}">${esc(item.name)}</span>
      <span class="env-source">${esc(item.source)}</span>
      <span class="env-value" title="${esc(item.value)}">${esc(item.value)}</span>
      <div class="env-actions">
        <button class="btn btn-secondary" onclick="onEnvEdit(${esc(JSON.stringify(item).replace(/"/g, "&quot;"))})">Edit</button>
        <button class="btn btn-danger" onclick="onEnvDelete(${esc(JSON.stringify(item).replace(/"/g, "&quot;"))})">Del</button>
      </div>
    </div>`
    )
    .join("");
}

async function renderToolInfo(cat) {
  const box = document.getElementById("env-tool-info");
  if (!TOOL_CATEGORIES.includes(cat)) {
    box.classList.remove("visible");
    return;
  }
  const info = await window.api.tools.getInfo(cat);
  if (!info.installed && (!info.details || !info.details.length)) {
    box.classList.remove("visible");
    return;
  }
  box.classList.add("visible");
  box.innerHTML = `
    <div class="info-title">${esc(cat)}</div>
    ${info.version ? `<div class="info-line">${esc(info.version)}</div>` : ""}
    ${info.details ? info.details.map((d) => `<div class="info-line">${esc(d)}</div>`).join("") : ""}
  `;
}

async function onEnvEdit(item) {
  const newVal = prompt(`Edit ${item.name}:`, item.value);
  if (newVal === null || newVal === item.value) return;
  document.getElementById("env-msg").textContent = `Setting ${item.name}...`;
  if (item.isPathEntry) {
    const pathVal = (await window.api.env.getCategorized())["Path"] || [];
    await window.api.env.deletePath(item.value, item.source);
    await window.api.env.addPath(newVal, item.source);
  } else {
    await window.api.env.set(item.name, newVal, item.source);
  }
  await loadEnvData();
}

async function onEnvDelete(item) {
  if (!confirm(`Delete ${item.name}${item.isPathEntry ? " PATH entry" : ""}?\nValue: ${item.value}`)) return;
  document.getElementById("env-msg").textContent = `Deleting ${item.name}...`;
  if (item.isPathEntry) {
    await window.api.env.deletePath(item.value, item.source);
  } else {
    await window.api.env.delete(item.name, item.source);
  }
  await loadEnvData();
}

async function onEnvAdd() {
  const cat = document.getElementById("env-category").value;
  const isPath = cat === "Path";
  const name = isPath ? "PATH" : prompt("Variable name:");
  if (!name) return;
  const value = prompt("Value:");
  if (value === null) return;
  const source = prompt("Source (user/system):", "user") || "user";
  document.getElementById("env-msg").textContent = `Adding ${name}...`;
  if (isPath) {
    await window.api.env.addPath(value, source);
  } else {
    await window.api.env.set(name, value, source);
  }
  await loadEnvData();
}

async function initPackagesTab() {
  const funcTags = await window.api.packages.getFuncTags();
  const langTags = await window.api.packages.getLangTags();

  const funcSel = document.getElementById("pkg-func");
  funcSel.innerHTML = `<option value="">All</option>` + funcTags.map((t) => `<option value="${t}">${t}</option>`).join("");
  funcSel.addEventListener("change", () => loadPackages());

  const langSel = document.getElementById("pkg-lang");
  langSel.innerHTML = `<option value="">All</option>` + langTags.map((t) => `<option value="${t}">${t}</option>`).join("");
  langSel.addEventListener("change", () => loadPackages());

  const installSel = document.getElementById("pkg-install");
  installSel.innerHTML = `<option value="">All</option><option value="Installed">Installed</option><option value="Not Installed">Not Installed</option>`;
  installSel.addEventListener("change", () => loadPackages());

  document.getElementById("pkg-install-btn").addEventListener("click", onPackageInstall);

  await loadPackages();
}

async function loadPackages() {
  const func = document.getElementById("pkg-func").value;
  const lang = document.getElementById("pkg-lang").value;
  const install = document.getElementById("pkg-install").value;
  document.getElementById("pkg-msg").textContent = "Loading...";
  try {
    pkgAllItems = await window.api.packages.getList(func, lang, install);
    pkgPage = 0;
    renderPackagePage();
  } finally {
    document.getElementById("pkg-msg").textContent = "";
  }
}

function renderPackagePage() {
  const list = document.getElementById("pkg-list");
  const nav = document.getElementById("pkg-nav");
  const total = pkgAllItems.length;
  const start = pkgPage * PAGE_SIZE;
  const end = Math.min(start + PAGE_SIZE, total);
  const pageItems = pkgAllItems.slice(start, end);

  list.innerHTML = pageItems
    .map(
      (item) => `
    <div class="pkg-row">
      <span class="pkg-tag func">${esc(item.func_tag)}</span>
      <span class="pkg-tag lang">${esc(item.lang_tag)}</span>
      <span class="pkg-tag ${item.install_tag === "Installed" ? "installed" : "not-installed"}">${esc(item.install_tag)}</span>
      <span class="pkg-name">${esc(item.name)}</span>
      <span class="pkg-version">${esc(item.version || "")}</span>
      ${
        item.install_tag === "Installed"
          ? `<button class="btn btn-danger" onclick="onPackageUninstall('${esc(item.name)}')">Del</button>`
          : `<button class="btn btn-success" onclick="onPackageAdd('${esc(item.name)}')">Add</button>`
      }
    </div>`
    )
    .join("");

  if (total > PAGE_SIZE) {
    const totalPages = Math.ceil(total / PAGE_SIZE);
    nav.innerHTML = `
      ${pkgPage > 0 ? `<button onclick="pkgPage--;renderPackagePage()">< Prev</button>` : ""}
      <span class="pager-info">${start + 1}-${end} / ${total}</span>
      ${pkgPage < totalPages - 1 ? `<button onclick="pkgPage++;renderPackagePage()">Next ></button>` : ""}
    `;
  } else {
    nav.innerHTML = "";
  }
}

async function onPackageInstall() {
  const name = prompt("Package name:");
  if (!name || !name.trim()) return;
  document.getElementById("pkg-msg").textContent = `Installing ${name}...`;
  const result = await window.api.packages.install(name.trim());
  document.getElementById("pkg-msg").textContent = `Install ${result.ok ? "success" : "failed"}: ${name}`;
  await loadPackages();
}

async function onPackageAdd(name) {
  if (!confirm(`Install ${name}?`)) return;
  document.getElementById("pkg-msg").textContent = `Installing ${name}...`;
  const result = await window.api.packages.install(name);
  document.getElementById("pkg-msg").textContent = `Install ${result.ok ? "success" : "failed"}: ${name}`;
  await loadPackages();
}

async function onPackageUninstall(name) {
  if (!confirm(`Uninstall ${name}?`)) return;
  document.getElementById("pkg-msg").textContent = `Uninstalling ${name}...`;
  const result = await window.api.packages.uninstall(name);
  document.getElementById("pkg-msg").textContent = `Uninstall ${result.ok ? "success" : "failed"}: ${name}`;
  await loadPackages();
}

function esc(str) {
  if (!str) return "";
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
