from __future__ import annotations

import argparse
import re
from pathlib import Path


def _normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n")


def _read(path: Path) -> str:
    return _normalize_newlines(path.read_text(encoding="utf-8"))


def _write(path: Path, text: str) -> None:
    path.write_text(_normalize_newlines(text), encoding="utf-8", newline="\n")


def fix_wrong_di_prefixes(text: str) -> str:
    # LLM typo: bpmn:BPMNShape/BPMNEdge instead of bpmndi:*
    text = text.replace("<bpmn:BPMNShape", "<bpmndi:BPMNShape")
    text = text.replace("</bpmn:BPMNShape>", "</bpmndi:BPMNShape>")
    text = text.replace("<bpmn:BPMNEdge", "<bpmndi:BPMNEdge")
    text = text.replace("</bpmn:BPMNEdge>", "</bpmndi:BPMNEdge>")
    return text


def _indent_block(block: str, prefix: str) -> str:
    block = block.rstrip("\n")
    if not block:
        return ""
    lines = block.split("\n")
    return "\n".join((prefix + line) if line.strip() else line for line in lines) + "\n"


def move_bpmn_model_from_planes_into_subprocesses(text: str) -> str:
    """
    Camunda Modeler (bpmn-moddle) does not accept BPMN model elements inside bpmndi:BPMNPlane.
    Some generated files wrongly embed <bpmn:startEvent>, <bpmn:task>, <bpmn:sequenceFlow>, ... inside the DI plane.

    This function:
      1) Detects those embedded <bpmn:*> blocks inside each <bpmndi:BPMNPlane bpmnElement="SubProcessId">.
      2) Removes them from the plane.
      3) Inserts them into the matching <bpmn:subProcess id="SubProcessId"> in the main model.
    """

    plane_re = re.compile(
        r'^(?P<indent>[ \t]*)<bpmndi:BPMNPlane\b(?P<attrs>[^>]*)\bbpmnElement="(?P<elem>[^"]+)"(?P<attrs2>[^>]*)>\n'
        r"(?P<body>.*?)(?P=indent)</bpmndi:BPMNPlane>\n",
        re.MULTILINE | re.DOTALL,
    )

    while True:
        target_plane: re.Match[str] | None = None
        for m in plane_re.finditer(text):
            body = m.group("body")
            first_di = min(
                [i for i in [body.find("<bpmndi:BPMNShape"), body.find("<bpmndi:BPMNEdge")] if i != -1] or [-1]
            )
            if first_di == -1:
                continue
            if "<bpmn:" in body[:first_di]:
                target_plane = m
                break

        if not target_plane:
            return text

        elem = target_plane.group("elem")
        plane_indent = target_plane.group("indent")
        body = target_plane.group("body")

        first_di = min([i for i in [body.find("<bpmndi:BPMNShape"), body.find("<bpmndi:BPMNEdge")] if i != -1])
        bpmn_block = body[:first_di].rstrip("\n") + "\n"
        di_rest = body[first_di:]

        # Replace the plane content without the BPMN block.
        plane_fixed = (
            f'{plane_indent}<bpmndi:BPMNPlane{target_plane.group("attrs")}bpmnElement="{elem}"{target_plane.group("attrs2")}>\n'
            f"{di_rest}"
            f"{plane_indent}</bpmndi:BPMNPlane>\n"
        )
        text = text[: target_plane.start()] + plane_fixed + text[target_plane.end() :]

        # Insert into matching subprocess in model.
        sub_re = re.compile(
            rf'^(?P<sindent>[ \t]*)<bpmn:subProcess\ id="{re.escape(elem)}"(?P<sattrs>[^>]*)>\n'
            r"(?P<sinner>.*?)(?P=sindent)</bpmn:subProcess>\n",
            re.MULTILINE | re.DOTALL,
        )
        sm = sub_re.search(text)
        if not sm:
            # If there is no matching subprocess, keep plane-fixed and drop model block.
            # Better to leave file parseable than to keep invalid DI.
            continue

        sinner = sm.group("sinner")
        # Idempotency: if subprocess already contains model detail, don't duplicate.
        if "<bpmn:startEvent" in sinner or "<bpmn:task" in sinner or "<bpmn:userTask" in sinner:
            continue

        target_indent = sm.group("sindent") + "  "
        moved = _indent_block(bpmn_block, target_indent)

        # Insert after last incoming/outgoing inside the subprocess.
        s_lines = sinner.split("\n")
        insert_at = 0
        for i, line in enumerate(s_lines):
            if re.search(r"<bpmn:(incoming|outgoing)>", line):
                insert_at = i + 1

        new_sinner = "\n".join(s_lines[:insert_at] + [moved.rstrip("\n")] + s_lines[insert_at:]).lstrip("\n") + "\n"
        text = text[: sm.start("sinner")] + new_sinner + text[sm.end("sinner") :]


