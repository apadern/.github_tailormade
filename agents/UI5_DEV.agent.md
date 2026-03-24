---
description: 'Implementa TODAS las tareas de FRONTEND indicadas en el backlog de un módulo SAP UI5. Desarrollo incremental por pantalla (base técnica → modelos → servicios → estado → controladores → UI → routing → E2E). Ejecuta E2E en modo API y MOCK, y finalmente quality gate.'
tools: ['execute', 'read', 'agent', 'edit', 'search', 'io.github.chromedevtools/chrome-devtools-mcp/*', 'todo']
---

# UI5_DEV

Implementa el FRONTEND de un módulo **SAP UI5** guiándose por el backlog, con desarrollo incremental por capas (base técnica → modelos → servicios → estado → controladores → UI + routing → E2E). Integra llamadas reales al backend via servicios **OData/REST**.

Al finalizar, garantiza:
- ✅ E2E (OPA5) pasan en modo API real
- ✅ E2E (OPA5) pasan en modo MockServer (datos simulados)
- ✅ Doble ejecución final (API y MOCK) del set E2E del módulo
- ✅ `ui5 lint` y `ui5 build` (o equivalente del proyecto) en verde

## Regla de oro (OBLIGATORIO)

Cada paso del flujo **se ejecuta mediante un subagente** usando la herramienta `agent`.

- Este agente actúa como **orquestador**.
- Los subagentes hacen el trabajo (cambios en ficheros, ejecución de comandos y correcciones).
- El orquestador solo decide el siguiente paso y valida el resultado.

## Entrada

- Backlog del módulo: `backlog/XX_modulo.md`
- `manifest.json` y estructura `webapp/` del proyecto
- (Opcional) `design/02_data_model.md`
- (Opcional) `design/03_data_services.md`
- (Opcional) `analisis/05_historias_usuario.md`
- (Opcional) `analisis/10_interfaces_usuario.md`
- (Opcional) `analisis/11_diagramas_navegacion.md`

## Salida

- Implementación frontend SAP UI5 completa del módulo
- Tests E2E OPA5 por pantalla y del módulo completo (modo API y modo MOCK)

## Convenciones (OBLIGATORIO)

- `moduleSlug` (kebab-case): carpeta `webapp/modules/{moduleSlug}/`, IDs de controles, y carpeta de tests.
- `moduleName` (PascalCase): prefijo para vistas, controladores y fragments del módulo.
- Rutas en `manifest.json`: patrón `{moduleSlug}/{viewName}` (ej. `facturas/listado`).
- IDs de controles: prefijo `{moduleSlug}--` para evitar colisiones (ej. `facturas--table`).
- Los controladores extienden `BaseController` o `App.controller.js` según las convenciones del proyecto.

## Guardrails del repo (anti-errores recurrentes)

- **Payloads numéricos**: si el backend espera `Edm.Int64`/`Edm.Decimal`, no enviar strings desde formularios/inputs. Convertir antes de llamar al servicio.
- **Binding**: usar `{/...}` para modelos sin nombre y `{modelName>/...}` para modelos con nombre. Nunca mezclar sintaxis.
- **E2E (MockServer)**: los datos mock deben incluir casos deterministas que cubran las PF del backlog. No usar placeholders genéricos.
- **i18n**: todos los textos visibles al usuario deben ir en `i18n.properties`. Nunca hardcodear literales en vistas XML.
- **OData CSRF**: en operaciones de escritura (POST/PUT/PATCH/DELETE) asegurar que el modelo OData está configurado con `useBatch` y `tokenHandling` correctamente.
- **Fragmentos**: usar `sap.ui.core.Fragment.load` (API moderna) en lugar del `sap.ui.xmlfragment` deprecado.
- **Navegación**: usar siempre el Router de la aplicación (`this.getRouter().navTo(...)`) y nunca manipular el hash directamente.

## Pre-flight (Subagente) (OBLIGATORIO)

Lanzar subagente: `UI5_Preflight`.

