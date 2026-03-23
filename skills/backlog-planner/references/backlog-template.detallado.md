# Template Backlog Detallado (Referencia del Skill)

Este archivo define el **formato y granularidad obligatoria** para los backlogs generados por el skill `backlog-planner`.

## Principios

- Cada ítem debe ser una tarea **atómica y verificable**.
- Cada tarea debe mencionar un **artefacto concreto**: archivo/símbolo/método/acción/componente/ruta/test.
- Evitar tareas “macro” (p.ej. “Crear servicios”, “Implementar página completa”).
- Trazabilidad obligatoria:
  - Tareas de **Tipos/Servicios/Store/Backend/BD**: al menos `(RF-XXX)` y, si aplica, también `(CU-XXX)`.
  - Tareas de **Páginas/Rutas**: `Ref: [Pantalla P-XXX] (HU-XXX) (RF-XXX)` y, si aplica, también `(CU-XXX)`.
  - Tareas de **Tests (E2E/UI)**: `Ref: [Pantalla P-XXX] (PF-XXX) (HU-XXX) (RF-XXX)` y, si aplica, también `(CU-XXX)`.

## Convenciones de formato (OBLIGATORIO)

- Cada tarea es un bullet con checkbox: `- [ ] ...`.
- La trazabilidad debe estar en la misma línea con prefijo `Ref:`.
- Se permite agrupar por archivo/artefacto usando subtítulos `### Archivo: ...` / `### FooService` / `#### Archivo: ...`.

### Prohibido (para evitar backlogs “narrativos”)

