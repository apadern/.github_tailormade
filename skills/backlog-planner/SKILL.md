---
name: backlog-planner
description: Genera backlog de tareas técnicas para un módulo funcional del MVP full-stack (frontend web + backend Java). Valida cobertura individualmente tras cada backlog. Usar después de generar el diseño técnico.
---

# Backlog Planner

Genera backlog técnico para UN módulo funcional específico (frontend + backend + BD).

## Nivel de detalle requerido (OBLIGATORIO)

El backlog generado debe tener **un nivel de granularidad y detalle alto**, siguiendo el template incluido como recurso en este skill:

- `references/backlog-template.detallado.md`

### Templates Reutilizables del Proyecto

Al generar tareas de **páginas frontend**, considerar los templates reutilizables disponibles en `frontend/src/shared/templates/`:

- **ListPageTemplate**: Para páginas de listado con búsqueda, filtros, paginación (pageSize=10 por defecto), ordenamiento y exportación.
- **FormPageTemplate**: Para formularios crear/editar con manejo de estado, validaciones, navegación y botones (Guardar/Cancelar).
- **DetailPageTemplate**: Para vistas de detalle con acciones, breadcrumbs y navegación.

**Componentes compartidos** en `frontend/src/shared/components/`:
- `DataTable`, `SearchHeader`, `Pagination`, `ErrorAlert`, `PageHeader`, `FilterCard`, `StatusBadge`, `LoadingState`, `EmptyState`

**Implicaciones para el backlog:**
- Las tareas de páginas deben referenciar explícitamente el template usado (si aplica).
- Los filtros, tablas y componentes específicos se crean como props/configuración del template, NO como componentes independientes completos.
- Ejemplo: "Configurar columnas del ListPageTemplate" en lugar de "Crear componente TablaX".

### Granularidad de Tareas

Esto implica:

- Separar tareas por **artefacto concreto** (archivo / método / acción / componente / ruta / test).
- Incluir **nombres explícitos** de archivos y símbolos (`FooService.ts`, `getAll(filters?)`, `BarPage.tsx`, `bazStore.ts`, etc.).
- Para **tipos (Frontend)** (CRÍTICO): prohibido usar `enum` en TypeScript en este repo; definir enums como `const ... as const` + `type` union derivado.
- Para **servicios**: contemplar el **modelo dual** (por defecto mock) con:
    - una tarea de creación de `...ServiceMock.ts` + tareas por cada método relevante (mock + latencia)
    - una tarea de creación de `...Service.ts` + tareas por cada método relevante (API)
        - una tarea para que **el store del módulo** seleccione la implementación activa con `SERVICE_MODE` (derivado de `VITE_USE_MOCK=true|false`) para que la UI no cambie.
            - No exigir `services/index.ts` como fachada/selector salvo que el diseño lo pida explícitamente.
- Para **contrato API** (OBLIGATORIO):
    - Incluir una tarea explícita de **“normalizar respuesta backend”** cuando el backend use wrappers (p.ej. `ApiResponse{success,message,data}`).
      - La tarea debe vivir en la sección **Servicios (Frontend)** y describir el cambio de forma atómica, por ejemplo:
        - "En `[Entidad]Service.ts`, soportar payload envuelto (`ApiResponse<T>`) extrayendo `.data` y propagando errores coherentes".
    - Si el diseño no indica el formato exacto de respuesta, el backlog debe incluir una tarea de verificación del contrato real (inspeccionar respuesta HTTP) y ajuste del service.
