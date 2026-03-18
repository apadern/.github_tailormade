#!/usr/bin/env python3
"""
PF placement validator (module-scope).

Ensures that every PF (functional test) that belongs to the module appears as a task
inside the "Tests E2E" section of the module backlog, not just somewhere in the file.

Derivation of PFs for the module:
- Screens for module: design/01 route table (Ruta | Pantalla | Modulo).
- PFs for those screens: analisis/13_pruebas_funcionales.md rows referencing those P-XXX.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Set, Tuple

sys.dont_write_bytecode = True

P_ID_RE = re.compile(r"\bP-\d{3}\b", re.IGNORECASE)
PF_ID_RE = re.compile(r"\bPF-\d{3}\b", re.IGNORECASE)
HEADING_RE = re.compile(r"^(#{2,4})\s+(.+?)\s*$")


@dataclass(frozen=True)
class PfCheck:
    pf_id: str
    pantalla: str
    in_tests_e2e: bool
    reason: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def extract_screens_for_module(design01_text: str, module_slug: str) -> List[str]:
    screens: Set[str] = set()
    module_l = module_slug.strip().lower()
    for line in design01_text.splitlines():
        if "|" not in line or "----" in line or ":--" in line:
            continue
        parts = [p.strip().strip("`") for p in line.strip().strip("|").split("|")]
        if len(parts) < 3:
            continue
        row_l = " ".join(parts).lower()
        if module_l not in row_l:
            continue
        for m in P_ID_RE.finditer(line):
            screens.add(m.group(0).upper())
    return sorted(screens)


def slice_tests_section(backlog_text: str) -> str:
    lines = backlog_text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        hm = HEADING_RE.match(ln.strip())
        if not hm:
            continue
        if hm.group(1) == "##" and hm.group(2).strip().lower() == "tests e2e":
            start = i
            break
    if start is None:
        return ""
    end = len(lines)
    for j in range(start + 1, len(lines)):
        hm = HEADING_RE.match(lines[j].strip())
        if hm and hm.group(1) == "##":
            end = j
            break
    return "\n".join(lines[start:end])


def pfs_for_screens_from_pf_doc(pf_text: str, screens: Sequence[str]) -> Dict[str, str]:
    screen_set = {s.upper() for s in screens}
    out: Dict[str, str] = {}
    for line in pf_text.splitlines():
        pfs = [m.upper() for m in PF_ID_RE.findall(line)]
        if not pfs:
            continue
        ps = [m.upper() for m in P_ID_RE.findall(line)]
        if not ps:
            continue
        # The PF table has one PF per row, pick first screen and pf.
        pantalla = ps[0]
        pf_id = pfs[0]
        if pantalla in screen_set:
            out[pf_id] = pantalla
    return out


def build_report(module_slug: str, backlog_path: Path, checks: Sequence[PfCheck], screens: Sequence[str]) -> str:
    missing = [c for c in checks if not c.in_tests_e2e]
    lines: List[str] = []
    lines.append("# Check PF en Tests E2E")
    lines.append("")
    lines.append(f"- module: {module_slug}")
    lines.append(f"- backlog: {backlog_path.as_posix()}")
    lines.append(f"- pantallas: {', '.join(screens) if screens else '(none)'}")
    lines.append("")
    lines.append("## Resultados")
    lines.append("")
    lines.append("| PF | Pantalla | En Tests E2E | Detalle |")
    lines.append("|---|---|---|---|")
    for c in sorted(checks, key=lambda x: x.pf_id):
        lines.append(f"| {c.pf_id} | {c.pantalla} | {'OK' if c.in_tests_e2e else 'NO'} | {c.reason} |")
    lines.append("")
    lines.append("## Resumen")
    lines.append("")
    lines.append(f"- PF revisadas: {len(checks)}")
    lines.append(f"- PF faltantes en Tests E2E (ERROR): {len(missing)}")
    lines.append("")
    if missing:
        lines.append("### PF faltantes (ERROR)")
        lines.append("")
        for c in missing:
            lines.append(f"- {c.pf_id} ({c.pantalla})")
        lines.append("")
    return "\n".join(lines)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Valida que PFs del modulo esten en la seccion Tests E2E del backlog.")
    p.add_argument("--backlog", type=Path, required=True)
    p.add_argument("--module-scope", dest="module_scope", required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--design01", type=Path, default=Path("design/01_technical_design.md"))
    p.add_argument("--pf", type=Path, default=Path("analisis/13_pruebas_funcionales.md"))
    return p.parse_args(list(argv))


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    backlog_path: Path = args.backlog
    module_slug: str = args.module_scope
    out_path: Path = args.out

    if not backlog_path.exists():
        raise SystemExit(f"ERROR: backlog not found: {backlog_path}")
    for dep in (args.design01, args.pf):
        if not dep.exists():
            raise SystemExit(f"ERROR: file not found: {dep}")

    design_text = read_text(args.design01)
    screens = extract_screens_for_module(design_text, module_slug)
    if not screens:
        raise SystemExit(f"ERROR: no screens found for module-scope='{module_slug}' in {args.design01}")

    pf_text = read_text(args.pf)
    pf_map = pfs_for_screens_from_pf_doc(pf_text, screens)
    if not pf_map:
        raise SystemExit(f"ERROR: no PFs found for screens: {', '.join(screens)}")

    backlog_text = read_text(backlog_path)
    tests_section = slice_tests_section(backlog_text)
    if not tests_section:
        raise SystemExit("ERROR: Tests E2E section not found in backlog")
    tests_l = tests_section.lower()

    checks: List[PfCheck] = []
    for pf_id, pantalla in sorted(pf_map.items()):
        pf_l = pf_id.lower()
        ok = pf_l in tests_l
        reason = "found in Tests E2E section" if ok else "missing in Tests E2E section"
        checks.append(PfCheck(pf_id=pf_id, pantalla=pantalla, in_tests_e2e=ok, reason=reason))

    report = build_report(module_slug, backlog_path, checks, screens)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    missing = [c for c in checks if not c.in_tests_e2e]
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

