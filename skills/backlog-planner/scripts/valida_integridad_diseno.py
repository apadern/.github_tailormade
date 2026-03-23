#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Validador de integridad Backlog <-> Diseño (por módulo).

Valida que un fichero de backlog del módulo contenga tareas que cubran:
- Rutas UI del módulo (design/01_technical_design.md -> "Rutas UI (Frontend)")
- Servicios expuestos del módulo (design/01_technical_design.md -> tabla de endpoints/servicios API u OData del backend)
- Entidades del módulo (design/02_data_model.md -> "Catálogo de Entidades")
- Enums asociados a entidades del módulo (design/02_data_model.md -> "Detalle por Entidad")
- Servicios del módulo (design/03_data_services.md -> "Catálogo de Servicios")

Uso:
    python skills/backlog-planner/scripts/valida_integridad_diseno.py ^
    --backlog backlog/03_configuracion.md ^
    --module-scope configuracion
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

sys.dont_write_bytecode = True

TASK_LINE_RE = re.compile(r"^\s*-\s*\[[xX ]\]\s+")
HEADING_RE = re.compile(r"^(?P<level>#{1,6})\s+(?P<title>.+?)\s*$")
SECTION_PREFIX_RE = re.compile(r"^\d+(?:\.\d+)*(?:[.)])?\s*")
BACKTICK_TOKEN_RE = re.compile(r"`([^`]+)`")
KIND_ROUTES_UI = "Rutas UI"
KIND_ENDPOINTS_API = "Endpoints API"
KIND_ENTITIES = "Entidades"
KIND_ENUMS = "Enums"
KIND_SERVICES = "Servicios"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def strip_md_code(s: str) -> str:
    s = s.strip()
    if s.startswith("`") and s.endswith("`") and len(s) >= 2:
        return s[1:-1].strip()
    return s


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.casefold()
    s = re.sub(r"\s+", " ", s).strip()
    return s


def strip_section_prefix(s: str) -> str:
    return SECTION_PREFIX_RE.sub("", s).strip()


def iter_backtick_basenames(task: str) -> Iterable[str]:
    for token in BACKTICK_TOKEN_RE.findall(task):
        token = token.strip()
        if not token:
            continue
        yield token.replace("\\", "/").split("/")[-1]


def matches_identifier_basename(basename: str, identifier: str, suffixes: Sequence[str]) -> bool:
    basename_n = norm(basename)
    identifier_n = norm(identifier)
    targets = {identifier_n, *(norm(f"{identifier}{suffix}") for suffix in suffixes)}
    return basename_n in targets or identifier_n in basename_n


def first_matching_artifact_task(
    tasks: Sequence[str],
    identifier: str,
    hint_re: re.Pattern[str],
    suffixes: Sequence[str],
) -> Optional[str]:
    identifier_n = norm(identifier)
    if not identifier_n:
        return None
    for task in tasks:
        task_n = norm(task)
        if identifier_n not in task_n:
            continue
        if any(matches_identifier_basename(basename, identifier, suffixes) for basename in iter_backtick_basenames(task)):
            return task
        if hint_re.search(task) and first_matching_identifier_task((task,), identifier):
            return task
    return first_matching_identifier_task(tasks, identifier)


def extract_task_lines(backlog_md: str) -> List[str]:
    tasks: List[str] = []
    for line in backlog_md.splitlines():
        if TASK_LINE_RE.match(line):
            tasks.append(line.strip())
    return tasks


def find_heading_index(lines: Sequence[str], heading_text: str) -> Optional[int]:
    target = norm(heading_text)
    target_no_prefix = strip_section_prefix(target)
    for i, line in enumerate(lines):
        m = HEADING_RE.match(line.strip())
        if not m:
            continue
        title = norm(m.group("title"))
        title_no_prefix = strip_section_prefix(title)
        if (
            title == target
            or title_no_prefix == target
            or title == target_no_prefix
            or title_no_prefix == target_no_prefix
        ):
            return i
    return None