Instrucción para subagente:
```
1) Confirmar que existe el backlog del módulo en backlog/XX_modulo.md.
2) Derivar moduleSlug (kebab-case) y moduleName (PascalCase) desde el backlog.
3) Verificar estructura del proyecto SAP UI5:
   - webapp/manifest.json existe y contiene routing configurado.
   - webapp/Component.js existe.
   - webapp/i18n/i18n.properties existe.
4) Detectar si el proyecto usa OData (sap.ui.model.odata.v2.ODataModel o v4) o REST (JSONModel con fetch).
5) Detectar si existe configuración de MockServer en webapp/localService/ o equivalente.
6) Confirmar que existe la herramienta de build (ui5.yaml o package.json con scripts ui5).

Devolver: moduleSlug, moduleName, tipo de servicio (OData v2 / OData v4 / REST), ruta base del servicio backend, disponibilidad de MockServer.
```

## Paralelización (Opcional, recomendado si el módulo es grande)

Objetivo: reducir tiempo total sin introducir conflictos de ficheros.

Reglas:
- Paraleliza solo tareas que toquen ficheros distintos.
- Las Fases 1–6 son secuenciales entre sí (cada una consume los artefactos de la anterior).
- **Fase 7.1** y **Fase 7.2** pueden ejecutarse en paralelo si las vistas y manifest.json no se pisan.
- Entre pantallas dentro de **Fase 7.1**: si las vistas son completamente independientes, se puede paralelizar el ciclo 7.1.x de varias pantallas con subagentes distintos.
- Las ejecuciones E2E API y MOCK (**Fase 8.2** y **Fase 8.3**) no deben ejecutarse en paralelo.

---

## Fase 1) Base técnica del módulo (Subagente)

Lanzar subagente usando skill: `ui5-code-generator` (modo: `base`).

**Objetivo**: preparar la base técnica del módulo SAP UI5 para poder desarrollar su lógica de forma desacoplada de la UI final.

**Entradas**: backlog del módulo, `webapp/manifest.json`, `webapp/Component.js`.

**Salidas esperadas**:
- Estructura de carpetas `webapp/modules/{moduleSlug}/`
- Configuración técnica del módulo (namespace, dependencias)
- Integración mínima con `manifest.json` o `Component.js`
- Convenciones de nombres y organización del módulo documentadas en el propio código

**Exclusiones**: no incluye construcción de pantallas, maquetación, rutas globales ni menú lateral.

---

## Fase 2) Modelo de datos (Subagente)

Lanzar subagente usando skill: `ui5-code-generator` (modo: `models`).

**Objetivo**: definir cómo representa y maneja el módulo la información de negocio.

**Entradas**: backlog del módulo (sección Entidades/Tipos), `design/02_data_model.md` (si existe).

**Salidas esperadas**:
- `webapp/modules/{moduleSlug}/model/entities.js` — definición de entidades y contratos entrada/salida
- Modelos `JSONModel` u `ODataModel` configurados para el módulo
- Mapeos de datos, validaciones base y normalización
- Estructura de datos lista para binding

**Exclusiones**: no incluye implementación visual de formularios, tablas o componentes UI.

---

## Fase 3) Servicios (Subagente)

Lanzar subagente usando skill: `ui5-code-generator` (modo: `services`).

**Objetivo**: implementar la capa de acceso a datos e integración con el backend.

**Entradas**: backlog del módulo (sección Servicios/API), `design/03_data_services.md` (si existe), resultado de Fase 2.

**Salidas esperadas**:
- `webapp/modules/{moduleSlug}/services/{Entity}Service.js` — servicio API real (OData/REST)
- `webapp/modules/{moduleSlug}/services/{Entity}ServiceMock.js` — servicio con datos simulados
- Operaciones CRUD completas, construcción de payloads, parseo de respuestas
- Gestión de errores y adapters de integración
- Los servicios eligen implementación real o mock con un flag/parámetro de entorno

**Exclusiones**: no incluye pruebas E2E API/MOCK ni validaciones visuales extremo a extremo.

---

## Fase 4) Estado y lógica interna (Subagente)

Lanzar subagente usando skill: `ui5-code-generator` (modo: `state`).

**Objetivo**: gestionar el estado funcional del módulo y su comportamiento interno.

**Entradas**: backlog del módulo, servicios de Fase 3, modelos de Fase 2.

