/* مسارك (DegreePath AI) - frontend SPA (vanilla JS, hash routing) */

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
  Object.keys(localStorage).forEach((k) => { if (k.startsWith("dpc:")) localStorage.removeItem(k); });
}

// Stale-while-revalidate: paint the last saved copy instantly, then refresh it.
async function swr(path, nav, paint) {
  const key = "dpc:" + (state.user ? state.user.id : "x") + ":" + path;
  let old = null;
  try { old = JSON.parse(localStorage.getItem(key)); } catch (_) {}
  if (old) paint(old);
  let fresh;
  try { fresh = await api(path); } catch (err) { if (old) return; throw err; }
  alive(nav);
  const txt = JSON.stringify(fresh);
  if (!old || txt !== JSON.stringify(old)) paint(fresh);
  try { localStorage.setItem(key, txt); } catch (_) {}
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

let navId = 0;
class Stale extends Error {}

function render(templateId) {
  const tpl = document.getElementById(templateId);
  app.innerHTML = "";
  app.appendChild(tpl.content.cloneNode(true));
  return ++navId;
}

// After any await, a newer navigation may have replaced the page. Stop quietly.
function alive(nav) {
  if (nav !== navId) throw new Stale();
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
  const nav = render("tpl-auth");
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
  const nav = render("tpl-dashboard");
  const [skillsData, matchesData, profileData] = await Promise.all([
    api("/skills"),
    api("/matches"),
    api("/profile"),
  ]);
  alive(nav);

  const summary = document.getElementById("dashSummary");
  const best = matchesData.matches[0];
  summary.innerHTML = `
    <div class="summary-cards">
      <div class="summary-card"><div class="num">${skillsData.skills.length}</div><div class="lbl">مهارة عندك</div></div>
      <div class="summary-card"><div class="num">${best ? Math.round(best.match_pct) + "%" : "-"}</div><div class="lbl">أعلى نسبة تطابق</div></div>
      <div class="summary-card"><div class="num">${best ? esc(best.title_ar || best.title) : "-"}</div><div class="lbl">أقرب وظيفة ليك</div></div>
      <div class="summary-card"><div class="num">${esc(profileData.profile.target_job_title_ar || "-")}</div><div class="lbl">هدفك</div></div>
    </div>`;

  const rm = document.getElementById("dashRoadmap");
  const tid = profileData.profile.target_job_id;
  try {
    const jobs = (await api("/careers")).careers;
    alive(nav);
    const opts = '<option value="">اختر مسار...</option>' + jobs.map((c) => `<option value="${c.id}"${c.id == tid ? " selected" : ""}>${esc(c.title_ar || c.title)}</option>`).join("");
    rm.innerHTML = `<div class="card"><h3>🎯 مسارك والخطة</h3><p class="muted">اختار المسار وهتشوف الخطة كاملة (مهارات + كورسات مجانية) حتى من غير ما تضيف مهارات.</p><select id="dashTrack">${opts}</select><div id="dashTrackBody"></div></div>`;
    const body = document.getElementById("dashTrackBody");
    const sel = document.getElementById("dashTrack");
    async function draw(id) {
      if (!id) { body.innerHTML = ""; return; }
      body.innerHTML = '<p class="muted">جاري التحميل...</p>';
      const r = await api("/careers/" + id);
      alive(nav);
      body.innerHTML = `<p><a href="#/careers/${id}">صفحة المسار كاملة</a></p>` + roadmapHTML(r) + sourcesHTML(r);
    }
    sel.onchange = () => draw(sel.value).catch((e) => { if (!(e instanceof Stale)) body.innerHTML = `<p class="error">${esc(e.message)}</p>`; });
    if (tid) await draw(String(tid));
  } catch (e) { if (e instanceof Stale) return; }

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
    summary.innerHTML += `<div class="card"><p class="muted">💡 لسه ما أضفتش مواد. روح لصفحة <a href="#/courses">مهاراتي</a> وضيف مهاراتك (مش لازم مواد) عشان النظام ويطابقها بالوظائف.</p></div>`;
  }
}

