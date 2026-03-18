from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


NS = {
    "bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL",
    "bpmndi": "http://www.omg.org/spec/BPMN/20100524/DI",
    "dc": "http://www.omg.org/spec/DD/20100524/DC",
    "di": "http://www.omg.org/spec/DD/20100524/DI",
}


@dataclass(frozen=True)
class ValidationIssue:
    level: str  # "error" | "warn"
    message: str


def _local_name(tag: str) -> str:
    if tag.startswith("{") and "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _ns_uri(tag: str) -> str | None:
    if tag.startswith("{") and "}" in tag:
        return tag[1:].split("}", 1)[0]
    return None


def validate_file(path: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        return [ValidationIssue("error", f"XML parse error: {e}")]

    root = tree.getroot()

    # Detect duplicate @id (Camunda rejects duplicates).
    id_counts: dict[str, int] = {}
    for el in root.iter():
        el_id = el.attrib.get("id")
        if el_id:
            id_counts[el_id] = id_counts.get(el_id, 0) + 1
    for el_id, count in sorted(id_counts.items()):
        if count > 1:
            issues.append(ValidationIssue("warn", f'duplicate id="{el_id}" x{count}'))

    all_ids: set[str] = set(id_counts.keys())

    # Wrong namespace prefixes: bpmn:BPMNShape / bpmn:BPMNEdge are invalid (must be bpmndi:*).
    for el in root.iter():
        if _ns_uri(el.tag) == NS["bpmn"] and _local_name(el.tag) in {"BPMNShape", "BPMNEdge", "BPMNDiagram", "BPMNPlane"}:
            issues.append(
                ValidationIssue(
                    "warn",
                    f"invalid DI element in BPMN namespace: {_local_name(el.tag)} (id={el.attrib.get('id')})",
                )
            )

    # bpmnElement references in DI
    for el in list(root.findall(".//bpmndi:BPMNShape", NS)) + list(root.findall(".//bpmndi:BPMNEdge", NS)):
        ref = el.attrib.get("bpmnElement")
        if not ref:
            issues.append(ValidationIssue("warn", f"{_local_name(el.tag)} missing @bpmnElement (id={el.attrib.get('id')})"))
            continue
        if ref not in all_ids:
            issues.append(ValidationIssue("warn", f"DI references missing element: {ref} (from {el.attrib.get('id')})"))

    # SequenceFlow references
    for flow in root.findall(".//bpmn:sequenceFlow", NS):
        fid = flow.attrib.get("id", "<no-id>")
        src = flow.attrib.get("sourceRef")
        tgt = flow.attrib.get("targetRef")
        if src and src not in all_ids:
            issues.append(ValidationIssue("warn", f"sequenceFlow {fid} sourceRef unresolved: {src}"))
        if tgt and tgt not in all_ids:
            issues.append(ValidationIssue("warn", f"sequenceFlow {fid} targetRef unresolved: {tgt}"))

    # Model elements inside BPMNPlane (invalid)
    for plane in root.findall(".//bpmndi:BPMNPlane", NS):
        for child in list(plane):
            if child.tag.startswith("{%s}" % NS["bpmn"]):
                issues.append(
                    ValidationIssue(
                        "warn",
                        f"BPMNPlane contains BPMN model element: {_local_name(child.tag)} (plane={plane.attrib.get('id')})",
                    )
                )

    return issues


def _collect_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for p in paths:
        if p.is_dir():
            files.extend(sorted(p.glob("*.bpmn")))
        else:
            files.append(p)
    return files


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", help="BPMN .bpmn files or directories")
    args = ap.parse_args(argv[1:])

    files = _collect_files([Path(p) for p in args.paths])
    any_errors = False
    any_warns = False

    for f in files:
        issues = validate_file(f)
        if not issues:
            continue
        print(f"\n{f}:")
        for issue in issues:
            if issue.level == "error":
                any_errors = True
            if issue.level == "warn":
                any_warns = True
            print(f"  [{issue.level}] {issue.message}")

    if any_errors:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

