/* DegreePath AI - frontend SPA (vanilla JS, hash routing) */

const state = {
  token: localStorage.getItem("dp_token") || null,
  user: JSON.parse(localStorage.getItem("dp_user") || "null"),
};

const app = document.getElementById("app");
const navbar = document.getElementById("navbar");

function saveAuth(token, user) {
  state.token = token;
  state.user = user;
  localStorage.setItem("dp_token", token);
  localStorage.setItem("dp_user", JSON.stringify(user));
}

function clearAuth() {
  state.token = null;
  state.user = null;
  localStorage.removeItem("dp_token");
  localStorage.removeItem("dp_user");
}

async function api(path, opts = {}) {
  const headers = { "Content-Type": "application/json", ...(opts.headers || {}) };
  if (state.token) headers["Authorization"] = "Bearer " + state.token;
  const res = await fetch("/api" + path, { ...opts, headers });
  const data = await res.json().catch(() => ({}));
  if (res.status === 401 && state.token) {
    clearAuth();
    location.hash = "#/auth";
    throw new Error("انتهت الجلسة، سجل دخولك تاني");
  }
  if (!res.ok) throw new Error(data.error || "حصل خطأ غير متوقع");
  return data;
}

function render(templateId) {
  const tpl = document.getElementById(templateId);
  app.innerHTML = "";
  app.appendChild(tpl.content.cloneNode(true));
}

function esc(s) {
  const d = document.createElement("div");
  d.textContent = s == null ? "" : String(s);
  return d.innerHTML;
}

function skillChip(s, cls = "") {
  const core = s.importance === 3 ? " core" : "";
  return `<span class="chip ${cls}${core}" title="${esc(s.name)}">${esc(s.name_ar || s.name)}</span>`;
}

function matchBar(pct) {
  const cls = pct >= 70 ? "high" : pct >= 40 ? "mid" : "";
  return `<div class="match-bar ${cls}"><div style="width:${pct}%"></div></div>`;
}

function importanceLabel(i) {
  return i === 3 ? "أساسية" : i === 2 ? "مهمة" : "ميزة إضافية";
}

/* ---------- views ---------- */

function showAuth() {
  navbar.classList.add("hidden");
  render("tpl-auth");
  const loginForm = document.getElementById("loginForm");
  const registerForm = document.getElementById("registerForm");
  const tabLogin = document.getElementById("tabLogin");
  const tabRegister = document.getElementById("tabRegister");
  const errEl = document.getElementById("authError");

  tabLogin.onclick = () => {
    tabLogin.classList.add("active");
    tabRegister.classList.remove("active");
    loginForm.classList.remove("hidden");
    registerForm.classList.add("hidden");
    errEl.textContent = "";
  };
  tabRegister.onclick = () => {
    tabRegister.classList.add("active");
    tabLogin.classList.remove("active");
    registerForm.classList.remove("hidden");
    loginForm.classList.add("hidden");
    errEl.textContent = "";
  };

  loginForm.onsubmit = async (e) => {
    e.preventDefault();
    errEl.textContent = "";
    const fd = new FormData(loginForm);
    try {
      const data = await api("/login", {
        method: "POST",
        body: JSON.stringify({ email: fd.get("email"), password: fd.get("password") }),
      });
      saveAuth(data.token, data.user);
      location.hash = "#/dashboard";
    } catch (err) {
      errEl.textContent = err.message;
    }
  };

  registerForm.onsubmit = async (e) => {
    e.preventDefault();
    errEl.textContent = "";
    const fd = new FormData(registerForm);
    try {
      const data = await api("/register", {
        method: "POST",
        body: JSON.stringify({
          name: fd.get("name"),
          email: fd.get("email"),
          password: fd.get("password"),
        }),
      });
      saveAuth(data.token, data.user);
      location.hash = "#/profile";
    } catch (err) {
      errEl.textContent = err.message;
    }
  };
}

function showNav(route) {
  navbar.classList.remove("hidden");
  document.getElementById("navUser").textContent = state.user ? state.user.name : "";
  document.querySelectorAll(".nav-links a").forEach((a) => {
    a.classList.toggle("active", a.dataset.route === route);
  });
}

