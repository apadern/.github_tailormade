---
name: technical-designer
description: Genera el diseño técnico para un MVP full-stack (frontend web + backend Java Spring Boot). Usar cuando se necesite crear design/01_technical_design.md con arquitectura modular, rutas UI y contratos API. Requiere análisis funcional previo (carpeta analisis).
---

# Technical Designer

Genera documento de diseño técnico para un MVP full-stack (frontend web + backend Java).

## Objetivo del Skill

- Producir un diseño técnico consistente y accionable para **frontend + backend**, sin duplicar el detalle del modelo de datos ni de la especificación de servicios/contratos.
- Asegurar coherencia de nombres (módulos/rutas UI/endpoints API) y trazabilidad mínima (RF → módulo → rutas UI → endpoints API).

## Prerrequisitos

Este skill puede usar cualquier información relevante en `analisis/`.

Imprescindibles (MVP full-stack):
- `analisis/01_objetivo_y_alcance.md` - Alcance/no-alcance y objetivos
- `analisis/02_actores_y_roles.md` - Roles/permisos y accesos (UI + API)
- `analisis/03_requerimientos_funcionales.md` - RFs (base para módulos)
- `analisis/10_interfaces_usuario.md` - Pantallas (IDs P-XXX) para mapeo UI→módulo
- `analisis/11_diagramas_navegacion.md` - Flujos y navegación (rutas UI)

Recomendados (mejoran calidad del diseño):
- `analisis/04_requerimientos_tecnicos.md` - Restricciones no funcionales (seguridad, rendimiento, infraestructura)
- `analisis/06_casos_uso.md` - Secuencias de casos de uso (derivar endpoints/casos de uso)
- `analisis/07_diagramas_procesos.md` - Procesos (sincronizaciones/envíos, jobs)
- `analisis/08_integraciones.md` - Integraciones (WordAid, SAP, SSO)
- `analisis/09_diagramas_estados.md` - Estados/transiciones (derivar endpoints/validaciones por estado)
- `analisis/12_prototipos_interfaz.md` - Acciones de UI no evidentes (botones "Probar/Validar/Restaurar", confirmaciones)

## Referencias

- Ver [references/frontend-template-structure.md](references/frontend-template-structure.md) para estructura frontend
- Ver [references/backend-template-structure.md](references/backend-template-structure.md) para estructura backend
- Ver [references/ABAP-template-structure.md](references/ABAP-template-structure.md) para estructura ABAP


## Stack Tecnológico (Fijo)

Frontend:
- React (Vite) + TypeScript Strict
- Tailwind CSS + Shadcn/UI
- Zustand (estado global)
- Capa de servicios con modo dual: **mock (por defecto)** o **backend** (conmutable por env vars)

Backend:
- Java 21 + Spring Boot 3.2.x (Maven)
- PostgreSQL + Flyway (migraciones)
- Spring Security (autenticación/autorización)
- SSO corporativo (SAML 2.0) cuando aplique según el análisis
- JWT solo si se requiere (p.ej. APIs internas o integración distinta a SSO)
- OpenAPI/Swagger (springdoc)

## Estructura de Salida

Generar `design/01_technical_design.md` con exactamente estas 3 secciones:

### 1. Resumen Ejecutivo
Máximo 15 líneas describiendo alcance y enfoque.

**Incluir obligatoriamente (sin crear secciones adicionales):**
- Alcance / no-alcance del MVP (frontend UI5 + backend CAP + backend ABAP).
- Supuestos del MVP: persistencia en PostgreSQL, seguridad (SSO SAML2 y control de acceso por rol), documentación OpenAPI, e integraciones con WordAid/SAP si están en alcance.
- Modelo dual frontend: por defecto **frontend-only (servicios mock)** y opción de ejecutar contra backend sin cambiar pantallas.
- Referencias cruzadas:
	- El detalle de entidades y enums vive en `design/02_data_model.md`.
	- El detalle de métodos y contratos (API/servicios) vive en `design/03_data_services.md`.

### 2. Arquitectura Modular

Usar estructura de [references/frontend-template-structure.md](references/frontend-template-structure.md).

Para backend, respetar [references/backend-template-structure.md](references/backend-template-structure.md) y/o la estructura real del repositorio.

Listar módulos identificados de los RFs:

| Módulo | Descripción | RFs Asociados |
|--------|-------------|---------------|
| auth | Autenticación y control de sesión | Transversal |
| admin-usuarios | Gestión de usuarios, roles y permisos | RF-001, RF-002... |
| auditoria | Consulta de logs de actividad y cambios | RF-AUD... |

**Además, dentro de esta misma sección (como subsecciones o bullets):**
- Capas de arquitectura (alto nivel):
	- Frontend: UI (pages/components) → estado (Zustand) → services (mock o API client) → (mock data o backend).
	- Backend: controllers (REST) → application/services → repositories (JPA) → PostgreSQL.