async function showCourses() {
  showNav("courses");
  const nav = render("tpl-courses");
  const form = document.getElementById("courseForm");
  const result = document.getElementById("courseResult");

  async function refresh() {
    const [coursesData, skillsData] = await Promise.all([api("/courses"), api("/skills")]);
    alive(nav);
    const skillCourse = {};
    coursesData.courses.filter((c) => c.kind === "skill").forEach((c) => c.skills.forEach((s) => (skillCourse[s.id] = c.id)));
    document.getElementById("allSkills").innerHTML =
      skillsData.skills.map((s) => skillChip(s, "have") .replace("</span>", skillCourse[s.id] ? ` <button class="x" data-delskill="${skillCourse[s.id]}" aria-label="حذف المهارة">×</button></span>` : "</span>")).join("") ||
      `<span class="muted">لسه ما أضفتش أي مهارة. ابحث فوق واضغط على المهارة.</span>`;
    document.querySelectorAll("[data-delskill]").forEach((b) => {
      b.onclick = async () => { await api("/courses/" + b.dataset.delskill, { method: "DELETE" }); refresh(); drawSkillResults(); };
    });
    document.getElementById("courseList").innerHTML =
      coursesData.courses.filter((c) => c.kind !== "skill")
        .map(
          (c) => `
      <div class="card course-item">
        <div>
          <h4>${esc(c.title)} <span class="badge">${c.kind === "skill" ? "مهارة" : c.kind === "certification" ? "شهادة" : "مادة"}</span></h4>
          ${c.description ? `<p class="muted">${esc(c.description)}</p>` : ""}
          <div class="chips">${c.skills.map((s) => skillChip(s, "have")).join("") || '<span class="muted">لم تُستخرج مهارات</span>'}</div>
        </div>
        <button class="btn small danger" data-del="${c.id}">حذف</button>
      </div>`
        )
        .join("") || `<div class="empty-state">مفيش مواد مسجلة (ده اختياري). المهم تضيف مهاراتك من فوق.</div>`;
    document.querySelectorAll("[data-del]").forEach((btn) => {
      btn.onclick = async () => {
        await api("/courses/" + btn.dataset.del, { method: "DELETE" });
        refresh();
      };
    });
  }

  const skillQ = document.getElementById("skillQ");
  const skillBox = document.getElementById("skillResults");
  let skillTimer;
  async function drawSkillResults() {
    const r = await api("/skills/search?q=" + encodeURIComponent(skillQ.value.trim()));
    alive(nav);
    skillBox.innerHTML = r.skills.length
      ? r.skills.map((s) => `<button class="chipb pickb${s.have ? " on" : ""}" data-sid="${s.id}" ${s.have ? "disabled" : ""}>${s.have ? "✓" : "+"} ${esc(s.name_ar || s.name)} <small>${esc(s.name)}</small></button>`).join("")
      : `<span class="muted">مفيش مهارة بالاسم ده. جرّب كلمة تانية، أو أضف مادة من الأسفل.</span>`;
  }
  skillQ.oninput = () => { clearTimeout(skillTimer); skillTimer = setTimeout(drawSkillResults, 250); };
  skillBox.onclick = async (e) => {
    const b = e.target.closest("[data-sid]");
    if (!b || b.disabled) return;
    document.getElementById("skillErr").textContent = "";
    try {
      const r = await api("/skills/add", { method: "POST", body: JSON.stringify({ skill_id: Number(b.dataset.sid) }) });
      document.getElementById("skillMsg").textContent = "اتضافت المهارة: " + (r.skill.name_ar || r.skill.name);
      await refresh();
      await drawSkillResults();
    } catch (err) {
      document.getElementById("skillErr").textContent = err.message;
    }
  };
  drawSkillResults().catch((e) => { if (!(e instanceof Stale)) document.getElementById("skillErr").textContent = e.message; });

  /* faculty picker */
  const facDept = document.getElementById("facDept");
  const facList = document.getElementById("facList");
  const facYears = document.getElementById("facYears");
  const fac = { all: [], depts: [], year: 1 };
  function facDraw() {
    facYears.innerHTML = [1, 2, 3, 4, 5].map((y) => `<button type="button" class="chipb pickb${fac.year === y ? " on" : ""}" data-y="${y}">${y === 5 ? "الخامسة / خريج (الكل)" : "السنة " + y}</button>`).join("");
    const rows = fac.all.filter((c) => c.department === facDept.value && (fac.year === 5 || c.level === fac.year));
    const groups = {};
    rows.forEach((c) => { const k = fac.year === 5 ? `السنة ${c.level} - ترم ${c.semester}` : `ترم ${c.semester}`; (groups[k] = groups[k] || []).push(c); });
    facList.innerHTML = Object.keys(groups).map((k) => `<h4 class="stage-title">${esc(k)}</h4>` + groups[k].map((c) => `<label class="facrow"><input type="checkbox" value="${c.id}"> ${esc(c.title)}${c.kind === "elective" ? ' <span class="badge">اختياري</span>' : ""}</label>`).join("")).join("") || '<p class="muted">مفيش مواد.</p>';
  }
  facYears.onclick = (e) => { const b = e.target.closest("[data-y]"); if (!b) return; fac.year = Number(b.dataset.y); facDraw(); };
  facDept.onchange = facDraw;
  document.getElementById("facAll").onclick = () => { const bs = facList.querySelectorAll("input"); const on = [...bs].some((i) => !i.checked); bs.forEach((i) => (i.checked = on)); };
  document.getElementById("facAdd").onclick = async () => {
    const ids = [...facList.querySelectorAll("input:checked")].map((i) => Number(i.value));
    const msg = document.getElementById("facMsg"), err = document.getElementById("facErr");
    msg.textContent = ""; err.textContent = "";
    if (!ids.length) { err.textContent = "علّم على مادة واحدة على الأقل"; return; }
    try {
      const r = await api("/courses/from-catalog", { method: "POST", body: JSON.stringify({ catalog_ids: ids }) });
      msg.textContent = `اتضاف ${r.added} مادة${r.skipped ? "، " + r.skipped + " كانت مضافة قبل كده" : ""}، واتستخرج ${(r.extracted_skills || []).length} مهارة ✅`;
      facList.querySelectorAll("input").forEach((i) => (i.checked = false));
      refresh();
    } catch (e2) { err.textContent = e2.message; }
  };
  api("/catalog").then(async (d) => {
    alive(nav);
    fac.all = d.catalog; fac.depts = d.departments || [];
    let mine = "";
    try { mine = ((await api("/profile")).profile || {}).department || ""; } catch (e) {}
    facDept.innerHTML = fac.depts.map((x) => `<option value="${x.key}"${x.key === mine ? " selected" : ""}>${esc(x.label)}</option>`).join("");
    facDraw();
  }).catch((e) => { if (!(e instanceof Stale)) facList.innerHTML = '<p class="error">تعذر تحميل مواد الكلية</p>'; });

  const catalogSelect = document.getElementById("catalogSelect");
  const catalogError = document.getElementById("catalogError");
  try {
    const catalogData = await api("/catalog");
    alive(nav);
    catalogSelect.innerHTML = catalogData.catalog
      .map(
        (c) =>
          `<option value="${c.id}">[مستوى ${c.level} - ترم ${c.semester}] ${esc(c.title)}</option>`
      )
      .join("");
  } catch (e) {
    if (e instanceof Stale) return;
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

const careerState = { cat: "" };

function careerCard(c) {
  return `
    <div class="card job-card" onclick="location.hash='#/careers/${c.id}'">
      <h4>${esc(c.title_ar || c.title)}</h4>
      <div class="cat">${esc(c.title)}</div>
      <div class="chips">${c.top_skills.map((n) => `<span class="chip">${esc(n)}</span>`).join("")}${
        c.n_skills > c.top_skills.length ? `<span class="chip">+${c.n_skills - c.top_skills.length}</span>` : ""
      }</div>
      <div class="muted">🗺️ شوف خطة التعلم (${c.n_skills} مهارة)</div>
    </div>`;
}

async function showJobs() {
  showNav("jobs");
  const nav = render("tpl-jobs");
  const draw = (data) => {
    const bar = document.getElementById("careerCats");
    const list = document.getElementById("careersList");
    if (!bar || !list) return;
    bar.innerHTML =
      `<button class="chipb${careerState.cat === "" ? " on" : ""}" data-k="">الكل (${data.careers.length})</button>` +
      data.categories.map((c) => `<button class="chipb${careerState.cat === c.key ? " on" : ""}" data-k="${esc(c.key)}">${esc(c.label)} (${c.count})</button>`).join("");
    bar.onclick = (e) => {
      if (e.target.dataset.k !== undefined) { careerState.cat = e.target.dataset.k; draw(data); }
    };
    list.innerHTML = data.careers.filter((c) => !careerState.cat || c.category === careerState.cat).map(careerCard).join("");
  };
  // personalised block loads after the careers are on screen
  api("/matches").then((m) => {
    if (nav !== navId) return;
    const el = document.getElementById("topMatches");
    if (!el) return;
    const mine = m.matches.slice(0, 6);
    el.innerHTML = mine.map((x) => `
      <div class="card job-card" onclick="location.hash='#/jobs/${x.job_id}'">
        <h4>${esc(x.title_ar || x.title)}</h4>
        ${matchBar(x.match_pct)}
        <div><span class="match-pct">${Math.round(x.match_pct)}%</span> تطابق مع مهاراتك</div>
      </div>`).join("");
  }).catch(() => {});
  await swr("/careers", nav, draw);
}

function roadmapHTML(r) {
  return `<h3>خطة التعلم الكاملة (Roadmap) - ${r.total_skills} مهارة</h3>
  ${r.stages.map((st) => `
    <h4 class="stage-title">${esc(st.label)}</h4>
    <div class="roadmap">${st.skills.map((sk) => `
      <div class="roadmap-step${sk.have ? " done" : ""}">
        <div class="step-title">${sk.step}. ${esc(sk.skill_ar || sk.skill)}
          <span class="muted">(${esc(sk.skill)})</span>
          ${sk.have ? '<span class="badge">✔ عندك</span>' : ""}</div>
        ${sk.resources.length
          ? `<ul>${sk.resources.map((x) => `<li><a href="${esc(x.url)}" target="_blank" rel="noopener">${esc(x.title)}</a> <span class="badge">${esc(x.kind)}</span></li>`).join("")}</ul>`
          : '<p class="muted">ابحث عن كورس مجاني في المهارة دي.</p>'}
      </div>`).join("")}</div>`).join("")}`;
}

function sourcesHTML(r) {
  const s = r.sources || [];
  if (!s.length) return "";
  return `<div class="card sources"><h4>📚 مصادر المهارات المطلوبة للمسار ده</h4>
    <ul>${s.map((x) => `<li><a href="${esc(x.url)}" target="_blank" rel="noopener">${esc(x.label || x.url)}</a></li>`).join("")}</ul></div>`;
}

async function showCareer(jobId) {
  showNav("jobs");
  const nav = render("tpl-career");
  await swr("/careers/" + jobId, nav, (r) => {
    const el = document.getElementById("careerDetail");
    if (!el) return;
    const j = r.job;
    el.innerHTML = `
      <h2>${esc(j.title_ar || j.title)}</h2>
      <div class="muted">${esc(j.title)} - ${esc(j.category_label || "")}</div>
      <div class="card"><p>${esc(j.description)}</p>
        <a class="btn primary" href="#/jobs/${j.id}">حلل فجوتي مع المسار ده</a>
        <button class="btn" id="setTarget">🎯 خلّي ده هدفي</button> <span class="success" id="targetMsg"></span></div>
      ${roadmapHTML(r)}
      ${sourcesHTML(r)}`;
    const tb = document.getElementById("setTarget");
    if (tb) tb.onclick = async () => {
      try {
        const pr = (await api("/profile")).profile || {};
        await api("/profile", { method: "PUT", body: JSON.stringify({ university: pr.university || "", major: pr.major || "", study_year: pr.study_year || "", department: pr.department || "", target_job_id: j.id }) });
        document.getElementById("targetMsg").textContent = "تم ✅ هتلاقي الخطة في لوحة التحكم";
      } catch (e) { document.getElementById("targetMsg").textContent = e.message; }
    };
  });
}

async function showJobDetail(jobId) {
  showNav("jobs");
  const nav = render("tpl-job-detail");
  const [jobData, analysis] = await Promise.all([
    api("/jobs/" + jobId),
    api("/analysis/" + jobId),
  ]);
  alive(nav);
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
  const nav = render("tpl-profile");
  const [profileData, jobsData] = await Promise.all([api("/profile"), api("/jobs")]);
  alive(nav);
  const p = profileData.profile || {};
  const form = document.getElementById("profileForm");
  form.university.value = p.university || "";
  form.major.value = p.major || "";
  form.study_year.value = p.study_year || "";
  if (form.department) form.department.value = p.department || "";
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
          department: fd.get("department") || "",
          target_job_id: fd.get("target_job_id") ? Number(fd.get("target_job_id")) : null,
        }),
      });
      document.getElementById("profileMsg").textContent = "تم الحفظ ✅";
    } catch (err) {
      document.getElementById("profileMsg").textContent = err.message;
    }
  };
}


