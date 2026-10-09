const categories = [
  "VLAN_ASSIGNMENT", "TRUNK_VLAN", "SUBNET_MASK", "DEFAULT_GATEWAY",
  "INTERFACE_SHUTDOWN", "STATIC_ROUTE", "ACL", "NAT", "IP_ADDRESS",
  "DUPLEX_SPEED", "STP", "DHCP", "DNS", "PORT_SECURITY", "OTHER",
];

const state = { cases: [], selectedCaseId: "", diagnosis: null, evaluation: null, decision: "Accepted", dashboard: null };
const byId = (id) => document.getElementById(id);
const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
const selectedCase = () => state.cases.find((item) => item.case_id === state.selectedCaseId);

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.error || `Request failed (${response.status})`);
  return body;
}

function showAlert(message) {
  const alert = byId("app-alert");
  alert.textContent = message;
  alert.classList.remove("hidden");
}
function clearAlert() {
  byId("app-alert").classList.add("hidden");
  byId("app-alert").textContent = "";
}

function setPage(page) {
  const isDashboard = page === "dashboard";
  byId("diagnose-page").classList.toggle("hidden", isDashboard);
  byId("dashboard-page").classList.toggle("hidden", !isDashboard);
  byId("breadcrumb-current").textContent = isDashboard ? "Operational analytics" : "Incident diagnosis";
  document.querySelectorAll(".nav-item").forEach((item) => item.classList.toggle("active", item.dataset.page === page));
  if (isDashboard) loadDashboard();
}

function renderCase() {
  const item = selectedCase();
  if (!item) return;
  state.diagnosis = null;
  state.evaluation = null;
  byId("diagnosis-result").classList.add("hidden");
  byId("diagnosis-empty").classList.remove("hidden");
  byId("diagnosis-loading").classList.add("hidden");
  byId("review-saved").classList.add("hidden");
  clearAlert();
  byId("case-type").textContent = item.issue_type || "Network incident";
  const severity = item.severity || "Unspecified";
  byId("case-severity").textContent = severity;
  byId("severity-tag").textContent = `${severity.toUpperCase()} SEVERITY`;
  byId("severity-tag").className = `tag tag-${severity.toLowerCase() === "high" || severity.toLowerCase() === "critical" ? "high" : severity.toLowerCase() === "medium" ? "medium" : "low"}`;
  byId("case-symptom").textContent = item.symptom || "No symptom provided.";
  byId("case-topology").textContent = item.topology_note || "No topology notes supplied.";
  byId("case-command").textContent = item.show_command || "No diagnostic command supplied.";
  byId("case-output").textContent = item.show_command_output || "No command output supplied.";
  byId("case-verification").textContent = item.verification_result || "No verification result supplied.";
}

function fillDiagnosis(diagnosis, evaluation) {
  const status = evaluation.evaluation_status || "Needs Review";
  const banner = byId("result-banner");
  banner.classList.toggle("warning", status === "Needs Review");
  banner.classList.toggle("incorrect", status === "Incorrect");
  byId("result-status-title").textContent = status === "Correct" ? "Evidence aligned" : status === "Incorrect" ? "Review this diagnosis" : "Diagnosis needs review";
  byId("result-status-copy").textContent = `${evaluation.expected_category || "Expected category unavailable"} expected · human review required`;
  byId("result-category").textContent = diagnosis.fault_category || "OTHER";
  byId("result-osi").textContent = diagnosis.osi_layer || "OSI layer not specified";
  byId("result-root-cause").textContent = diagnosis.root_cause || "No root cause returned.";
  byId("result-concept").textContent = diagnosis.networking_concept || "Not specified";
  byId("result-evidence-text").textContent = diagnosis.evidence || "No supporting evidence returned.";
  byId("result-command").textContent = diagnosis.next_command || "No next command suggested.";
  byId("result-fix").textContent = diagnosis.fix_steps || "No corrective action returned.";
  const confidence = Number(diagnosis.confidence);
  byId("confidence-pill").textContent = Number.isFinite(confidence) ? `${Math.round(confidence * 100)}% confidence` : "Confidence unavailable";
  byId("diagnosis-empty").classList.add("hidden");
  byId("diagnosis-loading").classList.add("hidden");
  byId("diagnosis-result").classList.remove("hidden");
}

