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


/* ---------- live feed (daily jobs + linked free courses) ---------- */

const feedState = { source: "", offset: 0 };

function minutesLabel(m) {
  if (!m) return "";
  return m >= 60 ? Math.round(m / 60) + " ساعة" : m + " دقيقة";
}

function freeBadge(f) {
  return f === "audit"
    ? '<span class="chip" title="مجاني للمشاهدة، الشهادة مدفوعة">مجاني (Audit)</span>'
    : '<span class="chip have">مجاني</span>';
}

function feedCard(j) {
  const miss = j.missing.slice(0, 4).map((s) => skillChip(s, "missing")).join("");
  return `<div class="card job-card" onclick="location.hash='#/feed/${j.id}'">
    <h3>${esc(j.title)}</h3>
    <p class="muted">${esc(j.company)} · ${esc(j.location)}${j.posted_at ? " · " + esc(j.posted_at) : ""}</p>
    <p><span class="chip">${esc(j.source_name)}</span></p>
    <p>نسبة التطابق: <b>${j.match_pct}%</b></p>${matchBar(j.match_pct)}
    <div class="chips">${miss}</div>
  </div>`;
}

async function loadFeed(append) {
  const q = document.getElementById("feedQ").value.trim();
  const sort = document.getElementById("feedSort").value;
  const limit = 24;
  if (!append) feedState.offset = 0;
  const params = new URLSearchParams({ q, sort, limit, offset: feedState.offset });
  if (feedState.source) params.set("source", feedState.source);
  const data = await api("/feed/jobs?" + params.toString());
  const list = document.getElementById("feedList");
  const html = data.jobs.map(feedCard).join("");
  if (append) list.insertAdjacentHTML("beforeend", html);
  else list.innerHTML = html || '<p class="muted">لسه مفيش وظائف، البيانات بتتحمّل... جرّب بعد دقيقة.</p>';
  feedState.offset += data.jobs.length;
  const more = document.getElementById("feedMore");
  more.innerHTML = feedState.offset < data.total
    ? `<button class="btn primary" id="feedMoreBtn">عرض المزيد (${data.total - feedState.offset})</button>` : "";
  const btn = document.getElementById("feedMoreBtn");
  if (btn) btn.onclick = () => loadFeed(true);
}

async function showFeed() {
  showNav("feed");
  render("tpl-feed");
  const st = await api("/feed/status");
  const when = st.last_refresh_utc ? st.last_refresh_utc + " UTC" : "لسه";
  document.getElementById("feedStatus").textContent = st.total_jobs
    ? `${st.total_jobs} وظيفة من ${st.job_sources.length} مصادر، و${st.total_courses} كورس مجاني. آخر تحديث: ${when}. بيتحدث تلقائيًا كل 24 ساعة.`
    : (st.refreshing ? "بنحمّل وظائف النهارده من المصادر... استنى دقيقة وحدّث الصفحة." : "جاري التحضير...");
  const chips = ['<span class="chip" data-s="" style="cursor:pointer">الكل</span>']
    .concat(st.job_sources.map((s) => `<span class="chip" data-s="${esc(s.source)}" style="cursor:pointer">${esc(s.name)} (${s.count})</span>`));
  const box = document.getElementById("feedSources");
  box.innerHTML = chips.join("");
  const mark = () => box.querySelectorAll(".chip").forEach((c) => c.classList.toggle("have", c.dataset.s === feedState.source));
  box.onclick = (e) => {
    if (e.target.dataset && e.target.dataset.s !== undefined) {
      feedState.source = e.target.dataset.s; mark(); loadFeed(false);
    }
  };
  mark();
  document.getElementById("feedSourcesInfo").innerHTML =
    "<ul>" + st.job_sources.concat(st.course_sources).map((s) =>
      `<li><a href="${esc(s.site)}" target="_blank" rel="noopener">${esc(s.name)}</a> (${s.count})${s.note ? " - " + esc(s.note) : ""}</li>`).join("") +
    "</ul><p>الوظائف دي من مصادر عامة بتسمح بالاستخدام، ومش من Wuzzuf أو LinkedIn لأنهم مفيهمش واجهة مجانية رسمية. معظمها ريموت وبيقبل من مصر، لكن اقرأ شرط الموقع قبل التقديم. بيانات الخدمة المجانية بتتحمّل من جديد مع كل تشغيل.</p>";
  let timer;
  document.getElementById("feedQ").oninput = () => { clearTimeout(timer); timer = setTimeout(() => loadFeed(false), 350); };
  document.getElementById("feedSort").onchange = () => loadFeed(false);
  await loadFeed(false);
}

async function showFeedDetail(id) {
  showNav("feed");
  render("tpl-feed-detail");
  const { job: j } = await api("/feed/jobs/" + id);
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
      <p>نسبة التطابق: <b>${j.match_pct}%</b></p>${matchBar(j.match_pct)}
      <h4>مهاراتك المطابقة</h4><div class="chips">${have}</div>
      <h4>المهارات الناقصة</h4><div class="chips">${j.missing.map((s) => skillChip(s, "missing")).join("") || "مفيش، أنت جاهز ✅"}</div>
      <p>${esc(j.description).slice(0, 700)}...</p>
    </div>
    <h3>١) الكورسات المجانية اللي تسد الفجوة</h3>
    ${steps || "<p>أنت مغطي كل مهارات الوظيفة دي.</p>"}
    <h3>٢) قدّم على الوظيفة</h3>
    <p><a class="btn primary" href="${esc(j.apply_url)}" target="_blank" rel="noopener">قدّم على ${esc(j.source_name)} ↗</a></p>`;
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
  if (page === "feed" && parts[1]) {
    try { await showFeedDetail(parts[1]); } catch (err) {
      app.innerHTML = `<div class="page"><div class="card"><p class="error">${esc(err.message)}</p></div></div>`;
    }
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
