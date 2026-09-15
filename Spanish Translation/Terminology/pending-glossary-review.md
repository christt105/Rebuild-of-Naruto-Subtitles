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

### `{ICHA}` — "Make-Out Paradise" (Kakashi's book)
S01E02, cue 732: `There's no time to read "Make-Out Paradise."`. This is the
English localization's name for Kakashi's Icha Icha book, a running gag
across the whole series, so it will recur constantly in later episodes. No
glossary entry exists. Left untranslated as "Make-Out Paradise" this
episode pending a decision on whether to translate the title (and to what)
or keep it in English/Japanese. Christian's recollection: "Icha Icha" is
likely the actual Spain dub/manga term (the Japanese title kept as-is, same
pattern as Rasengan/Chidori) rather than "Make-Out Paradise", but unconfirmed.
He owns the full manga tomes plus an official character/data guide, both on
Jellyfin under `/Manga` (not being detected correctly there yet, separate
issue from this glossary), which could settle this and future dudas once
reviewed.

### `{COPYN}` — "Copy Ninja" (Kakashi's epithet)
S01E03, cues 359 and 401: "The Copy Ninja of the Hidden Leaf Village..." and
"Kakashi, the Copy Ninja." Translated as "el Ninja Copión". This epithet for
Kakashi recurs constantly across the whole series, so it needs to be locked
consistently rather than re-decided per episode. "Ninja Copión" is the
common fan/dub-adjacent term in Spanish-language Naruto material, but it is
not yet cross-checked against the official Planeta guide or a verified
Spain-dub source.

### `{MANJI}` — "Manji Formation"
S01E03, cue 378: "Form the Manji Formation..." (Kakashi ordering Team 7 into
a defensive formation against Zabuza). Translated as "Formación Manji",
keeping "Manji" as the Japanese name (卍, the swastika-shaped symbol), same
pattern as other untranslated Japanese proper nouns in the glossary (Kage,
Chakra, etc.). Not verified against an official source.

### `{BINGO}` — "Bingo Book"
S01E03, cues 397, 477 and 517 (also referenced again around cue 655):
Zabuza's shinobi bounty/rogue-ninja record book. Translated as "Libro
Bingo" (literal calque, already common across Spanish-language fan
material). This term recurs heavily for the rest of the series (used to
introduce named rogue/elite ninja), so it needs a locked, consistent
translation. Not verified against the official Planeta guide.

### `{HMIST}` — "Ninja Art: Hidden Mist Jutsu"
S01E03, cue 413: Zabuza's technique to fill the area with concealing mist
("<i>Ninja Art: Hidden Mist Jutsu.</i>"). Translated as "Arte Ninja:
Ocultación en la Niebla". The "Ninja Art:" prefix here is distinct from the
elemental-release prefixes already fixed in the main glossary (Técnica
ígnea/acuática/de viento/etc.), since this is a general ninjutsu rather than
a Water Release technique. Working choice only, unconfirmed against the
official guide.

### `{WPRIS}` — "Water Prison Jutsu"
S01E03, cue 463 (referenced again around cues 485-486): Zabuza's signature
technique for trapping an opponent in a sphere of water. Translated as
"Técnica acuática: Prisión de Agua", reusing the "Técnica acuática:" prefix
already established in the main glossary for Water Release techniques.
Only the prefix is confirmed by that convention; the name "Prisión de Agua"
itself is a working choice, not individually verified. This technique is
central to the Zabuza arc and will recur in the next few episodes.

### `{DWSHU}` — "Demon Wind Shuriken"
S01E03, cues 585 and 601: the giant shuriken Kakashi uses hidden inside a
Shadow Clone to defeat Zabuza (Fūma Shuriken in Japanese). Translated as
"Shuriken del Viento Demoníaco" (literal calque, keeping "shuriken"
untranslated per existing convention). This weapon/technique reappears
across the wider series with other characters, so it should be locked
rather than re-translated ad hoc. Not verified against an official source.

### `{SILKI}` — "Silent Killing" (Hidden Mist technique)
S01E03, cue 419: Zabuza described as "an expert of the Silent Killing
technique" (Kirigakure's assassination method). Translated as "la técnica
de la Matanza Silenciosa". Working choice only; an alternative like
"Asesinato Silencioso" is equally defensible and unconfirmed against an
official source.

### `{WDRAG}` — "Water Style: Water Dragon Jutsu"
S01E03, cue 618: Zabuza and Kakashi's simultaneous technique
("<i>Water Style: Water Dragon Jutsu!</i>"). Translated as "Técnica
acuática: Dragón de Agua", reusing the confirmed "Técnica acuática:" prefix
from the main glossary; only the name "Dragón de Agua" itself is an
unverified working choice.

### `{TRACK}` — "Tracker Ninja" / "Corpse Disposal Unit"
S01E03, cues 656, 659, 707-709, 718, 726, 735, 745 and 749: Haku's role
(hunter-nin), and the dark nickname used for the role in-dialogue
("commonly known as 'Corpse Disposal Unit'"). Translated "Tracker Ninja" as
"Ninja Rastreador" and the nickname as "Unidad de Eliminación de
Cadáveres", tagged together under the same code since both refer to the
same role in the same scene. This concept recurs later in the series
whenever hunter-nin come up, so it needs a locked, consistent translation.
Neither rendering is verified against an official source.
