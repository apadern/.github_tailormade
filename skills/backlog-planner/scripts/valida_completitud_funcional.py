#!/usr/bin/env python3
"""
Validador de completitud funcional (por modulo) usando prototipos de UI.

Objetivo:
- Detectar acciones "especiales" (no CRUD) presentes en los prototipos (analisis/12_prototipos_interfaz.md)
  para las pantallas del modulo (segun design/01_technical_design.md) y verificar que el backlog del modulo
  menciona dichas acciones en alguna tarea.

Notas:
- Este validador NO reemplaza a la trazabilidad por IDs; complementa para evitar backlog "OK por IDs"
  pero incompleto en acciones derivadas de prototipos.
- Se centra en acciones con verbos como "probar", "validar", "restaurar", etc. para minimizar falsos positivos.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Set, Tuple
import unicodedata

sys.dont_write_bytecode = True

P_ID_RE = re.compile(r"\bP-\d{3}\b", re.IGNORECASE)
HEADING_RE = re.compile(r"^###\s+(P-\d{3})\b", re.IGNORECASE)
BRACKET_RE = re.compile(r"\[([^\[\]]+)\]")
LEADING_MARKER_RE = re.compile(r"^(?:v|x|ok|on|off)\s+", re.IGNORECASE)

STOPWORDS = {
    "de",
    "del",
    "la",
    "las",
    "el",
    "los",
    "y",
    "o",
    "a",
    "en",
    "por",
    "para",
    "con",
    "sin",
    "un",
    "una",
    "al",
}

SPECIAL_VERBS = {
    "probar",
    "validar",
    "confirmar",
    "restaurar",
    "reintentar",
    "sincronizar",
    "derivar",
    "generar",
    "descargar",
    "subir",
    "importar",
    "exportar",
    "ejecutar",
    "ver",
    "configurar",
    "reprocesar",
    "publicar",
    "previsualizar",
    "enviar",
    "activar",
    "desactivar",
    "solicitar",
    "cargar",
    "aplicar",
    "iniciar",
    "revisar",
    "aprobar",
    "rechazar",
    "asignar",
    "recalcular",
    "firmar",
    "anular",
    "desbloquear",
    "registrar",
    "corregir",
    "programar",
    "prorrogar",
    "excluir",
    "admitir",
    "notificar",
    "procesar",
    "reordenar",
    "resolver",
    "suscribirse",
    "marcar",
    "clonar",
}

GENERIC_BUTTONS = {
    "guardar",
    "guardar configuracion",
    "guardar mascara",
    "guardar reglas",
    "guardar cambios",
    "cancelar",
    "editar",
    "eliminar",
    "actualizar",
    "cerrar",
    "cerrar sesion",
    "cerrar sesión",
    "volver",
    "examinar",
    "logo",
    "usuario",
    "usuario v",
}

NON_ACTION_PREFIXES = (
    "logo",
    "usuario",
    "pdf preview",
)


@dataclass(frozen=True)
class Finding:
    pantalla: str
    action: str
    found: bool
    reason: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def norm(s: str) -> str:
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    s = s.replace("\u00a0", " ")
    return s


def strip_icons(s: str) -> str:
    # Remove common UI icon glyphs that appear in brackets.
    return re.sub(r"[⟳⚙📊✓✗✕✖✔★☆•▶◀►◄↓↑→←⚠🔴🟢🟡◐○●◉◌]", "", s).strip()


def fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s


def normalize_action_label(raw: str) -> str:
    label = norm(strip_icons(raw))
    label = label.replace("...", " ").strip()
    label = LEADING_MARKER_RE.sub("", label).strip()
    label = re.sub(r"\s+", " ", label).strip(" -:")
    return label


def tokenize(s: str) -> List[str]:
    # Fold accents to improve matching between docs and backlog (e.g., "Índice" -> "indice").
    s = fold(s)
    words = re.split(r"[^a-z0-9]+", s.lower())
    out: List[str] = []
    for w in words:
        if not w or w in STOPWORDS:
            continue
        if len(w) < 4 and w not in SPECIAL_VERBS:
            continue
        out.append(w)
    return out


def token_matches(text_l: str, token: str) -> bool:
    variants = {
        "validar": ("validar", "validacion", "validaciones"),
        "ejecutar": ("ejecutar", "ejecucion", "ejecuciones"),
        "reprocesar": ("reprocesar", "reproceso", "reprocesado", "reprocesados", "reprocesar"),
        "procesar": ("procesar", "proceso", "procesado", "procesados", "procesamiento"),
        "publicar": ("publicar", "publicacion", "publicaciones", "publicado", "publicada", "publicable"),
        "previsualizar": ("previsualizar", "previsualizacion"),
        "enviar": ("enviar", "envio", "envios", "enviado", "enviada"),
        "activar": ("activar", "activacion", "activado", "activada"),
        "desactivar": ("desactivar", "desactivacion"),
        "solicitar": ("solicitar", "solicitud", "solicitudes"),
        "cargar": ("cargar", "carga", "cargado", "cargadas"),
        "aplicar": ("aplicar", "aplicacion", "aplicado"),
        "iniciar": ("iniciar", "inicio", "inicializar"),
        "revisar": ("revisar", "revision", "revisiones"),
        "aprobar": ("aprobar", "aprobacion", "aprobado", "aprobada"),
        "rechazar": ("rechazar", "rechazo", "rechazada", "rechazado"),
        "asignar": ("asignar", "asignacion", "asignaciones", "asignado"),
        "recalcular": ("recalcular", "recalculo", "recalculado"),
        "firmar": ("firmar", "firma", "firmado"),
        "anular": ("anular", "anulacion", "anulado", "anulada"),
        "desbloquear": ("desbloquear", "desbloqueo", "desbloqueado"),
        "registrar": ("registrar", "registro", "registros"),
        "corregir": ("corregir", "correccion", "correcciones"),
        "programar": ("programar", "programacion", "programado"),
        "prorrogar": ("prorrogar", "prorroga", "prorrogado"),
        "excluir": ("excluir", "exclusion", "excluido", "excluida"),
        "admitir": ("admitir", "admision", "admitido", "admitida"),
        "notificar": ("notificar", "notificacion", "notificaciones", "notificado"),
        "resolver": ("resolver", "resolucion", "resoluciones"),
        "marcar": ("marcar", "marca", "marcado"),
        "clonar": ("clonar", "clonado"),
        "suscribirse": ("suscribir", "suscripcion", "suscrito"),
        "exportar": ("exportar", "exportacion", "exportaciones"),
        "importar": ("importar", "importacion", "importaciones"),
        "generar": ("generar", "generacion", "generado", "generada"),
        "descargar": ("descargar", "descarga", "descargado"),
        "subir": ("subir", "subida", "subido", "subidos"),
        "confirmar": ("confirmar", "confirmacion", "confirmado"),
        "ver": ("ver", "visualizar", "detalle"),
        "configurar": ("configurar",),
    }.get(token, (token,))

    # word-boundary matching to avoid false positives like "configurar" matching "configurable"
    for v in variants:
        if re.search(rf"\b{re.escape(v)}\b", text_l):
            return True
    return False


def extract_screens_for_module(design_text: str, module_slug: str) -> List[str]:
    screens: Set[str] = set()
    module_slug_l = module_slug.strip().lower()

    for line in design_text.splitlines():
        if "|" not in line:
            continue
        if "----" in line or ":--" in line:
            continue

        # Try to parse markdown table row.
        parts = [p.strip().strip("`") for p in line.strip().strip("|").split("|")]
        if len(parts) < 3:
            continue

        row_l = " ".join(parts).lower()
        if module_slug_l not in row_l:
            continue

        for m in P_ID_RE.finditer(line):
            screens.add(m.group(0).upper())

    return sorted(screens)


def slice_section_by_heading(text: str, pantalla: str) -> str:
    pantalla_u = pantalla.upper()
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        m = HEADING_RE.match(ln.strip())
        if m and m.group(1).upper() == pantalla_u:
            start = i
            break
    if start is None:
        return ""

    end = len(lines)
    for j in range(start + 1, len(lines)):
        if HEADING_RE.match(lines[j].strip()):
            end = j
            break
    return "\n".join(lines[start:end])


def extract_special_actions_from_prototype_section(section: str) -> List[str]:
    actions: Set[str] = set()
    section_l = fold(section).lower()
    for raw in BRACKET_RE.findall(section):
        label = normalize_action_label(raw)
        label_l = fold(label).lower()
        # Ignore dropdown-like controls in prototypes (commonly rendered as "[VALOR v]").
        if label_l.endswith(" v"):
            continue
        if not label_l or len(label_l) < 4:
            continue
        if label_l in GENERIC_BUTTONS:
            continue
        if any(label_l.startswith(prefix) for prefix in NON_ACTION_PREFIXES):
            continue
        if not re.search(r"[a-z]", label_l):
            continue

        tokens = tokenize(label_l)
        if not tokens:
            continue

        # Keep only "special" actions to reduce noise: must include one of the special verbs.
        if not any(v in tokens for v in SPECIAL_VERBS):
            continue

        # Drop very generic "ver" unless it is clearly a non-trivial action.
        if tokens == ["ver"] or (tokens and tokens[0] == "ver" and len(tokens) == 1):
            continue
        if tokens and tokens[0] == "ver" and not any(t in tokens for t in ("logs", "historico", "configuracion", "detalle", "discrepancias")):
            continue

        actions.add(label)

    # Derive non-button obligations from prototype content (best-effort).
    # These often show up as text blocks (not bracketed buttons) but still require backlog tasks.
    if "auditor" in section_l:
        actions.add("Auditoria de Cambios")
    if "justific" in section_l:
        actions.add("Justificacion")
    if "doble confirm" in section_l:
        actions.add("Doble confirmacion")
    if "confirm" in section_l and "impact" in section_l:
        actions.add("Confirmacion de impacto")
    return sorted(actions)


def action_covered_in_backlog(backlog_text_l: str, action: str) -> Tuple[bool, str]:
    action_l = fold(action).lower()
    if action_l in backlog_text_l:
        return True, "substring"

    tokens = tokenize(action_l)
    if not tokens:
        return False, "no tokens"

    # Prefer actions to match their verb + all significant tokens, allowing one optional miss only for >=3 tokens.
    matched = [t for t in tokens if token_matches(backlog_text_l, t)]
    required = len(tokens) if len(tokens) <= 2 else (len(tokens) - 1)
    if len(matched) >= required:
        return True, f"tokens: {', '.join(tokens)}"

    return False, f"missing tokens: {', '.join(tokens) if tokens else '(no tokens)'}"


def build_report(module_slug: str, backlog_path: Path, findings: Sequence[Finding], screens: Sequence[str]) -> str:
    missing = [f for f in findings if not f.found]
    lines: List[str] = []
    lines.append("# Check completitud funcional (prototipos)")
    lines.append("")
    lines.append(f"- module: {module_slug}")
    lines.append(f"- backlog: {backlog_path.as_posix()}")
    lines.append(f"- pantallas: {', '.join(screens) if screens else '(none)'}")
    lines.append("")
    lines.append("## Resultados")
    lines.append("")
    lines.append("| Pantalla | Accion (prototipo) | En backlog | Detalle |")
    lines.append("|---|---|---|---|")
    for f in findings:
        lines.append(f"| {f.pantalla} | {f.action} | {'OK' if f.found else 'NO'} | {f.reason} |")
    lines.append("")
    lines.append("## Resumen")
    lines.append("")
    lines.append(f"- acciones revisadas: {len(findings)}")
    lines.append(f"- faltantes: {len(missing)}")
    lines.append("")
    if missing:
        lines.append("### Acciones faltantes (sugerencia)")
        lines.append("")
        for f in missing:
            tok = tokenize(f.action.lower())
            example_fn = f"on{tok[0].title()}" if tok else "onAction"
            lines.append(f"- {f.pantalla} :: {f.action}")
            lines.append(f"  - UI5: implementar accion/boton/flujo \"{f.action}\" en XML View/controller de la pantalla {f.pantalla} (busy/error + feedback).")
            lines.append(f"  - Estado UI: añadir handler dedicado (p.ej. `{example_fn}`) y actualizar `viewModel.js`/JSONModel con el resultado.")
            lines.append("  - Servicio (mock/backend): añadir metodo en `*ServiceMock.js` y `*Service.js` o reutilizar la operacion OData/API existente si ya esta en design/03.")
            lines.append("  - Backend (si aplica): exponer action/operacion CAP, RAP o ABAP equivalente para la accion y validar permisos/errores.")
            lines.append(f"  - Tests E2E: añadir caso OPA5 alineado con `ui5-test-generator` que ejecute \"{f.action}\" y valide resultado visible.")
        lines.append("")
    return "\n".join(lines)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Valida completitud funcional del backlog por acciones de prototipos (por modulo).")
    p.add_argument("--backlog", type=Path, required=True, help="Ruta al backlog del modulo.")
    p.add_argument("--module-scope", dest="module_scope", required=True, help="Slug del modulo (segun design/01).")
    p.add_argument("--out", type=Path, required=True, help="Ruta del reporte markdown.")
    p.add_argument("--design", type=Path, default=Path("design/01_technical_design.md"), help="Ruta a design/01_technical_design.md")
    p.add_argument("--prototypes", type=Path, default=Path("analisis/12_prototipos_interfaz.md"), help="Ruta a analisis/12_prototipos_interfaz.md")
    return p.parse_args(list(argv))


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    backlog_path: Path = args.backlog
    module_slug: str = args.module_scope
    out_path: Path = args.out
    design_path: Path = args.design
    prototypes_path: Path = args.prototypes

    if not backlog_path.exists():
        raise SystemExit(f"ERROR: backlog no existe: {backlog_path}")
    if not design_path.exists():
        raise SystemExit(f"ERROR: design no existe: {design_path}")
    if not prototypes_path.exists():
        raise SystemExit(f"ERROR: prototipos no existe: {prototypes_path}")

    design_text = read_text(design_path)
    screens = extract_screens_for_module(design_text, module_slug)
    if not screens:
        raise SystemExit(f"ERROR: no se encontraron pantallas P-XXX para module-scope='{module_slug}' en {design_path}")

    proto_text = read_text(prototypes_path)
    backlog_text = read_text(backlog_path)
    # Fold accents for more robust matching.
    backlog_text_l = fold(backlog_text).lower()
    backlog_lines = backlog_text.splitlines()

    findings: List[Finding] = []
    for pantalla in screens:
        section = slice_section_by_heading(proto_text, pantalla)
        if not section:
            # Missing prototype section: report but do not fail hard (some projects may not prototype all screens).
            findings.append(Finding(pantalla=pantalla, action="(prototype section missing)", found=True, reason="skip"))
            continue
        actions = extract_special_actions_from_prototype_section(section)
        for action in actions:
            # Reduce false positives: check coverage within the backlog lines that reference the screen.
            pantalla_u = pantalla.upper()
            screen_scoped_text = "\n".join(
                ln for ln in backlog_lines
                if pantalla_u in ln or f"Pantalla {pantalla_u}" in ln
            )
            screen_scoped_text_l = fold(screen_scoped_text).lower()
            search_text = screen_scoped_text_l if screen_scoped_text_l.strip() else backlog_text_l
            ok, reason = action_covered_in_backlog(search_text, action)
            findings.append(Finding(pantalla=pantalla, action=action, found=ok, reason=reason))

    report = build_report(module_slug, backlog_path, findings, screens)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    missing = [f for f in findings if not f.found]
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