- Subtítulos del tipo `### Tarea XX-001: ...`.
- Bloques “Descripción: / Archivo: / Métodos: / Datos mock: / Criterios de aceptación:”.
- Tablas de métodos `| Método | ... |`.
- Bloques grandes de código (```typescript). Si necesitas detallar, divide en tareas por `interface`/`enum`/método.

---

## Esqueleto del Backlog

```markdown
# Backlog: [Nombre Módulo]

## Dependencias
- Requiere: [módulos previos]
- Requerido por: [módulos posteriores]

---

## Backend

### BD y Modelo Tecnico (CAP / ABAP)

- [ ] Definir entidad persistente principal en `db/[moduleSlug]/schema.cds` o crear objeto DDIC `Z[moduleKey]_[tabla]` (campos, PK, FKs, constraints, indices y tipos). Ref: (RF-XXX)
- [ ] Definir tipos reutilizables o enums en `db/[moduleSlug]/types.cds` o en dominio/elemento DDIC correspondiente. Ref: (RF-XXX)
- [ ] Crear datos iniciales en `db/data/[moduleKey]-[Entidad].csv` o customizing/fixture ABAP con datos base requeridos por el modulo (si aplica). Ref: (RF-XXX)

---

### API / Servicios (CAP / ABAP)

#### EntidadX (Persistencia)

- [ ] Definir entity/proyeccion `EntidadX` en `db/[moduleSlug]/schema.cds` o CDS `ZI_[EntidadX]` / tabla DDIC asociada. Ref: (RF-XXX)
- [ ] Crear artefacto de acceso `srv/[moduleSlug]/[moduleSlug]-service.cds` o proyeccion CDS `ZC_[EntidadX]` para exposición y consumo de la entidad. Ref: (RF-XXX)

#### Tipos y Contratos

- [ ] Definir contrato/tipo `EntidadXPayload` en `db/[moduleSlug]/types.cds`, estructura ABAP o metadata tecnica reutilizable para la operacion. Ref: (RF-XXX)
- [ ] Definir mapping de salida `EntidadXResult` en `srv/[moduleSlug]/[moduleSlug]-service.cds`, metadata extension o estructura ABAP equivalente. Ref: (RF-XXX)

#### Service

- [ ] Crear service `EntidadXService` en `srv/[moduleSlug]/[moduleSlug]-service.cds` o service definition `ZUI_[EntidadX]_SRV` con operación `getAll(...)`. Ref: (RF-XXX)
- [ ] Implementar handler/behavior `getById(id)` en `srv/[moduleSlug]/[moduleSlug]-service.js|ts` o clase/comportamiento ABAP equivalente. Ref: (RF-XXX)
- [ ] Implementar operación `create(payload)` con validaciones de negocio en handler CAP o RAP/ABAP correspondiente. Ref: (RF-XXX)
- [ ] Implementar operación `update(id, payload)` en handler CAP o RAP/ABAP correspondiente. Ref: (RF-XXX)
- [ ] Implementar acción `accionDeNegocio(...)` que ejecuta la regla [RB/operación]. Ref: (RF-XXX)

#### Exposicion OData / API

- [ ] Exponer entidad `EntidadX` en `srv/[moduleSlug]/[moduleSlug]-service.cds` o `ZUI_[EntidadX]_BIND` con path/servicio equivalente. Ref: (RF-XXX)
- [ ] Implementar operación `GET /odata/v4/[moduleSlug]/EntidadesX` o consulta RAP equivalente (paginación/filtros si aplica). Ref: (RF-XXX)
- [ ] Implementar operación `GET /odata/v4/[moduleSlug]/EntidadesX({id})` o lectura detalle equivalente con error cuando no existe. Ref: (RF-XXX)
- [ ] Implementar operación `POST /odata/v4/[moduleSlug]/EntidadesX` o create equivalente con validación del payload. Ref: (RF-XXX)
- [ ] Implementar operación `PATCH /odata/v4/[moduleSlug]/EntidadesX({id})` o update equivalente. Ref: (RF-XXX)
- [ ] Implementar acción `POST /odata/v4/[moduleSlug]/EntidadXService.accionDeNegocio(...)` o action RAP/ABAP equivalente (si aplica). Ref: (RF-XXX)

---

### Seguridad / Config (si aplica)

- [ ] Ajustar autorización del módulo en `srv/[moduleSlug]/authorization.cds`, DCL o artefacto ABAP equivalente (roles/permisos). Ref: (RF-XXX)
- [ ] Ajustar configuración técnica del módulo (`.cdsrc.json`, `package.json`, destinos, customizing o binding ABAP`) si hay nuevas rutas o integraciones. Ref: (RF-XXX)
- [ ] Habilitar auditoría con `managed`, handler CAP, behavior/determination o artefacto ABAP equivalente para registrar cambios relevantes. Ref: (RF-XXX)

---

### Integraciones / Jobs (si aplica)

- [ ] Crear integración `srv/[moduleSlug]/external/[Integracion].cds` / cliente CAP o clase/FM ABAP equivalente (contrato + timeouts + errores). Ref: (RF-XXX)
- [ ] Añadir **modo mock por configuración** para la integración (flag, destination, profile o doble técnico) para desacoplar dev/E2E del sistema externo real. Ref: (RF-XXX)
- [ ] Implementar comportamiento mock en `[Integracion]Service` o artefacto equivalente cuando el flag esté activo (datos de ejemplo + errores simulables si aplica). Ref: (RF-XXX)
- [ ] Crear job/evento técnico `Sync[Entidad]` en CAP o job/clase ABAP equivalente (schedule/trigger, idempotencia). Ref: (RF-XXX)
- [ ] Crear seed mínimo para dev/E2E (`db/data/*.csv`, fixtures o customizing ABAP`) con roles/permisos/usuario técnico/datos base requeridos por el módulo. Ref: (RF-XXX)

---

### Tests Backend

- [ ] Test de integración de `EntidadXService` con `@cap-js/cds-test` o prueba ABAP Unit/servicio equivalente para validación de negocio y errores. Ref: (RF-XXX)
- [ ] Test de exposición OData/action para `GET /odata/v4/[moduleSlug]/EntidadesX` o servicio equivalente verificando filtros, detalle y errores. Ref: (RF-XXX)
- [ ] Test de persistencia/autorización verificando `EntidadX` sobre CDS/CSV CAP o artefactos ABAP relacionados. Ref: (RF-XXX)

---

## Frontend

### Tipos y Entidades

- [ ] Definir shape de `EntidadX` en `webapp/modules/[moduleName]/model/models.js` con campos iniciales y normalización. Ref: (RF-XXX)
- [ ] Definir constante `EstadoEntidadX` en `webapp/modules/[moduleName]/util/constants.js` o `model/models.js`. Ref: (RF-XXX)
- [ ] Definir shape de `SubEntidadY` en `webapp/modules/[moduleName]/model/models.js`. Ref: (RF-XXX)
- [ ] Definir constante `TipoZ` en `webapp/modules/[moduleName]/util/constants.js`. Ref: (RF-XXX)
- [ ] Definir estructura de filtros en `webapp/modules/[moduleName]/model/viewModel.js` o `model/models.js`. Ref: (RF-XXX)
- [ ] Exportar modelos y constantes del módulo desde `webapp/modules/[moduleName]/model/models.js`. Ref: (RF-XXX)

---

## Servicios

### EntidadXService

- [ ] Crear `EntidadXServiceMock.js` con datos estáticos y latencia mock. Ref: (RF-XXX)
- [ ] Implementar método `getAll(filters?)` en EntidadXServiceMock (retorna lista mock N registros). Ref: (RF-XXX)
- [ ] Implementar método `getById(id)` en EntidadXServiceMock. Ref: (RF-XXX)
- [ ] Implementar método `create(payload)` en EntidadXServiceMock (si aplica). Ref: (RF-XXX)
- [ ] Implementar método `update(id, payload)` en EntidadXServiceMock (si aplica). Ref: (RF-XXX)
- [ ] Implementar método `accionDeNegocio(...)` en EntidadXServiceMock (si aplica). Ref: (RF-XXX)

- [ ] Crear `EntidadXService.js` que consume OData/CAP/ABAP usando el modelo del `OwnerComponent` o el cliente definido por el proyecto. Ref: (RF-XXX)
- [ ] En `EntidadXService.js`, **normalizar respuesta backend** cuando el servicio devuelva payload OData/action wrapper o estructura ABAP específica: extraer datos útiles y mapear errores a mensajes consistentes. Ref: (RF-XXX)
- [ ] Implementar método `getAll(filters?)` en EntidadXService (lectura del servicio correspondiente). Ref: (RF-XXX)
- [ ] Implementar método `getById(id)` en EntidadXService (lectura detalle). Ref: (RF-XXX)
- [ ] Implementar método `create(payload)` en EntidadXService (create). Ref: (RF-XXX)
- [ ] Implementar método `update(id, payload)` en EntidadXService (update). Ref: (RF-XXX)
- [ ] Implementar método `accionDeNegocio(...)` en EntidadXService (action/function/operación equivalente). Ref: (RF-XXX)

- [ ] (Si aplica) Definir helper compartido de normalización/error en `webapp/modules/[moduleName]/util/helpers.js` o módulo común equivalente para reutilizarlo en todos los services del módulo. Ref: (RF-XXX)

- [ ] En el controller o viewModel del módulo, seleccionar implementación (Mock/API) usando la configuración del proyecto. Ref: (RF-XXX)

Nota: NO usar tablas de métodos ni agrupar todos los métodos en una sola tarea.

---

## Store

- [ ] Crear `viewModel.js` con `JSONModel` para estado (lista, actual, filtros, busy, error). Ref: (RF-XXX)
- [ ] Implementar carga `fetchEntidadesX(filters?)` en controller/helper del módulo. Ref: (RF-XXX)
- [ ] Implementar carga `fetchEntidadXById(id)` en controller/helper del módulo. Ref: (RF-XXX)
- [ ] Implementar acción `accionDeNegocio(...)` actualizando `viewModel` y mensajes UI. Ref: (RF-XXX)
- [ ] Implementar helper/formatter equivalente a `getEntidadesXPendientes` para consumo de la vista. Ref: (RF-XXX)

---

## Páginas

### P-XXX: [Nombre Pantalla]

- [ ] Crear vista `[NombreEntidad].view.xml` en `webapp/modules/[moduleName]/view/` para la pantalla P-XXX. Ref: [Pantalla P-XXX] (HU-XXX) (CU-XXX) (RF-XXX)
- [ ] Implementar controller `[NombreEntidad].controller.js` con filtros, eventos y carga inicial de datos. Ref: [Pantalla P-XXX] (HU-XXX) (CU-XXX) (RF-XXX)
- [ ] Implementar fragment `fragments/[NombreEntidad]Filters.fragment.xml` o sección equivalente con filtros: ... Ref: [Pantalla P-XXX] (HU-XXX) (CU-XXX) (RF-XXX)
- [ ] Configurar columnas de `sap.m.Table` o `sap.ui.table.Table` para `[Entidad]`: ... + acciones: ... Ref: [Pantalla P-XXX] (HU-XXX) (CU-XXX) (RF-XXX)
- [ ] Configurar paginación, busy state y mensajes usando `viewModel.js` y controles UI5 correspondientes. Ref: [Pantalla P-XXX] (HU-XXX) (CU-XXX) (RF-XXX)
- [ ] Implementar botón "[Acción Principal]" que navega a `#/[moduleSlug]/[ruta-creacion]` o ruta equivalente en `manifest.json`. Ref: [Pantalla P-XXX] (HU-XXX) (CU-XXX) (RF-XXX)
- [ ] Implementar acción "[Acción Fila]" con `MessageBox`, diálogo o confirmación equivalente (si aplica). Ref: [Pantalla P-XXX] (HU-XXX) (CU-XXX) (RF-XXX)
- [ ] Implementar exportación a Excel/PDF (si aplica). Ref: [Pantalla P-XXX] (HU-XXX) (CU-XXX) (RF-XXX)

### Rutas

- [ ] Agregar route y target en `webapp/manifest.json` para `#/[moduleSlug]/[ruta]` asociado a P-XXX [Nombre Pantalla]. Ref: [Pantalla P-XXX] (HU-XXX) (CU-XXX) (RF-XXX)
- [ ] Agregar enlace del módulo en menú lateral, shell navigation o navegación equivalente cuando aplique. Ref: [Pantalla P-XXX] (HU-XXX) (CU-XXX) (RF-XXX)

---

## Componentes Compartidos (solo si aplica)

Incluir esta sección **únicamente** si existen componentes UI reutilizables entre 2+ pantallas del módulo, o si se usarán desde otros módulos.

Reglas:

- Si el componente será transversal, ubicarlo en una carpeta compartida del proyecto UI5 (`webapp/shared/`, `webapp/fragments/` o convención equivalente del repo).
- Si el componente es reutilizable dentro del módulo (pero no transversal), ubicarlo dentro de `webapp/modules/[moduleName]/` y **NO** crear esta sección.

Ejemplos de tareas:

- [ ] Crear fragmento reutilizable `DocumentoCard.fragment.xml` para visualización con metadata y bindings. Ref: [Pantalla P-XXX] (HU-XXX) (CU-XXX) (RF-XXX)
- [ ] Crear fragmento/control `FiltrosX.fragment.xml` (campos: ..., validaciones: ...). Ref: [Pantalla P-XXX] (HU-XXX) (CU-XXX) (RF-XXX)
- [ ] Crear control o fragmento `TablaX` con columnas: ... + acciones: ... Ref: [Pantalla P-XXX] (HU-XXX) (CU-XXX) (RF-XXX)

---

## Tests E2E

### Tests por PF (Pruebas Funcionales)

- [ ] Journey OPA5 `webapp/test/integration/{Feature}Journey.js` implementando PF-XXX para P-XXX validando [flujo concreto / criterio de aceptación]. Ref: [Pantalla P-XXX] (PF-XXX) (HU-XXX) (CU-XXX) (RF-XXX)
- [ ] Page Object o aserción OPA5 en `webapp/test/integration/pages/{ViewName}.js` implementando PF-XXX para P-XXX validando [validación/errores / caso alterno]. Ref: [Pantalla P-XXX] (PF-XXX) (HU-XXX) (CU-XXX) (RF-XXX)

```