/* ---------- live feed (daily jobs + linked free courses) ---------- */

const feedState = { tab: "jobs", country: "eg", lang: "", field: "", offset: 0, fields: {}, st: null };

function minutesLabel(m) {
  if (!m) return "";
  return m >= 60 ? Math.round(m / 60) + " ساعة" : m + " دقيقة";
}

function freeBadge(f) {
  if (f === "paid") return '<span class="chip paid" title="تجربة مجانية 7 أيام ثم اشتراك">💳 مدفوع بعد تجربة 7 أيام</span>';
  return f === "audit"
    ? '<span class="chip" title="مجاني للمشاهدة، الشهادة مدفوعة">مجاني (Audit)</span>'
    : '<span class="chip have">🆓 مجاني 100%</span>';
}

function feedCard(j) {
  const miss = j.n_skills ? j.missing.slice(0, 3).map((s) => skillChip(s, "missing")).join("") : "";
  const flag = j.egypt ? "🇪🇬 " : "🌍 ";
  return `<a class="card jobc" href="#/feed/${j.id}">
    <div class="jobc-top"><h3>${esc(j.title)}</h3>${j.n_skills ? `<b class="pct">${j.match_pct}%</b>` : ""}</div>
    <p class="muted">${esc(j.company)}</p>
    <p class="meta">${flag}${esc(j.location)}${j.posted_at ? " · " + esc(j.posted_at) : ""}</p>
    <div class="chips"><span class="chip">${esc(j.field_label)}</span>${miss}</div>
  </a>`;
}