- Convenciones transversales (solo enunciadas): IDs, fechas, moneda/decimales, paginación/ordenamiento, modelo de errores, logging/auditoría (automática vía AOP Aspect).
- Convenciones del modelo dual (solo enunciadas):
		- Modo por defecto: `mock`.
		- Conmutación global por variables `VITE_USE_MOCK=false` y `VITE_API_BASE_URL`.
		- Selector único de modo/URL en `frontend/src/shared/utils/serviceMode.ts` exporta constante `SERVICE_MODE` ('mock' | 'backend') y `API_BASE_URL` (la UI/stores/services no deben leer `import.meta.env` directamente).
		- Patrón del template por módulo: **dos implementaciones de servicio** (`*Service.ts` backend y `*ServiceMock.ts` mock), exportados como objetos/instancias constantes que implementan la misma interfaz.
		- Selección de implementación activa: el template la realiza en el **store** usando ternario `SERVICE_MODE === 'backend' ? service : serviceMock` (p.ej. `frontend/src/store/authStore.ts`). Centralizar esta selección una única vez al inicializar el store.
- Reglas de acoplamiento:
	- La UI no accede a arrays de datos mock directamente; todo pasa por services.
		- Los stores no hablan directo con `fetch`; delegan en services.
		- Evitar “ifs por modo” dentro de cada método de negocio; el template separa servicios mock/backend y elige la implementación activa una sola vez.
	- El backend expone contratos estables (DTOs) y no filtra entidades JPA como API pública (enunciado, sin detallar clases).

### 3. Estructura de Rutas

Mapeo de pantallas a rutas basado en `11_diagramas_navegacion.md`. Una sola tabla con todas las rutas del frontend, indicando claramente a qué módulo pertenecen y qué pantalla representan. Plantilla OBLIGATORIA:

```
### Rutas UI (Frontend)

| Ruta | Pantalla | Módulo |
|------|----------|--------|
| /usuarios | P-001: Gestion de Usuarios | gestion-usuarios |
```

**Reglas de consistencia:**
- Las rutas deben seguir un patrón por módulo (prefijo estable) y ser coherentes con los slugs de módulos.
- Evitar duplicar el detalle de pantallas (campos/acciones); eso se deriva de `analisis/10_interfaces_usuario.md`.

Además, incluir el mapeo de endpoints REST del backend (alto nivel, sin detallar payloads). Una sola tabla con todos los endpoints del backend, indicando método HTTP, ruta, recurso/caso de uso, módulo y roles de seguridad. . Plantilla OBLIGATORIA:

```
### Endpoints API (Backend)

| Método | Endpoint | Recurso/Caso de uso | Módulo | Seguridad |
|--------|----------|----------------------|--------|-----------|
| POST | /api/auth/login | Login | auth | Pública |
| GET | /api/usuarios | Listar usuarios | gestion-usuarios | ROLE_ADMIN  |
```

**Reglas de consistencia (API):**
- En este repo el backend suele usar `server.servlet.context-path=/api` (ver `backend/src/main/resources/application.yml`).
  - En el documento de diseño, describir endpoints tal como los consumirá el frontend (incluyendo `/api`).
  - En implementación backend, evitar duplicar `/api` en `@RequestMapping` si ya existe `context-path`.
- Seguir un patrón CRUD consistente por recurso (GET list/detail, POST create, PUT/PATCH update, DELETE delete) cuando aplique.
- Declarar explícitamente qué endpoints son públicos vs protegidos (p.ej. SSO/roles o JWT/roles, según integración definida en `analisis/08_integraciones.md`).
- Incluir endpoints **no-CRUD** cuando el análisis/prototipo lo implique (p.ej. `.../validate`, `.../test-access`, `.../restore-defaults`, `.../{id}/in-use`), sin detallar payloads.

## Restricciones

- NO generar código TypeScript ni Java
- NO incluir configuración de herramientas (vite, tailwind, tsconfig, Spring configs)
- NO detallar entidades (eso es del skill data-modeler)
- NO detallar servicios/contratos (eso es del skill services-designer)
- NO inventar módulos no presentes en RFs/diagramas; si se requiere un módulo transversal (p.ej. auth), justificarlo como “transversal” y mantenerlo mínimo.

## Proceso

1. Leer `analisis/` (priorizar 01, 02, 03, 10, 11; luego 04, 06, 07, 08, 09, 12)
2. Identificar módulos agrupando RFs
3. Mapear rutas UI desde diagramas de navegación
4. Proponer endpoints REST por módulo (alto nivel) coherentes con RFs
5. Generar `design/01_technical_design.md`

## Reglas para Validación de Diseño (Fase 4)

Cuando se use `scripts/validate_design.py` en validación:

- No se permite cerrar validación con errores críticos > 0.
- Está prohibido justificar errores críticos como "Fase 2", "posterior" o equivalentes.
- Si hay warnings, la justificación debe ser individual por warning en `design/check-design-warnings.md`.
- Para validar justificaciones usar `scripts/validate_warning_justifications.py`.
- Las justificaciones genéricas o por diferimiento a fases futuras deben considerarse inválidas.

## Output

```
Archivo design/01_technical_design.md generado:
- Módulos: X
- Rutas UI: Y
- Endpoints API: W
```
