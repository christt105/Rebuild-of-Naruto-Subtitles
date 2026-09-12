#!/usr/bin/env python3
"""Update one episode's row in Spanish Translation/PROGRESS.md.

Usage:
    update_progress.py <code> <Pendiente|PR abierta|Fusionado> [--pr N] [--nota "texto"]
"""

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PROGRESS = REPO_ROOT / "Spanish Translation" / "PROGRESS.md"
CODE_RE = re.compile(r"[Ss]\d{2}[Ee]\d{2}")
VALID_STATES = ("Pendiente", "PR abierta", "Fusionado")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("code", help="Código de episodio, p.ej. S01E01")
    parser.add_argument("estado", choices=VALID_STATES)
    parser.add_argument("--pr", type=int, help="Número de PR, se añade a la columna Notas")
    parser.add_argument("--nota", help="Texto adicional para la columna Notas")
    args = parser.parse_args()

    code = args.code.upper()
    if not CODE_RE.fullmatch(code):
        sys.exit(f"'{args.code}' no tiene forma de código de episodio (SxxExx)")

    lines = PROGRESS.read_text(encoding="utf-8").splitlines()
    row_idx = next((i for i, line in enumerate(lines) if line.startswith(f"| {code} |")), None)
    if row_idx is None:
        sys.exit(f"No se encontró una fila para {code} en {PROGRESS.relative_to(REPO_ROOT)}")

    cols = [c.strip() for c in lines[row_idx].strip().strip("|").split("|")]
    if len(cols) != 6:
        sys.exit(f"Fila de {code} no tiene el formato esperado de 6 columnas: {lines[row_idx]!r}")

    cols[4] = args.estado

    nota_parts = []
    if args.pr:
        nota_parts.append(f"PR #{args.pr}")
    if args.nota:
        nota_parts.append(args.nota)
    if nota_parts:
        addition = " — ".join(nota_parts)
        cols[5] = f"{cols[5]} — {addition}" if cols[5] else addition

    lines[row_idx] = "| " + " | ".join(cols) + " |"
    PROGRESS.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{code}: {args.estado}" + (f" (PR #{args.pr})" if args.pr else ""))


if __name__ == "__main__":
    main()