function courseCard(c) {
  return `<a class="card jobc" href="${esc(c.url)}" target="_blank" rel="noopener">
    <div class="jobc-top"><h3>${esc(c.title)}</h3></div>
    <p class="muted">${esc(c.summary).slice(0, 110)}${c.summary.length > 110 ? "…" : ""}</p>
    ${c.free === "paid" ? `<p class="paidnote">${esc(c.pricing_note)}</p>` : ""}<div class="chips"><span class="chip">${esc(c.provider)}</span>${freeBadge(c.free)}<span class="chip">${esc(c.field_label)}</span>${c.duration_min ? `<span class="chip">${minutesLabel(c.duration_min)}</span>` : ""}</div>
  </a>`;
}

async function loadFeed(append, nav = navId) {
  const q = document.getElementById("feedQ").value.trim();
  const sort = document.getElementById("feedSort").value;
  const isJobs = feedState.tab === "jobs";
  if (!append) feedState.offset = 0;
  const params = new URLSearchParams({ q, sort, limit: 20, offset: feedState.offset });
  if (feedState.field) params.set("field", feedState.field);
  if (isJobs && feedState.country) params.set("country", feedState.country);
  if (feedState.tab === "paid") params.set("pricing", "paid");
  if (feedState.tab === "courses" && feedState.lang === "ar") params.set("source", "arabic");
  const data = await api((isJobs ? "/feed/jobs?" : "/feed/courses?") + params.toString());
  alive(nav);
  const items = isJobs ? data.jobs : data.courses;
  const list = document.getElementById("feedList");
  const html = items.map(isJobs ? feedCard : courseCard).join("");
  if (append) list.insertAdjacentHTML("beforeend", html);
  else list.innerHTML = html || '<p class="empty-state">مفيش نتائج. جرّب مجال تاني أو "الكل".</p>';
  feedState.offset += items.length;
  const more = document.getElementById("feedMore");
  more.innerHTML = feedState.offset < data.total
    ? `<button class="btn primary block" id="feedMoreBtn">عرض المزيد (${data.total - feedState.offset})</button>` : "";
  const btn = document.getElementById("feedMoreBtn");
  if (btn) btn.onclick = () => loadFeed(true, nav);
}

