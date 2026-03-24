---
name: backlog-planner
description: Genera backlog de tareas técnicas para un módulo funcional del MVP full-stack (frontend SAPUI5 + backend CAP/ABAP). Valida cobertura individualmente tras cada backlog. Usar después de generar el diseño técnico.
---

# Backlog Planner

Genera backlog técnico para UN módulo funcional específico (frontend UI5 + backend CAP o ABAP + persistencia/integraciones).

## Nivel de detalle requerido (OBLIGATORIO)

El backlog generado debe tener **un nivel de granularidad y detalle alto**, siguiendo el template incluido como recurso en este skill:

- `references/backlog-template.detallado.md`

### Templates Reutilizables del Proyecto

Al generar tareas de **pantallas frontend UI5**, considerar la separación técnica y artefactos reutilizables alineados con la metodología del proyecto:

- **Modelos UI5**: `webapp/modules/[moduleName]/model/models.js` y `viewModel.js` para shape de datos, catálogos y estado UI.
- **Servicios UI5**: `webapp/modules/[moduleName]/services/[Entidad]Service.js` y `[Entidad]ServiceMock.js` para modo dual Mock/API.
- **Controladores y utilidades**: `webapp/modules/[moduleName]/controller/*.controller.js`, `util/formatters.js`, `util/helpers.js`, `util/constants.js`.
- **Testing E2E UI5**: `webapp/test/integration/*Journey.js`, `pages/*.js`, `AllJourneys.js` siguiendo la skill `ui5-test-generator`.

**Implicaciones para el backlog:**
- Las tareas de pantallas deben referenciar explícitamente los artefactos UI5 usados (XML View, controller, fragment, `manifest.json`, Page Object/Journey si aplica).
- El estado UI vive en `JSONModel`/`viewModel.js` y en la lógica del controller, NO en stores de SPA.
- Ejemplo: "Configurar columnas de `sap.m.Table` en `[Entidad].view.xml`" en lugar de "Crear componente TablaX".

### Granularidad de Tareas

Esto implica:

- Separar tareas por **artefacto concreto** (archivo / método / acción / vista / controller / ruta / servicio / test).
- Incluir **nombres explícitos** de archivos y símbolos (`schema.cds`, `[modulo]-service.cds`, `[Entidad]Service.js`, `[Entidad].controller.js`, `[Entidad].view.xml`, `viewModel.js`, `ZI_[Entidad]`, `ZBP_[Entidad]`, etc.).
- Para **tipos y estado (Frontend UI5)** (CRÍTICO): alinear con `ui5-code-generator`; modelar catálogos, estados y shape inicial en `model/*.js` o `util/constants.js`. No asumir TypeScript salvo que el proyecto UI5 ya lo use explícitamente.
- Para **servicios**: contemplar el **modelo dual** (por defecto mock) con:
    - una tarea de creación de `...ServiceMock.js` + tareas por cada método relevante (mock + latencia + datos deterministas)
    - una tarea de creación de `...Service.js` + tareas por cada método relevante (OData/CAP/ABAP)
        - una tarea para que **el controller o viewModel del módulo** seleccione la implementación activa según la configuración del proyecto, para que la UI no cambie.
            - No exigir una fachada adicional salvo que el diseño lo pida explícitamente.
- Para **contrato API/OData** (OBLIGATORIO):
    - Incluir una tarea explícita de **“normalizar respuesta backend”** cuando CAP/ABAP use wrappers, actions con payload propio u OData con mapeos adicionales.
      - La tarea debe vivir en la sección **Servicios (Frontend)** y describir el cambio de forma atómica, por ejemplo:
        - "En `[Entidad]Service.js`, normalizar respuesta OData/action extrayendo payload útil y propagando errores coherentes para UI5".
    - Si el diseño no indica el formato exacto de respuesta, el backlog debe incluir una tarea de verificación del contrato real y ajuste del service.
