---
name: bpmn-diagrams
description: Genera diagramas BPMN 2.0 (XML + BPMNDI) compatibles con Camunda Modeler a partir de diagramas Mermaid de procesos (sección 7). Usar cuando se necesite convertir `analisis/07_diagramas_procesos.md` en ficheros `.bpmn` dentro de `analisis/bpmn/` (uno por proceso), con subprocesos colapsados y drill-down.
---

# BPMN Diagrams (Camunda)

Convierte diagramas Mermaid (`flowchart TD`) de procesos en BPMN 2.0 + BPMNDI (Camunda Modeler).

## Modos

| Modo | Acción |
|------|--------|
| **Completo** | Generar BPMN por cada proceso de la sección 7 |
| **Prototipo** | **Omitir completamente** |

## Prerrequisitos

- `analisis/07_diagramas_procesos.md`
- `analisis/02_actores_y_roles.md` (para inferir nombres de lanes/roles)

## Salida requerida (OBLIGATORIO)

Un fichero BPMN por proceso:

- `analisis/bpmn/<id>_<slug>.bpmn`

Ejemplo:
- Proceso `7.1` → `analisis/bpmn/01_ingesta_y_validacion_multicanal.bpmn`

## Plantilla BPMN (OBLIGATORIO)

Usar como base la plantilla:

- `.github/skills/bpmn-diagrams/references/template.bpmn`

Esta plantilla define:

- Diagrama principal con lanes y subprocesos colapsados (`isExpanded="false"`)
- Un `BPMNDiagram` adicional por cada `bpmn:subProcess` para habilitar drill-down

### Cómo usar la plantilla

1) Copiar el fichero a `analisis/bpmn/<id>_<slug>.bpmn`
2) Reemplazar placeholders mínimos:
  - `{{PROCESS_NAME}}`, `{{PROCESS_DOC}}`, `{{SUBPROCESS_NAME}}`
3) Renombrar IDs TEMPLATE (IDs sin llaves, válidos para Camunda) y actualizar TODAS las referencias:
  - `Process_TEMPLATE` (y el `BPMNPlane @bpmnElement` del diagrama principal)
  - `SubProcess_TEMPLATE` (y su `BPMNShape` colapsada + su `BPMNPlane @bpmnElement` en el diagrama de drill-down)
3) Por cada subproceso del Mermaid:
  - Crear un `bpmn:subProcess id="..."` en el modelo
  - En el diagrama principal, su `BPMNShape` debe tener `isExpanded="false"`
  - Crear un `bpmndi:BPMNDiagram` adicional con `BPMNPlane @bpmnElement` apuntando al ID del subproceso
4) Mantener el diagrama principal SIN shapes/edges internos de subprocesos

## Flujo de trabajo

1) Identificar procesos del archivo `analisis/07_diagramas_procesos.md`:
   - Cada bloque `### 7.x. <Nombre del Proceso>` seguido de un bloque ```mermaid``` es un proceso a modelar.

2) Lanzar subagentes **en paralelo** (1 subagente por proceso) para acelerar la generación.
   - Requisito: cada subagente escribe **un único fichero** distinto en `analisis/bpmn/` (sin solaparse con otros subagentes).
   - Cada subagente debe:
     - Leer `analisis/07_diagramas_procesos.md` y extraer SOLO el proceso asignado (título + Mermaid).
     - Inferir lanes/roles desde `analisis/02_actores_y_roles.md`.
     - Escribir exactamente un `.bpmn` en `analisis/bpmn/` siguiendo la convención `<id>_<slug>.bpmn`.
     - No devolver el XML por consola: escribir el fichero.

3) Post-proceso + validación (recomendado, especialmente tras generación en paralelo)
   - Corregir automáticamente typos/errores recurrentes (mantener estos scripts fuera del skill para que no se pierdan si se regenera la carpeta):
     - `python .github\skills\bpmn-diagrams\scripts\fix_bpmn_outputs.py analisis/bpmn`
   - Validar estructura/referencias:
     - `python .github\skills\bpmn-diagrams\scripts\validate_bpmn.py analisis/bpmn`

## Reglas de modelado (BPMN)

### Interpretación del Mermaid

- Nodos tipo `([Inicio: ...])` → `bpmn:startEvent`
- Nodos tipo `([Fin: ...])` → `bpmn:endEvent`
- Nodos tipo `[Texto]` → `bpmn:task` (o `bpmn:userTask` si se indica Usuario/Rol o pantalla asociada (P-XXX); si no, `bpmn:task`)
- Nodos tipo `{¿... ?}` → `bpmn:exclusiveGateway`
- Etiquetas en ramas “Sí/No/…” → `bpmn:sequenceFlow @name="..."`