- Para **stores**: una tarea de creación del store + tareas por acción/selector.
- Para **páginas**: una tarea de creación de la página (especificando template reutilizable si aplica: ListPageTemplate/FormPageTemplate/DetailPageTemplate) + tareas para configuración de columnas, filtros, validaciones, botones/acciones, exportaciones. Si la página usa template, los componentes base (DataTable, SearchHeader, Pagination) NO requieren tareas adicionales.
- Para **backend (API)**: tareas por artefacto (migración Flyway / entity JPA / repository / service / controller / DTOs / config / jobs) y **1 tarea por método/end-point relevante**.
- Para **BD**: al menos 1 tarea por migración Flyway (tablas/índices/constraints) y, si aplica, seeds/datos iniciales.
- Para **BD/JPA (anti-schema-validation)**: si una columna es `numeric`, planificar entidad con `BigDecimal` (no `Double`). Si una columna usa dominio Postgres, planificar `@Column(columnDefinition = "<dominio>")`. Si hay cambio en migraciones existentes: **nueva** migración (no editar una aplicada).
- Para **integraciones externas** (OBLIGATORIO cuando existan): el backlog debe incluir tareas para garantizar estabilidad en dev/E2E:
    - Una tarea de **modo mock por configuración** (p.ej. flag en `application-dev.yml`/env var) para no depender del sistema externo real.
    - Una tarea de **seed mínimo** para dev/E2E (roles/usuario admin/permisos/datos base necesarios) mediante migración Flyway.