- Para **estado UI**: una tarea de creación del `viewModel.js`/estado técnico + tareas por acción, carga, mutación o helper relevante.
- Para **páginas**: una tarea de creación de la vista/controller principal + tareas para configuración de tablas, filtros, validaciones, diálogos, navegación, mensajes y exportaciones. Si la pantalla reutiliza fragmentos o controles existentes, no crear tareas adicionales para artefactos base que solo se configuran.
- Para **backend (API)**: tareas por artefacto (CAP: modelos CDS / servicios / handlers / autorizaciones / CSV / tests; ABAP: tablas-DDIC / CDS / behavior / service definition / service binding / clases / FM / jobs) y **1 tarea por operación/action/end-point relevante**.
- Para **BD**: al menos 1 tarea por artefacto persistente principal (CAP: `schema.cds`, `types.cds`, `db/data/*.csv`; ABAP: tabla DDIC, CDS raíz/proyección, dominios/elementos o customizing si aplica).
- Para **tipado de persistencia (anti-schema-validation)**: si una magnitud requiere precisión, planificar `Decimal(p,s)` en CDS o tipo/dominio ABAP explícito; no usar tipos ambiguos si el diseño exige precisión. Si hay cambio sobre un artefacto ya desplegado o transportado, planificar una evolución segura y no una sobreescritura destructiva.
- Para **integraciones externas** (OBLIGATORIO cuando existan): el backlog debe incluir tareas para garantizar estabilidad en dev/E2E:
    - Una tarea de **modo mock por configuración** o sustitución controlada para no depender del sistema externo real.
    - Una tarea de **seed mínimo** para dev/E2E (roles/usuario técnico/permisos/datos base necesarios) mediante CSV CAP, datos mock UI5 o customizing/fixtures ABAP según corresponda.
- Añadir sección **Componentes Compartidos** solo si hay componentes o fragmentos transversales reutilizables (ver template).
- Añadir sección **Rutas** (y navegación/menú) cuando el módulo exponga pantallas nuevas.
- En **tests E2E**: crear **1 tarea por cada `PF-XXX`** relevante del módulo (no solo “un test genérico”), para asegurar cobertura; cada tarea debe incluir `PF-XXX` en `Ref:`.
- En **tests E2E (anti-flaky/mocks)**: si un PF depende de IDs/casos concretos, incluir tarea explícita para datos mock deterministas en `*ServiceMock.js`, fixtures o modelos JSON (sin placeholders por defecto que rompan asserts).
- En **tests backend**: incluir tareas CAP de integración/autorización/acciones y/o ABAP Unit/servicio para operaciones críticas.

## Formato estricto (OBLIGATORIO)

El backlog **debe** seguir el template con estructura y estilo homogéneos.

Reglas de formato:

- Cada tarea debe ser un ítem de lista con checkbox: `- [ ] ...`.
- Cada tarea debe incluir trazabilidad en la misma línea:
    - Tipos/Servicios/Store/Backend/BD: `Ref: (RF-XXX)` y, si aplica, también `(CU-XXX)`.
    - Páginas/Rutas (UI): `Ref: [Pantalla P-XXX] (HU-XXX) (RF-XXX)` y, si aplica, también `(CU-XXX)`.
    - Tests (UI/E2E): `Ref: [Pantalla P-XXX] (PF-XXX) (HU-XXX) (RF-XXX)` y, si aplica, también `(CU-XXX)`.
- Se permite agrupar por archivo usando subtítulos como `### Archivo: ...` o `### FooService`.
- **Prohibido** usar bloques por “tarea” con subtítulos tipo `### Tarea XX-001: ...`.
- **Prohibido** incluir “Criterios de aceptación” dentro del backlog (eso vive en HUs); el backlog solo crea tareas atómicas referenciadas.
- **Prohibido** incluir tablas tipo `| Método | ... |` y bloques grandes de código. En su lugar, crear 1 tarea por método/tipo/componente como en el template.

Antipatrones comunes que deben corregirse antes de validar:

- Secciones narrativas por tarea (Descripción/Archivo/Métodos/Criterios de aceptación).
- Código embebido para definir entidades/estructuras completas (debe descomponerse en tareas por tipo/enum/campo/artefacto relevante).
- “Implementar servicio completo” sin dividir por métodos, actions, handlers o binding expuesto.
- “Implementar pantalla completa” sin dividir por vista, controller, fragmentos, filtros, tabla/columnas, acciones y validaciones.

## Prerrequisitos

