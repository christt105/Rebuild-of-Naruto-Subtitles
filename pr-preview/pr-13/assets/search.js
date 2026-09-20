import { fetchJSON, escapeHtml } from "./app.js";

const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");
const queryInput = document.getElementById("query");

const MAX_RESULTS = 200;

statusEl.textContent = "Cargando episodios...";
const index = await fetchJSON("./data/index.json");
const codes = index.episodes.filter((e) => !e.srt_error).map((e) => e.code);
const episodes = await Promise.all(codes.map((code) => fetchJSON(`./data/episodes/${code}.json`)));

const allCues = [];
for (const episode of episodes) {
  for (const cue of episode.cues) {
    allCues.push({ episode, cue });
  }
}
statusEl.textContent = `${allCues.length.toLocaleString("es-ES")} cues cargadas de ${episodes.length} episodios.`;

function highlight(text, term) {
  const escaped = escapeHtml(text);
  if (!term) return escaped;
  const re = new RegExp(term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "ig");
  return escaped.replace(re, (m) => `<mark>${m}</mark>`);
}

function render(term) {
  if (!term) {
    resultsEl.innerHTML = "";
    return;
  }
  const lower = term.toLowerCase();
  const matches = allCues.filter(
    ({ cue }) => cue.en.toLowerCase().includes(lower) || cue.es.toLowerCase().includes(lower)
  );
  const shown = matches.slice(0, MAX_RESULTS);
  resultsEl.innerHTML = shown
    .map(
      ({ episode, cue }) => `
    <div class="search-result">
      <a href="./episode.html?code=${episode.code}#cue-${cue.index}"><strong>${episode.code}</strong> — ${escapeHtml(episode.title_es)} · cue #${cue.index}</a>
      <div class="muted">EN: ${highlight(cue.en, term)}</div>
      <div class="muted">ES: ${highlight(cue.es, term)}</div>
    </div>`
    )
    .join("<hr>");
  if (matches.length > MAX_RESULTS) {
    resultsEl.innerHTML += `<p class="muted">Mostrando ${MAX_RESULTS} de ${matches.length} resultados. Afina la búsqueda para ver más.</p>`;
  }
}

queryInput.addEventListener("input", () => render(queryInput.value.trim()));
