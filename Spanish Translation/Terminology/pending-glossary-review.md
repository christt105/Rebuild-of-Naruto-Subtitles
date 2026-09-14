# Pending glossary review

Terms tagged inline with `{CODE}` during episode translation, staged here for
a periodic review pass (not resolved per-episode). Once a term is confirmed
against a reliable source (or fixed as this project's own convention), add it
to `naruto_glosario_es_es.yml` and strip the `{CODE}` tag from every episode
that used it.

Append new entries at the end — do not edit existing ones — so concurrent
episode translations don't conflict on this file.

Entry format (parsed by `scripts/build_site_data.py` to show a tooltip for
the tag in the site's episode viewer):

```
### `{CODE}` — short title
Free-text explanation of the term/decision, as long as needed.
```

---

### `{NIETO}` — "Honorable Grandson" (Konohamaru's epithet)
S01E02 repeatedly addresses Konohamaru as "Honorable Grandson" (capitalized,
used as a name substitute by Ebisu and the guard, e.g. cues 61, 96, 97, 125,
139) instead of his actual name. No existing glossary entry covers this.
It's structurally similar to the already-verified `-sama` convention
("Lord Hokage" -> "el Hokage", honorific dropped when context is clear), but
since this is a recurring epithet tied to one specific character (Konohamaru
reappears in later episodes), it's flagged here instead of silently applying
that convention. Working translation used this episode: "Honorable Nieto".
Review should decide whether to keep the honorific or strip it per the
`-sama` convention (e.g. plain "nieto del Hokage").

### `{SXHR}` — "Sexy Jutsu" vs. "Harem Jutsu" split
The existing glossary entry ("Sexy Jutsu / Harem Jutsu" -> "Jutsu Sexy
Harem", verified: false) treats both English names as one merged Spanish
phrase. S01E02 (cues 84, 134, 153) uses them as two distinct, separately
named techniques in the dialogue itself: "Sexy Jutsu" (Naruto's original
transformation) and "Harem Jutsu" (the multi-clone escalation of it, cue
153: `I call this one... the "Harem Jutsu"!`). This episode splits the
glossary phrase into "Jutsu Sexy" (for Sexy Jutsu) and "Jutsu Harem" (for
Harem Jutsu) to match the source. Review should confirm and split the
glossary entry into two, or restore the merged phrasing if that was
intentional.

### `{STGR}` — "Sign of the Tiger" (hand seal)
S01E02, cue 616: `Is that the Sign of the Tiger?!`. No glossary entry for
hand-seal names exists yet. Translated as "el Sello del Tigre" this episode.
Likely to recur whenever hand seals are called out by name in future
episodes; review should fix a consistent convention for hand-seal names
generally (Tiger, Horse, etc. appear as cues 741-742 in this same episode
but untitled there, just shouted as "Horse!"/"Tiger!").

### `{MAD}` — "A Thousand Years of Death"
S01E02, cue 625: Kakashi's joke taijutsu technique, `<i>A Thousand Years of
Death!</i>`. No glossary entry exists. Translated as "Los Mil Años de
Dolor", the widely-known fan/meme rendering of this move in Spanish (rather
than a literal "de Muerte"), but this hasn't been confirmed against an
actual Spain dub/sub source. Review should verify or correct.

### `{ICHA}` — "Make-Out Paradise" (Kakashi's book)
S01E02, cue 732: `There's no time to read "Make-Out Paradise."`. This is the
English localization's name for Kakashi's Icha Icha book, a running gag
across the whole series, so it will recur constantly in later episodes. No
glossary entry exists. Left untranslated as "Make-Out Paradise" this
episode pending a decision on whether to translate the title (and to what)
or keep it in English/Japanese.