async function showDashboard() {
  showNav("dashboard");
  render("tpl-dashboard");
  const [skillsData, matchesData, profileData] = await Promise.all([
    api("/skills"),
    api("/matches"),
    api("/profile"),
  ]);

  const summary = document.getElementById("dashSummary");
  const best = matchesData.matches[0];
  summary.innerHTML = `
    <div class="summary-cards">
      <div class="summary-card"><div class="num">${skillsData.skills.length}</div><div class="lbl">مهارة عندك</div></div>
      <div class="summary-card"><div class="num">${best ? Math.round(best.match_pct) + "%" : "-"}</div><div class="lbl">أعلى نسبة تطابق</div></div>
      <div class="summary-card"><div class="num">${best ? esc(best.title_ar || best.title) : "-"}</div><div class="lbl">أقرب وظيفة ليك</div></div>
      <div class="summary-card"><div class="num">${esc(profileData.profile.target_job_title_ar || "-")}</div><div class="lbl">هدفك</div></div>
    </div>`;

  const wrap = document.getElementById("dashMatches");
  if (!matchesData.matches.length) {
    wrap.innerHTML = `<div class="empty-state">لسه مفيش وظائف في النظام.</div>`;
    return;
  }
  wrap.innerHTML = matchesData.matches
    .slice(0, 6)
    .map(
      (m) => `
    <div class="card job-card" onclick="location.hash='#/jobs/${m.job_id}'">
      <h4>${esc(m.title_ar || m.title)}</h4>
      <div class="cat">${esc(m.title)}</div>
      ${matchBar(m.match_pct)}
      <div><span class="match-pct">${Math.round(m.match_pct)}%</span> تطابق -
        ${m.matched.length} مهارة عندك، ${m.missing.length} ناقصة</div>
    </div>`
    )
    .join("");
  if (!skillsData.skills.length) {
    summary.innerHTML += `<div class="card"><p class="muted">💡 لسه ما أضفتش مواد. روح لصفحة <a href="#/courses">موادي وكورساتي</a> وضيف موادك عشان النظام يستخرج مهاراتك ويطابقها بالوظائف.</p></div>`;
  }
}

async function showCourses() {
  showNav("courses");
  render("tpl-courses");
  const form = document.getElementById("courseForm");
  const result = document.getElementById("courseResult");

  async function refresh() {
    const [coursesData, skillsData] = await Promise.all([api("/courses"), api("/skills")]);
    document.getElementById("allSkills").innerHTML =
      skillsData.skills.map((s) => skillChip(s, "have")).join("") ||
      `<span class="muted">لسه مفيش مهارات مستخرجة.</span>`;
    document.getElementById("courseList").innerHTML =
      coursesData.courses
        .map(
          (c) => `
      <div class="card course-item">
        <div>
          <h4>${esc(c.title)} <span class="badge">${c.kind === "certification" ? "شهادة" : "مادة"}</span></h4>
          ${c.description ? `<p class="muted">${esc(c.description)}</p>` : ""}
          <div class="chips">${c.skills.map((s) => skillChip(s, "have")).join("") || '<span class="muted">لم تُستخرج مهارات</span>'}</div>
        </div>
        <button class="btn small danger" data-del="${c.id}">حذف</button>
      </div>`
        )
        .join("") || `<div class="empty-state">لسه ما أضفتش مواد.</div>`;
    document.querySelectorAll("[data-del]").forEach((btn) => {
      btn.onclick = async () => {
        await api("/courses/" + btn.dataset.del, { method: "DELETE" });
        refresh();
      };
    });
  }

  const catalogSelect = document.getElementById("catalogSelect");
  const catalogError = document.getElementById("catalogError");
  try {
    const catalogData = await api("/catalog");
    catalogSelect.innerHTML = catalogData.catalog
      .map(
        (c) =>
          `<option value="${c.id}">[مستوى ${c.level} - ترم ${c.semester}] ${esc(c.title)}</option>`
      )
      .join("");
  } catch (_) {
    catalogSelect.innerHTML = "<option>تعذر تحميل القائمة</option>";
  }
  document.getElementById("catalogAddBtn").onclick = async () => {
    catalogError.textContent = "";
    try {
      await api("/courses/from-catalog", {
        method: "POST",
        body: JSON.stringify({ catalog_id: Number(catalogSelect.value) }),
      });
      refresh();
    } catch (err) {
      catalogError.textContent = err.message;
    }
  };

  form.onsubmit = async (e) => {
    e.preventDefault();
    const fd = new FormData(form);
    try {
      const data = await api("/courses", {
        method: "POST",
        body: JSON.stringify({
          title: fd.get("title"),
          description: fd.get("description"),
          kind: fd.get("kind"),
        }),
      });
      result.innerHTML = `<div class="card"><strong>المهارات المستخرجة:</strong><div class="chips">${
        data.extracted_skills.map((s) => skillChip(s, "have")).join("") ||
        '<span class="muted">لم تُستخرج مهارات من الوصف ده - جرّب تكتب وصف أدق</span>'
      }</div></div>`;
      form.reset();
      refresh();
    } catch (err) {
      result.innerHTML = `<p class="error">${esc(err.message)}</p>`;
    }
  };

  await refresh();
}

async function showJobs() {
  showNav("jobs");
  render("tpl-jobs");
  const data = await api("/jobs");
  document.getElementById("jobsList").innerHTML = data.jobs
    .map(
      (j) => `
    <div class="card job-card" onclick="location.hash='#/jobs/${j.id}'">
      <h4>${esc(j.title_ar || j.title)}</h4>
      <div class="cat">${esc(j.title)}</div>
      <p class="muted">${esc(j.description).slice(0, 120)}...</p>
      <div class="chips">${j.required_skills.slice(0, 4).map((s) => skillChip(s)).join("")}${
        j.required_skills.length > 4 ? `<span class="chip">+${j.required_skills.length - 4}</span>` : ""
      }</div>
    </div>`
    )
    .join("");
}