function drawFilters() {
  const st = feedState.st, isJobs = feedState.tab === "jobs";
  const c = document.getElementById("feedCountry");
  const isFree = feedState.tab === "courses";
  c.classList.toggle("hidden", !(isJobs || isFree));
  const opts = isJobs
    ? [["eg", `🇪🇬 مصر (${st.egypt_jobs})`], ["world", `🌍 برّه مصر (${st.total_jobs - st.egypt_jobs})`], ["", "الكل"]]
    : [["ar", `🇪🇬 كورسات بالعربي (${st.arabic_courses || 0})`], ["", "كل اللغات"]];
  const cur = isJobs ? feedState.country : feedState.lang;
  c.innerHTML = opts.map(([v, l]) => `<button class="chipb${cur === v ? " on" : ""}" data-c="${v}">${l}</button>`).join("");
  const fields = isJobs ? st.job_fields : feedState.tab === "paid" ? st.paid_course_fields : st.course_fields;
  document.getElementById("paidNotice").classList.toggle("hidden", feedState.tab !== "paid");
  document.getElementById("freeNotice").classList.toggle("hidden", feedState.tab !== "courses");
  document.getElementById("feedFields").innerHTML =
    `<button class="chipb${feedState.field === "" ? " on" : ""}" data-f="">كل المجالات</button>` +
    fields.map((f) => `<button class="chipb${feedState.field === f.field ? " on" : ""}" data-f="${esc(f.field)}">${esc(f.label)} (${f.count})</button>`).join("");
  document.getElementById("feedSort").classList.toggle("hidden", !isJobs);
  document.querySelectorAll("#feedTabs button").forEach((b) => b.classList.toggle("on", b.dataset.t === feedState.tab));
}

