#!/usr/bin/env python3
"""
HU completeness validator (module-scope).

Checks, for the given module:
- Which HUs belong to it (derived from design/01 RF->module and analisis/14 matrix RF->HU).
- That each HU is present in the backlog, and that it appears in Backend, Frontend and Tests E2E sections.
- (Soft) Criteria coverage: heuristically checks keywords from HU acceptance criteria against tasks referencing the HU.

This is meant to complement ID coverage: it catches "HU referenced once" backlogs that miss work in a whole area.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

sys.dont_write_bytecode = True

RF_ID_RE = re.compile(r"\bRF-(\d{3})\b", re.IGNORECASE)
HU_ID_RE = re.compile(r"\bHU-\d{3}\b", re.IGNORECASE)

MATRIX_ROW_RE = re.compile(r"^\|\s*\*\*?(RF-\d{3})", re.IGNORECASE)

HU_HEADING_RE = re.compile(r"^####\s+.*?(HU-\d{3})\b", re.IGNORECASE)
CRITERIA_START_RE = re.compile(r"^\*\*?Criterios de aceptaci", re.IGNORECASE)
BULLET_CRITERIA_RE = re.compile(r"^\s*-\s*\[\s*[xX ]\s*\]\s*(.+?)\s*$")
RELATED_RFS_RE = re.compile(r"^\*\*ID Requerimientos relacionados:\*\*\s*(.+?)\s*$", re.IGNORECASE)
PF_ID_RE = re.compile(r"\bPF-\d{3}\b", re.IGNORECASE)
PF_ROW_RE = re.compile(r"^\|\s*\*\*?PF-\d{3}\*?\*", re.IGNORECASE)

HEADING_RE = re.compile(r"^(#{2,4})\s+(.+?)\s*$")

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
    "se",
    "su",
    "sus",
    "que",
}

GENERIC_WORDS = {
    "sistema",
    "permite",
    "permitir",
    "configura",
    "configurar",
    "parametriza",
    "parametrizar",
    "interfaz",
    "cambios",
    "registra",
    "registrar",
    "usuario",
    "fecha",
    "hora",
    "automaticamente",
    "automatica",
    "automático",
    "automático",
    "aplica",
    "aplicar",
}


@dataclass(frozen=True)
class HuCheck:
    hu_id: str
    in_backlog: bool
    in_backend: bool
    in_frontend: bool
    in_tests: bool
    criteria_total: int
    criteria_mapped: int
    criteria_unmapped: int
    unmapped_details: Tuple[str, ...]
    pf_total: int
    pf_missing_in_tests: int


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def norm(s: str) -> str:
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    return s


def tokenize(text: str) -> List[str]:
    words = re.split(r"[^a-z0-9áéíóúñü]+", text.lower())
    out: List[str] = []
    for w in words:
        w = w.strip()
        if not w or w in STOPWORDS:
            continue
        if len(w) < 4:
            continue
        if w in GENERIC_WORDS:
            continue
        out.append(w)
    return out


def tokenize_mapping(text: str) -> List[str]:
    """
    Less aggressive tokenization for mapping HU criteria -> PF criteria column.
    Keep domain-generic verbs like 'configurar' because they appear in PF criteria.
    """
    def fold_accents(s: str) -> str:
        return "".join(ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch))

    def canonical_token(w: str) -> str:
        w = fold_accents(w)
        # Singularize simple plurals (carpetas->carpeta, fallos->fallo) to improve matches.
        if len(w) >= 5 and w.endswith("s"):
            w = w[:-1]
        if len(w) >= 7 and w.endswith("es"):
            w = w[:-2]
        # Light verb normalization (procesar->proces, procesa->proces) to reduce false unmapped.
        for suf in ("ando", "iendo"):
            if len(w) >= 7 and w.endswith(suf):
                w = w[: -len(suf)]
                break
        for suf in ("ar", "er", "ir"):
            if len(w) >= 6 and w.endswith(suf):
                w = w[: -len(suf)]
                break
        return w

    words = re.split(r"[^a-z0-9áéíóúñü]+", text.lower())
    out: List[str] = []
    for w in words:
        w = w.strip()
        if not w or w in STOPWORDS:
            continue
        if len(w) < 3:
            continue
        out.append(canonical_token(w))
    return out


def parse_pf_rows(pf_text: str) -> List[Tuple[str, str, str]]:
    """
    Returns list of tuples: (pf_id, hu_id, criteria_text_from_pf_doc)

    NOTE: we concatenate "Criterios de Aceptación" + "Resultado Esperado" to make
    HU criterio -> PF mapping more robust (wording differs between sources).
    """
    rows: List[Tuple[str, str, str]] = []
    for line in pf_text.splitlines():
        if "|" not in line:
            continue
        if not PF_ID_RE.search(line):
            continue
        if "---" in line and "PF" in line:
            continue

        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 6:
            continue

        pf_match = PF_ID_RE.search(parts[0])
        if not pf_match:
            continue
        pf_id = pf_match.group(0).upper()

        hu_match = HU_ID_RE.search(parts[1])
        if not hu_match:
            continue
        hu_id = hu_match.group(0).upper()

        # Expected shape: ... | Criterios de Aceptación | Resultado Esperado |
        criteria_col = parts[4]
        expected_col = parts[5] if len(parts) >= 6 else ""
        rows.append((pf_id, hu_id, norm(f"{criteria_col} {expected_col}")))

    return rows


def best_pf_match_for_criterion(criterion: str, pf_candidates: Sequence[Tuple[str, str]]) -> Tuple[Optional[str], float]:
    """
    pf_candidates: sequence of (pf_id, pf_criteria_text)
    Returns (pf_id, score) where score is overlap ratio [0..1]
    """
    crit_tokens = set(tokenize_mapping(criterion))
    if not crit_tokens:
        return None, 0.0

    best_pf: Optional[str] = None
    best_score = 0.0
    for pf_id, pf_crit in pf_candidates:
        pf_tokens = set(tokenize_mapping(pf_crit))
        if not pf_tokens:
            continue
        overlap = len(crit_tokens & pf_tokens)
        # F1-style score balances short-vs-long texts better than min(len).
        precision = overlap / max(1, len(pf_tokens))
        recall = overlap / max(1, len(crit_tokens))
        score = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
        if score > best_score:
            best_score = score
            best_pf = pf_id
    return best_pf, best_score


def expand_rf_range(tokens: Sequence[str]) -> List[str]:
    # Supports patterns like "RF-052 a RF-055" or "RF-052 - RF-055".
    rfs = [int(m.group(1)) for t in tokens for m in RF_ID_RE.finditer(t)]
    if len(rfs) >= 2 and any(sep in " ".join(tokens).lower() for sep in (" a ", " - ", "–", "—", "to")):
        start, end = rfs[0], rfs[1]
        if start <= end and (end - start) <= 50:
            return [f"RF-{i:03d}" for i in range(start, end + 1)]
    # Fallback: distinct RFs found.
    return sorted({f"RF-{i:03d}" for i in rfs})


def rfs_for_module_from_design01(design_text: str, module_slug: str) -> List[str]:
    module_l = module_slug.strip().lower()
    for line in design_text.splitlines():
        if "|" not in line or "----" in line or ":--" in line:
            continue
        parts = [p.strip().strip("`").strip("*") for p in line.strip().strip("|").split("|")]
        if len(parts) < 3:
            continue
        if parts[0].strip().lower() != module_l:
            continue
        # RFs are usually in last column.
        rf_col = parts[-1]
        tokens = [rf_col]
        return expand_rf_range(tokens)
    return []


def hus_for_rfs_from_matrix(matrix_text: str, rf_ids: Sequence[str]) -> List[str]:
    rf_set = {rf.upper() for rf in rf_ids}
    hus: Set[str] = set()
    for line in matrix_text.splitlines():
        m = MATRIX_ROW_RE.match(line.strip())
        if not m:
            continue
        rf = m.group(1).upper()
        if rf not in rf_set:
            continue
        for hu in HU_ID_RE.findall(line):
            hus.add(hu.upper())
    return sorted(hus)


def extract_hu_criteria(hu_text: str, hu_ids: Sequence[str]) -> Dict[str, List[str]]:
    hu_set = {h.upper() for h in hu_ids}
    lines = hu_text.splitlines()
    result: Dict[str, List[str]] = {h: [] for h in hu_set}

    current: Optional[str] = None
    in_criteria = False
    for ln in lines:
        m = HU_HEADING_RE.match(ln.strip())
        if m:
            current = m.group(1).upper()
            in_criteria = False
            continue
        if current is None or current not in hu_set:
            continue
        if CRITERIA_START_RE.search(ln):
            in_criteria = True
            continue
        if in_criteria:
            # Stop when we reach another bold section or empty line before next heading.
            if ln.strip().startswith("**ID Requerimientos"):
                in_criteria = False
                continue
            bm = BULLET_CRITERIA_RE.match(ln)
            if bm:
                result[current].append(norm(bm.group(1)))
            elif ln.strip().startswith("**") and "Requerimientos" in ln:
                in_criteria = False
    return result


def extract_hu_related_rfs(hu_text: str, hu_ids: Sequence[str]) -> Dict[str, List[str]]:
    hu_set = {h.upper() for h in hu_ids}
    lines = hu_text.splitlines()
    result: Dict[str, List[str]] = {h: [] for h in hu_set}

    current: Optional[str] = None
    for ln in lines:
        m = HU_HEADING_RE.match(ln.strip())
        if m:
            current = m.group(1).upper()
            continue
        if current is None or current not in hu_set:
            continue
        rm = RELATED_RFS_RE.match(ln.strip())
        if rm:
            rfs = [f"RF-{int(x):03d}" for x in re.findall(r"\bRF-(\d{3})\b", rm.group(1), flags=re.IGNORECASE)]
            result[current] = sorted(set(rfs))
    return result


def extract_pfs_for_hu(pf_text: str, hu_id: str) -> List[str]:
    hu_u = hu_id.upper()
    out: Set[str] = set()
    for line in pf_text.splitlines():
        if hu_u not in line:
            continue
        for pf in PF_ID_RE.findall(line):
            out.add(pf.upper())
    return sorted(out)


def slice_sections(backlog_text: str) -> Dict[str, str]:
    # Returns a mapping for major sections, best-effort.
    lines = backlog_text.splitlines()
    # Identify header indices for "Backend", "Frontend", "Tests E2E" by heading text.
    idx: Dict[str, int] = {}
    for i, ln in enumerate(lines):
        hm = HEADING_RE.match(ln.strip())
        if not hm:
            continue
        title = hm.group(2).strip().lower()
        if title == "backend":
            idx["backend"] = i
        elif title == "frontend":
            idx["frontend"] = i
        elif title == "tests e2e":
            idx["tests"] = i

    def section_text(key: str) -> str:
        if key not in idx:
            return ""
        start = idx[key]
        # End at next top-level "##" heading.
        end = len(lines)
        for j in range(start + 1, len(lines)):
            hm = HEADING_RE.match(lines[j].strip())
            if hm and hm.group(1) == "##":
                end = j
                break
        return "\n".join(lines[start:end])

    return {
        "all": backlog_text,
        "backend": section_text("backend"),
        "frontend": section_text("frontend"),
        "tests": section_text("tests"),
    }


def map_criteria_to_pf(criteria: Sequence[str], pf_candidates: Sequence[Tuple[str, str]], min_score: float = 0.34) -> Tuple[Dict[str, Optional[str]], int]:
    """
    Returns:
    - mapping: criterion -> matched PF id (or None)
    - mapped_count
    """
    mapping: Dict[str, Optional[str]] = {}
    mapped = 0
    for c in criteria:
        best_pf, score = best_pf_match_for_criterion(c, pf_candidates)
        if best_pf is not None and score >= min_score:
            mapping[c] = best_pf
            mapped += 1
        else:
            mapping[c] = None
    return mapping, mapped


def unmapped_criteria_details(
    mapping: Dict[str, Optional[str]],
    pf_candidates: Sequence[Tuple[str, str]],
    min_score: float,
) -> Tuple[str, ...]:
    details: List[str] = []
    for crit, pf in mapping.items():
        if pf is not None:
            continue
        best_pf, best_score = best_pf_match_for_criterion(crit, pf_candidates)
        if best_pf is None:
            details.append(f"- {crit} (no hay PF candidata)")
        else:
            details.append(f"- {crit} (mejor candidata: {best_pf} score={best_score:.2f} < {min_score:.2f})")
    return tuple(details)


def build_report(module_slug: str, backlog_path: Path, rf_ids: Sequence[str], checks: Sequence[HuCheck]) -> str:
    missing = [c for c in checks if not (c.in_backlog and c.in_backend and c.in_frontend and c.in_tests) or c.pf_missing_in_tests > 0]
    total_unmapped = sum(c.criteria_unmapped for c in checks)
    total_pf_missing = sum(c.pf_missing_in_tests for c in checks)
    lines: List[str] = []
    lines.append("# Check completitud por HU")
    lines.append("")
    lines.append(f"- module: {module_slug}")
    lines.append(f"- backlog: {backlog_path.as_posix()}")
    lines.append(f"- RFs: {', '.join(rf_ids) if rf_ids else '(none)'}")
    lines.append("")
    lines.append("## Resultados")
    lines.append("")
    lines.append("| HU | En backlog | Backend | Frontend | Tests E2E | PF(HU) | PF faltantes en Tests (ERROR) | Criterios | Criterios mapeados a PF | Criterios sin mapear (WARN) |")
    lines.append("|---|---|---|---|---|---:|---:|---:|---:|---:|")
    for c in checks:
        lines.append(
            f"| {c.hu_id} | {'OK' if c.in_backlog else 'NO'} | {'OK' if c.in_backend else 'NO'} | "
            f"{'OK' if c.in_frontend else 'NO'} | {'OK' if c.in_tests else 'NO'} | "
            f"{c.pf_total} | {c.pf_missing_in_tests} | {c.criteria_total} | {c.criteria_mapped} | {c.criteria_unmapped} |"
        )
    lines.append("")
    lines.append("## Resumen")
    lines.append("")
    lines.append(f"- HUs revisadas: {len(checks)}")
    lines.append(f"- HUs faltantes por seccion (ERROR): {len(missing)}")
    lines.append(f"- PF faltantes en Tests E2E (ERROR): {total_pf_missing}")
    lines.append(f"- criterios sin mapear a PF (WARN): {total_unmapped}")
    lines.append("")
    if missing:
        lines.append("### HUs con faltantes (ERROR)")
        lines.append("")
        for c in missing:
            parts = []
            if not c.in_backlog:
                parts.append("no aparece en backlog")
            if not c.in_backend:
                parts.append("sin tareas en Backend")
            if not c.in_frontend:
                parts.append("sin tareas en Frontend")
            if not c.in_tests:
                parts.append("sin tareas en Tests E2E")
            if c.pf_missing_in_tests:
                parts.append(f"PF faltantes en Tests E2E: {c.pf_missing_in_tests}")
            lines.append(f"- {c.hu_id}: {', '.join(parts)}")
        lines.append("")

    if total_unmapped:
        lines.append("## Detalle criterios sin mapear a PF (WARN)")
        lines.append("")
        for c in checks:
            if not c.unmapped_details:
                continue
            lines.append(f"### {c.hu_id}")
            lines.append("")
            lines.extend(list(c.unmapped_details))
            lines.append("")
    return "\n".join(lines)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Valida completitud del backlog por HU (module-scope).")
    p.add_argument("--backlog", type=Path, required=True)
    p.add_argument("--module-scope", dest="module_scope", required=True, help="Module slug as in design/01.")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--design01", type=Path, default=Path("design/01_technical_design.md"))
    p.add_argument("--mat", type=Path, default=Path("analisis/14_matriz_trazabilidad.md"))
    p.add_argument("--hu", type=Path, default=Path("analisis/05_historias_usuario.md"))
    p.add_argument("--pf", type=Path, default=Path("analisis/13_pruebas_funcionales.md"))
    p.add_argument("--min-score", type=float, default=0.34, help="Umbral minimo de score para mapear criterio HU -> PF (default: 0.34)")
    return p.parse_args(list(argv))


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    backlog_path: Path = args.backlog
    module_slug: str = args.module_scope
    out_path: Path = args.out

    if not backlog_path.exists():
        raise SystemExit(f"ERROR: backlog not found: {backlog_path}")
    for dep in (args.design01, args.mat, args.hu):
        if not dep.exists():
            raise SystemExit(f"ERROR: file not found: {dep}")
    if not args.pf.exists():
        raise SystemExit(f"ERROR: file not found: {args.pf}")

    design_text = read_text(args.design01)
    rf_ids = rfs_for_module_from_design01(design_text, module_slug)
    if not rf_ids:
        raise SystemExit(f"ERROR: RFs not found for module-scope='{module_slug}' in {args.design01}")

    matrix_text = read_text(args.mat)
    hu_ids = hus_for_rfs_from_matrix(matrix_text, rf_ids)
    if not hu_ids:
        raise SystemExit(f"ERROR: no HUs found in matrix for RFs: {', '.join(rf_ids)}")

    hu_text = read_text(args.hu)
    hu_criteria = extract_hu_criteria(hu_text, hu_ids)
    hu_related_rfs = extract_hu_related_rfs(hu_text, hu_ids)
    pf_text = read_text(args.pf)
    pf_rows = parse_pf_rows(pf_text)
    pf_by_hu: Dict[str, List[Tuple[str, str]]] = {}
    for pf_id, hu_id, pf_crit in pf_rows:
        pf_by_hu.setdefault(hu_id, []).append((pf_id, pf_crit))

    backlog_text = read_text(backlog_path)
    sections = slice_sections(backlog_text)
    backlog_all_l = sections["all"].lower()
    backend_l = sections["backend"].lower()
    frontend_l = sections["frontend"].lower()
    tests_l = sections["tests"].lower()

    checks: List[HuCheck] = []
    for hu_id in hu_ids:
        hu_l = hu_id.lower()
        in_backlog = hu_l in backlog_all_l

        related_rfs = hu_related_rfs.get(hu_id, [])
        rf_hits_backend = any(rf.lower() in backend_l for rf in related_rfs)
        rf_hits_frontend = any(rf.lower() in frontend_l for rf in related_rfs)

        # Coverage by section: allow matching by HU id OR by its related RFs (more robust with existing backlog style).
        in_backend = (hu_l in backend_l) or rf_hits_backend
        in_frontend = (hu_l in frontend_l) or rf_hits_frontend

        # Tests: require PFs for HU to be present in Tests E2E if they exist.
        pfs = extract_pfs_for_hu(pf_text, hu_id)
        in_tests = (hu_l in tests_l) or any(pf.lower() in tests_l for pf in pfs)
        pf_missing_in_tests = 0
        if pfs:
            for pf in pfs:
                if pf.lower() not in tests_l:
                    pf_missing_in_tests += 1
        criteria = hu_criteria.get(hu_id, [])

        pf_candidates = pf_by_hu.get(hu_id, [])
        _mapping, mapped_count = map_criteria_to_pf(criteria, pf_candidates, min_score=float(args.min_score))
        unmapped = max(0, len(criteria) - mapped_count)
        unmapped_details = unmapped_criteria_details(_mapping, pf_candidates, min_score=float(args.min_score))

        checks.append(
            HuCheck(
                hu_id=hu_id,
                in_backlog=in_backlog,
                in_backend=in_backend,
                in_frontend=in_frontend,
                in_tests=in_tests,
                criteria_total=len(criteria),
                criteria_mapped=mapped_count,
                criteria_unmapped=unmapped,
                unmapped_details=unmapped_details,
                pf_total=len(pfs),
                pf_missing_in_tests=pf_missing_in_tests,
            )
        )

    report = build_report(module_slug, backlog_path, rf_ids, checks)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    missing = [c for c in checks if not (c.in_backlog and c.in_backend and c.in_frontend and c.in_tests) or c.pf_missing_in_tests > 0]
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
