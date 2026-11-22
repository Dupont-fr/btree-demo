const API = "/api/apply";
let treeType = "bst"; // bst | rb
let currentTree = null;
let selectedKey = null;
let steps = [];
let stepIndex = 0;

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
  } else {
    steps = [];
    stepIndex = 0;
    $("stepCounter").textContent = "0 / 0";
    $("stepList").innerHTML = "";
    $("stepMessage").textContent = data.message || "Operation terminee.";
    renderTree(currentTree);
  }
  return data;
}

function showStep(i) {
  if (!steps.length) return;
  if (i < 0) i = 0;
  if (i >= steps.length) i = steps.length - 1;
  stepIndex = i;
  const s = steps[i];
  $("stepCounter").textContent = (i + 1) + " / " + steps.length;
  $("stepMessage").textContent = s.message;
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
  const R = 20;
  const H = 56;
  const GAP = 12;
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
  const unit = R * 2 + GAP;
  const width = totalUnits * unit + 40;
  const height = (maxDepth(snap) + 1) * H + 40;
  svg.setAttribute("width", width);
  svg.setAttribute("height", height);

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
document.querySelectorAll(".btn-grid button").forEach((btn) => {
  btn.addEventListener("click", () => {
    const op = btn.getAttribute("data-op");
    const v = $("valueInput").value.trim();
    if (["insert","delete","search","succ","pred","rotate_left","rotate_right"].includes(op) && v === "") {
      $("stepMessage").textContent = "Veuillez saisir une valeur.";
      return;
    }
    call(op, v === "" ? null : v);
  });
});

$("btnTypeBst").addEventListener("click", () => setType("bst"));
$("btnTypeRb").addEventListener("click", () => setType("rb"));

$("btnBfs").addEventListener("click", () => call("bfs"));
$("btnDfs").addEventListener("click", () => call("traversals_all"));
$("btnValidate").addEventListener("click", () => call("validate"));
$("btnExample").addEventListener("click", () => call("example"));
$("btnReset").addEventListener("click", () => call("reset"));

$("prevStep").addEventListener("click", () => { if (steps.length) showStep(stepIndex - 1); });
$("nextStep").addEventListener("click", () => { if (steps.length) showStep(stepIndex + 1); });
$("finishSteps").addEventListener("click", () => {
  steps = [];
  stepIndex = 0;
  $("stepCounter").textContent = "0 / 0";
  $("stepList").innerHTML = "";
  $("stepMessage").textContent = "Visualisation de l'arbre final.";
  renderTree(currentTree);
});

// init
setType("bst");
