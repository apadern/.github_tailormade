---
name: mermaid-diagrams
description: Genera diagramas Mermaid para análisis funcional - procesos (flowchart) y estados (stateDiagram-v2). Usar cuando se necesite generar las secciones 7 y 9 de un análisis funcional.
---

# Mermaid Diagrams

Genera diagramas técnicos en formato Mermaid (procesos y estados).

## Modos

| Modo | Acción |
|------|--------|
| **Completo** | Generar secciones 7, 9 |
| **Prototipo** | **Omitir completamente** |

## Prerrequisitos

- `analisis/05_historias_usuario.md` (definición de HUs; usar para determinar cobertura real del proceso)
- `analisis/10_interfaces_usuario.md` (mapeo HU <-> pantallas P-XXX; usar para etiquetar pasos de usuario)
- `analisis/06_casos_uso.md` (CUs con flujos principales y alternativos)
- `analisis/03_requerimientos_funcionales.md` (entidades para diagramas de estados)

## Sección 7: Diagramas de Procesos

Modelar flujos de negocio complejos identificados en CUs:

```markdown
## 7. Diagramas de Procesos

### 7.x. <Nombre del Proceso>

> **HUs cubiertas:** HU-XXX, HU-YYY

` ` `mermaid
%% HUs cubiertas: HU-XXX, HU-YYY
flowchart TD
    subgraph "Contexto"
        A[Inicio] --> B{Decisión}
        B -- Sí --> C[Acción]
        B -- No --> D[Alternativa]
    end
` ` `
```

### Reglas de trazabilidad (OBLIGATORIO)

- Para cada diagrama Mermaid de proceso, incluir SIEMPRE un comentario al inicio del bloque:
  - `%% HUs cubiertas: HU-..., HU-...`
- Identificar las HUs cubiertas revisando `analisis/05_historias_usuario.md` (y su correspondencia con los CUs de `analisis/06_casos_uso.md`).
- En cada paso donde intervenga un usuario/rol (cualquier acción dentro de un `subgraph` de un actor humano), indicar la(s) pantalla(s) utilizada(s) según `analisis/10_interfaces_usuario.md`:
  - Ejemplo: `U --> V[Administrador accede a Listado de Convocatorias (P-001)]`
  - Si para una acción no existe pantalla definida en Sección 10, indicarlo explícitamente como `(Sin pantalla)`.

### Elementos flowchart

- `[texto]` - Nodo rectangular (acción)
- `{texto}` - Nodo rombo (decisión)
- `([texto])` - Nodo estadio (inicio/fin)
- `subgraph "título"` - Agrupar por contexto/actor

Guardar como: `analisis/07_diagramas_procesos.md`

## Sección 9: Diagramas de Estados

Modelar ciclo de vida de entidades clave:

```markdown
## 9. Diagramas de Estados

### 9.x. Diagrama de Estados: <Entidad>

` ` `mermaid
stateDiagram-v2
    [*] --> Estado1: Evento
    Estado1 --> Estado2: Transición
    Estado2 --> [*]
` ` `
```

### Entidades típicas

- Expediente, Solicitud, Factura, Usuario, Incidencia, Remesa

Guardar como: `analisis/09_diagramas_estados.md`

## Reglas

- Usar sintaxis Mermaid válida
- Diagramas deben reflejar los flujos de los CUs
- Un diagrama por proceso/entidad relevante
- **Sección 7:** cada bloque `mermaid` debe incluir `%% HUs cubiertas: ...` y cada paso de usuario debe referenciar pantalla(s) `(P-XXX)` obtenidas desde `analisis/10_interfaces_usuario.md`
- **En modo prototipo: omitir este skill completamente**
- **NO incluir resúmenes, conclusiones ni secciones adicionales al final del documento**
