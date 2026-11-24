/* مسارك - owner dashboard (read-only) */
const app = document.getElementById("app");
let token = localStorage.getItem("admin_token") || "";
let usersCache = [];

function tpl(id) {
  app.innerHTML = "";
  app.appendChild(document.getElementById(id).content.cloneNode(true));
}

async function api(path, opts = {}) {
  opts.headers = Object.assign(
    { "Content-Type": "application/json", Authorization: "Bearer " + token },
    opts.headers || {}
  );
  const res = await fetch("/api/admin" + path, opts);
  const data = await res.json().catch(() => ({}));
  if (res.status === 401) {
    localStorage.removeItem("admin_token");
    token = "";
    showLogin();
    throw new Error(data.error || "غير مصرّح");
  }
  if (!res.ok) throw new Error(data.error || "حصل خطأ");
  return data;
}

function showLogin() {
  tpl("tpl-login");
  document.getElementById("adminLoginForm").onsubmit = async (e) => {
    e.preventDefault();
    const err = document.getElementById("adminError");
    err.textContent = "";
    try {
      const data = await api("/login", {
        method: "POST",
        body: JSON.stringify({ password: e.target.password.value }),
      });
      token = data.token;
      localStorage.setItem("admin_token", token);
      showDash();
    } catch (ex) {
      err.textContent = ex.message;
    }
  };
}

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => "&#" + c.codePointAt(0) + ";");
}

function renderUsers(filter) {
  const q = (filter || "").trim().toLowerCase();
  const rows = usersCache.filter(
    (u) =>
      !q ||
      (u.name || "").toLowerCase().includes(q) ||
      (u.email || "").toLowerCase().includes(q) ||
      (u.university || "").toLowerCase().includes(q)
  );
  document.getElementById("userCount").textContent = rows.length;
  document.getElementById("userRows").innerHTML = rows
    .map(
      (u) => `<tr>
      <td>${u.id}</td>
      <td>${esc(u.name)}</td>
      <td>${esc(u.email)}</td>
      <td>${esc(u.university || "—")}</td>
      <td>${esc(u.major || "—")}</td>
      <td>${esc(u.study_year || "—")}</td>
      <td>${esc(u.target_job || "—")}</td>
      <td>${u.n_courses}</td>
      <td>${u.n_skills}</td>
      <td>${u.n_analyses}</td>
      <td>${esc((u.created_at || "").slice(0, 16))}</td>
    </tr>`
    )
    .join("");
}

async function showDash() {
  tpl("tpl-dash");
  let data;
  try {
    data = await api("/overview");
  } catch (ex) {
    return;
  }
  const s = data.stats;
  document.getElementById("statGrid").innerHTML = [
    ["الحسابات", s.total_users],
    ["تسجيلات النهارده", s.signups_today],
    ["المواد المضافة", s.total_courses],
    ["التحليلات", s.total_analyses],
    ["وظائف النظام", s.catalog_jobs],
    ["وظائف اليوم", s.live_jobs],
  ]
    .map(([label, v]) => `<div class="stat"><b>${v}</b><span>${label}</span></div>`)
    .join("");
  document.getElementById("byDay").innerHTML = data.signups_by_day.length
    ? data.signups_by_day
        .map((r) => `<div class="dayrow"><span>${esc(r.d)}</span><b>${r.c}</b></div>`)
        .join("")
    : '<p class="muted">مفيش تسجيلات لسه.</p>';
  usersCache = data.users;
  renderUsers("");
  document.getElementById("userFilter").oninput = (e) => renderUsers(e.target.value);
  document.getElementById("adminLogout").onclick = async () => {
    try {
      await api("/logout", { method: "POST" });
    } catch (e) {}
    localStorage.removeItem("admin_token");
    token = "";
    showLogin();
  };
}

if (token) {
  showDash();
} else {
  showLogin();
}