async function showJobDetail(jobId) {
  showNav("jobs");
  render("tpl-job-detail");
  const [jobData, analysis] = await Promise.all([
    api("/jobs/" + jobId),
    api("/analysis/" + jobId),
  ]);
  const j = jobData.job;
  const el = document.getElementById("jobDetail");
  el.innerHTML = `
    <h2>${esc(j.title_ar || j.title)}</h2>
    <div class="muted">${esc(j.title)} - ${esc(j.category || "")}</div>
    <div class="card"><p>${esc(j.description)}</p></div>

    <div class="card">
      <h3>نسبة تطابقك مع الوظيفة دي</h3>
      ${matchBar(analysis.match_pct)}
      <div><span class="match-pct">${Math.round(analysis.match_pct)}%</span></div>
    </div>

    <div class="card">
      <h3>تحليل الفجوة في المهارات (Skill Gap)</h3>
      <h4>مهارات عندك بالفعل (${analysis.matched.length}) ✔</h4>
      <div class="chips">${analysis.matched.map((s) => skillChip(s, "have")).join("") || '<span class="muted">لا يوجد</span>'}</div>
      <h4>مهارات ناقصة (${analysis.missing.length}) ✗</h4>
      <div class="chips">${analysis.missing.map((s) => skillChip(s, "missing")).join("") || '<span class="muted">لا يوجد - انت جاهز!</span>'}</div>
    </div>

    <h3>خطة التعلم المقترحة (Learning Roadmap)</h3>
    <div class="roadmap">
      ${
        analysis.roadmap
          .map(
            (step) => `
        <div class="roadmap-step">
          <div class="step-title">الخطوة ${step.step}: اتعلم ${esc(step.skill_ar || step.skill)}
            <span class="badge">${importanceLabel(step.importance)}</span></div>
          ${
            step.resources.length
              ? `<ul>${step.resources
                  .map((r) => `<li><a href="${esc(r.url)}" target="_blank" rel="noopener">${esc(r.title)}</a> <span class="badge">${esc(r.kind)}</span></li>`)
                  .join("")}</ul>`
              : '<p class="muted">ابحث عن كورس مجاني في المهارة دي.</p>'
          }
        </div>`
          )
          .join("") || '<div class="card"><p>🎉 مهاراتك بتغطي متطلبات الوظيفة دي!</p></div>'
      }
    </div>`;
}

async function showProfile() {
  showNav("profile");
  render("tpl-profile");
  const [profileData, jobsData] = await Promise.all([api("/profile"), api("/jobs")]);
  const p = profileData.profile || {};
  const form = document.getElementById("profileForm");
  form.university.value = p.university || "";
  form.major.value = p.major || "";
  form.study_year.value = p.study_year || "";
  const sel = document.getElementById("targetJobSelect");
  sel.innerHTML =
    '<option value="">اختر وظيفة...</option>' +
    jobsData.jobs
      .map((j) => `<option value="${j.id}">${esc(j.title_ar || j.title)}</option>`)
      .join("");
  if (p.target_job_id) sel.value = p.target_job_id;

  form.onsubmit = async (e) => {
    e.preventDefault();
    const fd = new FormData(form);
    try {
      await api("/profile", {
        method: "PUT",
        body: JSON.stringify({
          university: fd.get("university"),
          major: fd.get("major"),
          study_year: fd.get("study_year"),
          target_job_id: fd.get("target_job_id") ? Number(fd.get("target_job_id")) : null,
        }),
      });
      document.getElementById("profileMsg").textContent = "تم الحفظ ✅";
    } catch (err) {
      document.getElementById("profileMsg").textContent = err.message;
    }
  };
}

/* ---------- router ---------- */

const routes = {
  auth: showAuth,
  dashboard: showDashboard,
  courses: showCourses,
  jobs: showJobs,
  profile: showProfile,
};

async function route() {
  const hash = location.hash || "#/dashboard";
  const parts = hash.slice(2).split("/");
  const page = parts[0] || "dashboard";
  if (!state.token && page !== "auth") {
    location.hash = "#/auth";
    return;
  }
  if (state.token && page === "auth") {
    location.hash = "#/dashboard";
    return;
  }
  if (page === "jobs" && parts[1]) {
    await showJobDetail(parts[1]);
    return;
  }
  const view = routes[page] || showDashboard;
  try {
    await view();
  } catch (err) {
    if (state.token) {
      app.innerHTML = `<div class="page"><div class="card"><p class="error">${esc(err.message)}</p></div></div>`;
    }
  }
}

document.getElementById("logoutBtn").onclick = async (e) => {
  e.preventDefault();
  try {
    await api("/logout", { method: "POST" });
  } catch (_) {}
  clearAuth();
  location.hash = "#/auth";
};

window.addEventListener("hashchange", route);
route();
