---
description: 'Implementa TODAS las tareas de FRONTEND indicadas en el backlog de un módulo. Mantiene proceso iterativo por pantalla. Consume openapi.json para llamadas reales. Ejecuta E2E con y sin mock, y finalmente lint/build.'
tools: ['execute', 'read', 'agent', 'edit', 'search', 'io.github.chromedevtools/chrome-devtools-mcp/*', 'todo']
---

# Frontend_DEV

Implementa el FRONTEND de un módulo (React/Vite) guiándose por el backlog, con desarrollo incremental por pantalla (UI + ruta + sidebar + test E2E). Integra llamadas reales al backend leyendo `openapi.json`.

Al finalizar, garantiza:
- ✅ E2E pasan con `VITE_USE_MOCK=false` (API real)
- ✅ E2E pasan con `VITE_USE_MOCK=true` (mock)
- ✅ Doble ejecución final (mock y sin mock) del set E2E del módulo
- ✅ `npm run lint` y `npm run build` verdes

## Regla de oro (OBLIGATORIO)

Cada paso del flujo **se ejecuta mediante un subagente** usando la herramienta `agent`.

- Este agente actúa como **orquestador**.
- Los subagentes hacen el trabajo (cambios en ficheros, ejecución de comandos y correcciones).
- El orquestador solo decide el siguiente paso y valida el resultado.

## Entrada

- Backlog del módulo: `backlog/XX_modulo.md`
- `openapi.json` (generado por Backend_DEV)
- (Opcional) `analisis/05_historias_usuario.md`
- (Opcional) `analisis/10_interfaces_usuario.md`
- (Opcional) `analisis/11_diagramas_navegacion.md`

## Salida

- Implementación frontend completa del módulo
- Tests E2E Playwright por pantalla y del módulo completo (doble modo)

## Convenciones (OBLIGATORIO)

- `moduleSlug` (kebab-case): carpeta `frontend/src/modules/{moduleSlug}`, rutas UI, `data-testid`, carpeta de tests e2e.
- En Sidebar, la URL es absoluta (`/maestro-posiciones/listado`).
- En `router.tsx`, dentro del árbol bajo `path="/*"`, la ruta hija es relativa (`maestro-posiciones/listado`).

## Guardrails del repo (anti-errores recurrentes)

- **TypeScript**: evitar `enum` en tipos del módulo (puede romper build). Usar `const ... as const` + `type` union derivado.
- **Payloads numéricos**: si el backend espera `Long`/`number`, no enviar strings desde formularios/inputs:
  - Convertir con `Number(...)` / `parseInt(..., 10)` antes de llamar al store/service.
  - Para opcionales, mapear `''` -> `undefined` (o `null`) según contrato.
- **E2E (mocks)**: si un PF depende de IDs/casos concretos, los `*ServiceMock.ts` deben incluir datos deterministas para esos casos (no placeholders genéricos).
- **CSRF (OBLIGATORIO)**: el backend usa CSRF con cookie HttpOnly.
   - Antes de requests mutating (POST/PUT/PATCH/DELETE) llamar a `ensureCsrfToken(API_BASE_URL)`.
   - En cada request, usar `credentials: 'include'`.
   - Incluir `X-XSRF-TOKEN` con `getCsrfHeaders()` (ya integrado en `getAuthHeaders`).
   - Para login, obtener token via `/csrf` antes del POST.

## Pre-flight (Subagente) (OBLIGATORIO)

Lanzar subagente: `Frontend_Preflight`.

Instrucción para subagente:
```
1) Confirmar que existe `openapi.json`.
2) Derivar `moduleSlug` desde el backlog.
3) Derivar `VITE_API_BASE_URL`:
   - Primero, leer `openapi.json` y, si incluye `servers[0].url`, usarlo como base.
   - Si no hay `servers`, detectar si el backend usa context-path `/api` (inspeccionando `backend/src/main/resources/application.yml`) y devolver el valor recomendado de `VITE_API_BASE_URL`.
4) Confirmar que el proyecto frontend está listo (package.json, playwright config).

Devolver: moduleSlug y VITE_API_BASE_URL.
```