async function showFeed() {
  showNav("feed");
  const nav = render("tpl-feed");
  const st = await api("/feed/status");
  alive(nav);
  feedState.st = st;
  const when = st.last_refresh_utc ? st.last_refresh_utc.slice(0, 16) + " UTC" : "لسه";
  document.getElementById("feedStatus").textContent = st.total_jobs
    ? `${st.total_jobs} وظيفة (${st.egypt_jobs} في مصر) و${st.total_courses} كورس مجاني 100%${st.paid_courses ? " (و" + st.paid_courses + " كورس مدفوع في تبويب منفصل)" : ""}. آخر تحديث: ${when}`
    : (st.refreshing ? "بنحمّل الوظائف... استنى دقيقة وحدّث الصفحة." : "جاري التحضير...");
  drawFilters();
  document.getElementById("feedCountry").onclick = (e) => {
    if (e.target.dataset.c !== undefined) {
      if (feedState.tab === "courses") feedState.lang = e.target.dataset.c; else feedState.country = e.target.dataset.c;
      drawFilters(); loadFeed(false);
    }
  };
  document.getElementById("feedFields").onclick = (e) => {
    if (e.target.dataset.f !== undefined) { feedState.field = e.target.dataset.f; drawFilters(); loadFeed(false); }
  };
  document.getElementById("feedTabs").onclick = (e) => {
    if (e.target.dataset.t) { feedState.tab = e.target.dataset.t; feedState.field = ""; drawFilters(); loadFeed(false); }
  };
  document.getElementById("feedSourcesInfo").innerHTML =
    "<ul>" + st.job_sources.concat(st.course_sources).map((s) =>
      `<li><a href="${esc(s.site)}" target="_blank" rel="noopener">${esc(s.name)}</a> (${s.count})${s.note ? " - " + esc(s.note) : ""}</li>`).join("") +
    "</ul><p>أغلب الوظائف جوه مصر. أي وظيفة بتفضل في القائمة طول ما هي مفتوحة في موقعها الأصلي، وبتتشال أول ما تتقفل أو تنتهي. القائمة بتتجدد تلقائيًا كل 24 ساعة. التقديم دايمًا من صفحة الوظيفة الأصلية.</p>";
  let timer;
  document.getElementById("feedQ").oninput = () => { clearTimeout(timer); timer = setTimeout(() => loadFeed(false), 350); };
  document.getElementById("feedSort").onchange = () => loadFeed(false);
  await loadFeed(false, nav);
}

