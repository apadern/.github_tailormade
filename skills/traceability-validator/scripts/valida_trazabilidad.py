#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Validador de trazabilidad (matriz + backlog opcional).

Soporta dos modos de validación:
- PROTOTIPO: Valida RF, HU y Pantallas
- COMPLETO: Valida RF, HU, CU (Casos de Uso), Pantallas y Pruebas Funcionales

El modo se detecta automáticamente según la estructura de la matriz.

Valida, para cada fila de la matriz (por defecto: analisis/14_matriz_trazabilidad.md):
1) El RF existe en analisis/03_requerimientos_funcionales.md y su título coincide.
2) Las HU referenciadas existen en analisis/05_historias_usuario.md y declaran relación con el RF
     (vía el campo "ID Requerimientos relacionados").
3) Las pantallas referenciadas existen en analisis/10_interfaces_usuario.md y están asociadas a
     alguna de las HU del RF (columna de HU asociadas en el documento de interfaces).
4) [MODO COMPLETO] Los CU referenciados existen en analisis/06_casos_uso.md y están asociados 
     a las HU del RF.
5) [MODO COMPLETO] Las Pruebas referenciadas existen en analisis/13_pruebas_funcionales.md y están
     asociadas a las HU, CU y Pantallas del RF.

Además (matriz):
- Detecta HUs/Pantallas/CU/Pruebas duplicadas en una misma fila.
- Detecta inconsistencias de "NO APLICA" (RF tachado / marcado en fuente vs matriz).
- Detecta cobertura global de IDs en el documento de matriz:
    - RF/HU/Pantallas/CU/Pruebas definidas en fuentes pero no mencionadas en la matriz.
    - IDs mencionados en la matriz que no existen en las fuentes (WARN).

Backlog (opcional con --backlog):
- Valida consistencia backlog<->matriz usando líneas con "Ref:" (pares RF<->HU, RF<->Pantalla, etc.).
- Valida cobertura global de IDs en el backlog:
    - RF/HU/Pantallas/CU/Pruebas definidas en fuentes pero no mencionadas en el backlog.
    - IDs mencionados en el backlog que no existen en las fuentes (WARN).

Salida:
- Genera un markdown con el informe en analisis/check_trazabilidad.md (por defecto).

Uso básico:
    python valida_trazabilidad.py

Con backlog:
    python valida_trazabilidad.py --backlog 02_backlog.md

Con backlog en modo módulo (solo valida IDs presentes, no cobertura total):
    python valida_trazabilidad.py --backlog backlog/01_repositorio-documental.md --module-scope

Con carpeta de backlogs (validación consolidada final):
    python valida_trazabilidad.py --backlog-dir backlog/ --out backlog/check_final.md

Opcional (rutas explícitas para modo COMPLETO):
    python valida_trazabilidad.py \
        --req analisis/03_requerimientos_funcionales.md \
        --hu analisis/05_historias_usuario.md \
        --cu analisis/06_casos_uso.md \
        --ui analisis/10_interfaces_usuario.md \
        --pf analisis/13_pruebas_funcionales.md \
        --mat analisis/14_matriz_trazabilidad.md \
        --out analisis/check_trazabilidad.md

Modo genérico (misma estructura de documentos/tablas, pero otros prefijos/IDs/labels):
    python valida_trazabilidad.py \
        --rf-id-pattern "\\bREQ-\\d{3}\\b" \
        --hu-id-pattern "\\bUS-\\d{3}\\b" \
        --cu-id-pattern "\\bUC-\\d{3}\\b" \
        --ui-id-pattern "\\bUI-[A-Z]{2}-\\d{2}\\b" \
        --pf-id-pattern "\\bTC-\\d{3}\\b" \
        --hu-related-label "ID Requerimientos relacionados"
