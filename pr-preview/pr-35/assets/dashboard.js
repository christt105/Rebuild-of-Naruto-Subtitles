import { fetchJSON, statusBadge, escapeHtml } from "./app.js";

const index = await fetchJSON("./data/index.json");

const statRow = document.getElementById("stat-row");
const pct = index.totals.cues_total
  ? Math.round((index.totals.cues_translated / index.totals.cues_total) * 100)
  : 0;
statRow.innerHTML = `
  <div class="stat-tile"><div class="label">Episodios</div><div class="value">${index.totals.episodes}</div></div>
  <div class="stat-tile"><div class="label">Cues traducidas</div><div class="value">${pct}%</div></div>
  <div class="stat-tile"><div class="label">Cues totales</div><div class="value">${index.totals.cues_total.toLocaleString("es-ES")}</div></div>
  <div class="stat-tile"><div class="label">Tags {CODE} sin resolver</div><div class="value">${index.totals.unresolved_tags}</div></div>
`;

const bySeason = new Map();
for (const season of index.seasons) bySeason.set(season, []);
for (const ep of index.episodes) bySeason.get(ep.season).push(ep);

const container = document.getElementById("seasons");
container.innerHTML = index.seasons
  .map((season) => {
    const episodes = bySeason.get(season);
    const total = episodes.reduce((a, e) => a + e.cue_count, 0);
    const translated = episodes.reduce((a, e) => a + e.translated_count, 0);
    const seasonPct = total ? Math.round((translated / total) * 100) : 0;
    const rows = episodes
      .map(
        (ep) => `
      <tr class="episode-row" data-code="${ep.code}">
        <td>${ep.code}</td>
        <td>${escapeHtml(ep.title_es)}</td>
        <td>${statusBadge(ep.status)}</td>
        <td>${ep.translated_count}/${ep.cue_count}</td>
        <td>${ep.unresolved_tags.length ? ep.unresolved_tags.map((t) => `{${t}}`).join(", ") : ""}</td>
        <td>${ep.srt_error ? '<span class="status-dot critical" title="' + escapeHtml(ep.srt_error) + '"></span> error de origen' : ""}</td>
      </tr>`
      )
      .join("");
    return `
      <section class="season-block">
        <h2>${escapeHtml(season)} — ${seasonPct}%</h2>
        <div class="meter"><span style="width:${seasonPct}%"></span></div>
        <div class="table-scroll">
          <table>
            <thead><tr><th>Código</th><th>Título</th><th>Estado</th><th>Cues</th><th>Tags</th><th></th></tr></thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
      </section>`;
  })
  .join("");

container.addEventListener("click", (e) => {
  const row = e.target.closest(".episode-row");
  if (!row) return;
  window.location.href = `./episode.html?code=${row.dataset.code}`;
});
