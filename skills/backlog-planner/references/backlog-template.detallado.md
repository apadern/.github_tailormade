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

### BD y Migraciones (Flyway)

- [ ] Crear migración `backend/src/main/resources/db/migration/VXX__[moduleKey]_create_enums.sql` (para todos los enums del modulo). Ref: (RF-XXX)
- [ ] Crear migración `backend/src/main/resources/db/migration/VXX__[moduleKey]_create_[tabla].sql` (tabla, PK, FKs, constraints, índices para consultas frecuentes, comentarios). Ref: (RF-XXX)
- [ ] Crear migración `backend/src/main/resources/db/migration/VXX__[moduleKey]_seed_data.sql` con datos iniciales (si aplica). Ref: (RF-XXX)

---

### API (Spring Boot)

#### EntidadX (JPA)

- [ ] Crear entity `EntidadX.java` en `backend/src/main/java/com/nttdata/backend/[modulePackage]/model/` con anotaciones JPA y validaciones. Ref: (RF-XXX)
- [ ] Crear repository `EntidadXRepository.java` en `backend/src/main/java/com/nttdata/backend/[modulePackage]/repository/` (métodos derivados / queries). Ref: (RF-XXX)

#### DTOs

- [ ] Crear DTO `EntidadXRequest.java` (campos + @Valid) en `backend/src/main/java/com/nttdata/backend/[modulePackage]/dto/`. Ref: (RF-XXX)
- [ ] Crear DTO `EntidadXResponse.java` en `backend/src/main/java/com/nttdata/backend/[modulePackage]/dto/`. Ref: (RF-XXX)

#### Service

- [ ] Crear service `EntidadXService.java` en `backend/src/main/java/com/nttdata/backend/[modulePackage]/service/` con método `getAll(...)`. Ref: (RF-XXX)
- [ ] Implementar método `getById(id)` en EntidadXService. Ref: (RF-XXX)
- [ ] Implementar método `create(request)` en EntidadXService (validaciones de negocio). Ref: (RF-XXX)
- [ ] Implementar método `update(id, request)` en EntidadXService. Ref: (RF-XXX)
- [ ] Implementar método `accionDeNegocio(...)` que ejecuta la regla [RB/operación]. Ref: (RF-XXX)

#### Controller (REST)

- [ ] Crear controller `EntidadXController.java` en `backend/src/main/java/com/nttdata/backend/[modulePackage]/controller/` con base path `"/[moduleSlug]"` (sin prefijo `/api`, lo aporta `server.servlet.context-path`). Ref: (RF-XXX)
- [ ] Implementar endpoint `GET /api/[moduleSlug]/entidades-x` (paginación/filtros si aplica). Ref: (RF-XXX)
- [ ] Implementar endpoint `GET /api/[moduleSlug]/entidades-x/{id}` con 404 cuando no existe. Ref: (RF-XXX)
- [ ] Implementar endpoint `POST /api/[moduleSlug]/entidades-x` con `@Valid` y respuesta estándar. Ref: (RF-XXX)
- [ ] Implementar endpoint `PUT /api/[moduleSlug]/entidades-x/{id}`. Ref: (RF-XXX)
- [ ] Implementar endpoint `POST /api/[moduleSlug]/entidades-x/{id}/accion` (si aplica). Ref: (RF-XXX)

---

### Seguridad / Config (si aplica)

- [ ] Ajustar reglas de acceso del módulo en `backend/src/main/java/com/nttdata/backend/config/SecurityConfig.java` (roles/permisos). Ref: (RF-XXX)
- [ ] Ajustar CORS del módulo en `backend/src/main/java/com/nttdata/backend/config/CorsConfig.java` si hay nuevas rutas. Ref: (RF-XXX)
- [ ] Registrar controladores del módulo en `backend/src/main/java/com/nttdata/backend/audit/aspect/AuditAspect.java` (pointcut y mapeo de info de entidad) para habilitar auditoría automática. Ref: (RF-XXX)

---

### Integraciones / Jobs (si aplica)

