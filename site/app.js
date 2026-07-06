async function loadRuns() {
  const container = document.getElementById("runs");
  try {
    const res = await fetch("data/demo.json");
    const data = await res.json();
    container.innerHTML = data.runs.map(renderRun).join("");
  } catch (e) {
    container.innerHTML = "<p class='muted'>Run <code>scripts/export_site_data.sh</code> to generate demo.json</p>";
  }
}

function renderRun(entry) {
  const d = entry.doctor;
  const s = entry.summary;
  const status = d.overall_status;
  const signals = (d.signals || [])
    .map((sig) => `<div class="signal ${sig.status === 'fail' ? 'fail' : sig.status === 'warn' ? 'warn' : 'pass'}">[${sig.status}] ${sig.signal}: ${sig.message}</div>`)
    .join("");

  return `
    <article class="card ${status}">
      <span class="badge ${status}">${status}</span>
      <h3>${d.run_id}</h3>
      <p class="muted">${s.experiment_name || "—"} · peak series ${s.reward_series_length || 0} iters</p>
      <p>${d.baseline_grade?.message || ""}</p>
      ${signals}
    </article>`;
}

loadRuns();