def parse_table_after_heading(
    lines: Sequence[str],
    heading_text: str,
    required_header_tokens: Sequence[str],
) -> Tuple[List[str], List[List[str]]]:
    heading_idx = find_heading_index(lines, heading_text)
    if heading_idx is None:
        raise ValueError(f"No se encontró el heading '{heading_text}'.")

    required_header_tokens_norm = [norm(t) for t in required_header_tokens]

    header_idx: Optional[int] = None
    for i in range(heading_idx + 1, len(lines) - 1):
        line = lines[i].strip()
        if not line.startswith("|"):
            continue
        header_norm = norm(line)
        if all(tok in header_norm for tok in required_header_tokens_norm):
            header_idx = i
            break

    if header_idx is None:
        raise ValueError(f"No se encontró una tabla tras '{heading_text}'.")

    header_line = lines[header_idx].strip()
    headers = [c.strip() for c in header_line.strip().strip("|").split("|")]

    rows: List[List[str]] = []
    for j in range(header_idx + 2, len(lines)):
        row_line = lines[j].strip()
        if not row_line.startswith("|"):
            break
        cells = [c.strip() for c in row_line.strip().strip("|").split("|")]
        if len(cells) < len(headers):
            # Filas de "título de grupo" (p.ej. | **Auth** |) u otras inconsistencias.
            continue
        rows.append(cells[: len(headers)])
    return headers, rows


def parse_table_after_heading_options(
    lines: Sequence[str],
    heading_options: Sequence[str],
    required_header_token_options: Sequence[Sequence[str]],
) -> Tuple[List[str], List[List[str]]]:
    errors: List[str] = []
    for heading_text in heading_options:
        for required_tokens in required_header_token_options:
            try:
                return parse_table_after_heading(lines, heading_text, required_tokens)
            except ValueError as exc:
                errors.append(str(exc))
    headings = ", ".join(heading_options)
    raise ValueError(f"No se encontró una tabla compatible tras ninguno de estos headings: {headings}. Detalle: {' | '.join(errors)}")


def find_header_index(headers: Sequence[str], candidates: Sequence[str]) -> int:
    headers_norm = [norm(h) for h in headers]
    for candidate in candidates:
        candidate_norm = norm(candidate)
        for idx, header in enumerate(headers_norm):
            if candidate_norm == header or candidate_norm in header:
                return idx
    raise ValueError(f"No se encontró ninguna columna compatible con {candidates} en headers {headers}")


def extract_ui_routes(design01_md: str, module_scope: str) -> List[str]:
    lines = design01_md.splitlines()
    _, rows = parse_table_after_heading(
        lines,
        heading_text=KIND_ROUTES_UI + " (Frontend)",
        required_header_tokens=("Ruta", "Pantalla", "Modulo"),
    )
    out: List[str] = []
    for r in rows:
        # | Ruta | Pantalla | Módulo | Descripción |
        route = strip_md_code(r[0])
        module = strip_md_code(r[2])
        if norm(module) == norm(module_scope):
            out.append(route)
    return sorted(set(out))


def extract_api_endpoints(design01_md: str, module_scope: str) -> List[Tuple[str, str]]:
    lines = design01_md.splitlines()
    headers, rows = parse_table_after_heading_options(
        lines,
        heading_options=(
            "Endpoints API (Backend)",
            "Servicios API/OData (Backend)",
            "Servicios OData/API (Backend)",
            "Servicios expuestos (Backend)",
        ),
        required_header_token_options=(
            ("Metodo", "Endpoint", "Modulo"),
            ("Metodo", "Servicio", "Modulo"),
            ("Operacion", "Endpoint", "Modulo"),
            ("Operacion", "Servicio", "Modulo"),
        ),
    )
    method_idx = find_header_index(headers, ("Metodo", "Metodo HTTP", "Operacion", "Action"))
    endpoint_idx = find_header_index(headers, ("Endpoint", "Servicio", "Ruta", "Path"))
    module_idx = find_header_index(headers, ("Modulo",))
    out: List[Tuple[str, str]] = []
    for r in rows:
        method = strip_md_code(r[method_idx])
        endpoint = strip_md_code(r[endpoint_idx])
        module = strip_md_code(r[module_idx])
        if not method or method.startswith("**"):
            continue
        if norm(module) == norm(module_scope):
            out.append((method.upper(), endpoint))
    out = sorted(set(out), key=lambda x: (x[1], x[0]))
    return out


def extract_entities(design02_md: str, module_scope: str) -> Dict[str, str]:
    lines = design02_md.splitlines()
    _, rows = parse_table_after_heading(
        lines,
        heading_text="1. Catalogo de Entidades",
        required_header_tokens=("Entidad", "Modulo"),
    )
    entities: Dict[str, str] = {}
    for r in rows:
        # | Entidad | Descripción | Módulo |
        entity = strip_md_code(r[0])
        module = strip_md_code(r[2])
        if norm(module) == norm(module_scope):
            entities[entity] = module
    return dict(sorted(entities.items(), key=lambda kv: norm(kv[0])))


