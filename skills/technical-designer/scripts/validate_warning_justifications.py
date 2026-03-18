#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import re
import sys
from datetime import datetime

sys.dont_write_bytecode = True

DEFERRED_PATTERNS = [
    r"\bfase\s*[0-9ivx]+\b",
    r"fase posterior",
    r"iteracion posterior",
    r"iteracion futura",
    r"siguiente fase",
    r"proxima fase",
    r"mas adelante",
    r"no prioritario",
    r"backlog futuro",
    r"se abordara luego",
    r"se abordara en",
]


def normalize_text(value: str) -> str:
    value = value or ""
    value = value.strip().lower()
    value = re.sub(r"\s+", " ", value)
    return value


def normalize_key(value: str) -> str:
    value = normalize_text(value)
    replacements = str.maketrans(
        {
            "á": "a",
            "é": "e",
            "í": "i",
            "ó": "o",
            "ú": "u",
            "ü": "u",
            "ñ": "n",
        }
    )
    return value.translate(replacements)


def parse_warnings_from_report(report_path: str):
    if not os.path.exists(report_path):
        raise FileNotFoundError(f"No existe el reporte: {report_path}")

    with open(report_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    warnings = []
    in_warnings = False
    current_category = ""

    for raw_line in lines:
        line = raw_line.rstrip("\n")
        stripped = line.strip()

        if stripped.startswith("## ") and "warnings" in normalize_key(stripped):
            in_warnings = True
            current_category = ""
            continue

        if in_warnings and stripped.startswith("## "):
            break

        if not in_warnings:
            continue

        if stripped.startswith("### "):
            current_category = stripped[4:].strip()
            continue

        if stripped.startswith("- "):
            warnings.append(
                {
                    "category": current_category,
                    "warning": stripped[2:].strip(),
                }
            )

    return warnings


def is_separator_line(line: str) -> bool:
    line = line.strip()
    if "|" not in line or "-" not in line:
        return False
    remainder = re.sub(r"[\|\-:\s]", "", line)
    return len(remainder) == 0


def parse_markdown_table(file_path: str):
    if not os.path.exists(file_path):
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    headers = []
    rows = []
    in_table = False

    for i, raw_line in enumerate(lines):
        line = raw_line.strip()
        if "|" in line and i + 1 < len(lines) and is_separator_line(lines[i + 1].strip()):
            headers = [h.strip() for h in line.split("|") if h.strip()]
            in_table = True
            continue

        if not in_table:
            continue

        if is_separator_line(line):
            continue

        if not line or "|" not in line:
            if rows:
                break
            continue

        cols = [c.strip() for c in line.split("|")]
        if cols and cols[0] == "":
            cols = cols[1:]
        if cols and cols[-1] == "":
            cols = cols[:-1]

        row = {}
        for idx, header in enumerate(headers):
            if idx < len(cols):
                row[header] = cols[idx].strip()
        if row:
            rows.append(row)

    return {"headers": headers, "rows": rows} if headers else None


def detect_column(headers, options):
    normalized = {h: normalize_key(h) for h in headers}
    for candidate in options:
        candidate_norm = normalize_key(candidate)
        for h, h_norm in normalized.items():
            if candidate_norm == h_norm:
                return h
    for candidate in options:
        candidate_norm = normalize_key(candidate)
        for h, h_norm in normalized.items():
            if candidate_norm in h_norm:
                return h
    return None


def write_validation_report(output_path: str, errors, notes, warnings_count, rows_count):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    status = "VALIDO" if not errors else "INVALIDO"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Reporte de Validacion de Justificaciones de Warnings\n\n")
        f.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Estado:** {'✅ ' if not errors else '❌ '}{status}\n\n")
        f.write("## Resumen\n\n")
        f.write(f"- Warnings detectados en `check-design.md`: {warnings_count}\n")
        f.write(f"- Filas en `check-design-warnings.md`: {rows_count}\n")
        f.write(f"- Errores de validacion: {len(errors)}\n")
        f.write(f"- Notas: {len(notes)}\n")

        if errors:
            f.write("\n## Errores\n\n")
            for err in errors:
                f.write(f"- {err}\n")

        if notes:
            f.write("\n## Notas\n\n")
            for note in notes:
                f.write(f"- {note}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Valida justificaciones por warning en design/check-design-warnings.md"
    )
    parser.add_argument(
        "--report",
        default=os.path.join("design", "check-design.md"),
        help="Reporte generado por validate_design.py",
    )
    parser.add_argument(
        "--justifications",
        default=os.path.join("design", "check-design-warnings.md"),
        help="Archivo con tabla de justificaciones por warning",
    )
    parser.add_argument(
        "--output",
        default=os.path.join("design", "check-design-warnings-validation.md"),
        help="Archivo de salida del reporte de validacion",
    )

    args = parser.parse_args()

    errors = []
    notes = []

    try:
        report_warnings = parse_warnings_from_report(args.report)
    except Exception as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    if not report_warnings:
        notes.append("No hay warnings en check-design.md. El archivo de justificaciones no es obligatorio.")
        write_validation_report(args.output, errors, notes, 0, 0)
        print("OK: sin warnings.")
        sys.exit(0)

    table = parse_markdown_table(args.justifications)
    if not table:
        errors.append(
            "Hay warnings en check-design.md pero no se encontro una tabla valida en check-design-warnings.md."
        )
        write_validation_report(args.output, errors, notes, len(report_warnings), 0)
        print("ERROR: archivo de justificaciones invalido o ausente.")
        sys.exit(1)

    headers = table["headers"]
    rows = table["rows"]

    col_category = detect_column(headers, ["Categoria", "Category"])
    col_warning = detect_column(headers, ["Warning"])
    col_decision = detect_column(headers, ["Decision"])
    col_just = detect_column(headers, ["Justificacion", "Justificación"])
    col_evidence = detect_column(headers, ["Evidencia", "Evidence"])

    missing_columns = []
    if not col_warning:
        missing_columns.append("Warning")
    if not col_decision:
        missing_columns.append("Decision")
    if not col_just:
        missing_columns.append("Justificacion")
    if not col_evidence:
        missing_columns.append("Evidencia")

    if missing_columns:
        errors.append(
            "Faltan columnas obligatorias en tabla de justificaciones: "
            + ", ".join(missing_columns)
        )
        write_validation_report(args.output, errors, notes, len(report_warnings), len(rows))
        print("ERROR: columnas obligatorias faltantes.")
        sys.exit(1)

    rows_by_warning = {}
    repeated_justifications = {}

    for index, row in enumerate(rows, start=1):
        warning_text = (row.get(col_warning) or "").strip()
        decision = normalize_key(row.get(col_decision) or "")
        justification = (row.get(col_just) or "").strip()
        evidence = (row.get(col_evidence) or "").strip()
        category = (row.get(col_category) or "").strip() if col_category else ""

        if not warning_text:
            errors.append(f"Fila {index}: Warning vacio.")
            continue

        warning_key = normalize_text(warning_text)
        if warning_key in rows_by_warning:
            errors.append(f"Warning duplicado en justificaciones: '{warning_text}'.")
            continue

        if decision not in {"aceptado", "corregido"}:
            errors.append(
                f"Fila {index} ('{warning_text}'): Decision invalida '{row.get(col_decision)}'. Use ACEPTADO o CORREGIDO."
            )

        if len(justification) < 20:
            errors.append(
                f"Fila {index} ('{warning_text}'): Justificacion demasiado corta, debe ser especifica por warning."
            )
        else:
            justification_norm = normalize_key(justification)
            for pattern in DEFERRED_PATTERNS:
                if re.search(pattern, justification_norm):
                    errors.append(
                        f"Fila {index} ('{warning_text}'): Justificacion invalida por diferimiento a fases futuras."
                    )
                    break

            repeated_justifications.setdefault(justification_norm, []).append(warning_text)

        if len(evidence) < 10:
            errors.append(
                f"Fila {index} ('{warning_text}'): Evidencia vacia o insuficiente."
            )

        rows_by_warning[warning_key] = {
            "row_index": index,
            "warning": warning_text,
            "category": category,
        }

    for report_item in report_warnings:
        expected_warning = report_item["warning"].strip()
        expected_key = normalize_text(expected_warning)
        if expected_key not in rows_by_warning:
            errors.append(
                f"Falta justificacion para warning: '{expected_warning}'."
            )
            continue

        if col_category:
            row_category = rows_by_warning[expected_key]["category"]
            if row_category and normalize_key(row_category) != normalize_key(report_item["category"]):
                notes.append(
                    f"Categoria distinta para warning '{expected_warning}': reporte='{report_item['category']}' tabla='{row_category}'."
                )

    report_warning_keys = {normalize_text(w["warning"]) for w in report_warnings}
    for row_warning_key, row_data in rows_by_warning.items():
        if row_warning_key not in report_warning_keys:
            notes.append(
                f"Warning en tabla no presente en reporte actual: '{row_data['warning']}'."
            )

    for justification_norm, warning_list in repeated_justifications.items():
        if len(warning_list) > 1:
            errors.append(
                "Justificacion repetida en multiples warnings; cada warning requiere justificacion individual: "
                + " | ".join(warning_list[:5])
                + (" | ..." if len(warning_list) > 5 else "")
            )

    write_validation_report(
        args.output,
        errors,
        notes,
        len(report_warnings),
        len(rows),
    )

    if errors:
        print(f"ERROR: {len(errors)} error(es) de validacion.")
        sys.exit(1)

    print("OK: justificaciones por warning validadas.")
    sys.exit(0)


if __name__ == "__main__":
    main()