### Subprocesos

- Cada `subgraph "..."` que agrupa varios pasos debe convertirse en un `bpmn:subProcess` (dentro de `bpmn:process`).
- Dentro de cada `bpmn:subProcess` crear el detalle completo (start/end internos, tasks, gateways y sequenceFlows internos).
- En el diagrama principal, el subproceso debe verse COLAPSADO (ver reglas BPMNDI).

### Lanes (roles)

- Debe existir `bpmn:laneSet` y lanes con roles inferidos desde `analisis/02_actores_y_roles.md` (usar el **nombre del rol** tal cual aparece en la tabla).
- Asignar cada elemento DE NIVEL SUPERIOR (start/end/gateways/subProcess) a un lane mediante `bpmn:flowNodeRef`.
- No incluir nodos internos de subprocesos en los lanes del proceso principal (solo nivel superior).
- Si no se puede inferir el rol, asignar a `Sistema` (o el rol del sistema más cercano: `Sistema GESAC`, `Sistema SCLV`).

## Reglas de diagrama (BPMNDI) para Camunda (CRÍTICO)

1) Debe existir un diagrama principal:
- `bpmndi:BPMNDiagram` + `bpmndi:BPMNPlane bpmnElement="<id_del_process>"`
- Shapes de lanes (`bpmndi:BPMNShape bpmnElement="Lane_..." isHorizontal="true"`) con `dc:Bounds`
- Shapes SOLO de elementos de nivel superior (start/end/gateways/subProcess)
- Edges SOLO de `sequenceFlow` de nivel superior

2) Subprocesos colapsados en el diagrama principal:
- En el plane principal, el `bpmndi:BPMNShape` del subproceso debe tener `isExpanded="false"`.
- En el plane principal NO puede aparecer ningún `BPMNShape`/`BPMNEdge` que apunte a IDs internos del subproceso.

3) Drill-down / detalle del subproceso:
- Por CADA `bpmn:subProcess id="Sub_..."` crear un `bpmndi:BPMNDiagram` adicional con:
  - `bpmndi:BPMNPlane bpmnElement="Sub_..."` (el bpmnElement del plane es el ID del subproceso)
  - Shapes y edges para TODOS los nodos/flows internos del subproceso

**Prohibido (causa errores de parsing en Camunda Modeler):**
- No insertar elementos `bpmn:*` (startEvent/task/gateway/endEvent/sequenceFlow/...) dentro de `bpmndi:BPMNPlane`. En el plane SOLO van `bpmndi:BPMNShape` y `bpmndi:BPMNEdge`.
- No modelar el detalle de un subproceso como un `bpmn:process` separado. El detalle debe ir DENTRO de `<bpmn:subProcess>...</bpmn:subProcess>` del proceso principal.
- No usar `bpmn:BPMNShape`/`bpmn:BPMNEdge` (namespace incorrecto). Deben ser `bpmndi:BPMNShape`/`bpmndi:BPMNEdge`.
- No reutilizar IDs (especialmente en `bpmn:sequenceFlow`): cada elemento BPMN/DI debe tener `id` único.

4) Layout:
- Usar coordenadas (`dc:Bounds`) razonables para evitar solapes
- Diagrama principal: left-to-right simple
- Subdiagramas: layout simple (horizontal o vertical), pero legible

## Reglas de XML

- Encabezado: `<?xml version="1.0" encoding="UTF-8"?>`
- Namespaces mínimos: `bpmn`, `bpmndi`, `dc`, `di` (y `camunda` si se usan propiedades)
- IDs únicos en TODO el fichero (modelo + DI)
- Escapar correctamente `&`, `<`, `>`
- Corregir mojibake del input si aparece (ej.: `ValidaciÃƒÂ³n` → `Validación`, `SÃƒÂ­` → `Sí`)

## Checklist de validación

- Cada `bpmndi:* @bpmnElement` referencia un ID existente del modelo BPMN
- Ningún shape/edge interno del subproceso está en el plane principal
- Cada subproceso tiene su `BPMNDiagram`+`BPMNPlane` propio con shapes/edges internos
- Hay lanes y sus `LaneShape` visibles
- No faltan tareas: todas las del Mermaid existen en el modelo (nivel superior o dentro del subproceso correspondiente)
- Todas las tareas del Mermaid que referencian a pantallas (P-XXX) se definen como userTask.