async function showFeedDetail(id) {
  showNav("feed");
  const nav = render("tpl-feed-detail");
  const { job: j } = await api("/feed/jobs/" + id);
  alive(nav);
  const have = j.matched.map((s) => skillChip(s, "have")).join("") || '<span class="muted">لسه مفيش</span>';
  const steps = j.roadmap.map((st) => `
    <div class="card">
      <h4>${st.step}. ${esc(st.skill_ar || st.skill)} <span class="muted">(${esc(st.skill)} · ${importanceLabel(st.importance)})</span></h4>
      ${st.courses.length ? st.courses.map((c) => `
        <p>📚 <a href="${esc(c.url)}" target="_blank" rel="noopener">${esc(c.title)}</a>
        <span class="muted">${esc(c.provider)}${c.duration_min ? " · " + minutesLabel(c.duration_min) : ""}</span> ${freeBadge(c.free)}</p>`).join("")
        : '<p class="muted">مفيش كورس متسجل للمهارة دي لسه.</p>'}
    </div>`).join("");
  document.getElementById("feedDetail").innerHTML = `
    <div class="card">
      <h2>${esc(j.title)}</h2>
      <p class="muted">${esc(j.company)} · ${esc(j.location)}${j.posted_at ? " · " + esc(j.posted_at) : ""} · المصدر: <a href="${esc(j.source_site)}" target="_blank" rel="noopener">${esc(j.source_name)}</a></p>
      <p><span class="chip">${esc(j.field_label)}</span></p>
      ${j.n_skills ? `<p>نسبة التطابق: <b>${j.match_pct}%</b></p>${matchBar(j.match_pct)}
      <h4>مهاراتك المطابقة</h4><div class="chips">${have}</div>
      <h4>المهارات الناقصة</h4><div class="chips">${j.missing.map((s) => skillChip(s, "missing")).join("") || "مفيش، أنت جاهز ✅"}</div>`
      : '<p class="muted">الوظيفة دي مش من مجال المهارات التقنية اللي النظام بيحللها، اقرأ الوصف وقدّم من الرابط.</p>'}
      <p class="desc">${esc(j.description).slice(0, 1200)}...</p>
    </div>
    <h3>١) الكورسات المجانية اللي تسد الفجوة</h3>
    ${steps || (j.n_skills ? "<p>أنت مغطي كل مهارات الوظيفة دي.</p>" : "")}
    <h3>٢) قدّم على الوظيفة</h3>
    <div class="applybar"><a class="btn primary block" href="${esc(j.apply_url)}" target="_blank" rel="noopener">قدّم على الوظيفة ↗</a></div>`;
}

/* ---------- router ---------- */

const routes = {
  auth: showAuth,
  dashboard: showDashboard,
  courses: showCourses,
  jobs: showJobs,
  feed: showFeed,
  profile: showProfile,
};

let routeSeq = 0;
async function route() {
  const seq = ++routeSeq;
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
  if (page === "feed" && parts[1]) {
    try { await showFeedDetail(parts[1]); } catch (err) {
      if (err instanceof Stale || seq !== routeSeq) return;
      app.innerHTML = `<div class="page"><div class="card"><p class="error">${esc(err.message)}</p></div></div>`;
    }
    return;
  }
  if (page === "careers" && parts[1]) {
    try { await showCareer(parts[1]); } catch (err) {
      if (err instanceof Stale || seq !== routeSeq) return;
      if (state.token) app.innerHTML = `<div class="page"><div class="card"><p class="error">${esc(err.message)}</p></div></div>`;
    }
    return;
  }
  if (page === "jobs" && parts[1]) {
    try { await showJobDetail(parts[1]); } catch (err) {
      if (err instanceof Stale || seq !== routeSeq) return;
      if (state.token) app.innerHTML = `<div class="page"><div class="card"><p class="error">${esc(err.message)}</p></div></div>`;
    }
    return;
  }
  const view = routes[page] || showDashboard;
  try {
    await view();
  } catch (err) {
    if (err instanceof Stale || seq !== routeSeq) return;
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

window.addEventListener("unhandledrejection", (e) => {
  if (e.reason instanceof Stale) e.preventDefault();
});
window.addEventListener("hashchange", route);
route();
