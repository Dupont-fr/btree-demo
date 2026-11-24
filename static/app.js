const API = "/api/apply";
let treeType = "bst"; // bst | rb
let currentTree = null;
let selectedKey = null;
let steps = [];
let stepIndex = 0;
let playTimer = null;

const $ = (id) => document.getElementById(id);

function setType(t) {
  treeType = t;
  $("btnTypeBst").classList.toggle("active", t === "bst");
  $("btnTypeRb").classList.toggle("active", t === "rb");
  // reset
  currentTree = null;
  steps = [];
  stepIndex = 0;
  renderTree(null);
  updateStats(null);
  $("stepMessage").textContent = "Aucune operation.";
  $("stepList").innerHTML = "";
  $("stepCounter").textContent = "0 / 0";
  $("violations").textContent = "";
  $("result").textContent = "";
}

async function call(op, value = null, tree = currentTree) {
  const body = { type: treeType, op, tree };
  if (value !== null && value !== undefined && value !== "") body.value = value;
  let res;
  try {
    res = await fetch(API, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  } catch (e) {
    $("stepMessage").textContent = "Erreur reseau: " + e;
    return null;
  }
  const data = await res.json();
  if (!data.ok) {
    $("stepMessage").textContent = "Erreur: " + (data.error || "inconnue");
    return null;
  }
  if (data.tree !== undefined) currentTree = data.tree;
  if (data.stats) updateStats(data.stats);
  if (data.violations) {
    $("violations").textContent = data.violations.join("\n");
  } else {
    $("violations").textContent = "";
  }
  if (data.result !== null && data.result !== undefined) {
    if (Array.isArray(data.result)) {
      $("result").textContent = "Resultat: " + data.result.join(", ");
    } else if (typeof data.result === "object") {
      const parts = [];
      for (const k in data.result) parts.push(k + ": " + data.result[k].join(", "));
      $("result").textContent = "Resultats: " + parts.join(" | ");
    } else {
      $("result").textContent = "Resultat: " + data.result;
    }
  } else if (data.message) {
    $("result").textContent = data.message;
  } else {
    $("result").textContent = "";
  }
  if (data.steps && data.steps.length) {
    steps = data.steps;
    stepIndex = 0;
    showStep(0);
    // Auto-play the detailed steps, ending on the final state.
    if (playTimer) clearTimeout(playTimer);
    let i = 0;
    const advance = () => {
      if (i < steps.length - 1) {
        i++;
        showStep(i);
        playTimer = setTimeout(advance, 700);
      } else {
        playTimer = null;
      }
    };
    if (steps.length > 1) playTimer = setTimeout(advance, 700);
  } else {
    steps = [];
    stepIndex = 0;
    $("stepCounter").textContent = "0 / 0";
    $("stepList").innerHTML = "";
    $("stepMessage").textContent = data.message || "Operation terminee.";
    const vsm = $("vizStepMsg");
    if (vsm) vsm.textContent = data.message || "Operation terminee.";
    renderTree(currentTree);
  }
  if (window.innerWidth < 900) {
    activateTab("viz");
    const panel = document.getElementById("tab-viz");
    if (panel) panel.scrollIntoView({ behavior: "smooth", block: "start" });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
  return data;
}

function activateTab(name) {
  document.querySelectorAll(".tab").forEach((x) => x.classList.remove("active"));
  document.querySelectorAll(".tab-panel").forEach((x) => x.classList.remove("active"));
  const t = document.querySelector('.tab[data-tab="' + name + '"]');
  if (t) t.classList.add("active");
  const p = document.getElementById("tab-" + name);
  if (p) p.classList.add("active");
}

function showStep(i) {
  if (!steps.length) return;
  if (i < 0) i = 0;
  if (i >= steps.length) i = steps.length - 1;
  stepIndex = i;
  const s = steps[i];
  $("stepCounter").textContent = (i + 1) + " / " + steps.length;
  $("stepMessage").textContent = s.message;
  const vsm = $("vizStepMsg");
  if (vsm) vsm.textContent = s.message;
  renderTree(s.tree, s.highlight || []);
  // list
  const ol = $("stepList");
  ol.innerHTML = "";
  steps.forEach((st, idx) => {
    const li = document.createElement("li");
    li.textContent = (idx + 1) + ". " + st.message;
    if (idx === i) li.classList.add("active");
    li.addEventListener("click", () => showStep(idx));
    ol.appendChild(li);
  });
  const active = ol.querySelector("li.active");
  if (active) active.scrollIntoView({ block: "nearest" });
}

function renderTree(snap, highlight) {
  highlight = highlight || [];
  const svg = $("treeSvg");
  svg.innerHTML = "";
  if (!snap) {
    svg.setAttribute("width", "100%");
    svg.setAttribute("height", "200");
    return;
  }
  const wrap = $("svgWrap");
  const avail = Math.max(280, (wrap ? wrap.clientWidth : window.innerWidth) - 24);
  // compute layout
  function assign(node, depth, xStart) {
    if (!node) return 0;
    const lw = assign(node.left, depth + 1, xStart);
    node._x = xStart + lw + 0.5;
    node._y = depth;
    const rw = assign(node.right, depth + 1, xStart + lw + 1);
    return lw + 1 + rw;
  }
  const totalUnits = assign(snap, 0, 0);
  const md = maxDepth(snap);
  // Fit to available width: scale unit, keeping a minimum node size.
  let unit = 44;
  if (totalUnits * unit + 40 > avail) {
    unit = Math.max(26, (avail - 40) / Math.max(1, totalUnits));
  }
  const R = Math.max(12, Math.min(20, unit * 0.42));
  const H = Math.max(44, R * 2.6);
  const GAP = Math.max(4, unit - R * 2);
  const width = totalUnits * unit + 40;
  const height = (md + 1) * H + 40;
  svg.setAttribute("width", "100%");
  svg.setAttribute("height", height);
  svg.setAttribute("viewBox", "0 0 " + width + " " + height);
  svg.style.maxWidth = width + "px";

  // center
  const offsetX = 20;
  const offsetY = 30;

  // draw edges first
  function drawEdges(node) {
    if (!node) return;
    const x = offsetX + node._x * unit;
    const y = offsetY + node._y * H;
    if (node.left) {
      const cx = offsetX + node.left._x * unit;
      const cy = offsetY + node.left._y * H;
      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      line.setAttribute("x1", x);
      line.setAttribute("y1", y + R);
      line.setAttribute("x2", cx);
      line.setAttribute("y2", cy - R);
      line.setAttribute("stroke", "#9ca3af");
      line.setAttribute("stroke-width", "2");
      svg.appendChild(line);
      drawEdges(node.left);
    }
    if (node.right) {
      const cx = offsetX + node.right._x * unit;
      const cy = offsetY + node.right._y * H;
      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      line.setAttribute("x1", x);
      line.setAttribute("y1", y + R);
      line.setAttribute("x2", cx);
      line.setAttribute("y2", cy - R);
      line.setAttribute("stroke", "#9ca3af");
      line.setAttribute("stroke-width", "2");
      svg.appendChild(line);
      drawEdges(node.right);
    }
  }
  drawEdges(snap);

  // draw nodes
  function drawNodes(node) {
    if (!node) return;
    const x = offsetX + node._x * unit;
    const y = offsetY + node._y * H;
    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
    g.style.cursor = "pointer";
    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", x);
    circle.setAttribute("cy", y);
    circle.setAttribute("r", R);
    const isRed = (node.color === "red");
    circle.setAttribute("fill", isRed ? "#ef4444" : "#1f2937");
    circle.setAttribute("stroke", highlight.includes(node.key) ? "#fbbf24" : (selectedKey === node.key ? "#3b82f6" : "#fff"));
    circle.setAttribute("stroke-width", highlight.includes(node.key) ? "4" : "2");
    g.appendChild(circle);
    const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
    text.setAttribute("x", x);
    text.setAttribute("y", y + 5);
    text.setAttribute("text-anchor", "middle");
    text.setAttribute("fill", "#fff");
    text.setAttribute("font-size", "13");
    text.setAttribute("font-weight", "600");
    text.textContent = node.key;
    g.appendChild(text);
    g.addEventListener("click", () => {
      selectedKey = node.key;
      $("valueInput").value = node.key;
      $("selectedNode").textContent = node.key;
      renderTree(currentTree, (steps.length ? steps[stepIndex].highlight : []));
    });
    svg.appendChild(g);
    drawNodes(node.left);
    drawNodes(node.right);
  }
  drawNodes(snap);
}

function maxDepth(node) {
  if (!node) return 0;
  return 1 + Math.max(maxDepth(node.left), maxDepth(node.right));
}

function updateStats(s) {
  if (!s) { $("stats").textContent = ""; return; }
  const lines = [];
  lines.push("Type: " + (s.type === "bst" ? "ABR" : "ARN"));
  lines.push("Noeuds: " + s.count);
  lines.push("Hauteur: " + s.height);
  if (s.black_height !== undefined) lines.push("Hauteur noire: " + s.black_height);
  if (s.min !== null && s.min !== undefined) lines.push("Min: " + s.min + "  Max: " + s.max);
  $("stats").textContent = lines.join("\n");
}

// event wiring
function scrollToViz() {
  if (window.innerWidth >= 900) return;
  activateTab("viz");
  const panel = document.getElementById("tab-viz") || document.querySelector(".content");
  if (panel) panel.scrollIntoView({ behavior: "auto", block: "start" });
  window.scrollTo({ top: 0, behavior: "auto" });
}
document.querySelectorAll(".btn-grid button, .row.small button").forEach((btn) => {
  btn.addEventListener("click", () => {
    scrollToViz();
    const op = btn.getAttribute("data-op");
    const v = $("valueInput").value.trim();
    if (["insert","delete","search","succ","pred","rotate_left","rotate_right"].includes(op) && v === "") {
      $("stepMessage").textContent = "Veuillez saisir une valeur.";
      return;
    }
    call(op, v === "" ? null : v);
  });
});

$("btnTypeBst").addEventListener("click", () => { scrollToViz(); setType("bst"); });
$("btnTypeRb").addEventListener("click", () => { scrollToViz(); setType("rb"); });

$("btnBfs").addEventListener("click", () => { scrollToViz(); call("bfs"); });
$("btnDfs").addEventListener("click", () => { scrollToViz(); call("traversals_all"); });
$("btnValidate").addEventListener("click", () => { scrollToViz(); call("validate"); });
$("btnExample").addEventListener("click", () => { scrollToViz(); call("example"); });
$("btnReset").addEventListener("click", () => { scrollToViz(); call("reset"); });

$("prevStep").addEventListener("click", () => { if (playTimer) { clearTimeout(playTimer); playTimer = null; } if (steps.length) showStep(stepIndex - 1); });
$("nextStep").addEventListener("click", () => { if (playTimer) { clearTimeout(playTimer); playTimer = null; } if (steps.length) showStep(stepIndex + 1); });
$("finishSteps").addEventListener("click", () => {
  if (playTimer) { clearTimeout(playTimer); playTimer = null; }
  steps = [];
  stepIndex = 0;
  $("stepCounter").textContent = "0 / 0";
  $("stepList").innerHTML = "";
  $("stepMessage").textContent = "Visualisation de l'arbre final.";
  renderTree(currentTree);
});

// ---- Reviews ----
async function loadReviews() {
  try {
    const res = await fetch("/api/reviews");
    const data = await res.json();
    if (data.ok) renderReviews(data.reviews || []);
  } catch (e) {}
}
function renderReviews(list) {
  const el = $("reviewsList");
  if (!el) return;
  if (!list.length) { el.innerHTML = "<p style='color:var(--muted);font-size:0.85rem;'>Aucun avis pour le moment. Soyez le premier !</p>"; return; }
  el.innerHTML = list.map((r) => `
    <div class="review-item">
      <div class="review-head">
        <span class="review-name">${escapeHtml(r.name)}</span>
        <span>${r.date || ""}</span>
      </div>
      <div class="review-msg">${escapeHtml(r.message)}</div>
    </div>
  `).join("");
}
function escapeHtml(s) { return String(s).replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }

async function submitReview() {
  const name = $("reviewName").value.trim();
  const message = $("reviewMessage").value.trim();
  if (!name || !message) { alert("Nom et message requis."); return; }
  try {
    const res = await fetch("/api/reviews", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name, message }) });
    const data = await res.json();
    if (data.ok) {
      $("reviewName").value = "";
      $("reviewMessage").value = "";
      renderReviews(data.reviews || []);
      localStorage.setItem("hasReviewed", "1");
      hideReviewModal();
      alert("Merci pour votre avis !");
    } else {
      alert("Erreur: " + (data.error || "inconnue"));
    }
  } catch (e) { alert("Erreur réseau"); }
}