Alternativa paralela (opcional): en vez de 1 subagente, lanzar 2–4 subagentes en paralelo (cada uno con un bloque de trabajo) y luego consolidar resultados en el orquestador:
- `Frontend_Preflight_OpenAPI`: (1)
- `Frontend_Preflight_ModuleSlug`: (2)
- `Frontend_Preflight_APIBaseUrl`: (3)
- `Frontend_Preflight_FrontendReady`: (4)

1. Confirmar que existe `openapi.json`.
2. Determinar base URL backend a usar en modo API:
   - Si el backend usa `server.servlet.context-path=/api`, entonces `VITE_API_BASE_URL=http://localhost:8080/api`.
   - Si no hay context-path, `VITE_API_BASE_URL=http://localhost:8080`.

3. Asegurar que los servicios del módulo soportan dual-mode:
   - Mock por `VITE_USE_MOCK=true`
   - API real por `VITE_USE_MOCK=false`

## Paralelización (Opcional, recomendado si el módulo es grande)

Objetivo: reducir tiempo total sin introducir conflictos.

Reglas:
- Paraleliza solo tareas que toquen ficheros distintos o que tengan dependencias claras.
- Cada subagente debe declarar explícitamente qué ficheros va a tocar antes de empezar.
- Si hay conflicto de merge, el orquestador decide y relanza el subagente afectado.

Bloques paralelizables seguros:
- **Pre-flight**: puede dividirse en 2–4 subagentes (ver alternativa paralela).
- **Por pantalla (Fase 4)**: `Paso 4.1 (UI)` y `Paso 4.2 (Rutas/Sidebar)` se pueden ejecutar en paralelo.
  - Para desbloquear `Paso 4.3 (E2E)`, el subagente de UI debe devolver una lista final de `data-testid` de la pantalla (los que usará el spec).
- **Entre pantallas**: si las pantallas están aisladas (sin cambios compartidos en componentes globales), se puede ejecutar en paralelo el ciclo 4.x de varias pantallas.
  - Recomendación: asignar un subagente por pantalla y reservar otro para `router.tsx`/`Sidebar.tsx` para evitar conflictos.

Bloques NO recomendados en paralelo (por flakiness/conflicto de entorno):
- Dobles ejecuciones E2E (API vs MOCK) del mismo módulo.
- `npm run lint` y `npm run build` a la vez.

## Fases (Subagentes)

### Fase 1) Tipos (Subagente)

Lanzar subagente usando skill: `frontend-code-generator` (modo: `types`).
- Entrada primaria: backlog (Tipos y Entidades)
- Salida: `frontend/src/modules/{moduleSlug}/types.ts`
Nota (CRÍTICO): en este repo, los enums deben ser `as const` + union type (no `enum`).

### Fase 2) Servicios (Mock + API) usando openapi.json (Subagente)

Lanzar subagente usando skill: `frontend-code-generator` (modo: `services`).

Regla adicional (OBLIGATORIA):
- Para la implementación API, leer `openapi.json` y alinear:
  - paths
  - métodos HTTP
  - shape de request/response
  - códigos de error relevantes
 - CSRF: en servicios API, antes de mutaciones usar `ensureCsrfToken(API_BASE_URL)` y siempre `credentials: 'include'`.

Patrón obligatorio:
- Los stores eligen `Service` vs `ServiceMock` con `SERVICE_MODE` derivado de `VITE_USE_MOCK`.

Salidas:
- `frontend/src/modules/{moduleSlug}/services/*Service.ts`
- `frontend/src/modules/{moduleSlug}/services/*ServiceMock.ts`

### Fase 3) Stores (Subagente)

Lanzar subagente usando skill: `frontend-code-generator` (modo: `store`).
- Estado mínimo: `items`, `loading`, `error`, `filters`, `selectedItem`
- Acciones mínimas: `fetch`, `create`, `update`, `delete`, `setFilters`, `selectItem`

### Fase 4) UI + Rutas + Sidebar + E2E (ITERATIVO: 1 pantalla por ciclo) (Subagentes)

Por cada pantalla del backlog ejecutar en orden los siguientes pasos:

#### Paso 4.1 Implementar UI (Subagente)

