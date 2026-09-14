import { fetchJSON, escapeHtml, highlightTags, cueEsHtml, issueUrl, tagTooltipMap } from "./app.js";

const params = new URLSearchParams(window.location.search);
const [index, glossary] = await Promise.all([fetchJSON("./data/index.json"), fetchJSON("./data/glossary.json")]);
const tagMap = tagTooltipMap(glossary.pending_tags);

const seasonSelect = document.getElementById("season-select");
const episodeSelect = document.getElementById("episode-select");
const meta = document.getElementById("episode-meta");
const cueBody = document.getElementById("cue-body");

const bySeason = new Map();
for (const season of index.seasons) bySeason.set(season, []);
for (const ep of index.episodes) bySeason.get(ep.season).push(ep);

seasonSelect.innerHTML = index.seasons.map((s) => `<option value="${escapeHtml(s)}">${escapeHtml(s)}</option>`).join("");

function populateEpisodes(season) {
  episodeSelect.innerHTML = bySeason
    .get(season)
    .map((ep) => `<option value="${ep.code}">${ep.code} — ${escapeHtml(ep.title_es)}</option>`)
    .join("");
}

async function loadEpisode(code) {
  const summary = index.episodes.find((e) => e.code === code);
  if (!summary) {
    meta.textContent = "Episodio no encontrado";
    cueBody.innerHTML = "";
    return;
  }
  if (summary.srt_error) {
    meta.textContent = `Error de origen en el .srt: ${summary.srt_error}`;
    cueBody.innerHTML = "";
    return;
  }
  const episode = await fetchJSON(`./data/episodes/${code}.json`);
  meta.textContent = `${summary.status} · ${summary.translated_count}/${summary.cue_count} cues traducidas${summary.notes ? " · " + summary.notes : ""}`;
  cueBody.innerHTML = episode.cues
    .map(
      (cue) => `
    <tr id="cue-${cue.index}">
      <td class="time">#${cue.index}<br>${cue.start}</td>
      <td class="en">${escapeHtml(cue.en)}</td>
      <td class="es${cue.translated ? " is-translated" : ""}">${cueEsHtml(cue, tagMap)}</td>
      <td class="actions"><a class="propose-link" href="${issueUrl(episode, cue)}" target="_blank" rel="noopener">Proponer cambio</a></td>
    </tr>`
    )
    .join("");

  const hash = window.location.hash;
  if (hash) {
    const target = document.querySelector(hash);
    if (target) {
      target.scrollIntoView({ block: "center" });
      target.style.outline = "2px solid var(--seq-fill)";
    }
  }
}

seasonSelect.addEventListener("change", () => {
  populateEpisodes(seasonSelect.value);
  const code = episodeSelect.value;
  history.replaceState(null, "", `./episode.html?code=${code}`);
  loadEpisode(code);
});

episodeSelect.addEventListener("change", () => {
  const code = episodeSelect.value;
  history.replaceState(null, "", `./episode.html?code=${code}`);
  loadEpisode(code);
});

const initialCode = params.get("code") || index.episodes[0].code;
const initialEpisode = index.episodes.find((e) => e.code === initialCode) || index.episodes[0];
seasonSelect.value = initialEpisode.season;
populateEpisodes(initialEpisode.season);
episodeSelect.value = initialEpisode.code;
loadEpisode(initialEpisode.code);
