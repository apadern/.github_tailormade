#!/usr/bin/env python3
"""
Valida quality gates de backlog.

Soporta 2 alcances:
- module: valida XX_1..XX_6 para un modulo
- traceability: valida solo gate de trazabilidad (ej. check_final.md)

Reglas:
- Gate XX_1 (traceability): ERROR=0 y WARN=0 o WARN justificados individualmente.
- Gate XX_2 (design): Errores=0.
- Gate XX_3 (funcional): faltantes=0.
- Gate XX_4 (HU): HUs faltantes=0, PF faltantes=0 y WARN=0 o WARN justificados.
- Gate XX_5 (PF E2E): PF faltantes=0.
- Gate XX_6 (nav): rutas faltantes=0 y menu faltante=0.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

sys.dont_write_bytecode = True


@dataclass(frozen=True)
class GateCheck:
    name: str
    metric: str
    value: int
    passed: bool
    note: str = ""


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def extract_int(text: str, patterns: Sequence[str], label: str, source: Path) -> int:
    for pat in patterns:
        m = re.search(pat, text, flags=re.IGNORECASE | re.MULTILINE)
        if m:
            return int(m.group(1))
    raise ValueError(f"No se encontro metrica '{label}' en {source.as_posix()}")


def count_warn_justifications(path: Optional[Path]) -> int:
    if path is None or not path.exists():
        return 0
    text = read_text(path)

    ids = {m.group(1).upper() for m in re.finditer(r"\b(W-\d{3,4})\b", text, flags=re.IGNORECASE)}
    if ids:
        return len(ids)

    # Fallback: count rows in markdown table that look like justification rows.
    rows = 0
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        if re.match(r"^\|\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?$", s):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 4:
            continue
        header_like = "".join(cells).lower()
        if "warning" in header_like and "justificacion" in header_like:
            continue
        if any(c for c in cells):
            rows += 1
    return rows


def eval_warn_gate(
    gate_name: str,
    warn_value: int,
    justifications: int,
    file_hint: Optional[Path],
) -> GateCheck:
    if warn_value == 0:
        return GateCheck(gate_name, "WARN", 0, True, "sin observaciones")
    if justifications >= warn_value:
        return GateCheck(
            gate_name,
            "WARN",
            warn_value,
            True,
            f"justificados: {justifications}/{warn_value}",
        )
    missing = warn_value - justifications
    hint = file_hint.as_posix() if file_hint is not None else "(sin archivo)"
    return GateCheck(
        gate_name,
        "WARN",
        warn_value,
        False,
        f"faltan justificaciones: {missing} (archivo: {hint})",
    )


def eval_traceability_gate(
    traceability_path: Path,
    traceability_warn_justifications: Optional[Path],
) -> List[GateCheck]:
    text = read_text(traceability_path)
    errors = extract_int(
        text,
        patterns=(
            r"\|\s*Discrepancias\s*\(ERROR\)\s*\|\s*(\d+)\s*\|",
            r"-\s*Discrepancias\s*\(ERROR\)\s*:\s*(\d+)",
        ),
        label="Discrepancias (ERROR)",
        source=traceability_path,
    )
    warns = extract_int(
        text,
        patterns=(
            r"\|\s*Observaciones\s*\(WARN\)\s*\|\s*(\d+)\s*\|",
            r"-\s*Observaciones\s*\(WARN\)\s*:\s*(\d+)",
        ),
        label="Observaciones (WARN)",
        source=traceability_path,
    )
    checks: List[GateCheck] = [
        GateCheck("XX_1_check_traceability", "Discrepancias (ERROR)", errors, errors == 0),
    ]
    just_count = count_warn_justifications(traceability_warn_justifications)
    checks.append(
        eval_warn_gate("XX_1_check_traceability", warns, just_count, traceability_warn_justifications)
    )
    return checks


def eval_module_gates(
    traceability_path: Path,
    design_path: Path,
    funcional_path: Path,
    hu_path: Path,
    pf_e2e_path: Path,
    nav_path: Path,
    traceability_warn_justifications: Optional[Path],
    hu_warn_justifications: Optional[Path],
) -> List[GateCheck]:
    checks = eval_traceability_gate(traceability_path, traceability_warn_justifications)

    design_text = read_text(design_path)
    design_errors = extract_int(
        design_text,
        patterns=(r"-\s*Errores\s*:\s*(\d+)",),
        label="Errores",
        source=design_path,
    )
    checks.append(GateCheck("XX_2_check_design", "Errores", design_errors, design_errors == 0))

    funcional_text = read_text(funcional_path)
    funcional_missing = extract_int(
        funcional_text,
        patterns=(r"-\s*faltantes\s*:\s*(\d+)",),
        label="faltantes",
        source=funcional_path,
    )
    checks.append(
        GateCheck("XX_3_check_funcional", "faltantes", funcional_missing, funcional_missing == 0)
    )

    hu_text = read_text(hu_path)
    hu_missing = extract_int(
        hu_text,
        patterns=(r"-\s*HUs faltantes por seccion\s*\(ERROR\)\s*:\s*(\d+)",),
        label="HUs faltantes por seccion (ERROR)",
        source=hu_path,
    )
    hu_pf_missing = extract_int(
        hu_text,
        patterns=(r"-\s*PF faltantes en Tests E2E\s*\(ERROR\)\s*:\s*(\d+)",),
        label="PF faltantes en Tests E2E (ERROR)",
        source=hu_path,
    )
    hu_warn = extract_int(
        hu_text,
        patterns=(r"-\s*criterios sin mapear a PF\s*\(WARN\)\s*:\s*(\d+)",),
        label="criterios sin mapear a PF (WARN)",
        source=hu_path,
    )
    checks.append(
        GateCheck("XX_4_check_hu", "HUs faltantes por seccion (ERROR)", hu_missing, hu_missing == 0)
    )
    checks.append(
        GateCheck(
            "XX_4_check_hu",
            "PF faltantes en Tests E2E (ERROR)",
            hu_pf_missing,
            hu_pf_missing == 0,
        )
    )
    hu_just_count = count_warn_justifications(hu_warn_justifications)
    checks.append(eval_warn_gate("XX_4_check_hu", hu_warn, hu_just_count, hu_warn_justifications))

    pf_text = read_text(pf_e2e_path)
    pf_missing = extract_int(
        pf_text,
        patterns=(r"-\s*PF faltantes en Tests E2E\s*\(ERROR\)\s*:\s*(\d+)",),
        label="PF faltantes en Tests E2E (ERROR)",
        source=pf_e2e_path,
    )
    checks.append(
        GateCheck("XX_5_check_pf_e2e", "PF faltantes en Tests E2E (ERROR)", pf_missing, pf_missing == 0)
    )

    nav_text = read_text(nav_path)
    nav_missing = extract_int(
        nav_text,
        patterns=(r"-\s*rutas faltantes\s*\(ERROR\)\s*:\s*(\d+)",),
        label="rutas faltantes (ERROR)",
        source=nav_path,
    )
    nav_menu_missing = extract_int(
        nav_text,
        patterns=(r"-\s*menu faltante\s*\(ERROR\)\s*:\s*(\d+)",),
        label="menu faltante (ERROR)",
        source=nav_path,
    )
    checks.append(GateCheck("XX_6_check_nav", "rutas faltantes (ERROR)", nav_missing, nav_missing == 0))
    checks.append(
        GateCheck("XX_6_check_nav", "menu faltante (ERROR)", nav_menu_missing, nav_menu_missing == 0)
    )

    return checks


def render_report(scope: str, checks: Sequence[GateCheck]) -> str:
    lines: List[str] = []
    lines.append("# Check quality gates backlog")
    lines.append("")
    lines.append(f"- scope: {scope}")
    lines.append("")
    lines.append("## Resultado")
    lines.append("")
    lines.append("| Gate | Metrica | Valor | Estado | Nota |")
    lines.append("|---|---|---:|---|---|")
    for c in checks:
        lines.append(
            f"| {c.name} | {c.metric} | {c.value} | {'OK' if c.passed else 'FAIL'} | {c.note} |"
        )
    lines.append("")
    fail_count = sum(1 for c in checks if not c.passed)
    lines.append("## Resumen")
    lines.append("")
    lines.append(f"- checks: {len(checks)}")
    lines.append(f"- fallas: {fail_count}")
    lines.append(f"- estado: {'OK' if fail_count == 0 else 'FAIL'}")
    lines.append("")
    return "\n".join(lines)


def ensure_exists(paths: Sequence[Tuple[str, Optional[Path]]]) -> None:
    missing = [f"{name}={path}" for name, path in paths if path is not None and not path.exists()]
    if missing:
        raise SystemExit("ERROR: faltan archivos requeridos: " + ", ".join(missing))


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Valida quality gates de backlog por modulo o trazabilidad consolidada.")
    p.add_argument("--scope", choices=("module", "traceability"), default="module")
    p.add_argument("--traceability", type=Path, required=True, help="Reporte XX_1 o check_final.md")
    p.add_argument("--traceability-warn-justifications", type=Path, default=None)
    p.add_argument("--design", type=Path, default=None, help="Reporte XX_2")
    p.add_argument("--funcional", type=Path, default=None, help="Reporte XX_3")
    p.add_argument("--hu", type=Path, default=None, help="Reporte XX_4")
    p.add_argument("--hu-warn-justifications", type=Path, default=None)
    p.add_argument("--pf-e2e", type=Path, default=None, help="Reporte XX_5")
    p.add_argument("--nav", type=Path, default=None, help="Reporte XX_6")
    p.add_argument("--out", type=Path, default=None, help="Ruta del reporte de gates")
    return p.parse_args(list(argv))


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    ensure_exists(
        (
            ("traceability", args.traceability),
            ("design", args.design if args.scope == "module" else None),
            ("funcional", args.funcional if args.scope == "module" else None),
            ("hu", args.hu if args.scope == "module" else None),
            ("pf-e2e", args.pf_e2e if args.scope == "module" else None),
            ("nav", args.nav if args.scope == "module" else None),
        )
    )

    if args.scope == "traceability":
        checks = eval_traceability_gate(args.traceability, args.traceability_warn_justifications)
    else:
        required = {
            "design": args.design,
            "funcional": args.funcional,
            "hu": args.hu,
            "pf-e2e": args.pf_e2e,
            "nav": args.nav,
        }
        missing_required = [name for name, value in required.items() if value is None]
        if missing_required:
            raise SystemExit(
                "ERROR: faltan argumentos requeridos para scope=module: " + ", ".join(missing_required)
            )
        checks = eval_module_gates(
            traceability_path=args.traceability,
            design_path=args.design,
            funcional_path=args.funcional,
            hu_path=args.hu,
            pf_e2e_path=args.pf_e2e,
            nav_path=args.nav,
            traceability_warn_justifications=args.traceability_warn_justifications,
            hu_warn_justifications=args.hu_warn_justifications,
        )

    report = render_report(args.scope, checks)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
    else:
        print(report)

    fail_count = sum(1 for c in checks if not c.passed)
    return 1 if fail_count > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