"""

from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Iterable


# Patrones por defecto (configurables por CLI). Deben matchear el ID completo.
RF_ID_RE = re.compile(r"\bRF-\d{3}\b")
HU_ID_RE = re.compile(r"\bHU-\d{3}\b")
UI_ID_RE = re.compile(r"\bP-\d{3}\b")
CU_ID_RE = re.compile(r"\bCU-\d{2,3}\b")
PF_ID_RE = re.compile(r"\bPF-\d{3}\b")

NO_APLICA_RE = re.compile(r"\bNO\s+APLICA\b", re.IGNORECASE)
HU_RELATED_LABEL_RE = re.compile(r"^\*\*ID Requerimientos relacionados:\*\*\s*(.+?)\s*$", re.MULTILINE)


HU_RANGE_RE = re.compile(r"\b(HU-\d{3})\s*(?:a|to|\-|–|—)\s*(HU-\d{3})\b", re.IGNORECASE)


def _split_md_row(line: str) -> Optional[List[str]]:
    """Splits a markdown table row into trimmed cells.

    Returns None if the line doesn't look like a table row or is a header separator.
    """
    s = line.strip()
    if not (s.startswith("|") and s.endswith("|")):
        return None
    parts = [p.strip() for p in s.strip("|").split("|")]
    # Header separator rows: | :-- | ---: |
    if parts and all(re.fullmatch(r":?-{2,}:?", p.replace(" ", "")) for p in parts if p):
        return None
    return parts


GEN_NUMERIC_RANGE_RE = re.compile(
    r"\b(?P<prefix>[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*)-(?P<start>\d{2,4})\s*(?:a|to|\-|–|—)\s*(?P=prefix)-(?P<end>\d{2,4})\b",
    re.IGNORECASE,
)


def extract_ids_with_ranges(text: str, id_re: re.Pattern) -> List[str]:
    """Extracts IDs matching id_re and expands numeric ranges like 'RF-001 a RF-011'.

    The expansion is conservative: it only adds expanded IDs that match id_re.
    """
    ids: List[str] = []
    for m in id_re.finditer(text):
        ids.append(m.group(0))

    for m in GEN_NUMERIC_RANGE_RE.finditer(text):
        prefix = m.group("prefix")
        start_s = m.group("start")
        end_s = m.group("end")
        try:
            start_n = int(start_s)
            end_n = int(end_s)
        except ValueError:
            continue
        width = len(start_s)
        lo, hi = (start_n, end_n) if start_n <= end_n else (end_n, start_n)
        for n in range(lo, hi + 1):
            cand = f"{prefix}-{n:0{width}d}"
            if id_re.fullmatch(cand):
                ids.append(cand)

    # preserve order but unique
    seen: Set[str] = set()
    out: List[str] = []
    for x in ids:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


@dataclass(frozen=True)
class BacklogRef:
    line_no: int
    text: str
    rf_ids: List[str]
    hu_ids: List[str]
    ui_ids: List[str]
    cu_ids: List[str]
    pf_ids: List[str]


@dataclass(frozen=True)
class HuDef:
    hu_id: str
    title: str
    related_rfs: Set[str]
    body: str
    line_no: int
    role: str  # Extracted from "**Como**" field


@dataclass(frozen=True)
class RfDef:
    rf_id: str
    title: str
    desc: str
    line_no: int


@dataclass(frozen=True)
class UiDef:
    ui_id: str
    title: str
    ui_type: str
    desc: str
    roles: str
    hu_ids: Set[str]
    line_no: int


@dataclass(frozen=True)
class CuDef:
    cu_id: str
    title: str
    hu_ids: Set[str]
    desc: str
    line_no: int
    actor_principal: str  # Extracted from "**Actor Principal:**"
    actores_secundarios: Set[str]  # Extracted from "**Actores Secundarios:**"


@dataclass(frozen=True)
class PfDef:
    pf_id: str
    title: str
    hu_ids: Set[str]
    cu_ids: Set[str]
    pantallas: Set[str]
    line_no: int
    actor: str  # Extracted from "Actor" column in table


@dataclass(frozen=True)
class MatRow:
    rf_id: str
    rf_title: str
    hu_ids: List[str]
    cu_ids: List[str]
    ui_ids: List[str]
    pf_ids: List[str]
    no_aplica: bool
    raw_line: str
    line_no: int
    mode: str  # "PROTOTIPO" o "COMPLETO"


@dataclass
class Finding:
    rf_id: str
    kind: str
    severity: str  # ERROR | WARN
    message: str
    details: Optional[str] = None
    location: Optional[str] = None


def fmt_loc(doc: str, line_no: Optional[int]) -> Optional[str]:
    if not line_no:
        return None
    return f"{doc}:L{line_no}"


def first_occurrence_lines(text: str, id_re: re.Pattern) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for i, line in enumerate(text.splitlines(), start=1):
        for found in extract_ids_with_ranges(line, id_re):
            out.setdefault(found, i)
    return out


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


def norm_title(s: str) -> str:
    s = s.strip()
    s = s.replace("\u00a0", " ")
    s = s.replace("—", "-")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s*([,:;.!?])\s*", r"\1 ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def normalize_role(role: str) -> str:
    """Normalize a role name for comparison.
    
    Removes accents, converts to lowercase, normalizes whitespace.
    E.g., 'Jefe de Comercio Exterior' -> 'jefe de comercio exterior'
    """
    s = role.strip()
    s = s.replace("\u00a0", " ")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower()
    s = re.sub(r"\s+", " ", s).strip()
    return s


ES_STOPWORDS: Set[str] = {
    "a",
    "al",
    "algo",
    "algunas",
    "algunos",
    "ante",
    "antes",
    "asi",
    "aun",
    "aunque",
    "bajo",
    "bien",
    "cada",
    "casi",
    "como",
    "con",
    "contra",
    "cual",
    "cuales",
    "cuando",
    "de",
    "del",
    "desde",
    "donde",
    "dos",
    "el",
    "ella",
    "ellas",
    "ellos",
    "en",
    "entre",
    "era",
    "eran",
    "es",
    "esa",
    "esas",
    "ese",
    "eso",
    "esos",
    "esta",
    "estaba",
    "estaban",
    "estas",
    "este",
    "esto",
    "estos",
    "ex",
    "fin",
    "fue",
    "fueron",
    "ha",
    "han",
    "hasta",
    "hay",
    "incluye",
    "incluyendo",
    "la",
    "las",
    "le",
    "les",
    "lo",
    "los",
    "mas",
    "me",
    "mi",
    "mis",
    "mismo",
    "muy",
    "no",
    "nos",
    "o",
    "otra",
    "otras",
    "otro",
    "otros",
    "para",
    "pero",
    "por",
    "porque",
    "que",
    "quien",
    "se",
    "segun",
    "ser",
    "si",
    "sin",
    "sobre",
    "su",
    "sus",
    "tambien",
    "tanto",
    "toda",
    "todas",
    "todo",
    "todos",
    "tras",
    "tres",
    "tu",
    "un",
    "una",
    "uno",
    "unos",
    "y",
    "ya",
}


def tokenize(text: str) -> Set[str]:
    if not text:
        return set()
    s = norm_title(text)
    # Keep letters/numbers as tokens; split otherwise
    raw = re.split(r"[^a-z0-9]+", s)
    toks: Set[str] = set()
    for t in raw:
        t = t.strip()
        if not t or len(t) < 3:
            continue
        if t in ES_STOPWORDS:
            continue
        # Drop pure numbers
        if t.isdigit():
            continue
        toks.add(t)
    return toks


def overlap_coeff(a: Set[str], b: Set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    denom = min(len(a), len(b))
    return inter / denom if denom else 0.0


def jaccard(a: Set[str], b: Set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def top_keywords(tokens: Set[str], k: int = 10) -> List[str]:
    # With set tokens we can't rank by frequency; approximate by preferring longer tokens
    # (often more specific) and stable sorting.
    return sorted(tokens, key=lambda x: (-len(x), x))[:k]


def parse_requirements(req_md: str) -> Tuple[Dict[str, RfDef], Set[str]]:
    """Returns (rf_id -> RfDef, set(no_aplica_rf_ids)).

    Genérico para tablas donde el RF está en alguna celda. Por defecto, toma:
    - Título: celda siguiente a la celda del ID
    - Descripción: concatenación del resto de celdas
    """
    rf_map: Dict[str, RfDef] = {}
    no_aplica: Set[str] = set()

    for line_no, line in enumerate(req_md.splitlines(), start=1):
        cells = _split_md_row(line)
        if not cells or len(cells) < 2:
            continue

        joined = " | ".join(cells)
        m = RF_ID_RE.search(joined)
        if not m:
            continue
        rf_id = m.group(0)

        id_cell_idx: Optional[int] = None
        for i, c in enumerate(cells):
            if RF_ID_RE.search(c):
                id_cell_idx = i
                break

        title = ""
        desc = ""
        if id_cell_idx is not None and id_cell_idx + 1 < len(cells):
            title = cells[id_cell_idx + 1]
            desc = " | ".join(cells[id_cell_idx + 2 :]).strip()
        else:
            # Fallback: remove id from row and use remaining text
            remainder = RF_ID_RE.sub("", joined).strip(" -|\t")
            title = remainder

        title = re.sub(r"\*\*|~~", "", title).strip()
        desc = re.sub(r"\*\*|~~", "", desc).strip()

        rf_map[rf_id] = RfDef(rf_id=rf_id, title=title, desc=desc, line_no=line_no)

        # Consider NO APLICA only when explicitly stated or strikethrough.
        if "~~" in joined or NO_APLICA_RE.search(joined):
            no_aplica.add(rf_id)

    return rf_map, no_aplica


def parse_hus(hu_md: str) -> Dict[str, HuDef]:
    """Parse HU blocks from headings and related RF line."""
    # Split by HU heading
    # Example: #### **HU-012: Inscribirse en Convocatoria como Aspirante**
    # Generic: accept any **<HU_ID>: Title** header; validate HU id via HU_ID_RE
    heading_re = re.compile(r"^#{3,6}\s+\*\*(?:~~)?(.+?):\s*(.+?)(?:~~)?\*\*\s*$", re.MULTILINE)
    matches = list(heading_re.finditer(hu_md))

    # Regex to extract role from "**Como** Rol"
    como_re = re.compile(r"^\*\*Como\*\*\s+(.+?)\s*$", re.MULTILINE | re.IGNORECASE)

    hus: Dict[str, HuDef] = {}
    for idx, m in enumerate(matches):
        hu_id_raw = m.group(1).strip()
        hu_id_m = HU_ID_RE.search(hu_id_raw)
        if not hu_id_m:
            continue
        hu_id = hu_id_m.group(0)
        title = re.sub(r"~~", "", m.group(2)).strip()
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(hu_md)
        block = hu_md[start:end].strip("\n")

        line_no = hu_md.count("\n", 0, m.start()) + 1

        related: Set[str] = set()
        rel_m = HU_RELATED_LABEL_RE.search(block)
        if rel_m:
            related = set(RF_ID_RE.findall(rel_m.group(1)))

        # Extract role from "**Como** Role"
        role = ""
        como_m = como_re.search(block)
        if como_m:
            role = como_m.group(1).strip()

        hus[hu_id] = HuDef(hu_id=hu_id, title=title, related_rfs=related, body=block, line_no=line_no, role=role)

    return hus


def parse_casos_uso(cu_md: str) -> Dict[str, CuDef]:
    """Parse CU blocks from headings and associated HU line."""
    # Example: #### CU-01: Título del Caso de Uso (with or without ** markers)
    heading_re = re.compile(r"^#{3,6}\s+\*?\*?(?:~~)?(CU-\d{2,3}):\s*(.+?)(?:~~)?\*?\*?\s*(?:\(.+?\))?\s*$", re.MULTILINE)
    matches = list(heading_re.finditer(cu_md))

    # Regex to extract Actor Principal and Actores Secundarios
    actor_principal_re = re.compile(r"^\*\s*\*\*Actor Principal:\*\*\s*(.+?)\s*$", re.MULTILINE)
    actores_secundarios_re = re.compile(r"^\*\s*\*\*Actores Secundarios:\*\*\s*(.+?)\s*$", re.MULTILINE)

    cus: Dict[str, CuDef] = {}
    for idx, m in enumerate(matches):
        cu_id = m.group(1).strip()
        title = re.sub(r"~~", "", m.group(2)).strip()
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(cu_md)
        block = cu_md[start:end].strip("\n")

        line_no = cu_md.count("\n", 0, m.start()) + 1

        # Extract HU IDs from the block (typically in "Historia de Usuario Asociada" or similar)
        hu_ids: Set[str] = set(HU_ID_RE.findall(block))

        # Extract Actor Principal
        actor_principal = ""
        actor_m = actor_principal_re.search(block)
        if actor_m:
            actor_principal = actor_m.group(1).strip()

        # Extract Actores Secundarios (comma-separated list)
        actores_secundarios: Set[str] = set()
        actores_m = actores_secundarios_re.search(block)
        if actores_m:
            actores_text = actores_m.group(1).strip()
            # Split by comma and clean each actor
            if actores_text.lower() not in ("ninguno", "n/a", "-", ""):
                for actor in re.split(r"[,;]", actores_text):
                    actor_clean = actor.strip()
                    # Remove "(Sistema)" or similar parenthetical annotations
                    actor_clean = re.sub(r"\s*\([^)]*\)\s*", "", actor_clean).strip()
                    if actor_clean and actor_clean.lower() not in ("ninguno", "n/a", "-"):
                        actores_secundarios.add(actor_clean)

        cus[cu_id] = CuDef(
            cu_id=cu_id, 
            title=title, 
            hu_ids=hu_ids, 
            desc=block[:200], 
            line_no=line_no,
            actor_principal=actor_principal,
            actores_secundarios=actores_secundarios
        )

    return cus


def parse_pruebas(pf_md: str) -> Dict[str, PfDef]:
    """Parse PF (Pruebas Funcionales) from table or structured format.
    
    Expected table format:
    | ID Prueba | HU / CU | Pantalla(s) | Actor | Criterios de Aceptación | Resultado Esperado |
    | **PF-001** | HU-001 / CU-01 | `P-001`, `P-002` | Comprador | ... | ... |
    """
    # Try table format first: | **PF-001** | ...
    pruebas: Dict[str, PfDef] = {}
    
    for line_no, line in enumerate(pf_md.splitlines(), start=1):
        cells = _split_md_row(line)
        if cells and len(cells) >= 4:
            # Look for PF ID in first cell
            first = cells[0]
            pf_m = PF_ID_RE.search(first)
            if pf_m:
                pf_id = pf_m.group(0)
                title = re.sub(r"\*\*|~~", "", first).replace(pf_id, "").strip(" :-")
                
                # Column structure: | ID Prueba | HU / CU | Pantalla(s) | Actor | ...
                # cells[0]: ID Prueba
                # cells[1]: HU / CU
                # cells[2]: Pantalla(s)
                # cells[3]: Actor
                hu_cu_col = cells[1] if len(cells) > 1 else ""
                pantalla_col = cells[2] if len(cells) > 2 else ""
                actor_col = cells[3] if len(cells) > 3 else ""
                
                hu_ids = set(HU_ID_RE.findall(hu_cu_col))
                cu_ids = set(CU_ID_RE.findall(hu_cu_col))
                pantallas = set(UI_ID_RE.findall(pantalla_col))
                actor = actor_col.strip()
                
                pruebas[pf_id] = PfDef(
                    pf_id=pf_id,
                    title=title,
                    hu_ids=hu_ids,
                    cu_ids=cu_ids,
                    pantallas=pantallas,
                    line_no=line_no,
                    actor=actor
                )
    
    # Alternative: heading format #### **PF-001: Title**
    if not pruebas:
        heading_re = re.compile(r"^#{3,6}\s+\*\*(?:~~)?(.+?):\s*(.+?)(?:~~)?\*\*\s*$", re.MULTILINE)
        matches = list(heading_re.finditer(pf_md))
        for idx, m in enumerate(matches):
            pf_id_raw = m.group(1).strip()
            pf_id_m = PF_ID_RE.search(pf_id_raw)
            if not pf_id_m:
                continue
            pf_id = pf_id_m.group(0)
            title = re.sub(r"~~", "", m.group(2)).strip()
            start = m.end()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(pf_md)
            block = pf_md[start:end].strip("\n")
            line_no = pf_md.count("\n", 0, m.start()) + 1
            
            hu_ids = set(HU_ID_RE.findall(block))
            cu_ids = set(CU_ID_RE.findall(block))
            pantallas = set(UI_ID_RE.findall(block))
            
            # Try to extract actor from block if available (e.g., "**Actor:** Comprador")
            actor = ""
            actor_m = re.search(r"\*\*Actor(?:es)?:\*\*\s*(.+?)(?:\n|$)", block)
            if actor_m:
                actor = actor_m.group(1).strip()
            
            pruebas[pf_id] = PfDef(
                pf_id=pf_id,
                title=title,
                hu_ids=hu_ids,
                cu_ids=cu_ids,
                pantallas=pantallas,
                line_no=line_no,
                actor=actor
            )
    
    return pruebas


def parse_ui(ui_md: str) -> Dict[str, UiDef]:
    """Parse UI table rows. Expects pattern: | **P-001: Title** | Type | Desc... | ... | HU-001, ... |"""
    ui: Dict[str, UiDef] = {}
    # Parse UI rows by splitting table lines (more robust across projects)
    for line_no, line in enumerate(ui_md.splitlines(), start=1):
        cells = _split_md_row(line)
        if not cells or len(cells) < 5:
            continue

        first = cells[0]
        m = re.search(r"\*\*(?:~~)?(.+?):\s*(.+?)(?:~~)?\*\*", first)
        if not m:
            continue
        ui_id_raw = m.group(1).strip()
        ui_id_m = UI_ID_RE.search(ui_id_raw)
        if not ui_id_m:
            continue
        ui_id = ui_id_m.group(0)
        title = re.sub(r"~~", "", m.group(2)).strip()

        ui_type = (cells[1] if len(cells) > 1 else "").strip()
        desc = (cells[2] if len(cells) > 2 else "").strip()
        roles = (cells[3] if len(cells) > 3 else "").strip()
        hu_col = (cells[4] if len(cells) > 4 else "")

        hu_ids: Set[str] = set(HU_ID_RE.findall(hu_col))
        for start_id, end_id in HU_RANGE_RE.findall(hu_col):
            start_n = int(start_id.split("-")[1])
            end_n = int(end_id.split("-")[1])
            lo, hi = (start_n, end_n) if start_n <= end_n else (end_n, start_n)
            for n in range(lo, hi + 1):
                hu_ids.add(f"HU-{n:03d}")

        ui.setdefault(ui_id, UiDef(ui_id=ui_id, title=title, ui_type=ui_type, desc=desc, roles=roles, hu_ids=hu_ids, line_no=line_no))

    return ui


def split_csv_ids(cell: str, prefix: str) -> List[str]:
    if prefix == "HU":
        ids = HU_ID_RE.findall(cell)
        # Expand ranges present inside the matrix cells too (rare but safe)
        for start_id, end_id in HU_RANGE_RE.findall(cell):
            start_n = int(start_id.split("-")[1])
            end_n = int(end_id.split("-")[1])
            lo, hi = (start_n, end_n) if start_n <= end_n else (end_n, start_n)
            for n in range(lo, hi + 1):
                ids.append(f"HU-{n:03d}")
    else:
        ids = UI_ID_RE.findall(cell)
    # preserve order but unique
    seen: Set[str] = set()
    out: List[str] = []
    for x in ids:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def parse_matrix(mat_md: str) -> List[MatRow]:
    rows: List[MatRow] = []
    # Detect mode by checking header
    mode = "PROTOTIPO"
    for line in mat_md.splitlines()[:20]:  # Check first 20 lines for header
        if "Caso(s) de Uso" in line or "Prueba(s)" in line:
            mode = "COMPLETO"
            break
    
    for line_no, line in enumerate(mat_md.splitlines(), start=1):
        if not line.strip().startswith("|"):
            continue
        # We want matrix rows for both active and strikethrough RFs.
        if not RF_ID_RE.search(line):
            continue

        # Split columns
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 3:
            continue

        rf_cell = parts[0]
        hu_cell = parts[1]
        
        # Column mapping based on mode
        if mode == "COMPLETO" and len(parts) >= 5:
            # COMPLETO: RF | HU | CU | Pantallas | Pruebas
            cu_cell = parts[2]
            ui_cell = parts[3]
            pf_cell = parts[4] if len(parts) > 4 else ""
        else:
            # PROTOTIPO: RF | HU | Pantallas
            cu_cell = ""
            ui_cell = parts[2] if len(parts) > 2 else ""
            pf_cell = ""

        # Skip the later summary table ("Elementos Marcados como NO APLICA")
        # which has column 2 like "Requerimiento" and does not contain any HU-xxx.
        if not HU_ID_RE.search(hu_cell):
            continue

        rf_id_m = RF_ID_RE.search(rf_cell)
        if not rf_id_m:
            continue
        rf_id = rf_id_m.group(0)

        # Extract title from rf_cell removing markdown, id, separators
        rf_title = rf_cell
        rf_title = re.sub(r"\*\*", "", rf_title)
        rf_title = re.sub(r"~~", "", rf_title)
        rf_title = rf_title.replace(rf_id, "")
        rf_title = rf_title.replace(":", " ")
        rf_title = rf_title.strip()
        rf_title = re.sub(r"\s+", " ", rf_title)

        no_aplica = ("~~" in rf_cell) or bool(NO_APLICA_RE.search(ui_cell))

        hu_ids = split_csv_ids(hu_cell, "HU")
        cu_ids = []
        pf_ids = []
        ui_ids = []
        
        if mode == "COMPLETO":
            for cu in CU_ID_RE.findall(cu_cell):
                if cu not in cu_ids:
                    cu_ids.append(cu)
            for pf in PF_ID_RE.findall(pf_cell):
                if pf not in pf_ids:
                    pf_ids.append(pf)
        
        ui_ids = split_csv_ids(ui_cell, "P")

        rows.append(MatRow(
            rf_id=rf_id, 
            rf_title=rf_title, 
            hu_ids=hu_ids, 
            cu_ids=cu_ids,
            ui_ids=ui_ids, 
            pf_ids=pf_ids,
            no_aplica=no_aplica, 
            raw_line=line, 
            line_no=line_no,
            mode=mode
        ))

    return rows


def parse_backlog(backlog_md: str) -> List[BacklogRef]:
    refs: List[BacklogRef] = []
    for i, line in enumerate(backlog_md.splitlines(), start=1):
        if "Ref:" not in line:
            continue
        # Backlog format: "[ ] ... Ref: [Pantalla P-XXX] (HU-XXX) (RF-XXX) (CU-XXX) (PF-XXX)"
        # Important: only treat IDs as references if they appear in the Ref: segment.
        # This avoids false positives when a task description mentions IDs in free text.
        ref_segment = line.split("Ref:", 1)[1]
        rf_ids = extract_ids_with_ranges(ref_segment, RF_ID_RE)
        hu_ids = extract_ids_with_ranges(ref_segment, HU_ID_RE)
        ui_ids = extract_ids_with_ranges(ref_segment, UI_ID_RE)
        cu_ids = extract_ids_with_ranges(ref_segment, CU_ID_RE)
        pf_ids = extract_ids_with_ranges(ref_segment, PF_ID_RE)
        if not (rf_ids or hu_ids or ui_ids or cu_ids or pf_ids):
            continue
        refs.append(BacklogRef(line_no=i, text=line.strip(), rf_ids=rf_ids, hu_ids=hu_ids, ui_ids=ui_ids, cu_ids=cu_ids, pf_ids=pf_ids))
    return refs


def make_report(
    findings: List[Finding],
    rf_rows: List[MatRow],
    req_map: Dict[str, RfDef],
    hu_map: Dict[str, HuDef],
    ui_map: Dict[str, UiDef],
    req_no_aplica: Set[str],
    mat_path: Path,
    req_path: Path,
    hu_path: Path,
    ui_path: Path,
    cu_path: Optional[Path],
    pf_path: Optional[Path],
    backlog_path: Optional[Path],
    backlog_stats: Optional[Dict[str, int]],
    semantic_cfg: Dict[str, float],
) -> str:
    total = len(rf_rows)
    rf_ids = sorted({r.rf_id for r in rf_rows})
    error_count = sum(1 for f in findings if f.severity == "ERROR")
    warn_count = sum(1 for f in findings if f.severity == "WARN")

    # group by rf
    by_rf: Dict[str, List[Finding]] = {}
    for f in findings:
        by_rf.setdefault(f.rf_id, []).append(f)

    lines: List[str] = []
    lines.append("# Informe de Validación Exhaustiva de Matriz de Trazabilidad")
    lines.append("")
    lines.append(f"**Fecha de validación:** {date.today().isoformat()}")
    lines.append(f"**Documento validado:** [{mat_path.name}]({mat_path.name})")
    lines.append("**Documentos de referencia:**")
    lines.append(f"- [{req_path.name}]({req_path.name})")
    lines.append(f"- [{hu_path.name}]({hu_path.name})")
    if cu_path is not None and cu_path.exists():
        lines.append(f"- [{cu_path.name}]({cu_path.name})")
    lines.append(f"- [{ui_path.name}]({ui_path.name})")
    if pf_path is not None and pf_path.exists():
        lines.append(f"- [{pf_path.name}]({pf_path.name})")
    if backlog_path is not None:
        lines.append(f"- [{backlog_path.name}]({backlog_path.name})")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Resumen")
    lines.append("")
    lines.append("| Métrica | Valor |")
    lines.append("| :-- | --: |")
    lines.append(f"| Filas RF en matriz | {total} |")
    lines.append(f"| RF únicos en matriz | {len(rf_ids)} |")
    lines.append(f"| RF definidos en [03_requerimientos_funcionales.md] | {len(req_map)} |")
    lines.append(f"| HU definidos en [05_historias_usuario.md] | {len(hu_map)} |")
    cu_count = sum(1 for r in rf_rows if r.mode == "COMPLETO")
    if cu_count > 0:
        cu_map = semantic_cfg.get("cu_map", {})
        lines.append(f"| CU definidos en [06_casos_uso.md] | {len(cu_map)} |")
    lines.append(f"| Pantallas definidas en [10_interfaces_usuario.md] | {len(ui_map)} |")
    if cu_count > 0:
        pf_map = semantic_cfg.get("pf_map", {})
        lines.append(f"| Pruebas definidas en [13_pruebas_funcionales.md] | {len(pf_map)} |")
    lines.append(f"| Discrepancias (ERROR) | {error_count} |")
    lines.append(f"| Observaciones (WARN) | {warn_count} |")
    if backlog_stats:
        lines.append(f"| Referencias en backlog (líneas con Ref + IDs) | {backlog_stats.get('refs', 0)} |")
        lines.append(f"| RF únicos en backlog | {backlog_stats.get('rf_unique', 0)} |")
        lines.append(f"| HU únicas en backlog | {backlog_stats.get('hu_unique', 0)} |")
        lines.append(f"| Pantallas únicas en backlog | {backlog_stats.get('ui_unique', 0)} |")
    lines.append("")

    lines.append("## Configuración semántica")
    lines.append("")
    lines.append("| Parámetro | Valor |")
    lines.append("| :-- | --: |")
    lines.append(f"| min_sim_hu | {semantic_cfg.get('min_sim_hu', 0.0):.3f} |")
    lines.append(f"| min_sim_ui | {semantic_cfg.get('min_sim_ui', 0.0):.3f} |")
    lines.append(f"| min_kw_coverage | {semantic_cfg.get('min_kw_coverage', 0.0):.3f} |")
    lines.append(f"| rf_keywords_k | {semantic_cfg.get('rf_keywords_k', 0.0):.0f} |")
    lines.append("")

    # High level lists
    if findings:
        lines.append("## Discrepancias detectadas")
        lines.append("")
        lines.append("| Severidad | RF | Tipo | Ubicación | Descripción |")
        lines.append("| :-- | :-- | :-- | :-- | :-- |")
        for f in sorted(findings, key=lambda x: (x.severity != "ERROR", x.rf_id, x.kind, x.location or "", x.message)):
            short = f.message
            short = short.replace("|", "\\|")
            loc = (f.location or "").replace("|", "\\|")
            lines.append(f"| {f.severity} | {f.rf_id} | {f.kind} | {loc} | {short} |")
        lines.append("")

        lines.append("## Detalle por Requerimiento")
        lines.append("")
        for rf in rf_ids:
            if rf not in by_rf:
                continue
            lines.append(f"### {rf}")
            rf_src = req_map.get(rf)
            if rf_src:
                lines.append(f"- **Título en requerimientos:** {rf_src.title}")
            mat_titles = [r.rf_title for r in rf_rows if r.rf_id == rf]
            if mat_titles:
                lines.append(f"- **Título en matriz:** {mat_titles[0]}")
            for f in by_rf[rf]:
                loc = f" ({f.location})" if f.location else ""
                if f.details:
                    lines.append(f"- **{f.severity} [{f.kind}]** {f.message}{loc}\\n  - {f.details}")
                else:
                    lines.append(f"- **{f.severity} [{f.kind}]** {f.message}{loc}")
            lines.append("")

        # Include findings that are not keyed by an RF in the matrix (e.g., backlog-only UI/HU IDs)
        other_ids = sorted(set(by_rf.keys()) - set(rf_ids))
        if other_ids:
            lines.append("## Detalle (Backlog / Otros IDs)")
            lines.append("")
            for oid in other_ids:
                lines.append(f"### {oid}")
                for f in by_rf[oid]:
                    loc = f" ({f.location})" if f.location else ""
                    if f.details:
                        lines.append(f"- **{f.severity} [{f.kind}]** {f.message}{loc}\\n  - {f.details}")
                    else:
                        lines.append(f"- **{f.severity} [{f.kind}]** {f.message}{loc}")
                lines.append("")
    else:
        lines.append("## Discrepancias detectadas")
        lines.append("")
        lines.append("No se han detectado discrepancias con las reglas automáticas aplicadas.")
        lines.append("")

    # Notes about limitations
    lines.append("---")
    lines.append("")
    lines.append("## Nota sobre el criterio de \"relación\"")
    lines.append("")
    lines.append(
        "La validación de relación RF<->HU y RF<->Pantalla se basa principalmente en: "
        "(1) la declaración explícita en HU (campo \"ID Requerimientos relacionados\"), "
        "y (2) la asociación Pantalla<->HU en 10_interfaces_usuario.md. "
        "Cuando estos vínculos no existen o no coinciden, se marca como discrepancia; "
        "cuando existen pero son indirectos o ambiguos, se marca como WARN."
    )
    lines.append("")

    return "\n".join(lines)


def validate(
    req_map: Dict[str, RfDef],
    req_no_aplica: Set[str],
    hu_map: Dict[str, HuDef],
    ui_map: Dict[str, UiDef],
    cu_map: Dict[str, CuDef],
    pf_map: Dict[str, PfDef],
    mat_rows: List[MatRow],
    *,
    min_sim_hu: float,
    min_sim_ui: float,
    min_kw_coverage: float,
    rf_keywords_k: int,
    mat_text: str,
) -> List[Finding]:
    findings: List[Finding] = []

    rf_first = first_occurrence_lines(mat_text, RF_ID_RE)
    hu_first = first_occurrence_lines(mat_text, HU_ID_RE)
    ui_first = first_occurrence_lines(mat_text, UI_ID_RE)
    cu_first = first_occurrence_lines(mat_text, CU_ID_RE)
    pf_first = first_occurrence_lines(mat_text, PF_ID_RE)

    # Build reverse mapping UI->HUs, CU->HUs, PF->HUs, PF->CUs
    ui_hus: Dict[str, Set[str]] = {k: v.hu_ids for k, v in ui_map.items()}
    cu_hus: Dict[str, Set[str]] = {k: v.hu_ids for k, v in cu_map.items()}
    pf_hus: Dict[str, Set[str]] = {k: v.hu_ids for k, v in pf_map.items()}
    pf_cus: Dict[str, Set[str]] = {k: v.cu_ids for k, v in pf_map.items()}
    pf_pantallas: Dict[str, Set[str]] = {k: v.pantallas for k, v in pf_map.items()}

    for row in mat_rows:
        rf_id = row.rf_id
        row_loc = fmt_loc("MATRIZ", row.line_no)

        # 1) RF existence and title match
        if rf_id not in req_map:
            findings.append(Finding(rf_id, "RF", "ERROR", f"RF no existe en 03_requerimientos_funcionales.md", row.raw_line, row_loc))
        else:
            src_title = req_map[rf_id].title
            if norm_title(src_title) != norm_title(row.rf_title):
                src_loc = fmt_loc("REQ", req_map[rf_id].line_no)
                findings.append(
                    Finding(
                        rf_id,
                        "RF",
                        "ERROR",
                        "Título de RF en matriz no coincide con el fichero de requerimientos",
                        f"Matriz: '{row.rf_title}' | Fuente: '{src_title}'",
                        f"{row_loc or 'MATRIZ'} | {src_loc or 'REQ'}",
                    )
                )

        # NO APLICA consistency
        is_na_src = rf_id in req_no_aplica
        if row.no_aplica and not is_na_src:
            findings.append(
                Finding(
                    rf_id,
                    "NO_APLICA",
                    "WARN",
                    "RF marcado como NO APLICA en matriz pero no está NO APLICA en requerimientos",
                    row.raw_line,
                    row_loc,
                )
            )
        if (not row.no_aplica) and is_na_src:
            src_loc = fmt_loc("REQ", req_map.get(rf_id).line_no if rf_id in req_map else None)
            findings.append(
                Finding(
                    rf_id,
                    "NO_APLICA",
                    "ERROR",
                    "RF está NO APLICA en requerimientos pero aparece activo en matriz",
                    row.raw_line,
                    f"{row_loc or 'MATRIZ'} | {src_loc or 'REQ'}",
                )
            )

        # 2) HU checks
        if not row.no_aplica:
            if not row.hu_ids:
                findings.append(Finding(rf_id, "HU", "ERROR", "Fila de matriz sin HU asociadas", location=row_loc))
            else:
                # duplicates
                if len(set(row.hu_ids)) != len(row.hu_ids):
                    findings.append(Finding(rf_id, "HU", "WARN", "HU duplicadas en la fila de matriz", ", ".join(row.hu_ids), row_loc))

                for hu_id in row.hu_ids:
                    hu = hu_map.get(hu_id)
                    if not hu:
                        findings.append(
                            Finding(
                                rf_id,
                                "HU",
                                "ERROR",
                                f"HU referenciada no existe en 05_historias_usuario.md: {hu_id}",
                                location=row_loc,
                            )
                        )
                        continue

                    if hu.related_rfs and rf_id not in hu.related_rfs:
                        hu_loc = fmt_loc("HU", hu.line_no)
                        findings.append(
                            Finding(
                                rf_id,
                                "RF_HU",
                                "ERROR",
                                f"La HU no declara relación con este RF en 'ID Requerimientos relacionados': {hu_id}",
                                f"Relacionado en HU: {', '.join(sorted(hu.related_rfs)) or '(vacío)'}",
                                f"{row_loc or 'MATRIZ'} | {hu_loc or 'HU'}",
                            )
                        )
                    elif not hu.related_rfs:
                        hu_loc = fmt_loc("HU", hu.line_no)
                        findings.append(
                            Finding(
                                rf_id,
                                "RF_HU",
                                "WARN",
                                f"La HU no tiene 'ID Requerimientos relacionados' (no se puede confirmar relación): {hu_id}",
                                location=f"{row_loc or 'MATRIZ'} | {hu_loc or 'HU'}",
                            )
                        )

                # Semantic (básico): RF↔HU similarity/keywords
                rf_src = req_map.get(rf_id)
                if rf_src:
                    rf_text = f"{rf_src.title}. {rf_src.desc}"
                    rf_tokens = tokenize(rf_text)
                    rf_kws = top_keywords(rf_tokens, k=rf_keywords_k)
                    for hu_id in row.hu_ids:
                        hu = hu_map.get(hu_id)
                        if not hu:
                            continue
                        hu_tokens = tokenize(f"{hu.title}. {hu.body}")
                        sim = max(overlap_coeff(rf_tokens, hu_tokens), jaccard(rf_tokens, hu_tokens))
                        kw_hit = len(set(rf_kws) & hu_tokens)
                        kw_cov = (kw_hit / len(rf_kws)) if rf_kws else 0.0
                        if sim < min_sim_hu and kw_cov < min_kw_coverage:
                            findings.append(
                                Finding(
                                    rf_id,
                                    "SEM_RF_HU",
                                    "WARN",
                                    f"Relación semántica RF<->HU débil para {hu_id}",
                                    f"sim={sim:.3f}, kw_cov={kw_cov:.3f}, rf_kws={', '.join(rf_kws[:8])}",
                                    location=row_loc,
                                )
                            )

        # 3) UI checks
        if not row.no_aplica:
            if not row.ui_ids:
                findings.append(Finding(rf_id, "UI", "ERROR", "Fila de matriz sin pantallas asociadas", location=row_loc))
            else:
                if len(set(row.ui_ids)) != len(row.ui_ids):
                    findings.append(Finding(rf_id, "UI", "WARN", "Pantallas duplicadas en la fila de matriz", ", ".join(row.ui_ids), row_loc))

                for ui_id in row.ui_ids:
                    ui = ui_map.get(ui_id)
                    if not ui:
                        findings.append(
                            Finding(
                                rf_id,
                                "UI",
                                "ERROR",
                                f"Pantalla referenciada no existe en 10_interfaces_usuario.md: {ui_id}",
                                location=row_loc,
                            )
                        )
                        continue

                    # Must share at least one HU with the RF row
                    if row.hu_ids:
                        if not (ui_hus.get(ui_id, set()) & set(row.hu_ids)):
                            ui_loc = fmt_loc("UI", ui.line_no)
                            findings.append(
                                Finding(
                                    rf_id,
                                    "RF_UI",
                                    "ERROR",
                                    f"Pantalla no está asociada a ninguna HU listada en la fila del RF: {ui_id}",
                                    f"HU en pantalla: {', '.join(sorted(ui.hu_ids)) or '(ninguna)'} | HU en matriz: {', '.join(row.hu_ids)}",
                                    f"{row_loc or 'MATRIZ'} | {ui_loc or 'UI'}",
                                )
                            )
                    else:
                        findings.append(
                            Finding(
                                rf_id,
                                "RF_UI",
                                "WARN",
                                f"No hay HU en fila; no se puede validar relación pantalla<->HU: {ui_id}",
                                location=row_loc,
                            )
                        )

                # Heurística semántica (básico) por tipo de pantalla:
                # si el RF implica una acción de edición/registro/carga/modificación,
                # esperamos al menos una pantalla de tipo formulario/modal (no solo dashboard/detalle/listado).
                rf_src = req_map.get(rf_id)
                if rf_src and row.ui_ids:
                    rf_title_n = norm_title(rf_src.title)
                    implies_edit = any(
                        kw in rf_title_n
                        for kw in (
                            "modificacion",
                            "edicion",
                            "editar",
                            "registro",
                            "registrar",
                            "carga",
                            "cargar",
                            "aportacion",
                            "subir",
                            "configuracion",
                            "crear",
                            "creacion",
                            "importacion",
                            "enviar",
                            "envio",
                            "validacion",
                        )
                    )
                    if implies_edit:
                        allowed = {"formulario", "modal"}
                        action_re = re.compile(
                            r"\b(editar|modificar|actualizar|guardar|confirmar|enviar|registrar|subir|cargar|anadir|eliminar|reemplazar)\b",
                            re.IGNORECASE,
                        )
                        has_form = False
                        for ui_id in row.ui_ids:
                            ui = ui_map.get(ui_id)
                            if not ui:
                                continue
                            t = norm_title(ui.ui_type)
                            if any(a in t for a in allowed):
                                has_form = True
                                break
                            # Some screens are typed as Detalle/Listado/Dashboard but still expose actions via buttons.
                            # Accept them if their description clearly includes action verbs.
                            if ui.desc and action_re.search(ui.desc):
                                has_form = True
                                break
                        if not has_form:
                            findings.append(
                                Finding(
                                    rf_id,
                                    "SEM_UI_TYPE",
                                    "WARN",
                                    "RF implica acción de edición/registro pero no referencia ninguna pantalla de tipo Formulario/Modal",
                                    f"Pantallas en matriz: {', '.join(row.ui_ids)}",
                                    location=row_loc,
                                )
                            )

                # Semantic (básico): RF↔UI similarity/keywords
                rf_src = req_map.get(rf_id)
                if rf_src:
                    rf_text = f"{rf_src.title}. {rf_src.desc}"
                    rf_tokens = tokenize(rf_text)
                    rf_kws = top_keywords(rf_tokens, k=rf_keywords_k)
                    for ui_id in row.ui_ids:
                        ui = ui_map.get(ui_id)
                        if not ui:
                            continue
                        ui_tokens = tokenize(f"{ui.title}. {ui.desc}")
                        sim = max(overlap_coeff(rf_tokens, ui_tokens), jaccard(rf_tokens, ui_tokens))
                        kw_hit = len(set(rf_kws) & ui_tokens)
                        kw_cov = (kw_hit / len(rf_kws)) if rf_kws else 0.0
                        if sim < min_sim_ui and kw_cov < min_kw_coverage:
                            findings.append(
                                Finding(
                                    rf_id,
                                    "SEM_RF_UI",
                                    "WARN",
                                    f"Relación semántica RF<->Pantalla débil para {ui_id}",
                                    f"sim={sim:.3f}, kw_cov={kw_cov:.3f}, rf_kws={', '.join(rf_kws[:8])}",
                                    location=row_loc,
                                )
                            )

        # 4) CU checks (modo COMPLETO)
        if row.mode == "COMPLETO" and not row.no_aplica:
            if not row.cu_ids:
                findings.append(Finding(rf_id, "CU", "ERROR", "Fila de matriz sin CU asociados (modo COMPLETO)", location=row_loc))
            else:
                # duplicates
                if len(set(row.cu_ids)) != len(row.cu_ids):
                    findings.append(Finding(rf_id, "CU", "WARN", "CU duplicados en la fila de matriz", ", ".join(row.cu_ids), row_loc))

                for cu_id in row.cu_ids:
                    cu = cu_map.get(cu_id)
                    if not cu:
                        findings.append(
                            Finding(
                                rf_id,
                                "CU",
                                "ERROR",
                                f"CU referenciado no existe en 06_casos_uso.md: {cu_id}",
                                location=row_loc,
                            )
                        )
                        continue

                    # CU debe compartir al menos una HU con el RF
                    if row.hu_ids:
                        if not (cu_hus.get(cu_id, set()) & set(row.hu_ids)):
                            cu_loc = fmt_loc("CU", cu.line_no)
                            findings.append(
                                Finding(
                                    rf_id,
                                    "RF_CU",
                                    "ERROR",
                                    f"CU no está asociado a ninguna HU listada en la fila del RF: {cu_id}",
                                    f"HU en CU: {', '.join(sorted(cu.hu_ids)) or '(ninguna)'} | HU en matriz: {', '.join(row.hu_ids)}",
                                    f"{row_loc or 'MATRIZ'} | {cu_loc or 'CU'}",
                                )
                            )
                    else:
                        findings.append(
                            Finding(
                                rf_id,
                                "RF_CU",
                                "WARN",
                                f"No hay HU en fila; no se puede validar relación CU<->HU: {cu_id}",
                                location=row_loc,
                            )
                        )

        # 5) Pruebas checks (modo COMPLETO)
        if row.mode == "COMPLETO" and not row.no_aplica:
            if not row.pf_ids:
                findings.append(Finding(rf_id, "PRUEBA", "ERROR", "Fila de matriz sin Pruebas asociadas (modo COMPLETO)", location=row_loc))
            else:
                # duplicates
                if len(set(row.pf_ids)) != len(row.pf_ids):
                    findings.append(Finding(rf_id, "PRUEBA", "WARN", "Pruebas duplicadas en la fila de matriz", ", ".join(row.pf_ids), row_loc))

                for pf_id in row.pf_ids:
                    pf = pf_map.get(pf_id)
                    if not pf:
                        findings.append(
                            Finding(
                                rf_id,
                                "PRUEBA",
                                "ERROR",
                                f"Prueba referenciada no existe en 13_pruebas_funcionales.md: {pf_id}",
                                location=row_loc,
                            )
                        )
                        continue

                    # Prueba debe compartir al menos una HU con el RF
                    if row.hu_ids:
                        if not (pf_hus.get(pf_id, set()) & set(row.hu_ids)):
                            pf_loc = fmt_loc("PRUEBA", pf.line_no)
                            findings.append(
                                Finding(
                                    rf_id,
                                    "RF_PRUEBA",
                                    "ERROR",
                                    f"Prueba no está asociada a ninguna HU listada en la fila del RF: {pf_id}",
                                    f"HU en Prueba: {', '.join(sorted(pf.hu_ids)) or '(ninguna)'} | HU en matriz: {', '.join(row.hu_ids)}",
                                    f"{row_loc or 'MATRIZ'} | {pf_loc or 'PRUEBA'}",
                                )
                            )
                    
                    # Prueba debe compartir al menos un CU con el RF (si hay CUs en la fila)
                    if row.cu_ids:
                        if not (pf_cus.get(pf_id, set()) & set(row.cu_ids)):
                            pf_loc = fmt_loc("PRUEBA", pf.line_no)
                            findings.append(
                                Finding(
                                    rf_id,
                                    "CU_PRUEBA",
                                    "ERROR",
                                    f"Prueba no está asociada a ningún CU listado en la fila del RF: {pf_id}",
                                    f"CU en Prueba: {', '.join(sorted(pf.cu_ids)) or '(ninguno)'} | CU en matriz: {', '.join(row.cu_ids)}",
                                    f"{row_loc or 'MATRIZ'} | {pf_loc or 'PRUEBA'}",
                                )
                            )
                    
                    # Prueba debe compartir al menos una Pantalla con el RF (si hay Pantallas en la fila)
                    if row.ui_ids:
                        if not (pf_pantallas.get(pf_id, set()) & set(row.ui_ids)):
                            pf_loc = fmt_loc("PRUEBA", pf.line_no)
                            findings.append(
                                Finding(
                                    rf_id,
                                    "UI_PRUEBA",
                                    "ERROR",
                                    f"Prueba no está asociada a ninguna Pantalla listada en la fila del RF: {pf_id}",
                                    f"Pantallas en Prueba: {', '.join(sorted(pf.pantallas)) or '(ninguna)'} | Pantallas en matriz: {', '.join(row.ui_ids)}",
                                    f"{row_loc or 'MATRIZ'} | {pf_loc or 'PRUEBA'}",
                                )
                            )
                        sim = max(overlap_coeff(rf_tokens, ui_tokens), jaccard(rf_tokens, ui_tokens))
                        kw_hit = len(set(rf_kws) & ui_tokens)
                        kw_cov = (kw_hit / len(rf_kws)) if rf_kws else 0.0
                        if sim < min_sim_ui and kw_cov < min_kw_coverage:
                            findings.append(
                                Finding(
                                    rf_id,
                                    "SEM_RF_UI",
                                    "WARN",
                                    f"Relación semántica RF<->Pantalla débil para {ui_id}",
                                    f"sim={sim:.3f}, kw_cov={kw_cov:.3f}, rf_kws={', '.join(rf_kws[:8])}",
                                    location=row_loc,
                                )
                            )

        # 6) Role consistency validation: HU, CU, PF roles should match for each row
        if not row.no_aplica:
            # Collect roles from all HUs in this row
            hu_roles: Set[str] = set()
            for hu_id in row.hu_ids:
                hu = hu_map.get(hu_id)
                if hu and hu.role:
                    hu_roles.add(normalize_role(hu.role))
            
            # Collect roles from all CUs in this row (Actor Principal + Actores Secundarios)
            cu_roles: Set[str] = set()
            for cu_id in row.cu_ids:
                cu = cu_map.get(cu_id)
                if cu:
                    if cu.actor_principal:
                        cu_roles.add(normalize_role(cu.actor_principal))
                    for sec in cu.actores_secundarios:
                        cu_roles.add(normalize_role(sec))
            
            # Validate: PF role should be in HU roles, CU roles, OR roles from PF's own declared HUs/CUs
            if hu_roles or cu_roles:
                valid_roles = hu_roles | cu_roles
                for pf_id in row.pf_ids:
                    pf = pf_map.get(pf_id)
                    if pf and pf.actor:
                        pf_role_norm = normalize_role(pf.actor)
                        
                        # Also collect roles from HUs/CUs declared in the PF itself
                        # This handles cases where a PF covers multiple HUs with different roles
                        pf_hu_roles: Set[str] = set()
                        for pf_hu_id in pf.hu_ids:
                            pf_hu = hu_map.get(pf_hu_id)
                            if pf_hu and pf_hu.role:
                                pf_hu_roles.add(normalize_role(pf_hu.role))
                        
                        pf_cu_roles: Set[str] = set()
                        for pf_cu_id in pf.cu_ids:
                            pf_cu = cu_map.get(pf_cu_id)
                            if pf_cu:
                                if pf_cu.actor_principal:
                                    pf_cu_roles.add(normalize_role(pf_cu.actor_principal))
                                for sec in pf_cu.actores_secundarios:
                                    pf_cu_roles.add(normalize_role(sec))
                        
                        # PF is valid if its role matches row roles OR its own declared HU/CU roles
                        all_valid_roles = valid_roles | pf_hu_roles | pf_cu_roles
                        
                        if pf_role_norm not in all_valid_roles:
                            pf_loc = fmt_loc("PRUEBA", pf.line_no)
                            findings.append(
                                Finding(
                                    rf_id,
                                    "ROLE_MISMATCH",
                                    "ERROR",
                                    f"El rol de la Prueba no coincide con los roles de las HU/CU de la fila: {pf_id}",
                                    f"Rol en PF: '{pf.actor}' | Roles en HU: {', '.join(sorted(hu_roles)) or '(ninguno)'} | Roles en CU: {', '.join(sorted(cu_roles)) or '(ninguno)'}",
                                    f"{row_loc or 'MATRIZ'} | {pf_loc or 'PRUEBA'}",
                                )
                            )

    # Cobertura global:
    # la referencia cuenta si el ID aparece en cualquier parte del documento de matriz.
    rf_in_doc = set(extract_ids_with_ranges(mat_text, RF_ID_RE))
    hu_in_doc = set(extract_ids_with_ranges(mat_text, HU_ID_RE))
    ui_in_doc = set(extract_ids_with_ranges(mat_text, UI_ID_RE))
    cu_in_doc = set(extract_ids_with_ranges(mat_text, CU_ID_RE))
    pf_in_doc = set(extract_ids_with_ranges(mat_text, PF_ID_RE))

    rf_in_rows = {r.rf_id for r in mat_rows}
    hu_in_rows: Set[str] = set()
    ui_in_rows: Set[str] = set()
    cu_in_rows: Set[str] = set()
    pf_in_rows: Set[str] = set()
    for r in mat_rows:
        hu_in_rows.update(r.hu_ids)
        ui_in_rows.update(r.ui_ids)
        cu_in_rows.update(r.cu_ids)
        pf_in_rows.update(r.pf_ids)

    # Missing in matrix
    for rf_id in sorted(set(req_map.keys()) - rf_in_doc):
        if rf_id in req_no_aplica:
            continue
        findings.append(
            Finding(
                rf_id,
                "COBERTURA",
                "ERROR",
                "RF definido en requerimientos pero no aparece en la matriz",
                location=fmt_loc("REQ", req_map[rf_id].line_no),
            )
        )

    for hu_id in sorted(set(hu_map.keys()) - hu_in_doc):
        findings.append(
            Finding(
                hu_id,
                "COBERTURA",
                "ERROR",
                "HU definida en historias de usuario pero no aparece en la matriz",
                location=fmt_loc("HU", hu_map[hu_id].line_no),
            )
        )

    for ui_id in sorted(set(ui_map.keys()) - ui_in_doc):
        findings.append(
            Finding(
                ui_id,
                "COBERTURA",
                "ERROR",
                "Pantalla definida en interfaces de usuario pero no aparece en la matriz",
                location=fmt_loc("UI", ui_map[ui_id].line_no),
            )
        )

    # Cobertura CU y Pruebas (solo en modo COMPLETO)
    if any(r.mode == "COMPLETO" for r in mat_rows):
        for cu_id in sorted(set(cu_map.keys()) - cu_in_doc):
            findings.append(
                Finding(
                    cu_id,
                    "COBERTURA",
                    "ERROR",
                    "CU definido en casos de uso pero no aparece en la matriz",
                    location=fmt_loc("CU", cu_map[cu_id].line_no),
                )
            )

        for pf_id in sorted(set(pf_map.keys()) - pf_in_doc):
            findings.append(
                Finding(
                    pf_id,
                    "COBERTURA",
                    "ERROR",
                    "Prueba definida en pruebas funcionales pero no aparece en la matriz",
                    location=fmt_loc("PRUEBA", pf_map[pf_id].line_no),
                )
            )

    # Extra IDs in matrix not defined in sources (equivalente al "AVISO: sobrantes" del script antiguo)
    # Evitamos duplicar los errores ya emitidos por validación por fila.
    for rf_id in sorted((rf_in_doc - set(req_map.keys())) - rf_in_rows):
        findings.append(
            Finding(
                rf_id,
                "COBERTURA",
                "WARN",
                "RF aparece en la matriz pero no existe en requerimientos",
                location=fmt_loc("MATRIZ", rf_first.get(rf_id)),
            )
        )
    for hu_id in sorted((hu_in_doc - set(hu_map.keys())) - hu_in_rows):
        findings.append(
            Finding(
                hu_id,
                "COBERTURA",
                "WARN",
                "HU aparece en la matriz pero no existe en historias de usuario",
                location=fmt_loc("MATRIZ", hu_first.get(hu_id)),
            )
        )
    for ui_id in sorted((ui_in_doc - set(ui_map.keys())) - ui_in_rows):
        findings.append(
            Finding(
                ui_id,
                "COBERTURA",
                "WARN",
                "Pantalla aparece en la matriz pero no existe en interfaces de usuario",
                location=fmt_loc("MATRIZ", ui_first.get(ui_id)),
            )
        )
    
    # Sobrantes CU y Pruebas (solo en modo COMPLETO)
    if any(r.mode == "COMPLETO" for r in mat_rows):
        for cu_id in sorted((cu_in_doc - set(cu_map.keys())) - cu_in_rows):
            findings.append(
                Finding(
                    cu_id,
                    "COBERTURA",
                    "WARN",
                    "CU aparece en la matriz pero no existe en casos de uso",
                    location=fmt_loc("MATRIZ", cu_first.get(cu_id)),
                )
            )
        for pf_id in sorted((pf_in_doc - set(pf_map.keys())) - pf_in_rows):
            findings.append(
                Finding(
                    pf_id,
                    "COBERTURA",
                    "WARN",
                    "Prueba aparece en la matriz pero no existe en pruebas funcionales",
                    location=fmt_loc("MATRIZ", pf_first.get(pf_id)),
                )
            )

    return findings


def validate_backlog_consistency(
    backlog_refs: List[BacklogRef],
    *,
    backlog_text: str,
    req_map: Dict[str, RfDef],
    req_no_aplica: Set[str],
    hu_map: Dict[str, HuDef],
    ui_map: Dict[str, UiDef],
    cu_map: Dict[str, CuDef],
    pf_map: Dict[str, PfDef],
    mat_rows: List[MatRow],
    module_scope: bool = False,
) -> Tuple[List[Finding], Dict[str, int]]:
    findings: List[Finding] = []

    rf_first = first_occurrence_lines(backlog_text, RF_ID_RE)
    hu_first = first_occurrence_lines(backlog_text, HU_ID_RE)
    ui_first = first_occurrence_lines(backlog_text, UI_ID_RE)
    cu_first = first_occurrence_lines(backlog_text, CU_ID_RE)
    pf_first = first_occurrence_lines(backlog_text, PF_ID_RE)

    # Coverage & extra IDs in backlog:
    # cuenta si el ID aparece en cualquier parte del backlog, no solo en el segmento "Ref:".
    rf_in_backlog = set(RF_ID_RE.findall(backlog_text))
    hu_in_backlog = set(HU_ID_RE.findall(backlog_text))
    ui_in_backlog = set(UI_ID_RE.findall(backlog_text))
    cu_in_backlog = set(CU_ID_RE.findall(backlog_text))
    pf_in_backlog = set(PF_ID_RE.findall(backlog_text))

    rf_src = set(req_map.keys())
    hu_src = set(hu_map.keys())
    ui_src = set(ui_map.keys())
    cu_src = set(cu_map.keys())
    pf_src = set(pf_map.keys())

    # MODO MODULE-SCOPE: Solo validar que los IDs del backlog existan en fuentes
    # NO validar que todos los IDs de fuentes estén en el backlog (otros módulos)
    if not module_scope:
        # MODO TRADICIONAL: Validar cobertura completa (todos los IDs deben estar en backlog)
        for rf in sorted(rf_src - rf_in_backlog):
            findings.append(
                Finding(
                    rf,
                    "BACKLOG_COBERTURA",
                    "ERROR",
                    "RF definido en requerimientos pero no aparece en backlog",
                    location=fmt_loc("REQ", req_map[rf].line_no),
                )
            )
        for hu in sorted(hu_src - hu_in_backlog):
            findings.append(
                Finding(
                    hu,
                    "BACKLOG_COBERTURA",
                    "ERROR",
                    "HU definida en historias de usuario pero no aparece en backlog",
                    location=fmt_loc("HU", hu_map[hu].line_no),
                )
            )
        for ui in sorted(ui_src - ui_in_backlog):
            findings.append(
                Finding(
                    ui,
                    "BACKLOG_COBERTURA",
                    "ERROR",
                    "Pantalla definida en interfaces de usuario pero no aparece en backlog",
                    location=fmt_loc("UI", ui_map[ui].line_no),
                )
            )
        
        # Cobertura CU y PF en backlog (solo si existen)
        if cu_src:
            for cu in sorted(cu_src - cu_in_backlog):
                findings.append(
                    Finding(
                        cu,
                        "BACKLOG_COBERTURA",
                        "ERROR",
                        "CU definido en casos de uso pero no aparece en backlog",
                        location=fmt_loc("CU", cu_map[cu].line_no),
                    )
                )
        if pf_src:
            for pf in sorted(pf_src - pf_in_backlog):
                findings.append(
                    Finding(
                        pf,
                        "BACKLOG_COBERTURA",
                        "ERROR",
                        "Prueba definida en pruebas funcionales pero no aparece en backlog",
                        location=fmt_loc("PRUEBA", pf_map[pf].line_no),
                    )
                )

    # Sobrantes en backlog (WARN), equivalente al "AVISO: sobrantes" del script antiguo.
    for rf in sorted(rf_in_backlog - rf_src):
        findings.append(
            Finding(
                rf,
                "BACKLOG_SOBRANTES",
                "WARN",
                "RF aparece en backlog pero no existe en requerimientos",
                location=fmt_loc("BACKLOG", rf_first.get(rf)),
            )
        )
    for hu in sorted(hu_in_backlog - hu_src):
        findings.append(
            Finding(
                hu,
                "BACKLOG_SOBRANTES",
                "WARN",
                "HU aparece en backlog pero no existe en historias de usuario",
                location=fmt_loc("BACKLOG", hu_first.get(hu)),
            )
        )
    for ui in sorted(ui_in_backlog - ui_src):
        findings.append(
            Finding(
                ui,
                "BACKLOG_SOBRANTES",
                "WARN",
                "Pantalla aparece en backlog pero no existe en interfaces de usuario",
                location=fmt_loc("BACKLOG", ui_first.get(ui)),
            )
        )
    
    # Sobrantes CU y PF en backlog
    if cu_src:
        for cu in sorted(cu_in_backlog - cu_src):
            findings.append(
                Finding(
                    cu,
                    "BACKLOG_SOBRANTES",
                    "WARN",
                    "CU aparece en backlog pero no existe en casos de uso",
                    location=fmt_loc("BACKLOG", cu_first.get(cu)),
                )
            )
    if pf_src:
        for pf in sorted(pf_in_backlog - pf_src):
            findings.append(
                Finding(
                    pf,
                    "BACKLOG_SOBRANTES",
                    "WARN",
                    "Prueba aparece en backlog pero no existe en pruebas funcionales",
                    location=fmt_loc("BACKLOG", pf_first.get(pf)),
                )
            )

    # Aggregate repetitive errors to keep the report readable.
    agg: Dict[Tuple[str, str, str], Dict[str, object]] = {}

    def add_agg(primary_id: str, kind: str, severity: str, message: str, ctx: str, details: Optional[str] = None, location: Optional[str] = None) -> None:
        key = (kind, primary_id, message)
        entry = agg.get(key)
        if entry is None:
            entry = {"severity": severity, "primary_id": primary_id, "kind": kind, "message": message, "ctx": [], "details": details, "location": location}
            agg[key] = entry
        entry["ctx"].append(ctx)
        # Prefer keeping the first non-empty details
        if details and not entry.get("details"):
            entry["details"] = details
        if location and not entry.get("location"):
            entry["location"] = location

    rf_to_hus: Dict[str, Set[str]] = {}
    rf_to_uis: Dict[str, Set[str]] = {}
    hu_to_rfs_in_mat: Dict[str, Set[str]] = {}
    hu_to_uis_in_mat: Dict[str, Set[str]] = {}
    ui_to_hus_doc: Dict[str, Set[str]] = {ui_id: ui.hu_ids for ui_id, ui in ui_map.items()}

    for row in mat_rows:
        rf_to_hus.setdefault(row.rf_id, set()).update(row.hu_ids)
        rf_to_uis.setdefault(row.rf_id, set()).update(row.ui_ids)
        for hu in row.hu_ids:
            hu_to_rfs_in_mat.setdefault(hu, set()).add(row.rf_id)
            if row.ui_ids:
                hu_to_uis_in_mat.setdefault(hu, set()).update(row.ui_ids)

    for ref in backlog_refs:
        ctx = f"L{ref.line_no}: {ref.text}"
        ctx_loc = fmt_loc("BACKLOG", ref.line_no)

        # Existence in source docs
        for rf in ref.rf_ids:
            if rf not in req_map:
                add_agg(rf, "BACKLOG_RF", "ERROR", "RF referenciado en backlog no existe en requerimientos", ctx, location=ctx_loc)
        for hu in ref.hu_ids:
            if hu not in hu_map:
                add_agg(hu, "BACKLOG_HU", "ERROR", "HU referenciada en backlog no existe en historias de usuario", ctx, location=ctx_loc)
        for ui in ref.ui_ids:
            if ui not in ui_map:
                add_agg(ui, "BACKLOG_UI", "ERROR", "Pantalla referenciada en backlog no existe en interfaces de usuario", ctx, location=ctx_loc)
        for cu in ref.cu_ids:
            if cu not in cu_map:
                add_agg(cu, "BACKLOG_CU", "ERROR", "CU referenciado en backlog no existe en casos de uso", ctx, location=ctx_loc)
        for pf in ref.pf_ids:
            if pf not in pf_map:
                add_agg(pf, "BACKLOG_PF", "ERROR", "Prueba referenciada en backlog no existe en pruebas funcionales", ctx, location=ctx_loc)

        # Consistency with matrix
        for rf in ref.rf_ids:
            if rf in req_no_aplica:
                continue
            if rf not in rf_to_hus and rf not in rf_to_uis:
                add_agg(rf, "BACKLOG_RF", "ERROR", "RF referenciado en backlog no aparece en la matriz", ctx, location=ctx_loc)

        for hu in ref.hu_ids:
            if hu not in hu_to_rfs_in_mat:
                add_agg(hu, "BACKLOG_HU", "ERROR", "HU referenciada en backlog no aparece en la matriz", ctx, location=ctx_loc)

        # Pair checks: RF<->HU
        if ref.rf_ids and ref.hu_ids:
            for rf in ref.rf_ids:
                if rf in req_no_aplica:
                    continue
                mat_hus = rf_to_hus.get(rf, set())
                for hu in ref.hu_ids:
                    if hu not in mat_hus:
                        add_agg(
                            rf,
                            "BACKLOG_RF_HU",
                            "ERROR",
                            f"Backlog vincula {rf}<->{hu} pero la matriz no contiene esa relación",
                            ctx,
                            location=ctx_loc,
                        )

        # Pair checks: RF<->UI
        if ref.rf_ids and ref.ui_ids:
            for rf in ref.rf_ids:
                if rf in req_no_aplica:
                    continue
                mat_uis = rf_to_uis.get(rf, set())
                for ui in ref.ui_ids:
                    if ui not in mat_uis:
                        exp = ", ".join(sorted(mat_uis)) or "(ninguna)"
                        add_agg(
                            rf,
                            "BACKLOG_RF_UI",
                            "ERROR",
                            f"Backlog vincula {rf}<->{ui} pero la matriz no contiene esa relación",
                            ctx,
                            details=f"Pantallas esperadas según matriz para {rf}: {exp}",
                            location=ctx_loc,
                        )

        # Pair checks: UI<->HU (doc + matrix)
        if ref.ui_ids and ref.hu_ids:
            for ui in ref.ui_ids:
                doc_hus = ui_to_hus_doc.get(ui, set())
                if doc_hus and not (doc_hus & set(ref.hu_ids)):
                    add_agg(
                        ui,
                        "BACKLOG_UI_HU",
                        "ERROR",
                        f"Backlog vincula {ui} con HUs que no coinciden con 10_interfaces_usuario.md",
                        ctx,
                        details=f"HU en pantalla (10_*): {', '.join(sorted(doc_hus)) or '(ninguna)'}",
                        location=ctx_loc,
                    )

                # Matrix-level: UI should be reachable from at least one of those HUs
                reachable = set()
                for hu in ref.hu_ids:
                    reachable |= hu_to_uis_in_mat.get(hu, set())
                if reachable and ui not in reachable:
                    add_agg(
                        ui,
                        "BACKLOG_UI_HU",
                        "ERROR",
                        f"Backlog vincula {ui} con HUs, pero en la matriz esas HUs no conducen a esa pantalla",
                        ctx,
                        location=ctx_loc,
                    )

    # Emit aggregated findings (keep up to a few example lines)
    for (kind, primary, message), entry in sorted(agg.items(), key=lambda x: (x[0][0], x[0][1], x[0][2])):
        ctxs: List[str] = entry["ctx"]  # type: ignore[assignment]
        sev: str = entry["severity"]  # type: ignore[assignment]
        details: Optional[str] = entry.get("details")  # type: ignore[assignment]
        location: Optional[str] = entry.get("location")  # type: ignore[assignment]
        examples = "; ".join(ctxs[:5])
        if len(ctxs) > 5:
            examples += f"; (+{len(ctxs) - 5} más)"
        det = f"{len(ctxs)} ocurrencia(s). Ejemplos: {examples}"
        if details:
            det = f"{details} | {det}"
        findings.append(Finding(primary, kind, sev, message, det, location))

    # Coverage (WARN): matrix elements not mentioned in backlog at least once
    # (usa el backlog completo para minimizar falsos negativos).
    # En modo module-scope, solo validamos existencia, no cobertura matriz->backlog
    if not module_scope:
        rf_first_in_mat: Dict[str, int] = {}
        hu_first_in_mat: Dict[str, int] = {}
        ui_first_in_mat: Dict[str, int] = {}
        for r in mat_rows:
            rf_first_in_mat.setdefault(r.rf_id, r.line_no)
            for hu in r.hu_ids:
                hu_first_in_mat.setdefault(hu, r.line_no)
            for ui in r.ui_ids:
                ui_first_in_mat.setdefault(ui, r.line_no)

        mat_rf_ids = {r.rf_id for r in mat_rows if r.rf_id not in req_no_aplica}
        mat_hu_ids: Set[str] = set()
        mat_ui_ids: Set[str] = set()
        for r in mat_rows:
            if r.rf_id in req_no_aplica:
                continue
            mat_hu_ids.update(r.hu_ids)
            mat_ui_ids.update(r.ui_ids)

        for rf in sorted(mat_rf_ids - rf_in_backlog):
            findings.append(
                Finding(
                    rf,
                    "BACKLOG_COVERAGE",
                    "WARN",
                    "RF aparece en matriz pero no se menciona en backlog",
                    location=fmt_loc("MATRIZ", rf_first_in_mat.get(rf)),
                )
            )
        for hu in sorted(mat_hu_ids - hu_in_backlog):
            findings.append(
                Finding(
                    hu,
                    "BACKLOG_COVERAGE",
                    "WARN",
                    "HU aparece en matriz pero no se menciona en backlog",
                    location=fmt_loc("MATRIZ", hu_first_in_mat.get(hu)),
                )
            )
        for ui in sorted(mat_ui_ids - ui_in_backlog):
            findings.append(
                Finding(
                    ui,
                    "BACKLOG_COVERAGE",
                    "WARN",
                    "Pantalla aparece en matriz pero no se menciona en backlog",
                    location=fmt_loc("MATRIZ", ui_first_in_mat.get(ui)),
                )
            )

    stats = {
        "refs": len(backlog_refs),
        "rf_unique": len(rf_in_backlog),
        "hu_unique": len(hu_in_backlog),
        "ui_unique": len(ui_in_backlog),
        "cu_unique": len(cu_in_backlog),
        "pf_unique": len(pf_in_backlog),
    }
    return findings, stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Validador exhaustivo de matriz de trazabilidad")
    parser.add_argument("--req", type=Path, default=Path("analisis/03_requerimientos_funcionales.md"))
    parser.add_argument("--hu", type=Path, default=Path("analisis/05_historias_usuario.md"))
    parser.add_argument("--ui", type=Path, default=Path("analisis/10_interfaces_usuario.md"))
    parser.add_argument("--cu", type=Path, default=Path("analisis/06_casos_uso.md"), help="Ruta al archivo de casos de uso (modo COMPLETO)")
    parser.add_argument("--pf", type=Path, default=Path("analisis/13_pruebas_funcionales.md"), help="Ruta al archivo de pruebas funcionales (modo COMPLETO)")
    parser.add_argument("--mat", type=Path, default=Path("analisis/14_matriz_trazabilidad.md"))
    parser.add_argument("--out", type=Path, default=Path("analisis/check_trazabilidad.md"))
    parser.add_argument("--backlog", type=Path, default=None, help="Ruta al backlog (02_backlog.md) para validar consistencia backlog<->matriz")
    parser.add_argument("--backlog-dir", type=Path, default=None, help="Ruta a carpeta con múltiples backlogs (validación consolidada de todos los .md)")
    parser.add_argument("--module-scope", action="store_true", help="Modo validación por módulo: solo valida IDs presentes en backlog, no cobertura total")

    # Parámetros para reutilizar el validador en otras matrices con el mismo formato.
    parser.add_argument("--rf-id-pattern", default=r"\bRF-\d{3}\b", help="Regex para IDs RF (debe matchear el ID completo)")
    parser.add_argument("--hu-id-pattern", default=r"\bHU-\d{3}\b", help="Regex para IDs HU (debe matchear el ID completo)")
    parser.add_argument("--ui-id-pattern", default=r"\bP-\d{3}\b", help="Regex para IDs de pantallas (debe matchear el ID completo)")
    parser.add_argument("--cu-id-pattern", default=r"\bCU-\d{2,3}\b", help="Regex para IDs de casos de uso (debe matchear el ID completo)")
    parser.add_argument("--pf-id-pattern", default=r"\bPF-\d{3}\b", help="Regex para IDs de pruebas funcionales (debe matchear el ID completo)")
    parser.add_argument("--no-aplica-token", default="NO APLICA", help="Token textual para marcar NO APLICA")
    parser.add_argument(
        "--hu-related-label",
        default="ID Requerimientos relacionados",
        help="Texto del label en HU para relaciones con RF (por defecto: 'ID Requerimientos relacionados')",
    )
    parser.add_argument("--min-sim-hu", type=float, default=0.055, help="Umbral mínimo de similitud semántica RF<->HU para WARN")
    parser.add_argument("--min-sim-ui", type=float, default=0.040, help="Umbral mínimo de similitud semántica RF<->Pantalla para WARN")
    parser.add_argument("--min-kw-coverage", type=float, default=0.20, help="Cobertura mínima de keywords de RF en HU/UI para no advertir")
    parser.add_argument("--rf-keywords-k", type=int, default=12, help="Número de keywords a extraer del RF")
    args = parser.parse_args()

    # Reconfigurar patrones globales según CLI.
    global RF_ID_RE, HU_ID_RE, UI_ID_RE, CU_ID_RE, PF_ID_RE, NO_APLICA_RE, HU_RELATED_LABEL_RE
    RF_ID_RE = re.compile(args.rf_id_pattern)
    HU_ID_RE = re.compile(args.hu_id_pattern)
    UI_ID_RE = re.compile(args.ui_id_pattern)
    CU_ID_RE = re.compile(args.cu_id_pattern)
    PF_ID_RE = re.compile(args.pf_id_pattern)
    NO_APLICA_RE = re.compile(rf"\b{re.escape(args.no_aplica_token)}\b", re.IGNORECASE)
    HU_RELATED_LABEL_RE = re.compile(
        rf"^\*\*{re.escape(args.hu_related_label)}:\*\*\s*(.+?)\s*$",
        re.MULTILINE,
    )

    req_md = read_text(args.req)
    hu_md = read_text(args.hu)
    ui_md = read_text(args.ui)
    mat_md = read_text(args.mat)

    req_map, req_no_aplica = parse_requirements(req_md)
    hu_map = parse_hus(hu_md)
    ui_map = parse_ui(ui_md)
    mat_rows = parse_matrix(mat_md)
    
    # Cargar CU y Pruebas si existen (modo COMPLETO)
    cu_map: Dict[str, CuDef] = {}
    pf_map: Dict[str, PfDef] = {}
    if args.cu.exists():
        cu_md = read_text(args.cu)
        cu_map = parse_casos_uso(cu_md)
    if args.pf.exists():
        pf_md = read_text(args.pf)
        pf_map = parse_pruebas(pf_md)

    findings = validate(
        req_map,
        req_no_aplica,
        hu_map,
        ui_map,
        cu_map,
        pf_map,
        mat_rows,
        min_sim_hu=args.min_sim_hu,
        min_sim_ui=args.min_sim_ui,
        min_kw_coverage=args.min_kw_coverage,
        rf_keywords_k=args.rf_keywords_k,
        mat_text=mat_md,
    )

    backlog_stats: Optional[Dict[str, int]] = None
    backlog_path_for_report: Optional[Path] = None
    
    # Procesamiento de backlogs: individual o carpeta completa
    if args.backlog_dir is not None and args.backlog_dir.exists() and args.backlog_dir.is_dir():
        # Modo carpeta: consolidar todos los backlogs (excluyendo check_*.md)
        backlog_files = sorted([f for f in args.backlog_dir.glob("*.md") if not f.name.startswith("check_")])
        if backlog_files:
            print(f"Validando {len(backlog_files)} backlogs desde carpeta {args.backlog_dir}...")
            consolidated_backlog_md = ""
            for bf in backlog_files:
                print(f"  - {bf.name}")
                consolidated_backlog_md += read_text(bf) + "\n\n"
            
            backlog_refs = parse_backlog(consolidated_backlog_md)
            backlog_findings, backlog_stats = validate_backlog_consistency(
                backlog_refs,
                backlog_text=consolidated_backlog_md,
                req_map=req_map,
                req_no_aplica=req_no_aplica,
                hu_map=hu_map,
                ui_map=ui_map,
                cu_map=cu_map,
                pf_map=pf_map,
                mat_rows=mat_rows,
                module_scope=args.module_scope,
            )
            findings.extend(backlog_findings)
            backlog_path_for_report = args.backlog_dir
    elif args.backlog is not None and args.backlog.exists():
        # Modo individual
        backlog_md = read_text(args.backlog)
        backlog_refs = parse_backlog(backlog_md)
        backlog_findings, backlog_stats = validate_backlog_consistency(
            backlog_refs,
            backlog_text=backlog_md,
            req_map=req_map,
            req_no_aplica=req_no_aplica,
            hu_map=hu_map,
            ui_map=ui_map,
            cu_map=cu_map,
            pf_map=pf_map,
            mat_rows=mat_rows,
            module_scope=args.module_scope,
        )
        findings.extend(backlog_findings)
        backlog_path_for_report = args.backlog

    report = make_report(
        findings=findings,
        rf_rows=mat_rows,
        req_map=req_map,
        hu_map=hu_map,
        ui_map=ui_map,
        req_no_aplica=req_no_aplica,
        mat_path=args.mat,
        req_path=args.req,
        hu_path=args.hu,
        ui_path=args.ui,
        cu_path=args.cu if args.cu.exists() else None,
        pf_path=args.pf if args.pf.exists() else None,
        backlog_path=backlog_path_for_report,
        backlog_stats=backlog_stats,
        semantic_cfg={
            "min_sim_hu": float(args.min_sim_hu),
            "min_sim_ui": float(args.min_sim_ui),
            "min_kw_coverage": float(args.min_kw_coverage),
            "rf_keywords_k": float(args.rf_keywords_k),
            "cu_map": cu_map,
            "pf_map": pf_map,
        },
    )

    args.out.write_text(report, encoding="utf-8")

    # Mostrar resumen en consola
    error_count = sum(1 for f in findings if f.severity == "ERROR")
    print(f"Discrepancias (ERROR): {error_count}")
    print(f"Ver detalle en fichero {args.out}")

    # exit code: 1 if any ERROR
    return 1 if any(f.severity == "ERROR" for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