- Añadir sección **Componentes Compartidos** solo si hay componentes transversales reutilizables (ver template).
- Añadir sección **Rutas** (y navegación/Sidebar) cuando el módulo exponga pantallas nuevas.
- En **tests E2E**: crear **1 tarea por cada `PF-XXX`** relevante del módulo (no solo “un test genérico”), para asegurar cobertura; cada tarea debe incluir `PF-XXX` en `Ref:`.
- En **tests E2E (anti-flaky/mocks)**: si un PF depende de IDs/casos concretos, incluir tarea explícita para datos mock deterministas en `*ServiceMock.ts` (sin placeholders por defecto que rompan asserts).
- En **tests backend**: incluir tareas unitarias e integración (MockMvc / Testcontainers) para endpoints críticos.

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
- **Prohibido** incluir tablas tipo `| Método | ... |` y bloques grandes de código (```typescript). En su lugar, crear 1 tarea por método/tipo/componente como en el template.

Antipatrones comunes que deben corregirse antes de validar:

- Secciones narrativas por tarea (Descripción/Archivo/Métodos/Criterios de aceptación).
- Código embebido para definir interfaces completas (debe descomponerse en tareas por tipo/enum/interface/campo relevante).
- “Implementar servicio completo” sin dividir por métodos.
- “Implementar página completa” sin dividir por componentes, filtros, tabla/columnas, acciones y validaciones.

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
- `analisis/08_integraciones.md` - Integraciones (SAP/SSO) y sincronizaciones

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

Los módulos `auth`, `admin-usuarios`y `auditoria` ya vienen implementados en el template:
- **NO generar backlog** si no requieren modificaciones
- **Generar backlog** solo si el diseño técnico indica cambios específicos

## Estructura del Backlog

Generar el archivo `backlog/XX_[Nombre_Modulo].md` siguiendo **exactamente** el template del skill:

- `references/backlog-template.detallado.md`

Orden obligatorio de alto nivel (según template):

1. **Backend** (BD y migraciones → API Spring Boot → Seguridad/Config → Integraciones/Jobs → Tests Backend)
2. **Frontend** (Tipos → Servicios → Store → Páginas/Rutas → Componentes compartidos si aplica → Tests E2E)

Reglas:

- Copiar el esqueleto completo del template y reemplazar placeholders (`[modulo]`, `P-XXX`, `HU-XXX`, `CU-XXX`, `PF-XXX`, `RF-XXX`, rutas, nombres de archivos/símbolos).
- Reemplazar placeholders de módulo usando:
    - `[moduleSlug]` para carpetas frontend, rutas UI, tests E2E y `data-testid`.
    - `[modulePackage]` para rutas de archivos Java (packages) y tests backend.
    - `[moduleKey]` para nombres de migraciones Flyway.
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
    - Leer `analisis/06_casos_uso.md` y convertir **Flujo Principal + Flujos Alternativos** en tareas técnicas (UI/servicios/endpoints/validaciones/confirmaciones).
    - Leer `analisis/12_prototipos_interfaz.md` y convertir **acciones y componentes de pantalla** (botones "Probar/Validar/Restaurar", confirmaciones, bloques de auditoría, etc.) en tareas técnicas.
    - Leer `analisis/09_diagramas_estados.md` si aplica al módulo y convertir transiciones/estados en tareas (validaciones, permisos, endpoints y tests).
7. Generar tareas: frontend (tipos, servicios, stores, páginas, rutas), backend (migraciones, entities, repos, services, controllers, config, jobs), tests (backend + E2E)
8. Guardar en `backlog/XX_[Nombre_Modulo].md`
9. Verificar **formato estricto** (sin “### Tarea”, sin “Criterios de aceptación”, sin tablas de métodos, sin bloques de código largos)
10. Ejecutar validaciones `XX_1..XX_6`
11. Ejecutar `valida_quality_gates_backlog.py` y corregir hasta estado `OK` (incluye WARN con justificación individual cuando aplique)
12. Pasar al siguiente módulo (solo si gates `XX_1..XX_6` están en `OK`)

## Validación de Cobertura (Por Cada Backlog)

**IMPORTANTE:** La validación se ejecuta **inmediatamente después de generar cada backlog**, NO al final de todos.

```powershell
python .github/skills/traceability-validator/scripts/valida_trazabilidad.py --backlog backlog/XX_[Modulo].md --module-scope --out backlog/check/XX_1_check_traceability_[Modulo].md
```

Validación de integridad del backlog contra el diseño técnico y catálogo de datos/servicios:

```powershell
python .github/skills/backlog-planner/scripts/valida_integridad_diseno.py --backlog backlog/XX_[Modulo].md --module-scope <moduleSlug> --out backlog/check/XX_2_check_design_[Modulo].md
```

Validación de completitud funcional contra prototipos (acciones "especiales" derivadas de `analisis/12_prototipos_interfaz.md`):

```powershell
python .github/skills/backlog-planner/scripts/valida_completitud_funcional.py --backlog backlog/XX_[Modulo].md --module-scope <moduleSlug> --out backlog/check/XX_3_check_funcional_[Modulo].md
```

Validación de completitud por HU (tareas en Backend/Frontend/Tests E2E por HU):

```powershell
python .github/skills/backlog-planner/scripts/valida_completitud_hu.py --backlog backlog/XX_[Modulo].md --module-scope <moduleSlug> --out backlog/check/XX_4_check_hu_[Modulo].md
```

Validación de PF en sección Tests E2E (cada PF del módulo debe estar en Tests E2E):

```powershell
python .github/skills/backlog-planner/scripts/valida_pf_en_e2e.py --backlog backlog/XX_[Modulo].md --module-scope <moduleSlug> --out backlog/check/XX_5_check_pf_e2e_[Modulo].md
```

Validación de navegación (rutas + tarea de menú/sidebar) contra backlog:

```powershell
python .github/skills/backlog-planner/scripts/valida_navegacion_backlog.py --backlog backlog/XX_[Modulo].md --module-scope <moduleSlug> --out backlog/check/XX_6_check_nav_[Modulo].md
```

Validación consolidada de quality gates (OBLIGATORIA, bloqueante para avanzar al siguiente módulo):

```powershell
python .github/skills/backlog-planner/scripts/valida_quality_gates_backlog.py --scope module --traceability backlog/check/XX_1_check_traceability_[Modulo].md --traceability-warn-justifications backlog/check/XX_1_check_traceability_[Modulo]_warnings.md --design backlog/check/XX_2_check_design_[Modulo].md --funcional backlog/check/XX_3_check_funcional_[Modulo].md --hu backlog/check/XX_4_check_hu_[Modulo].md --hu-warn-justifications backlog/check/XX_4_check_hu_[Modulo]_warnings.md --pf-e2e backlog/check/XX_5_check_pf_e2e_[Modulo].md --nav backlog/check/XX_6_check_nav_[Modulo].md --out backlog/check/XX_8_check_quality_gates_[Modulo].md
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