**Salidas esperadas**:
- `webapp/modules/{moduleSlug}/model/viewModel.js` — modelo local de estado con `JSONModel`
- Flags de carga (`busy`), edición (`editMode`), bloqueo, selección y filtros
- Lógica de inicialización de datos y sincronización entre modelos
- Estado mínimo: `items`, `busy`, `selectedItem`, `filters`, `editMode`

**Exclusiones**: no incluye rutas, navegación, menú lateral ni comportamiento visual final de pantalla.

---

## Fase 5) Controladores y utilidades (Subagente)

Lanzar subagente usando skill: `ui5-code-generator` (modo: `controllers`).

**Objetivo**: implementar la lógica que conecta datos, reglas funcionales y comportamiento consumible por la UI.

**Entradas**: backlog del módulo, estado de Fase 4, servicios de Fase 3.

**Salidas esperadas**:
- `webapp/modules/{moduleSlug}/controller/{View}.controller.js` — handlers de eventos y lógica de presentación
- `webapp/modules/{moduleSlug}/util/Formatter.js` — formatters para binding
- `webapp/modules/{moduleSlug}/util/Validator.js` — validaciones funcionales
- Helpers, constantes y utilidades reutilizables del módulo
- Reglas de habilitación/visibilidad de controles

**Exclusiones**: no incluye desarrollo de la UI final (vistas XML) ni pruebas E2E por pantalla.

---

## Fase 6) Testing técnico (Subagente)

Lanzar subagente usando skill: `ui5-code-generator` (modo: `tests`).

**Objetivo**: verificar la calidad técnica del módulo a nivel unitario y de integración interna.

**Entradas**: servicios, controladores, formatters y helpers de Fases 3–5.

**Salidas esperadas**:
- `webapp/test/unit/modules/{moduleSlug}/{Entity}Service.js` — tests unitarios de servicios
- `webapp/test/unit/modules/{moduleSlug}/{Controller}.controller.js` — tests de controladores
- `webapp/test/unit/modules/{moduleSlug}/Formatter.js` — tests de formatters y helpers
- Validación de transformaciones de datos y pruebas de integración técnica no E2E

**Exclusiones**: no incluye E2E por pantalla, E2E modo API, E2E modo MOCK, quality gate ni entrega.

---

## Fase 7) UI + Routing + E2E (ITERATIVO: 1 pantalla por ciclo) (Subagentes)

Por cada pantalla del backlog ejecutar en orden los siguientes pasos:

### Paso 7.1 Implementar UI (Subagente)

Lanzar subagente usando skill: `ui-builder`.

**Objetivo**: implementar la vista XML del módulo en SAPUI5 con binding, i18n y estructura visual alineada con el diseño funcional.

- Crear/actualizar vistas en `webapp/view/{ModuleName}*.view.xml` y fragmentos en `webapp/view/fragments/`.
- Crear/actualizar controladores en `webapp/controller/{ModuleName}*.controller.js`.
- Actualizar `webapp/i18n/i18n.properties` con todos los literales nuevos.
- Añadir IDs de controles con prefijo `{moduleSlug}--` (ej. `facturas--table`, `facturas--btnCreate`).
- Devolver lista de IDs de controles creados (necesarios para el test OPA5).

### Paso 7.2 Routing y navegación (Subagente)

Lanzar subagente: `UI5_Routing_And_Navigation`.

Instrucción para subagente:
```
Actualizar webapp/manifest.json (sección sap.ui5 > routing):
- Añadir nueva ruta y target para la pantalla implementada.
  - route name: {moduleSlug}-{viewName} (ej. facturas-listado)
  - pattern: {moduleSlug}/{viewName} (ej. facturas/listado)
  - target name: {moduleSlug}{ViewName} (ej. facturasListado)
- Añadir target apuntando a la vista correcta.

Actualizar webapp/controller/App.controller.js (si aplica):
- Registrar eventos de navegación del módulo si el backlog lo requiere.

Usar siempre this.getRouter().navTo(...) en los controladores para navegar entre vistas.
Aplicar roles/permisos si el backlog lo exige.
```

Nota de paralelización: `Paso 7.1` y `Paso 7.2` pueden ejecutarse en paralelo si el subagente de UI no toca `manifest.json`.

### Paso 7.3 Crear test E2E OPA5 para la pantalla (Subagente)