- [ ] Crear client `WorkdayClient.java` / `SapClient.java` en `backend/src/main/java/com/nttdata/backend/[modulePackage]/integration/` (contrato + timeouts + errores). Ref: (RF-XXX)
- [ ] Añadir **modo mock por configuración** para la integración (flag en `backend/src/main/resources/application-dev.yml` + env var) para desacoplar dev/E2E del sistema externo real. Ref: (RF-XXX)
- [ ] Implementar comportamiento mock en `[Integracion]Client` cuando el flag esté activo (datos de ejemplo + errores simulables si aplica). Ref: (RF-XXX)
- [ ] Crear job `Sync[Entidad]Job.java` en `backend/src/main/java/com/nttdata/backend/[modulePackage]/job/` (schedule/trigger, idempotencia). Ref: (RF-XXX)
- [ ] Crear migración Flyway de **seed mínimo** para dev/E2E (roles/permisos/usuario admin/datos base requeridos por el módulo). Ref: (RF-XXX)

---

### Tests Backend

- [ ] Test unitario de `EntidadXService` (validación de negocio / errores) en `backend/src/test/java/com/nttdata/backend/[modulePackage]/service/EntidadXServiceTest.java`. Ref: (RF-XXX)
- [ ] Test de controller con MockMvc para `GET /api/[moduleSlug]/entidades-x` (ej: `get("/api/[moduleSlug]/entidades-x").contextPath("/api")`) en `backend/src/test/java/com/nttdata/backend/[modulePackage]/controller/EntidadXControllerTest.java`. Ref: (RF-XXX)
- [ ] Test de integración con Testcontainers verificando persistencia de EntidadX (repo + migraciones) en `backend/src/test/java/com/nttdata/backend/[modulePackage]/integration/EntidadXIntegrationTest.java`. Ref: (RF-XXX)

---

## Frontend

### Tipos y Entidades

- [ ] Definir interface `EntidadX` con campos: ... Ref: (RF-XXX)
- [ ] Definir enum `EstadoEntidadX`: ... Ref: (RF-XXX)
- [ ] Definir interface `SubEntidadY` con campos: ... Ref: (RF-XXX)
- [ ] Definir enum `TipoZ`: ... Ref: (RF-XXX)
- [ ] Definir tipos para filtros: EntidadXFilters, SubEntidadYFilters, ... Ref: (RF-XXX)
- [ ] Exportar todos los tipos desde `frontend/src/modules/[moduleSlug]/types.ts`. Ref: (RF-XXX)

---

## Servicios

### EntidadXService

- [ ] Crear `EntidadXServiceMock.ts` con datos estáticos y latencia mock. Ref: (RF-XXX)
- [ ] Implementar método `getAll(filters?)` en EntidadXServiceMock (retorna lista mock N registros). Ref: (RF-XXX)
- [ ] Implementar método `getById(id)` en EntidadXServiceMock. Ref: (RF-XXX)
- [ ] Implementar método `create(data)` en EntidadXServiceMock (si aplica). Ref: (RF-XXX)
- [ ] Implementar método `update(id, data)` en EntidadXServiceMock (si aplica). Ref: (RF-XXX)
- [ ] Implementar método `accionDeNegocio(...)` en EntidadXServiceMock (si aplica). Ref: (RF-XXX)

- [ ] Crear `EntidadXService.ts` que consume API (usa `VITE_API_BASE_URL`) y respeta el contrato de `design/03`. Ref: (RF-XXX)
- [ ] En `EntidadXService.ts`, **normalizar respuesta backend** cuando el API devuelva wrapper (p.ej. `ApiResponse{success,message,data}`): extraer `.data`, manejar `success=false` y mapear errores a mensajes consistentes. Ref: (RF-XXX)
- [ ] Implementar método `getAll(filters?)` en EntidadXService (GET al endpoint correspondiente). Ref: (RF-XXX)
- [ ] Implementar método `getById(id)` en EntidadXService (GET detalle). Ref: (RF-XXX)
- [ ] Implementar método `create(data)` en EntidadXService (POST). Ref: (RF-XXX)
- [ ] Implementar método `update(id, data)` en EntidadXService (PUT/PATCH). Ref: (RF-XXX)
- [ ] Implementar método `accionDeNegocio(...)` en EntidadXService (POST acción). Ref: (RF-XXX)

- [ ] (Si aplica) Definir `ApiResponse<T>` y/o helper `unwrapApiResponse<T>(payload)` en un módulo compartido (`frontend/src/shared/...`) para reutilizarlo en todos los services del módulo. Ref: (RF-XXX)

- [ ] En el store del módulo, seleccionar implementación (Mock/API) usando `SERVICE_MODE` (derivado de `VITE_USE_MOCK=true|false`). Ref: (RF-XXX)

