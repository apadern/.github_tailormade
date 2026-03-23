#!/usr/bin/env python3
"""
Navigation vs backlog validator (module-scope).

Checks:
- For each UI route of the module (from design/01 route table), the backlog mentions the route string.
- Ensures there is at least one task that adds a menu/sidebar link for the module (heuristic).
- (Soft) Verifies that the module screens appear in analisis/11 navigation diagrams.

This complements design-integrity: that script checks presence of expected routes/servicios expuestos/entities/services,
but does not ensure "menu link" tasks exist nor does it consider navigation diagrams explicitly.
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
ROUTE_RE = re.compile(r"/[-a-z0-9_:.{}]+(?:/[-a-z0-9_:.{}]+)*", re.IGNORECASE)
HEADING_RE = re.compile(r"^(#{2,4})\s+(.+?)\s*$")
ACTION_SEGMENTS = {"nuevo", "nueva", "crear", "edit", "editar", "new"}


@dataclass(frozen=True)
class RouteCheck:
    route: str
    pantalla: str
    in_backlog: bool
    reason: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def extract_routes_for_module(design01_text: str, module_slug: str) -> List[Tuple[str, str]]:
    # Returns list of (route, screen) tuples.
    module_l = module_slug.strip().lower()
    out: List[Tuple[str, str]] = []
    for line in design01_text.splitlines():
        if "|" not in line or "----" in line or ":--" in line:
            continue
        parts = [p.strip().strip("`") for p in line.strip().strip("|").split("|")]
        if len(parts) < 3:
            continue
        row_l = " ".join(parts).lower()
        if module_l not in row_l:
            continue
        # Heuristic: route table row: Ruta | Pantalla | Modulo
        route = parts[0].strip()
        pantalla = next((m.group(0).upper() for m in P_ID_RE.finditer(line)), "")
        if route.startswith("/") and pantalla:
            out.append((route, pantalla))
    # Deduplicate preserving order.
    seen: Set[Tuple[str, str]] = set()
    uniq: List[Tuple[str, str]] = []
    for it in out:
        if it in seen:
            continue
        seen.add(it)
        uniq.append(it)
    return uniq


def slice_routes_section(backlog_text: str) -> str:
    # If backlog has "### Rutas" prefer that subsection; else keep full backlog.
    lines = backlog_text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        hm = HEADING_RE.match(ln.strip())
        if hm and hm.group(2).strip().lower() == "rutas":
            start = i
            break
    if start is None:
        return backlog_text
    end = len(lines)
    for j in range(start + 1, len(lines)):
        hm = HEADING_RE.match(lines[j].strip())
        if hm and hm.group(1) == "###":
            end = j
            break
        if hm and hm.group(1) == "##":
            end = j
            break
    return "\n".join(lines[start:end])


def menu_task_present(backlog_text: str) -> bool:
    t = backlog_text.lower()
    # Keep it permissive; different projects name this differently.
    return any(k in t for k in ("enlace de menu", "enlace del menu", "sidebar", "menu ", "navegacion", "navegación"))


def screens_present_in_nav_doc(nav_text: str, screens: Sequence[str]) -> List[str]:
    nav_l = nav_text.lower()
    missing: List[str] = []
    for s in screens:
        if s.lower() not in nav_l:
            missing.append(s)
    return missing


def normalize_route_token(route: str) -> str:
    r = route.strip().strip("`'\"<>().,;")
    while r and r[-1] in ").,;`'\"":
        r = r[:-1]
    return r


def route_signature(route: str, *, drop_params: bool = True, drop_action: bool = False) -> str:
    clean = normalize_route_token(route).lower()
    if not clean.startswith("/"):
        return ""
    segments: List[str] = []
    for seg in clean.split("/"):
        if not seg:
            continue
        is_param = seg.startswith(":") or (
            (seg.startswith("{") and seg.endswith("}")) or (seg.startswith("[") and seg.endswith("]"))
        )
        if drop_params and is_param:
            continue
        segments.append(seg)
    if drop_action and segments and segments[-1] in ACTION_SEGMENTS:
        segments = segments[:-1]
    return "/" + "/".join(segments) if segments else "/"


def extract_routes_context(routes_section: str) -> Tuple[Set[str], Dict[str, List[str]]]:
    route_signatures: Set[str] = set()
    screen_to_routes: Dict[str, List[str]] = {}
    for line in routes_section.splitlines():
        routes = [normalize_route_token(m.group(0)) for m in ROUTE_RE.finditer(line)]
        routes = [r for r in routes if r.startswith("/")]
        if not routes:
            continue
        for r in routes:
            sig = route_signature(r, drop_params=True, drop_action=False)
            if sig:
                route_signatures.add(sig)
        screens = [m.group(0).upper() for m in P_ID_RE.finditer(line)]
        if not screens:
            continue
        for screen in screens:
            current = screen_to_routes.setdefault(screen, [])
            current.extend(routes)
    return route_signatures, screen_to_routes


def build_report(
    module_slug: str,
    backlog_path: Path,
    checks: Sequence[RouteCheck],
    menu_ok: bool,
    screens_missing_in_nav: Sequence[str],
) -> str:
    missing_routes = [c for c in checks if not c.in_backlog]
    lines: List[str] = []
    lines.append("# Check navegacion vs backlog")
    lines.append("")
    lines.append(f"- module: {module_slug}")
    lines.append(f"- backlog: {backlog_path.as_posix()}")
    lines.append("")
    lines.append("## Rutas")
    lines.append("")
    lines.append("| Ruta | Pantalla | En backlog | Detalle |")
    lines.append("|---|---|---|---|")
    for c in checks:
        lines.append(f"| {c.route} | {c.pantalla} | {'OK' if c.in_backlog else 'NO'} | {c.reason} |")
    lines.append("")
    lines.append("## Menu")
    lines.append("")
    lines.append(f"- task menu/sidebar: {'OK' if menu_ok else 'NO'}")
    lines.append("")
    lines.append("## Navegacion (analisis/11)")
    lines.append("")
    lines.append(f"- pantallas no encontradas (WARN): {len(screens_missing_in_nav)}")
    if screens_missing_in_nav:
        lines.append(f"- missing: {', '.join(screens_missing_in_nav)}")
    lines.append("")
    lines.append("## Resumen")
    lines.append("")
    lines.append(f"- rutas revisadas: {len(checks)}")
    lines.append(f"- rutas faltantes (ERROR): {len(missing_routes)}")
    lines.append(f"- menu faltante (ERROR): {0 if menu_ok else 1}")
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Valida rutas y tareas de menu del modulo contra el backlog.")
    p.add_argument("--backlog", type=Path, required=True)
    p.add_argument("--module-scope", dest="module_scope", required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--design01", type=Path, default=Path("design/01_technical_design.md"))
    p.add_argument("--nav", type=Path, default=Path("analisis/11_diagramas_navegacion.md"))
    return p.parse_args(list(argv))


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    backlog_path: Path = args.backlog
    module_slug: str = args.module_scope
    out_path: Path = args.out

    if not backlog_path.exists():
        raise SystemExit(f"ERROR: backlog not found: {backlog_path}")
    for dep in (args.design01, args.nav):
        if not dep.exists():
            raise SystemExit(f"ERROR: file not found: {dep}")

    design_text = read_text(args.design01)
    route_pairs = extract_routes_for_module(design_text, module_slug)
    if not route_pairs:
        raise SystemExit(f"ERROR: no routes found for module-scope='{module_slug}' in {args.design01}")

    backlog_text = read_text(backlog_path)
    routes_section = slice_routes_section(backlog_text)
    routes_l = routes_section.lower()
    route_signatures, screen_to_routes = extract_routes_context(routes_section)

    checks: List[RouteCheck] = []
    for route, pantalla in route_pairs:
        route_l = route.lower()
        sig = route_signature(route, drop_params=True, drop_action=False)
        ok = route_l in routes_l
        reason = "found"
        if not ok and sig and sig in route_signatures:
            ok = True
            reason = "found via parameterized route"
        if not ok:
            relaxed_sig = route_signature(route, drop_params=True, drop_action=True)
            screen_routes = screen_to_routes.get(pantalla, [])
            if relaxed_sig and any(
                route_signature(r, drop_params=True, drop_action=True) == relaxed_sig for r in screen_routes
            ):
                ok = True
                reason = "found via screen route variant"
        if not ok:
            reason = "missing route string"
        checks.append(RouteCheck(route=route, pantalla=pantalla, in_backlog=ok, reason=reason))

    menu_ok = menu_task_present(backlog_text)

    nav_text = read_text(args.nav)
    screens = sorted({p for _, p in route_pairs})
    screens_missing = screens_present_in_nav_doc(nav_text, screens)

    report = build_report(module_slug, backlog_path, checks, menu_ok, screens_missing)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    missing_routes = [c for c in checks if not c.in_backlog]
    return 1 if missing_routes or not menu_ok else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
