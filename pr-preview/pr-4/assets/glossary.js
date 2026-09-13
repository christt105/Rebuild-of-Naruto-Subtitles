import { fetchJSON, escapeHtml } from "./app.js";

const glossary = await fetchJSON("./data/glossary.json");
const body = document.getElementById("glossary-body");
const filterText = document.getElementById("filter-text");
const filterVerified = document.getElementById("filter-verified");

function render() {
  const text = filterText.value.trim().toLowerCase();
  const verified = filterVerified.value;
  const rows = glossary.entries.filter((e) => {
    if (verified && String(e.verified) !== verified) return false;
    if (!text) return true;
    return (
      e.japanese.toLowerCase().includes(text) ||
      e.english.toLowerCase().includes(text) ||
      e.spanish_es.toLowerCase().includes(text)
    );
  });
  body.innerHTML = rows
    .map(
      (e) => `
    <tr>
      <td>${escapeHtml(e.japanese)}</td>
      <td>${escapeHtml(e.english)}</td>
      <td>${escapeHtml(e.spanish_es)}</td>
      <td>${e.verified ? "✅" : "—"}</td>
      <td>${e.episodes.length ? e.episodes.join(", ") : '<span class="muted">sin coincidencias</span>'}</td>
    </tr>`
    )
    .join("");
}

filterText.addEventListener("input", render);
filterVerified.addEventListener("change", render);
render();

const pendingContainer = document.getElementById("pending-tags");
pendingContainer.innerHTML = glossary.pending_tags.length
  ? glossary.pending_tags
      .map(
        (t) => `<p><span class="tag">{${t.code}}</span> <strong>${escapeHtml(t.title)}</strong><br>${escapeHtml(t.body)}</p>`
      )
      .join("")
  : '<p class="muted">Sin tags pendientes de revisión.</p>';