async function diagnose() {
  if (!state.selectedCaseId) return;
  clearAlert();
  byId("diagnose-button").disabled = true;
  byId("diagnosis-empty").classList.add("hidden");
  byId("diagnosis-result").classList.add("hidden");
  byId("diagnosis-loading").classList.remove("hidden");
  try {
    const result = await api("/api/diagnose", { method: "POST", body: JSON.stringify({ case_id: state.selectedCaseId }) });
    state.diagnosis = result.diagnosis;
    state.evaluation = result.evaluation;
    fillDiagnosis(result.diagnosis, result.evaluation);
  } catch (error) {
    byId("diagnosis-loading").classList.add("hidden");
    byId("diagnosis-empty").classList.remove("hidden");
    showAlert(`AI diagnosis failed: ${error.message}`);
  } finally {
    byId("diagnose-button").disabled = false;
  }
}

function renderCategoryChart(counts) {
  const entries = Object.entries(counts || {}).sort((a, b) => b[1] - a[1]);
  const max = Math.max(1, ...entries.map(([, value]) => value));
  byId("category-chart").innerHTML = entries.length ? entries.map(([name, value]) => `
    <div class="bar-row"><span class="bar-name" title="${escapeHtml(name)}">${escapeHtml(name)}</span><div class="bar-track"><div class="bar-fill" style="width:${Math.max(2, value / max * 100)}%"></div></div><span class="bar-value">${value}</span></div>
  `).join("") : '<div class="empty-table">No category data.</div>';
}

function renderStatusChart(counts, total) {
  const values = [counts?.Correct || 0, counts?.Incorrect || 0, counts?.["Needs Review"] || 0];
  const colors = ["stack-correct", "stack-incorrect", "stack-review"];
  byId("status-chart").innerHTML = `
    <div class="status-summary"><span>Cases evaluated</span><strong>${total}</strong></div>
    <div class="stacked-track">${values.map((value, i) => `<span class="${colors[i]}" style="width:${total ? value / total * 100 : 0}%"></span>`).join("")}</div>
    <div class="status-legend"><span><i class="legend-dot legend-correct"></i>Correct ${values[0]}</span><span><i class="legend-dot legend-incorrect"></i>Incorrect ${values[1]}</span><span><i class="legend-dot legend-review"></i>Needs review ${values[2]}</span></div>
  `;
}

function outcomeClass(status) {
  return status === "Correct" ? "outcome-correct" : status === "Incorrect" ? "outcome-incorrect" : "outcome-review";
}

function renderCaseTable() {
  if (!state.dashboard) return;
  const filter = byId("status-filter").value;
  const search = byId("case-search").value.trim().toLowerCase();
  const rows = state.dashboard.cases.filter((item) => {
    const matchesStatus = filter === "all" || item.evaluation_status === filter;
    const matchesSearch = `${item.case_id} ${item.issue_type} ${item.expected_category} ${item.ai_predicted_category}`.toLowerCase().includes(search);
    return matchesStatus && matchesSearch;
  });
  byId("case-table-body").innerHTML = rows.length ? rows.map((item) => `
    <tr data-case-id="${escapeHtml(item.case_id)}" title="Open case in diagnosis">
      <td class="case-id-cell">${escapeHtml(item.case_id)}</td><td>${escapeHtml(item.issue_type || "—")}</td>
      <td><span class="severity-cell ${escapeHtml((item.severity || "").toLowerCase())}">${escapeHtml(item.severity || "—")}</span></td>
      <td>${escapeHtml(item.expected_category || "—")}</td><td>${escapeHtml(item.ai_predicted_category || "—")}</td>
      <td><span class="outcome-badge ${outcomeClass(item.evaluation_status)}">${escapeHtml(item.evaluation_status)}</span></td>
    </tr>
  `).join("") : '<tr><td class="empty-table" colspan="6">No cases match these filters.</td></tr>';
}