ENUMS_ASSOC_LABEL_RE = re.compile(r"^\*\*Enums asociados:\*\*\s*$", re.MULTILINE)


def extract_entity_enums(design02_md: str, entities: Iterable[str]) -> Dict[str, List[str]]:
    lines = design02_md.splitlines()
    entity_set = set(entities)
    out: Dict[str, List[str]] = {e: [] for e in entity_set}

    # Indexar heading "### {Entidad}"
    heading_to_index: Dict[str, int] = {}
    for i, line in enumerate(lines):
        m = HEADING_RE.match(line.strip())
        if not m or m.group("level") != "###":
            continue
        title = m.group("title").strip()
        if title in entity_set:
            heading_to_index[title] = i

    for entity, start_idx in heading_to_index.items():
        # Buscar bloque hasta la siguiente sección ### o ##
        end_idx = len(lines)
        for j in range(start_idx + 1, len(lines)):
            m = HEADING_RE.match(lines[j].strip())
            if m and m.group("level") in ("##", "###"):
                end_idx = j
                break
        block = "\n".join(lines[start_idx:end_idx])
        m = ENUMS_ASSOC_LABEL_RE.search(block)
        if not m:
            continue
        after = block[m.end() :].splitlines()
        enums: List[str] = []
        started = False
        for line in after:
            s = line.strip()
            if not s:
                if started:
                    break
                continue
            if s.startswith("---"):
                break
            if s.startswith("-") or s.startswith("*"):
                started = True
                item = s.lstrip("-*").strip()
                # Aceptar notaciones comunes para "no aplica" / "sin enums" para evitar falsos positivos.
                if norm(item) in {"ninguno", "n/a", "na", "no aplica", "no-aplica"}:
                    continue
                enums.append(strip_md_code(item))
            elif s.startswith("#"):
                break
            else:
                # Otra cosa distinta de lista: cortar.
                break
        out[entity] = sorted(set(enums), key=norm)

    return out


def extract_services(design03_md: str, module_scope: str) -> List[str]:
    lines = design03_md.splitlines()
    _, rows = parse_table_after_heading(
        lines,
        heading_text="1. Catalogo de Servicios",
        required_header_tokens=("Servicio", "Modulo"),
    )
    out: List[str] = []
    for r in rows:
        # | Servicio | Entidad Principal | Módulo | Descripción |
        service = strip_md_code(r[0])
        module = strip_md_code(r[2])
        if norm(module) == norm(module_scope):
            out.append(service)
    return sorted(set(out), key=norm)


@dataclass(frozen=True)
class CheckResult:
    kind: str
    expected: str
    found: bool
    matched_task: Optional[str] = None
    note: Optional[str] = None


def first_matching_task(tasks: Sequence[str], needle: str) -> Optional[str]:
    needle_n = norm(needle)
    for t in tasks:
        if needle_n and needle_n in norm(t):
            return t
    return None


def first_matching_identifier_task(tasks: Sequence[str], identifier: str) -> Optional[str]:
    ident_n = norm(identifier)
    if not ident_n:
        return None
    pat = re.compile(rf"(?<![a-z0-9_]){re.escape(ident_n)}(?![a-z0-9_])")
    for t in tasks:
        if pat.search(norm(t)):
            return t
    return None


def first_matching_entity_task(tasks: Sequence[str], entity: str) -> Optional[str]:
    entity_hint_re = re.compile(
        r"\b(entity|entidad|tabla|cds|projection|proyeccion|view|vista|behavior|bdef|ddic|rap)\b",
        re.IGNORECASE,
    )
    return first_matching_artifact_task(tasks, entity, entity_hint_re, (".java", ".cds"))


def first_matching_enum_task(tasks: Sequence[str], enum_name: str) -> Optional[str]:
    enum_n = norm(enum_name)
    if not enum_n:
        return None
    enum_re = re.compile(r"\b(enum|constante|constantes|dominio|catalogo|catalogo de valores|tipo)\b", re.IGNORECASE)
    for t in tasks:
        if enum_n not in norm(t) or not enum_re.search(t):
            continue
        for token in iter_backtick_basenames(t):
            token_n = norm(token)
            if token_n == enum_n or enum_n in token_n:
                return t
        if first_matching_identifier_task((t,), enum_name):
            return t
    return first_matching_identifier_task(tasks, enum_name)


