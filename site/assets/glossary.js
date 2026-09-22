import { fetchJSON, escapeHtml } from "./app.js";

const glossary = await fetchJSON("./data/glossary.json");
glossary.entries.forEach((e, i) => (e._id = i));

const body = document.getElementById("glossary-body");
const filterText = document.getElementById("filter-text");
const filterVerified = document.getElementById("filter-verified");

const INLINE_EPISODE_LIMIT = 6;
const episodeCache = new Map();

function loadEpisode(code) {
  if (!episodeCache.has(code)) {
    episodeCache.set(code, fetchJSON(`./data/episodes/${code}.json`));
  }
  return episodeCache.get(code);
}

function episodesCell(entryId, cues) {
  const codes = Object.keys(cues);
  if (!codes.length) return '<span class="muted">sin coincidencias</span>';
  const chips = codes
    .map(
      (code) =>
        `<button type="button" class="episode-chip cue-toggle" data-entry-id="${entryId}" data-code="${code}">${code} (${cues[code].length})</button>`
    )
    .join("");
  const inner = `<div class="episode-chips">${chips}</div><div class="cue-detail"></div>`;
  if (codes.length <= INLINE_EPISODE_LIMIT) {
    return `<div class="cue-cell">${inner}</div>`;
  }
  return `<details class="cue-cell"><summary class="episode-summary">${codes.length} episodios</summary>${inner}</details>`;
}

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
      <td>${episodesCell(e._id, e.cues)}</td>
    </tr>`
    )
    .join("");
}

async function showCues(container, code, indices) {
  container.innerHTML = '<p class="muted">Cargando cues...</p>';
  const episode = await loadEpisode(code);
  const byIndex = new Map(episode.cues.map((c) => [c.index, c]));
  const rows = indices
    .map((i) => byIndex.get(i))
    .filter(Boolean)
    .map(
      (cue) => `
    <div class="cue-match">
      <a href="./episode.html?code=${code}#cue-${cue.index}" target="_blank" rel="noopener">${code} · cue #${cue.index} · ${cue.start}</a>
      <div class="muted">EN: ${escapeHtml(cue.en)}</div>
      <div class="muted">ES: ${escapeHtml(cue.es)}</div>
    </div>`
    )
    .join("<hr>");
  container.innerHTML = rows || '<p class="muted">No se encontraron las cues.</p>';
}

body.addEventListener("click", (event) => {
  const btn = event.target.closest(".cue-toggle");
  if (!btn) return;
  const cell = btn.closest(".cue-cell");
  const container = cell.querySelector(".cue-detail");
  const code = btn.dataset.code;
  const entry = glossary.entries[Number(btn.dataset.entryId)];

  if (container.dataset.openCode === code) {
    container.innerHTML = "";
    delete container.dataset.openCode;
    btn.classList.remove("active");
    return;
  }
  cell.querySelectorAll(".cue-toggle").forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
  container.dataset.openCode = code;
  showCues(container, code, entry.cues[code]);
});

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