Nota: NO usar tablas de métodos ni agrupar todos los métodos en una sola tarea.

---

## Store

- [ ] Crear `entidadXStore.ts` con Zustand para estado (lista, actual, filtros, loading, error). Ref: (RF-XXX)
- [ ] Implementar acción `fetchEntidadesX(filters?)` en entidadXStore. Ref: (RF-XXX)
- [ ] Implementar acción `fetchEntidadXById(id)` en entidadXStore. Ref: (RF-XXX)
- [ ] Implementar acción `accionDeNegocio(...)` en entidadXStore. Ref: (RF-XXX)
- [ ] Implementar selector `getEntidadesXPendientes` (o equivalente). Ref: (RF-XXX)

---

## Páginas

### P-XXX: [Nombre Pantalla]

- [ ] Crear página `[NombreEntidad]ListPage.tsx` en `frontend/src/modules/[moduleSlug]/pages/` usando `ListPageTemplate` de `shared/templates`. Ref: [Pantalla P-XXX] (HU-XXX) (CU-XXX) (RF-XXX)
- [ ] Implementar componente `[NombreEntidad]FiltersBar.tsx` como `filterComponent` del `ListPageTemplate` con filtros: ... Ref: [Pantalla P-XXX] (HU-XXX) (CU-XXX) (RF-XXX)
- [ ] Configurar columnas del `ListPageTemplate` (array `Column<[Entidad]>`): ... + acciones: ... Ref: [Pantalla P-XXX] (HU-XXX) (CU-XXX) (RF-XXX)
- [ ] Configurar paginación del `ListPageTemplate` (page, pageSize, onPageChange desde `[entidad]Store`). Ref: [Pantalla P-XXX] (HU-XXX) (CU-XXX) (RF-XXX)
- [ ] Implementar botón "[Acción Principal]" que navega a `/[moduleSlug]/[ruta-creacion]`. Ref: [Pantalla P-XXX] (HU-XXX) (CU-XXX) (RF-XXX)
- [ ] Implementar acción "[Acción Fila]" con confirmación modal (si aplica). Ref: [Pantalla P-XXX] (HU-XXX) (CU-XXX) (RF-XXX)
- [ ] Implementar exportación a Excel/PDF (si aplica). Ref: [Pantalla P-XXX] (HU-XXX) (CU-XXX) (RF-XXX)

### Rutas

- [ ] Agregar ruta `/[moduleSlug]/[ruta]` para P-XXX [Nombre Pantalla]. Ref: [Pantalla P-XXX] (HU-XXX) (CU-XXX) (RF-XXX)
- [ ] Agregar enlace del módulo en menú lateral (Sidebar) cuando aplique. Ref: [Pantalla P-XXX] (HU-XXX) (CU-XXX) (RF-XXX)

---

## Componentes Compartidos (solo si aplica)

Incluir esta sección **únicamente** si existen componentes UI reutilizables entre 2+ pantallas del módulo, o si se usarán desde otros módulos.

Reglas:

- Si el componente será transversal, ubicarlo en `frontend/src/shared/components/`.
- Si el componente es reutilizable dentro del módulo (pero no transversal), ubicarlo en `frontend/src/modules/[moduleSlug]/components/` y **NO** crear esta sección.

Ejemplos de tareas:

- [ ] Crear componente `DocumentoCard.tsx` para visualización con metadata (props: ...). Ref: [Pantalla P-XXX] (HU-XXX) (CU-XXX) (RF-XXX)
- [ ] Crear componente `FiltrosX.tsx` (campos: ..., validaciones: ...). Ref: [Pantalla P-XXX] (HU-XXX) (CU-XXX) (RF-XXX)
- [ ] Crear componente `TablaX.tsx` con columnas: ... + acciones: ... Ref: [Pantalla P-XXX] (HU-XXX) (CU-XXX) (RF-XXX)

---

## Tests E2E

### Tests por PF (Pruebas Funcionales)

- [ ] Test E2E implementando PF-XXX para P-XXX validando [flujo concreto / criterio de aceptación]. Ref: [Pantalla P-XXX] (PF-XXX) (HU-XXX) (CU-XXX) (RF-XXX)
- [ ] Test E2E implementando PF-XXX para P-XXX validando [validación/errores / caso alterno]. Ref: [Pantalla P-XXX] (PF-XXX) (HU-XXX) (CU-XXX) (RF-XXX)

```