- `design/01_technical_design.md` - Diseño técnico con módulos
- `design/02_data_model.md` - Modelo de datos
- `design/03_data_services.md` - Especificación de servicios
- `analisis/03_requerimientos_funcionales.md` - RFs
- `analisis/05_historias_usuario.md` - HUs con criterios de aceptación
- `analisis/06_casos_uso.md` - Casos de uso (CUs)
- `analisis/10_interfaces_usuario.md` - Pantallas
- `analisis/11_diagramas_navegacion.md` - Rutas de navegación
- `analisis/13_pruebas_funcionales.md` - Pruebas funcionales (PFs)
- `analisis/14_matriz_trazabilidad.md` - Relaciones RF-HU-CU-Pantalla-PF

Opcionales (si aplican al módulo):
- `analisis/04_requerimientos_tecnicos.md` - Seguridad/SSO, rendimiento, requisitos no funcionales
- `analisis/08_integraciones.md` - Integraciones SAP/CAP/ABAP y sincronizaciones

## Parámetro de Entrada

El skill recibe:
1. **Nombre del módulo** a procesar
2. **Número de orden** del módulo (según tabla de dependencias en design/01)

## Ordenamiento de Módulos

El orden de los módulos viene **predefinido en `design/01_technical_design.md`** (Sección 4: Dependencias entre Módulos).

### Uso de la Tabla de Dependencias

Leer directamente la tabla de dependencias del diseño técnico:

```markdown
| Módulo | Depende de | Requerido por | Orden |
|--------|------------|---------------|-------|
| auth | - | todos | 01 |
| catalogos | auth | expedientes | 02 |
...
```

**NO recalcular dependencias** - usar el orden establecido en el diseño técnico.

### Módulos del Template

Los módulos `auth`, `admin-usuarios` y `auditoria` ya pueden existir en el template base:
- **NO generar backlog** si no requieren modificaciones
- **Generar backlog** solo si el diseño técnico indica cambios específicos

## Estructura del Backlog

Generar el archivo `backlog/XX_[Nombre_Modulo].md` siguiendo **exactamente** el template del skill:

- `references/backlog-template.detallado.md`

Orden obligatorio de alto nivel (según template):

1. **Backend** (BD y modelo técnico → Servicios CAP/ABAP → Seguridad/Config → Integraciones/Jobs → Tests Backend)
2. **Frontend** (Tipos/Modelos → Servicios → Estado → Páginas/Rutas → Componentes compartidos si aplica → Tests E2E)

Reglas:

- Copiar el esqueleto completo del template y reemplazar placeholders (`[modulo]`, `P-XXX`, `HU-XXX`, `CU-XXX`, `PF-XXX`, `RF-XXX`, rutas, nombres de archivos/símbolos`).
- Reemplazar placeholders de módulo usando:
    - `[moduleSlug]` para carpetas CAP, rutas UI5/hash, servicios expuestos y tests E2E.
    - `[moduleName]` para artefactos UI5/CAP en PascalCase y nombres lógicos de entidades/servicios.
    - `[moduleKey]` para identificadores técnicos, nombres snake_case, CSV, prefijos cortos u objetos ABAP cuando aplique.
- Mantener la misma granularidad: tareas atómicas por archivo/método/acción/componente/ruta/test.
- Mantener trazabilidad en cada ítem (según template).
- Mantener el formato de tareas como lista con checkbox; evitar cualquier formato alternativo.

## Proceso de Generación

1. Leer tabla de dependencias de `design/01_technical_design.md` (Sección 4)
2. Recibir nombre del módulo y número de orden (según tabla)
3. Obtener dependencias del módulo directamente de la tabla
4. Filtrar RFs del módulo desde diseño técnico
5. Obtener HUs, CUs, PFs y Pantallas asociadas desde matriz
6. Derivar requisitos de implementación **no evidentes por IDs** (OBLIGATORIO):
    - Leer `analisis/06_casos_uso.md` y convertir **Flujo Principal + Flujos Alternativos** en tareas técnicas (UI5/servicios/actions/validaciones/confirmaciones).
    - Leer `analisis/12_prototipos_interfaz.md` y convertir **acciones y componentes de pantalla** (botones, confirmaciones, bloques informativos, mensajes, auditoría, etc.) en tareas técnicas.
    - Leer `analisis/09_diagramas_estados.md` si aplica al módulo y convertir transiciones/estados en tareas (validaciones, permisos, actions/operations y tests).
7. Generar tareas: frontend (modelos, servicios, estado, pantallas, rutas), backend (persistencia, servicios CAP/ABAP, handlers/behavior, seguridad, integraciones, jobs), tests (backend + E2E)
8. Guardar en `backlog/XX_[Nombre_Modulo].md`
9. Verificar **formato estricto** (sin “### Tarea”, sin “Criterios de aceptación”, sin tablas de métodos, sin bloques de código largos)
10. Ejecutar validaciones `XX_1..XX_6`
11. Ejecutar `valida_quality_gates_backlog.py` y corregir hasta estado `OK` (incluye WARN con justificación individual cuando aplique)
12. Pasar al siguiente módulo (solo si gates `XX_1..XX_6` están en `OK`)

## Validación de Cobertura (Por Cada Backlog)

**IMPORTANTE:** La validación se ejecuta **inmediatamente después de generar cada backlog**, NO al final de todos.

```powershell
python skills/traceability-validator/scripts/valida_trazabilidad.py --backlog backlog/XX_[Modulo].md --module-scope --out backlog/check/XX_1_check_traceability_[Modulo].md
```

Validación de integridad del backlog contra el diseño técnico y catálogo de datos/servicios:

```powershell
python skills/backlog-planner/scripts/valida_integridad_diseno.py --backlog backlog/XX_[Modulo].md --module-scope <moduleSlug> --out backlog/check/XX_2_check_design_[Modulo].md
```

Validación de completitud funcional contra prototipos (acciones "especiales" derivadas de `analisis/12_prototipos_interfaz.md`):

```powershell
python skills/backlog-planner/scripts/valida_completitud_funcional.py --backlog backlog/XX_[Modulo].md --module-scope <moduleSlug> --out backlog/check/XX_3_check_funcional_[Modulo].md
```

Validación de completitud por HU (tareas en Backend/Frontend/Tests E2E por HU):

```powershell
python skills/backlog-planner/scripts/valida_completitud_hu.py --backlog backlog/XX_[Modulo].md --module-scope <moduleSlug> --out backlog/check/XX_4_check_hu_[Modulo].md
```

Validación de PF en sección Tests E2E (cada PF del módulo debe estar en Tests E2E):

```powershell
python skills/backlog-planner/scripts/valida_pf_en_e2e.py --backlog backlog/XX_[Modulo].md --module-scope <moduleSlug> --out backlog/check/XX_5_check_pf_e2e_[Modulo].md
```

Validación de navegación (rutas + tarea de menú/sidebar) contra backlog:

```powershell
python skills/backlog-planner/scripts/valida_navegacion_backlog.py --backlog backlog/XX_[Modulo].md --module-scope <moduleSlug> --out backlog/check/XX_6_check_nav_[Modulo].md
```

Validación consolidada de quality gates (OBLIGATORIA, bloqueante para avanzar al siguiente módulo):

```powershell
python skills/backlog-planner/scripts/valida_quality_gates_backlog.py --scope module --traceability backlog/check/XX_1_check_traceability_[Modulo].md --traceability-warn-justifications backlog/check/XX_1_check_traceability_[Modulo]_warnings.md --design backlog/check/XX_2_check_design_[Modulo].md --funcional backlog/check/XX_3_check_funcional_[Modulo].md --hu backlog/check/XX_4_check_hu_[Modulo].md --hu-warn-justifications backlog/check/XX_4_check_hu_[Modulo]_warnings.md --pf-e2e backlog/check/XX_5_check_pf_e2e_[Modulo].md --nav backlog/check/XX_6_check_nav_[Modulo].md --out backlog/check/XX_8_check_quality_gates_[Modulo].md
```

### Quality Gates (XX_1..XX_6)

- Para justificaciones de WARN en `XX_1` y `XX_4`, usar una entrada individual por warning.
- Formato recomendado:
  - `| ID | Warning | Decision | Justificacion | Evidencia |`
  - `| W-001 | ... | ACEPTADO/CORREGIDO | ... | ... |`

- `XX_1_check_traceability_[Modulo].md`
  - `Discrepancias (ERROR) = 0`
  - `Observaciones (WARN) = 0` o `WARN 100% justificados` (1 warning = 1 justificación individual en `XX_1_check_traceability_[Modulo]_warnings.md`)
- `XX_2_check_design_[Modulo].md`
  - `Errores = 0`
- `XX_3_check_funcional_[Modulo].md`
  - `faltantes = 0`
- `XX_4_check_hu_[Modulo].md`
  - `HUs faltantes por seccion (ERROR) = 0`
  - `PF faltantes en Tests E2E (ERROR) = 0`
  - `criterios sin mapear a PF (WARN) = 0` o `WARN 100% justificados` (1 warning = 1 justificación individual en `XX_4_check_hu_[Modulo]_warnings.md`)
- `XX_5_check_pf_e2e_[Modulo].md`
  - `PF faltantes en Tests E2E (ERROR) = 0`
- `XX_6_check_nav_[Modulo].md`
  - `rutas faltantes (ERROR) = 0`
  - `menu faltante (ERROR) = 0`

### Proceso de Corrección

```
MIENTRAS (quality_gates != OK):
    1. Leer backlog/check/XX_1_check_traceability_[Modulo].md (cobertura con traceability-validator)
    2. Leer backlog/check/XX_2_check_design_[Modulo].md (integridad con valida_integridad_diseno.py)
    3. Leer backlog/check/XX_3_check_funcional_[Modulo].md (completitud funcional por prototipos)
    4. Leer backlog/check/XX_4_check_hu_[Modulo].md (completitud por HU)
    5. Leer backlog/check/XX_5_check_pf_e2e_[Modulo].md (PF en Tests E2E)
    6. Leer backlog/check/XX_6_check_nav_[Modulo].md (navegación)
    7. Revisar backlog/check/XX_8_check_quality_gates_[Modulo].md (estado de gates)
    8. Corregir backlog para todos los ERROR > 0
    9. Para WARN en XX_1 y XX_4: corregir a 0 o documentar justificación individual por warning
   10. Re-ejecutar validaciones XX_1..XX_6
   11. Re-ejecutar valida_quality_gates_backlog.py
FIN MIENTRAS

Pasar al siguiente módulo
```

### Criterios de Validación

| Tipo | Criterio | Acción si falla |
|------|----------|-----------------|
| RF sin tarea | RF del módulo no tiene tarea asociada | Agregar tarea en sección correspondiente |
| HU sin test | HU no tiene test E2E | Agregar tarea en sección Tests E2E |
| PF sin tarea | PF del módulo no aparece referenciada en el backlog | Agregar tarea(s) en sección Tests E2E con `Ref: ... (PF-XXX)` |
| PF fuera de Tests E2E | PF aparece en backlog, pero no en sección Tests E2E | Mover o duplicar tarea dentro de Tests E2E |
| CU sin tarea | CU del módulo no aparece referenciada en el backlog | Agregar trazabilidad `(CU-XXX)` en tareas UI/Backend relevantes |
| Pantalla sin implementar | Pantalla del módulo sin tarea | Agregar tarea en sección Páginas |
| Navegación incompleta | Falta tarea de menú/sidebar o falta ruta | Agregar tareas en sección Rutas/Navegación |

## Escritura Incremental (Recomendado)

Para módulos extensos, generar archivo de forma INCREMENTAL:

1. **Crear archivo** con encabezado y dependencias
2. **Agregar secciones** progresivamente (Tipos → Servicios → Store → Páginas → Tests)
3. **Escribir 10-15 tareas** a la vez, luego append siguiente bloque
4. **NO acumular** todo en memoria antes de escribir

### Respuesta del Skill

Confirmar resultados de forma concisa, no devolver contenido completo.

## Output

```
Archivo backlog/XX_[Nombre_Modulo].md generado:
- Dependencias: [lista]
- Tareas: Y
- RFs cubiertos: Z
- HUs cubiertas: W
- Pantallas cubiertas: V
- Cobertura (traceability-validator): OK (0 errores)
- Integridad (diseno): OK (0 errores)
- Completitud funcional (prototipos): OK (0 errores)
- Completitud por HU: OK (0 errores)
- PF en Tests E2E: OK (0 errores)
- Navegacion (rutas + menu): OK (0 errores)
- Quality gates (XX_1..XX_6): OK (`backlog/check/XX_8_check_quality_gates_[Modulo].md`)
```