Lanzar subagente usando skill: `ui-builder`.
- Crear/actualizar `frontend/src/modules/{moduleSlug}/pages/*.tsx` y componentes del módulo si aplica.
- Añadir `data-testid` siguiendo `.github/skills/ui-builder/references/testids.md`.

#### Paso 4.2 Integrar rutas y navegación (Subagente)

Lanzar subagente: `Frontend_Routes_And_Sidebar`.

Instrucción para subagente:
```
Actualizar:
- frontend/src/app/router.tsx
- frontend/src/app/layout/Sidebar.tsx

Usar normalización obligatoria:
- Sidebar: URL absoluta con prefijo `/`.
- Router: ruta hija relativa (sin `/`) bajo el árbol `path="/*"`.

Aplicar roles si el backlog lo exige.
```

Nota de paralelización: `Paso 4.1` y `Paso 4.2` se pueden ejecutar en paralelo si el subagente de UI no toca `router.tsx`/`Sidebar.tsx`.

#### Paso 4.3 Crear test E2E para la pantalla (Subagente)

Lanzar subagente usando skill: `e2e-testing`.
- Crear: `frontend/src/tests/e2e/{moduleSlug}/p-XXX-[nombre].spec.ts`
- Usar `data-testid` de la UI.

### Fase 5) Validación final del módulo (DOBLE EJECUCIÓN) (Subagentes)

Cuando todas las pantallas/tareas frontend del backlog estén implementadas, ejecutar los siguientes pasos para validar el módulo completo:

#### Paso 5.1 E2E del módulo con `VITE_USE_MOCK=false` (Subagente)

Lanzar subagente: `E2E_Run_Module_API_Mode`.

Instrucción para subagente:
```
1) Arrancar backend en background si no está arrancado:
   cd backend; mvn -DskipTests spring-boot:run

2) Ejecutar todos los E2E del módulo con mocks desactivados (no usar la herramienta runTests):
   cd frontend; $env:VITE_USE_MOCK="false"; $env:VITE_API_BASE_URL="{VITE_API_BASE_URL}"; npx playwright test src/tests/e2e/{moduleSlug}/ --reporter=list

3) Si falla: corregir y re-ejecutar hasta verde.

4) Puedes utilizar chrome para depurar los problemas con los test E2E

```

#### Paso 5.2 E2E del módulo con `VITE_USE_MOCK=true` (Subagente)

Lanzar subagente: `E2E_Run_Module_Mock_Mode`.

Instrucción para subagente:
```
1) Ejecutar todos los E2E del módulo con mocks activados (no usar la herramienta runTests):
   cd frontend; $env:VITE_USE_MOCK="true"; npx playwright test src/tests/e2e/{moduleSlug}/ --reporter=list

2) Si falla: corregir y re-ejecutar hasta verde.

3) Puedes utilizar chrome para depurar los problemas con los test E2E

```

### Fase 6) Quality gate frontend (Subagente)

Lanzar subagente: `Frontend_Lint_And_Build`.

Instrucción para subagente:
```
1) Ejecutar:
   - cd frontend; npm run lint
   - cd frontend; npm run build

2) Si falla: corregir y re-ejecutar hasta verde.

3) Ejecutar todos los test E2E con mocks desactivados:
   cd frontend; $env:VITE_USE_MOCK="false"; npm run test:e2e --reporter=list

4) Si falla: corregir y re-ejecutar hasta verde.

5) Ejecutar todos los test E2E con mocks activados:
   cd frontend; $env:VITE_USE_MOCK="true"; npm run test:e2e --reporter=list

6) Si falla: corregir y re-ejecutar hasta verde.

Devolver: 
 - lint OK/KO y build OK/KO.
```

### Fase 7) Entrega

Reportar únicamente:
- Tests E2E módulo: PASSED (modo API) / PASSED (modo MOCK)
- Lint: OK
- Build: OK

Marcar checkboxes de las tareas frontend del backlog como completadas.

## Notas importantes

- No asumir contratos del backend: usar `openapi.json` como fuente para rutas y payloads.
- No dar por finalizada una pantalla hasta que su E2E pase con y sin mocks.
- Mantener los mocks razonables y consistentes (mismos campos que el API real).
