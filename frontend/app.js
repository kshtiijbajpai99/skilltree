(() => {
  "use strict";

  const API = ""; // same-origin

  const CATEGORY_LABEL = {
    math: "Math",
    fundamentals: "Fundamentals",
    web: "Web Dev",
    "data-science": "Data Science",
    devops: "DevOps",
    systems: "Systems",
  };

  const state = {
    allSkills: [],       // [{id,name,category}]
    graphNodes: [],       // raw /api/graph rows
    knownIds: new Set(),
    network: null,
    nodesDataSet: null,
    edgesDataSet: null,
  };

  const el = (id) => document.getElementById(id);

  // -------------------------------------------------------------------
  // API helpers
  // -------------------------------------------------------------------
  async function apiGet(path) {
    const res = await fetch(API + path);
    if (!res.ok) {
      let message = `Request failed (${res.status})`;
      try {
        const body = await res.json();
        if (body.message) message = body.message;
      } catch (_) { /* ignore */ }
      const err = new Error(message);
      err.status = res.status;
      throw err;
    }
    return res.json();
  }

  // -------------------------------------------------------------------
  // Boot sequence
  // -------------------------------------------------------------------
  async function boot() {
    showLoading();
    if (typeof vis === "undefined") {
      setConnectionStatus(false, "Disconnected");
      showError(
        "The graph visualization library didn't load (lib/vis-network.min.js). " +
        "If you're viewing this inside an embedded/editor browser preview, try " +
        "opening http://localhost:8000 in a normal browser tab instead."
      );
      return;
    }
    try {
      const [health, skills, graphRows] = await Promise.all([
        apiGet("/api/health"),
        apiGet("/api/skills"),
        apiGet("/api/graph"),
      ]);
      setConnectionStatus(true, `${health.skills} skills · ${health.courses} courses`);
      state.allSkills = skills;
      state.graphNodes = graphRows;
      populateTargetSelect(skills);
      renderGraph(graphRows);
      hideLoading();
    } catch (err) {
      setConnectionStatus(false, "Disconnected");
      showError(err.message);
    }
  }

  function setConnectionStatus(ok, text) {
    const dot = el("status-dot");
    dot.classList.toggle("ok", ok);
    dot.classList.toggle("error", !ok);
    el("status-text").textContent = text;
  }

  function showLoading() {
    el("graph-loading").hidden = false;
    el("graph-error").hidden = true;
  }
  function hideLoading() {
    el("graph-loading").hidden = true;
  }
  function showError(message) {
    el("graph-loading").hidden = true;
    el("graph-error").hidden = false;
    el("graph-error-body").textContent =
      message || "Something went wrong talking to the API.";
  }

  el("retry-btn").addEventListener("click", boot);

  // -------------------------------------------------------------------
  // Graph rendering (vis-network)
  // -------------------------------------------------------------------
  function categoryBaseColor(category) {
    return "#4a5578"; // used only as a subtle border tint fallback
  }

  function nodeColorForState(nodeState) {
    switch (nodeState) {
      case "known": return { bg: "#35c58f", border: "#7fe8bf" };
      case "learnable": return { bg: "#e8b14d", border: "#f7d38f" };
      case "target": return { bg: "#7c9cff", border: "#b7c6ff" };
      default: return { bg: "#232b42", border: "#3a4360" };
    }
  }

  function computeNodeState(skillId, frontierIds, targetId) {
    if (skillId === targetId) return "target";
    if (state.knownIds.has(skillId)) return "known";
    if (frontierIds.has(skillId)) return "learnable";
    return "locked";
  }

  function renderGraph(rows) {
    const nodes = rows.map((r) => ({
      id: r.id,
      label: r.name,
      title: `${r.name} (${CATEGORY_LABEL[r.category] || r.category})`,
      shape: "dot",
      size: 12,
      font: { color: "#c7cbe0", size: 12, face: "Inter" },
      color: nodeColorForState("locked"),
    }));

    const edges = [];
    rows.forEach((r) => {
      (r.unlocks || []).forEach((toId) => {
        if (toId) edges.push({ from: r.id, to: toId, arrows: "to" });
      });
    });

    state.nodesDataSet = new vis.DataSet(nodes);
    state.edgesDataSet = new vis.DataSet(edges);

    const data = { nodes: state.nodesDataSet, edges: state.edgesDataSet };
    const options = {
      autoResize: true,
      physics: {
        solver: "forceAtlas2Based",
        forceAtlas2Based: { gravitationalConstant: -50, springLength: 90, springConstant: 0.06 },
        stabilization: { iterations: 120 },
      },
      edges: {
        color: { color: "#2a3350", highlight: "#e8b14d", opacity: 0.55 },
        smooth: { type: "continuous" },
        width: 1,
        arrows: { to: { enabled: true, scaleFactor: 0.4 } },
      },
      nodes: {
        borderWidth: 2,
        shadow: false,
      },
      interaction: { hover: true, tooltipDelay: 120 },
    };

    state.network = new vis.Network(el("graph-canvas"), data, options);
    state.network.on("click", (params) => {
      if (params.nodes.length > 0) {
        openDetail(params.nodes[0]);
      }
    });

    refreshNodeColors();
  }

  async function refreshNodeColors(targetId) {
    if (!state.nodesDataSet) return;
    let frontierIds = new Set();
    try {
      const known = Array.from(state.knownIds).join(",");
      const frontier = await apiGet(`/api/next?known=${encodeURIComponent(known)}`);
      frontierIds = new Set(frontier.map((f) => f.id));
      renderNextList(frontier);
    } catch (_) {
      // Non-fatal: color update / next-list is best-effort.
    }

    const updates = state.nodesDataSet.map((n) => {
      const st = computeNodeState(n.id, frontierIds, targetId);
      const c = nodeColorForState(st);
      return {
        id: n.id,
        color: { background: c.bg, border: c.border, highlight: c },
        size: st === "target" ? 16 : st === "known" ? 13 : 12,
      };
    });
    state.nodesDataSet.update(updates);
  }

  function renderNextList(frontier) {
    const container = el("next-list");
    if (!frontier.length) {
      container.innerHTML =
        '<p class="empty-note">Nothing new to unlock yet — add more known skills, or you\'ve mastered everything reachable!</p>';
      return;
    }
    container.innerHTML = "";
    frontier.slice(0, 8).forEach((s) => {
      const div = document.createElement("div");
      div.className = "next-card";
      div.innerHTML = `<div class="name">${escapeHtml(s.name)}</div><div class="cat">${CATEGORY_LABEL[s.category] || s.category}</div>`;
      div.addEventListener("click", () => openDetail(s.id));
      container.appendChild(div);
    });
  }

  // -------------------------------------------------------------------
  // Known-skills autocomplete + chips
  // -------------------------------------------------------------------
  const searchInput = el("known-search");
  const suggestionsBox = el("known-suggestions");

  searchInput.addEventListener("input", () => {
    const q = searchInput.value.trim().toLowerCase();
    if (!q) {
      suggestionsBox.hidden = true;
      return;
    }
    const matches = state.allSkills
      .filter((s) => !state.knownIds.has(s.id) && s.name.toLowerCase().includes(q))
      .slice(0, 8);
    if (!matches.length) {
      suggestionsBox.hidden = true;
      return;
    }
    suggestionsBox.innerHTML = "";
    matches.forEach((s) => {
      const item = document.createElement("div");
      item.className = "autocomplete-item";
      item.innerHTML = `<span>${escapeHtml(s.name)}</span><span class="cat">${CATEGORY_LABEL[s.category] || s.category}</span>`;
      item.addEventListener("click", () => addKnownSkill(s.id));
      suggestionsBox.appendChild(item);
    });
    suggestionsBox.hidden = false;
  });

  document.addEventListener("click", (e) => {
    if (!el("known-autocomplete").contains(e.target)) {
      suggestionsBox.hidden = true;
    }
  });

  function addKnownSkill(id) {
    state.knownIds.add(id);
    searchInput.value = "";
    suggestionsBox.hidden = true;
    renderChips();
    refreshNodeColors(el("target-select").value || undefined);
  }

  function removeKnownSkill(id) {
    state.knownIds.delete(id);
    renderChips();
    refreshNodeColors(el("target-select").value || undefined);
  }

  function renderChips() {
    const container = el("known-chips");
    container.innerHTML = "";
    Array.from(state.knownIds).forEach((id) => {
      const skill = state.allSkills.find((s) => s.id === id);
      if (!skill) return;
      const chip = document.createElement("span");
      chip.className = "chip";
      chip.innerHTML = `${escapeHtml(skill.name)} <button aria-label="Remove ${escapeHtml(skill.name)}">✕</button>`;
      chip.querySelector("button").addEventListener("click", () => removeKnownSkill(id));
      container.appendChild(chip);
    });
    el("find-path-btn").disabled = !el("target-select").value;
  }

  // -------------------------------------------------------------------
  // Target select + path drawer
  // -------------------------------------------------------------------
  function populateTargetSelect(skills) {
    const select = el("target-select");
    const grouped = {};
    skills.forEach((s) => {
      grouped[s.category] = grouped[s.category] || [];
      grouped[s.category].push(s);
    });
    Object.keys(grouped).sort().forEach((cat) => {
      const group = document.createElement("optgroup");
      group.label = CATEGORY_LABEL[cat] || cat;
      grouped[cat].forEach((s) => {
        const opt = document.createElement("option");
        opt.value = s.id;
        opt.textContent = s.name;
        group.appendChild(opt);
      });
      select.appendChild(group);
    });
  }

  el("target-select").addEventListener("change", (e) => {
    el("find-path-btn").disabled = !e.target.value;
    refreshNodeColors(e.target.value || undefined);
  });

  el("find-path-btn").addEventListener("click", async () => {
    const target = el("target-select").value;
    if (!target) return;
    const btn = el("find-path-btn");
    btn.disabled = true;
    btn.textContent = "Plotting…";
    try {
      const known = Array.from(state.knownIds).join(",");
      const result = await apiGet(`/api/path?known=${encodeURIComponent(known)}&target=${encodeURIComponent(target)}`);
      renderPathDrawer(result);
      highlightPath(result);
    } catch (err) {
      renderPathDrawer(null, err.message);
    } finally {
      btn.disabled = false;
      btn.textContent = "Plot my path";
    }
  });

  function renderPathDrawer(result, errorMessage) {
    const drawer = el("path-drawer");
    const body = el("path-drawer-body");
    drawer.hidden = false;
    body.innerHTML = "";

    if (errorMessage) {
      body.innerHTML = `<p class="path-empty-note" style="color:#e8735a;background:#3a2420;border-color:#e8735a;">${escapeHtml(errorMessage)}</p>`;
      return;
    }

    if (result.already_known) {
      body.innerHTML = `<p class="path-empty-note">You already know this skill — nothing left to plot.</p>`;
      return;
    }

    if (!result.steps.length) {
      body.innerHTML = `<p class="path-empty-note">No path found — this skill may have no recorded prerequisites.</p>`;
      return;
    }

    const summary = document.createElement("div");
    summary.className = "path-summary";
    const totalHours = result.steps.reduce((sum, s) => sum + (s.course ? s.course.duration_hours || 0 : 0), 0);
    summary.textContent = `${result.steps.length} skills to learn · ~${totalHours}h of coursework`;
    body.appendChild(summary);

    result.steps.forEach((step, i) => {
      const row = document.createElement("div");
      row.className = "path-step";
      const courseHtml = step.course
        ? `<div class="step-course">${escapeHtml(step.course.title)} <span class="provider">— ${escapeHtml(step.course.provider)}, ${step.course.duration_hours}h</span></div>`
        : `<div class="step-course">No course found for this skill yet</div>`;
      row.innerHTML = `
        <div class="step-index">${i + 1}</div>
        <div class="step-body">
          <div class="step-name">${escapeHtml(step.skill.name)}</div>
          ${courseHtml}
        </div>`;
      body.appendChild(row);
    });
  }

  el("close-path-drawer").addEventListener("click", () => {
    el("path-drawer").hidden = true;
  });

  function highlightPath(result) {
    if (!result || !result.steps || !state.edgesDataSet) return;
    const pathIds = new Set(result.steps.map((s) => s.skill.id));
    pathIds.add(result.target);
    const updates = state.edgesDataSet.map((e) => ({
      id: e.id,
      color: pathIds.has(e.from) && pathIds.has(e.to)
        ? { color: "#e8b14d", opacity: 1 }
        : { color: "#2a3350", opacity: 0.35 },
      width: pathIds.has(e.from) && pathIds.has(e.to) ? 2.5 : 1,
    }));
    state.edgesDataSet.update(updates);
    refreshNodeColors(result.target);
  }

  // -------------------------------------------------------------------
  // Detail panel
  // -------------------------------------------------------------------
  async function openDetail(skillId) {
    el("detail-empty").hidden = true;
    const content = el("detail-content");
    content.hidden = false;
    content.innerHTML = '<p class="detail-none">Loading…</p>';
    try {
      const d = await apiGet(`/api/skill/${encodeURIComponent(skillId)}`);
      const prereqHtml = d.prerequisites.length
        ? `<ul>${d.prerequisites.map((p) => `<li>${escapeHtml(p.name)}</li>`).join("")}</ul>`
        : '<p class="detail-none">No prerequisites — this is a starting point.</p>';
      const unlocksHtml = d.unlocks.length
        ? `<ul>${d.unlocks.map((u) => `<li>${escapeHtml(u.name)}</li>`).join("")}</ul>`
        : '<p class="detail-none">Doesn\'t unlock anything further (yet).</p>';
      const coursesHtml = d.courses.length
        ? `<ul>${d.courses.map((c) => `<li class="course"><span class="title">${escapeHtml(c.title)}</span><span>${escapeHtml(c.provider)}</span></li>`).join("")}</ul>`
        : '<p class="detail-none">No course indexed for this skill yet.</p>';

      content.innerHTML = `
        <div class="cat-tag">${CATEGORY_LABEL[d.category] || d.category}</div>
        <h3>${escapeHtml(d.name)}</h3>
        <p class="desc">${escapeHtml(d.description || "")}</p>
        <div class="detail-section"><h4>Requires first</h4>${prereqHtml}</div>
        <div class="detail-section"><h4>Unlocks</h4>${unlocksHtml}</div>
        <div class="detail-section"><h4>Courses</h4>${coursesHtml}</div>
      `;
    } catch (err) {
      content.innerHTML = `<p class="detail-none">Couldn't load this skill: ${escapeHtml(err.message)}</p>`;
    }
  }

  // -------------------------------------------------------------------
  // Utilities
  // -------------------------------------------------------------------
  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str == null ? "" : String(str);
    return div.innerHTML;
  }

  boot();
})();