def first_matching_service_task(tasks: Sequence[str], service: str) -> Optional[str]:
    service_hint_re = re.compile(
        r"\b(service|servicio|handler|binding|action|accion|function|funcion|cds)\b",
        re.IGNORECASE,
    )
    return first_matching_artifact_task(tasks, service, service_hint_re, (".java", ".cds", ".js", ".ts"))


def first_matching_route_task(tasks: Sequence[str], route: str) -> Optional[str]:
    route_n = norm(route)
    if not route_n:
        return None
    candidates: List[str] = []
    for t in tasks:
        if route_n in norm(t):
            candidates.append(t)
    if not candidates:
        return None
    # Evitar falsos positivos: base paths de services o menciones incidentales.
    strong_hints = (
        "agregar ruta",
        "manifest.json",
        "routing",
        "target",
        "sidebar",
        "shell",
        "navegacion",
        "navegación",
        "pagina",
        "página",
        "view.xml",
        "controller.js",
    )
    for hint in strong_hints:
        hint_n = norm(hint)
        for t in candidates:
            if hint_n in norm(t):
                return t
    # Si solo aparece como cadena suelta, no considerarlo evidencia suficiente para UI routes.
    return None


def first_matching_endpoint_task(tasks: Sequence[str], method: str, path: str) -> Tuple[Optional[str], Optional[str]]:
    path_n = norm(path)
    method_n = norm(method)
    method_re = re.compile(rf"\b{re.escape(method_n)}\b")
    path_only_match: Optional[str] = None
    for t in tasks:
        t_n = norm(t)
        if path_n and path_n in t_n:
            if method_re.search(t_n):
                return t, None
            if path_only_match is None:
                path_only_match = t
    if path_only_match is not None:
        return path_only_match, "Encontrado por path; no aparece el método en la misma tarea."
    return None, None


def derive_default_out(backlog_path: Path, module_scope: str) -> Path:
    m = re.match(r"^(?P<ord>\d{2})_(?P<slug>.+)\.md$", backlog_path.name, re.IGNORECASE)
    if m:
        ord_ = m.group("ord")
        slug = m.group("slug")
        return backlog_path.parent / f"check_design_{ord_}_{slug}.md"
    safe_module = re.sub(r"[^a-zA-Z0-9_-]+", "_", module_scope.strip()) or "modulo"
    return backlog_path.parent / f"check_design_00_{safe_module}.md"


