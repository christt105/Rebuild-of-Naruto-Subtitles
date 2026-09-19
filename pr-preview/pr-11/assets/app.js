export const REPO = "christt105/Rebuild-of-Naruto-Subtitles";

export async function fetchJSON(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`No se pudo cargar ${path}: ${res.status}`);
  return res.json();
}

export function escapeHtml(str) {
  return str.replace(/[&<>"']/g, (c) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[c]);
}

const STATUS_DOT = {
  Pendiente: "neutral",
  "PR abierta": "warning",
  Fusionado: "good",
};

export function statusBadge(status) {
  const dot = STATUS_DOT[status] || "neutral";
  return `<span class="status"><span class="status-dot ${dot}"></span>${escapeHtml(status)}</span>`;
}

export function tagTooltipMap(pendingTags) {
  const map = {};
  for (const t of pendingTags) map[t.code] = t;
  return map;
}

export function highlightTags(text, tagMap) {
  return escapeHtml(text).replace(/\{([A-Z0-9]+)\}/g, (match, code) => {
    const entry = tagMap[code];
    const title = entry ? `${entry.title}: ${entry.body}` : "Pendiente de revisión";
    return `<span class="tag" title="${escapeHtml(title)}">{${code}}</span>`;
  });
}

export function issueUrl(episode, cue) {
  const title = `Propuesta de cambio: ${episode.code} cue #${cue.index}`;
  const body = [
    `Episodio: ${episode.code} — ${episode.title_es}`,
    `Cue: #${cue.index} (${cue.start} --> ${cue.end})`,
    "",
    "Texto EN:",
    cue.en,
    "",
    "Texto ES actual:",
    cue.es,
    "",
    "Propuesta:",
    "(escribe aquí tu propuesta de traducción)",
  ].join("\n");
  const params = new URLSearchParams({ title, body });
  return `https://github.com/${REPO}/issues/new?${params.toString()}`;
}

export function cueEsHtml(cue, tagMap) {
  if (cue.es_prev) {
    return `<span class="diff-old">${highlightTags(cue.es_prev, tagMap)}</span><span class="diff-new">${highlightTags(cue.es, tagMap)}</span>`;
  }
  return highlightTags(cue.es, tagMap);
}