def fix_duplicate_flow_r01_in_trazabilidad(text: str) -> str:
    """
    Fix pattern where multiple sequenceFlows share the same id="Flow_R01" from Start_Traza to different tasks.
    """
    if 'id="Start_Traza"' not in text:
        return text

    # If Flow_R01 doesn't exist, assume already fixed.
    if 'id="Flow_R01"' not in text and ">Flow_R01<" not in text:
        return text

    text = text.replace(
        "<bpmn:outgoing>Flow_R01</bpmn:outgoing>",
        "\n".join(
            [
                "<bpmn:outgoing>Flow_R01_EXP</bpmn:outgoing>",
                "<bpmn:outgoing>Flow_R01_Alerta</bpmn:outgoing>",
                "<bpmn:outgoing>Flow_R01_Escal</bpmn:outgoing>",
                "<bpmn:outgoing>Flow_R01_Desm</bpmn:outgoing>",
                "<bpmn:outgoing>Flow_R01_Ret</bpmn:outgoing>",
                "<bpmn:outgoing>Flow_R01_Pend</bpmn:outgoing>",
            ]
        ),
    )

    task_incoming_map = {
        "Task_RegFechaExp": "Flow_R01_EXP",
        "Task_RegAlerta": "Flow_R01_Alerta",
        "Task_RegEscalamiento": "Flow_R01_Escal",
        "Task_RegDesmarcado": "Flow_R01_Desm",
        "Task_RegTraslado": "Flow_R01_Ret",
        "Task_RegValidacion": "Flow_R01_Pend",
    }
    for task_id, flow_id in task_incoming_map.items():
        text = re.sub(
            rf'(<bpmn:(task|userTask)\b[^>]*\bid="{re.escape(task_id)}"[^>]*>[\s\S]*?<bpmn:incoming>)Flow_R01(</bpmn:incoming>)',
            rf"\g<1>{flow_id}\g<3>",
            text,
            count=1,
        )

    seq_block_re = re.compile(
        r'(?P<indent>[ \t]*)<bpmn:sequenceFlow id="Flow_R01" sourceRef="Start_Traza" targetRef="Task_RegFechaExp" />\n'
        r'(?P=indent)<bpmn:sequenceFlow id="Flow_R01" sourceRef="Start_Traza" targetRef="Task_RegAlerta" />\n'
        r'(?P=indent)<bpmn:sequenceFlow id="Flow_R01" sourceRef="Start_Traza" targetRef="Task_RegEscalamiento" />\n'
        r'(?P=indent)<bpmn:sequenceFlow id="Flow_R01" sourceRef="Start_Traza" targetRef="Task_RegDesmarcado" />\n'
        r'(?P=indent)<bpmn:sequenceFlow id="Flow_R01" sourceRef="Start_Traza" targetRef="Task_RegTraslado" />\n'
        r'(?P=indent)<bpmn:sequenceFlow id="Flow_R01" sourceRef="Start_Traza" targetRef="Task_RegValidacion" />\n',
        re.MULTILINE,
    )

    def _seq_repl(m: re.Match[str]) -> str:
        ind = m.group("indent")
        return "\n".join(
            [
                f'{ind}<bpmn:sequenceFlow id="Flow_R01_EXP" sourceRef="Start_Traza" targetRef="Task_RegFechaExp" />',
                f'{ind}<bpmn:sequenceFlow id="Flow_R01_Alerta" sourceRef="Start_Traza" targetRef="Task_RegAlerta" />',
                f'{ind}<bpmn:sequenceFlow id="Flow_R01_Escal" sourceRef="Start_Traza" targetRef="Task_RegEscalamiento" />',
                f'{ind}<bpmn:sequenceFlow id="Flow_R01_Desm" sourceRef="Start_Traza" targetRef="Task_RegDesmarcado" />',
                f'{ind}<bpmn:sequenceFlow id="Flow_R01_Ret" sourceRef="Start_Traza" targetRef="Task_RegTraslado" />',
                f'{ind}<bpmn:sequenceFlow id="Flow_R01_Pend" sourceRef="Start_Traza" targetRef="Task_RegValidacion" />',
                "",
            ]
        )

    text = seq_block_re.sub(_seq_repl, text)

    edge_map = {
        "Edge_Flow_R01a": "Flow_R01_EXP",
        "Edge_Flow_R01b": "Flow_R01_Alerta",
        "Edge_Flow_R01c": "Flow_R01_Escal",
        "Edge_Flow_R01d": "Flow_R01_Desm",
        "Edge_Flow_R01e": "Flow_R01_Ret",
        "Edge_Flow_R01f": "Flow_R01_Pend",
    }
    for edge_id, flow_id in edge_map.items():
        text = re.sub(
            rf'(<bpmndi:BPMNEdge\b[^>]*\bid="{re.escape(edge_id)}"[^>]*\bbpmnElement=")Flow_R01(")',
            rf"\g<1>{flow_id}\g<2>",
            text,
        )
    return text


def fix_file(path: Path) -> bool:
    before = _read(path)
    after = before
    after = fix_wrong_di_prefixes(after)
    after = fix_duplicate_flow_r01_in_trazabilidad(after)
    after = move_bpmn_model_from_planes_into_subprocesses(after)
    if after != before:
        _write(path, after)
        return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", help="BPMN .bpmn files or directories")
    args = ap.parse_args()

    targets: list[Path] = []
    for raw in args.paths:
        p = Path(raw)
        if p.is_dir():
            targets.extend(sorted(p.glob("*.bpmn")))
        else:
            targets.append(p)

    fixed = 0
    for p in targets:
        if not p.exists():
            continue
        if fix_file(p):
            fixed += 1

    return 0 if fixed >= 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())