function showReviewModal() {
  const m = $("reviewModal");
  if (m) m.style.display = "flex";
}
function hideReviewModal() {
  const m = $("reviewModal");
  if (m) m.style.display = "none";
}

// Floating button
document.addEventListener("DOMContentLoaded", () => {
  const btn = $("floatingReviewBtn");
  if (btn) btn.addEventListener("click", () => { showReviewModal(); /* scroll to reviews tab */ });
  const submit = $("submitReview");
  if (submit) submit.addEventListener("click", submitReview);
  const modalReview = $("modalReviewBtn");
  if (modalReview) modalReview.addEventListener("click", () => {
    hideReviewModal();
    // switch to reviews tab
    document.querySelectorAll(".tab").forEach((x) => x.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((x) => x.classList.remove("active"));
    const t = document.querySelector('.tab[data-tab="reviews"]');
    if (t) t.classList.add("active");
    const p = document.getElementById("tab-reviews");
    if (p) p.classList.add("active");
    const nameInput = $("reviewName");
    if (nameInput) nameInput.focus();
  });
  const modalLater = $("modalLaterBtn");
  if (modalLater) modalLater.addEventListener("click", hideReviewModal);
  loadReviews();
  // Prompt if not reviewed
  if (!localStorage.getItem("hasReviewed")) {
    setTimeout(() => {
      if (!localStorage.getItem("hasReviewed")) showReviewModal();
    }, 8000);
  }
});

// tabs
document.querySelectorAll(".tab").forEach((t) => {
  t.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((x) => x.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((x) => x.classList.remove("active"));
    t.classList.add("active");
    const panel = document.getElementById("tab-" + t.getAttribute("data-tab"));
    if (panel) panel.classList.add("active");
  });
});

// init
setType("bst");