function renderCorrections(reviews) {
  const edits = (reviews || []).filter((item) => item.decision === "Edited");
  byId("correction-count").textContent = `${edits.length} CORRECTION${edits.length === 1 ? "" : "S"}`;
  byId("corrections-content").innerHTML = edits.length ? edits.slice().reverse().map((item) => `
    <div class="correction-row"><strong>${escapeHtml(item.case_id)}</strong><span>Model: ${escapeHtml(item.ai_predicted_category || "—")}</span><span class="corrected-value">Human: ${escapeHtml(item.correction || "—")}</span><span class="review-note">${escapeHtml(item.reason || "No note added")}</span></div>
  `).join("") : '<div class="no-corrections">No human corrections have been recorded yet.</div>';
}

async function loadDashboard() {
  try {
    const data = await api("/api/dashboard");
    state.dashboard = data;
    byId("metric-total").textContent = data.total_cases;
    byId("metric-correct").textContent = data.correct_cases;
    byId("metric-incorrect").textContent = data.incorrect_cases;
    byId("metric-accuracy").textContent = `${(data.accuracy * 100).toFixed(1)}%`;
    renderCategoryChart(data.category_counts);
    renderStatusChart(data.status_counts, data.total_cases);
    renderCaseTable();
    renderCorrections(data.corrections);
  } catch (error) {
    showAlert(`Could not load dashboard: ${error.message}`);
  }
}

async function saveReview() {
  if (!state.diagnosis || !state.evaluation) return;
  clearAlert();
  const correction = byId("correction-category").value;
  const reason = byId("review-reason").value.trim();
  byId("save-review").disabled = true;
  try {
    const result = await api("/api/reviews", {
      method: "POST",
      body: JSON.stringify({
        case_id: state.selectedCaseId,
        decision: state.decision,
        correction,
        reason,
        ai_predicted_category: state.diagnosis.fault_category,
      }),
    });
    byId("review-saved").textContent = `Review saved for ${result.review.case_id}: ${result.review.decision.toLowerCase()}.`;
    byId("review-saved").classList.remove("hidden");
  } catch (error) {
    showAlert(`Could not save review: ${error.message}`);
  } finally {
    byId("save-review").disabled = false;
  }
}

async function initialize() {
  const correctionSelect = byId("correction-category");
  correctionSelect.innerHTML = categories.map((item) => `<option value="${item}">${item.replaceAll("_", " ")}</option>`).join("");
  document.querySelectorAll(".nav-item").forEach((button) => button.addEventListener("click", () => setPage(button.dataset.page)));
  byId("case-select").addEventListener("change", (event) => { state.selectedCaseId = event.target.value; renderCase(); });
  byId("diagnose-button").addEventListener("click", diagnose);
  byId("copy-output").addEventListener("click", async () => {
    const button = byId("copy-output");
    try { await navigator.clipboard.writeText(byId("case-output").textContent); button.innerHTML = "✓ Copied"; }
    catch { button.textContent = "Copy unavailable"; }
    window.setTimeout(() => { button.innerHTML = "<span>▢</span> Copy"; }, 1400);
  });
  document.querySelectorAll(".review-option").forEach((button) => button.addEventListener("click", () => {
    state.decision = button.dataset.decision;
    document.querySelectorAll(".review-option").forEach((item) => item.classList.toggle("selected", item === button));
    byId("correction-fields").classList.toggle("hidden", state.decision !== "Edited");
  }));
  byId("save-review").addEventListener("click", saveReview);
  byId("refresh-dashboard").addEventListener("click", loadDashboard);
  byId("status-filter").addEventListener("change", renderCaseTable);
  byId("case-search").addEventListener("input", renderCaseTable);
  byId("case-table-body").addEventListener("click", (event) => {
    const row = event.target.closest("tr[data-case-id]");
    if (!row) return;
    const caseId = row.dataset.caseId;
    if (state.cases.some((item) => item.case_id === caseId)) {
      byId("case-select").value = caseId;
      state.selectedCaseId = caseId;
      renderCase();
      setPage("diagnose");
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  });

  try {
    const data = await api("/api/cases");
    state.cases = data.cases || [];
    byId("case-select").innerHTML = state.cases.map((item) => `<option value="${escapeHtml(item.case_id)}">${escapeHtml(item.case_id)} · ${escapeHtml(item.issue_type || "Network case")}</option>`).join("");
    state.selectedCaseId = state.cases[0]?.case_id || "";
    renderCase();
  } catch (error) {
    showAlert(`Could not load case data: ${error.message}`);
  }
}

document.addEventListener("DOMContentLoaded", initialize);