def make_report(
    *,
    module_scope: str,
    backlog_path: Path,
    out_path: Path,
    design01_path: Path,
    design02_path: Path,
    design03_path: Path,
    results: Sequence[CheckResult],
    expected_counts: Dict[str, int],
) -> str:
    errors = [r for r in results if not r.found]
    warns = [r for r in results if r.found and r.note]

    def section_summary(kind: str) -> str:
        exp = expected_counts.get(kind, 0)
        missing = sum(1 for r in results if r.kind == kind and not r.found)
        return f"- {kind}: esperados {exp}, faltan {missing}"

    lines: List[str] = []
    lines.append(f"# Check diseño vs backlog (módulo: `{module_scope}`)")
    lines.append("")
    lines.append(f"- Fecha: {date.today().isoformat()}")
    lines.append(f"- Backlog: `{backlog_path.as_posix()}`")
    lines.append(f"- Output: `{out_path.as_posix()}`")
    lines.append(f"- Diseño: `{design01_path.as_posix()}`, `{design02_path.as_posix()}`, `{design03_path.as_posix()}`")
    lines.append("")
    lines.append("## Resumen")
    lines.append(section_summary(KIND_ROUTES_UI))
    lines.append(section_summary(KIND_ENDPOINTS_API))
    lines.append(section_summary(KIND_ENTITIES))
    lines.append(section_summary(KIND_ENUMS))
    lines.append(section_summary(KIND_SERVICES))
    lines.append("")
    lines.append(f"- Errores: {len(errors)}")
    lines.append(f"- Avisos: {len(warns)}")
    lines.append("")

    if errors:
        lines.append("## Errores (faltan tareas en backlog)")
        for r in errors:
            lines.append(f"- [{r.kind}] {r.expected}")
        lines.append("")

    if warns:
        lines.append("## Avisos")
        for r in warns:
            lines.append(f"- [{r.kind}] {r.expected} — {r.note}")
        lines.append("")

    lines.append("## Evidencias (tarea encontrada)")
    for r in results:
        if r.found and r.matched_task:
            lines.append(f"- [{r.kind}] {r.expected}")
            lines.append(f"  - {r.matched_task}")
    lines.append("")
    lines.append("## Nota")
    lines.append("- La búsqueda se limita a líneas de tareas con checkbox (`- [ ]` / `- [x]`).")
    lines.append("- Para servicios expuestos, se valida por path o endpoint; si no aparece la operación en la misma tarea, se emite aviso.")
    lines.append("")
    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Valida integridad Backlog <-> Diseño (por módulo).")
    parser.add_argument("--backlog", type=Path, required=True, help="Fichero de backlog a validar (markdown).")
    parser.add_argument("--module-scope", required=True, help="Slug del módulo (p.ej. configuracion).")
    parser.add_argument("--design01", type=Path, default=Path("design/01_technical_design.md"))
    parser.add_argument("--design02", type=Path, default=Path("design/02_data_model.md"))
    parser.add_argument("--design03", type=Path, default=Path("design/03_data_services.md"))
    parser.add_argument("--out", type=Path, default=None, help="Ruta de salida del informe (markdown).")
    args = parser.parse_args(argv)

    backlog_path: Path = args.backlog
    module_scope: str = args.module_scope
    design01_path: Path = args.design01
    design02_path: Path = args.design02
    design03_path: Path = args.design03
    out_path: Path = args.out or derive_default_out(backlog_path, module_scope)

    if not backlog_path.exists():
        raise SystemExit(f"Backlog no existe: {backlog_path}")
    if not design01_path.exists():
        raise SystemExit(f"Diseño 01 no existe: {design01_path}")
    if not design02_path.exists():
        raise SystemExit(f"Diseño 02 no existe: {design02_path}")
    if not design03_path.exists():
        raise SystemExit(f"Diseño 03 no existe: {design03_path}")

    backlog_md = read_text(backlog_path)
    tasks = extract_task_lines(backlog_md)

    design01_md = read_text(design01_path)
    design02_md = read_text(design02_path)
    design03_md = read_text(design03_path)

    ui_routes = extract_ui_routes(design01_md, module_scope)
    api_endpoints = extract_api_endpoints(design01_md, module_scope)
    entities = extract_entities(design02_md, module_scope)
    entity_enums = extract_entity_enums(design02_md, entities.keys())
    services = extract_services(design03_md, module_scope)

    results: List[CheckResult] = []

    expected_counts: Dict[str, int] = {
        KIND_ROUTES_UI: len(ui_routes),
        KIND_ENDPOINTS_API: len(api_endpoints),
        KIND_ENTITIES: len(entities),
        KIND_ENUMS: len({e for enums in entity_enums.values() for e in enums}),
        KIND_SERVICES: len(services),
    }

    for route in ui_routes:
        mt = first_matching_route_task(tasks, route)
        results.append(CheckResult(kind=KIND_ROUTES_UI, expected=route, found=mt is not None, matched_task=mt))

    for method, path in api_endpoints:
        mt, note = first_matching_endpoint_task(tasks, method, path)
        results.append(
            CheckResult(
                kind=KIND_ENDPOINTS_API,
                expected=f"{method} {path}",
                found=mt is not None,
                matched_task=mt,
                note=note,
            )
        )

    for entity in entities.keys():
        mt = first_matching_entity_task(tasks, entity)
        results.append(CheckResult(kind=KIND_ENTITIES, expected=entity, found=mt is not None, matched_task=mt))

    enum_set = sorted({e for enums in entity_enums.values() for e in enums}, key=norm)
    for enum_name in enum_set:
        mt = first_matching_enum_task(tasks, enum_name)
        results.append(CheckResult(kind=KIND_ENUMS, expected=enum_name, found=mt is not None, matched_task=mt))

    for service in services:
        mt = first_matching_service_task(tasks, service)
        results.append(CheckResult(kind=KIND_SERVICES, expected=service, found=mt is not None, matched_task=mt))

    report = make_report(
        module_scope=module_scope,
        backlog_path=backlog_path,
        out_path=out_path,
        design01_path=design01_path,
        design02_path=design02_path,
        design03_path=design03_path,
        results=results,
        expected_counts=expected_counts,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    error_count = sum(1 for r in results if not r.found)
    warn_count = sum(1 for r in results if r.found and r.note)
    print(f"OK: informe generado en {out_path} | errores={error_count} | avisos={warn_count} | tareas_analizadas={len(tasks)}")
    return 1 if error_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