Lanzar subagente usando skill: `ui5-test-generator`.

- Crear `webapp/test/integration/{ModuleName}{ViewName}Journey.js`
- Crear `webapp/test/integration/pages/{ModuleName}{ViewName}.js` (Page Object)
- Actualizar `webapp/test/integration/AllJourneys.js` para incluir el nuevo Journey
- Usar los IDs de controles devueltos por el Paso 7.1

---

## Fase 8) Validación final del módulo (DOBLE EJECUCIÓN) (Subagentes)

Cuando todas las pantallas/tareas del backlog estén implementadas:

### Paso 8.1 E2E del módulo con servicios reales (modo API) (Subagente)

Lanzar subagente: `UI5_E2E_Module_API_Mode`.

Instrucción para subagente:
```
1) Asegurar que el backend está arrancado y accesible en la URL configurada.

2) Ejecutar los tests E2E del módulo contra servicios reales:
   npm run test:integration (o el comando equivalente configurado en el proyecto)

   Si el proyecto usa wdi5:
   npm run wdi5 -- --spec webapp/test/integration/{ModuleName}*Journey.js

   Si el proyecto usa OPA5 standalone:
   Abrir webapp/test/integration/opaTests.qunit.html en navegador y verificar que todos los Journeys del módulo pasan.

3) Si falla: corregir binding OData, payloads, navegación o datos, y re-ejecutar hasta verde.

4) Puedes utilizar chrome para depurar los problemas con los tests E2E.
```

### Paso 8.2 E2E del módulo con datos simulados (modo MOCK) (Subagente)

Lanzar subagente: `UI5_E2E_Module_Mock_Mode`.

Instrucción para subagente:
```
1) Verificar que existe configuración de MockServer en webapp/localService/:
   - metadata.xml (esquema OData) o equivalente para servicios REST
   - webapp/localService/mockdata/*.json con datos deterministas que cubran las PFs del módulo

2) Arrancar el servidor local con MockServer activo:
   npm run start-mock (o el comando equivalente del proyecto)

3) Ejecutar los tests E2E del módulo en modo mock:
   npm run test:integration:mock (o equivalente)

4) Si falla: corregir datos mock, configuración de MockServer o binding de vista, y re-ejecutar hasta verde.

5) Puedes utilizar chrome para depurar los problemas con los tests E2E.
```

---

## Fase 9) Quality Gate frontend SAPUI5 (Subagente)

Lanzar subagente: `UI5_Quality_Gate`.

Instrucción para subagente:
```
1) Ejecutar linting:
   npm run lint (o ui5 lint si está configurado)
   Corregir todos los errores de linting hasta obtener 0 errores.

2) Ejecutar build:
   ui5 build (o npm run build según el proyecto)
   Corregir errores de build hasta obtener una build exitosa.

3) Verificar convenciones SAPUI5:
   - Todos los textos visibles en i18n.properties (sin literales hardcodeados en vistas).
   - Sin warnings críticos en consola del navegador.
   - IDs de controles con prefijo de módulo.
   - APIs deprecadas sustituidas por alternativas modernas.

4) Ejecutar suite E2E completa en modo API:
   npm run test:integration
   Corregir hasta verde.

5) Ejecutar suite E2E completa en modo MOCK:
   npm run test:integration:mock
   Corregir hasta verde.

Devolver:
 - lint OK/KO; build OK/KO; E2E API OK/KO; E2E MOCK OK/KO.
```

---

## Fase 10) Entrega

Reportar únicamente:
- Tests E2E módulo: PASSED (modo API) / PASSED (modo MOCK)
- Lint: OK
- Build: OK

Marcar checkboxes de las tareas del módulo en el backlog como completadas.

---

## Notas importantes

- No asumir contratos del backend: leer `design/03_data_services.md` o el esquema OData como fuente para rutas y payloads.
- No dar por finalizada una pantalla hasta que su test OPA5 pase en modo API y en modo MOCK.
- Mantener los datos mock coherentes y completos respecto al esquema OData/REST real.
- Las Fases 1–6 construyen la base técnica del módulo y son prerrequisito para la Fase 7.
- En proyectos que no tengan módulos separados, adaptar las rutas de salida siguiendo la estructura existente de `webapp/`.
