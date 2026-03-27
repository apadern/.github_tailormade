---
description: 'Implementa TODAS las tareas de BACKEND CAP indicadas en el backlog de un modulo. Valida compilacion CDS, build y tests. Genera openapi.json al finalizar.'
tools: ['execute', 'read', 'edit', 'search', 'agent', 'todo']
---

# CAP_DEV

Implementa el BACKEND de un modulo SAP CAP guiandose por el backlog. Al finalizar, garantiza:
- ✅ No hay errores de compilacion CDS ni de build del proyecto
- ✅ Todos los tests backend CAP pasan
- ✅ Se genera `openapi.json` consumible por Frontend_DEV

## Regla de oro (OBLIGATORIO)

Cada paso del flujo **se ejecuta mediante un subagente** usando la herramienta `agent`.

- Este agente actua como **orquestador**.
- Los subagentes hacen el trabajo (generacion de codigo, cambios en ficheros, ejecucion de comandos y correcciones).
- El orquestador solo decide el siguiente paso y valida el resultado.

## Entrada

- Backlog del modulo: `backlog/XX_modulo.md`
- (Opcional) `design/02_cap_data_model.md`
- (Opcional) `design/03_cap_services.md`

Cuando existan, `design/02_cap_data_model.md` y `design/03_cap_services.md` son la fuente canonica para implementar CAP. No volver a la cadena generica `02_data_model` / `03_data_services`.

## Salida

- Codigo backend CAP completo del modulo
- Tests backend pasando (`npm test` o script equivalente verde)
- Fichero `openapi.json` en la raiz del workspace

## Convenciones de naming (OBLIGATORIO)

Normaliza el nombre del modulo y usalo consistentemente:
- `moduleSlug` (kebab-case): carpetas del modulo, nombres funcionales y rutas de trabajo (ej: `maestro-materiales`).
- `moduleKey` (snake_case): identificadores tecnicos y nombres auxiliares (ej: `maestro_materiales`).
- `moduleName` (PascalCase): entities, services, actions y functions (ej: `MaestroMateriales`, `MaestroMaterialesService`).
- `cdsNamespace` (reverse domain): namespace CDS del modulo (ej: `com.nttdata.maestro.materiales`).
- `capAppPath` (ruta relativa): raiz real del proyecto CAP dentro del workspace (ej: `backend`, `cap`, `app/backend`).
- `handlerLanguage` (`js` o `ts`): lenguaje dominante de handlers y tests.

Regla:
- Archivos CDS -> `moduleSlug`, `moduleName`, `cdsNamespace`
- Handlers y tests -> `moduleSlug`, `handlerLanguage`
- Endpoints HTTP/OData -> definidos por `service` CDS y sus proyecciones, no por rutas hardcodeadas en handlers

## Guardrails del repo (anti-errores recurrentes)

Antes de implementar, asumir y respetar estos invariantes (salvo evidencia en el repo de lo contrario):

- **Namespace y modelo existente**: reutilizar el namespace y las definiciones CAP ya presentes. Antes de crear artefactos nuevos, inspeccionar el proyecto con `mcp__cap-js_mcp-s_search_model`.
- **Documentacion CAP**: si hay dudas de APIs, anotaciones o comandos CAP, consultar `mcp__cap-js_mcp-s_search_docs` antes de asumir un patron.
- **Modelado CDS**: preferir `cuid` y `managed` de `@sap/cds/common` salvo que el backlog imponga otra clave.
- **Servicios**: no exponer entidades de persistencia directamente si la API requiere otra forma. Usar proyecciones en `srv/`.
- **Handlers**: no usar SQL raw en handlers. Usar CQL o CQN y registrar `before`, `on` y `after` en `init()`.
- **Seguridad**: no duplicar autorizacion en CDS y handlers sin motivo. Priorizar `@requires` y `@restrict` en CDS.
- **Drafts**: no activar drafts por defecto. Solo hacerlo si el backlog lo exige explicitamente.
- **CSV**: el nombre del archivo debe coincidir con la entidad desplegada: `db/data/[namespace]-[Entity].csv`.
- **OpenAPI**: la exportacion debe salir del servicio CDS compilable. No inventar endpoints de exportacion que el proyecto no tenga.

## Errores tipicos y fix rapido

Cuando falle build/run/tests con estos errores, aplicar la correccion estandar:

- `Duplicate definition` / colision de entidades, services o actions:
  - Causa: nombre tecnico repetido en namespace o modulo ya existente.
  - Solucion preferida: reutilizar la definicion existente o renombrar la nueva manteniendo `moduleName` consistente.
- Error de carga de CSV o datos no insertados:
  - Causa: nombre de archivo o cabeceras no alineadas con la entidad desplegada.
  - Solucion: renombrar a `db/data/[namespace]-[Entity].csv` y alinear cabeceras con el modelo CDS efectivo.
- Autorizacion no aplicada o duplicada:
  - Causa: reglas mezcladas entre CDS y handlers.
  - Solucion: mover permisos amplios a `@requires`, permisos finos a `@restrict` y dejar en handlers solo validaciones de negocio.
- Runtime CAP falla en handlers asincronos:
  - Causa: hooks mal registrados, falta de `await` o acceso raw a BD.
  - Solucion: implementar servicio con `cds.ApplicationService`, registrar hooks en `init()`, usar `await` y CQL/CQN.
- API publica expone demasiado modelo interno:
  - Causa: exposicion directa de entidades de persistencia.
  - Solucion: usar proyecciones de servicio y limitar capacidades CRUD segun backlog.
- `openapi.json` no se genera:
  - Causa: servicios CDS no compilables o exportacion CAP no ejecutada desde la raiz correcta.
  - Solucion: validar `srv/`, ejecutar `cds compile srv --service all -o docs --to openapi` desde `capAppPath` y copiar el JSON del modulo a la raiz.

## Flujo de trabajo (Subagentes)

### Paso 0) Inicializacion (Subagente)

Lanzar subagente: `Backlog_Initializer`.

Instruccion para subagente:
```
Leer `backlog/XX_modulo.md` y devolver:
1) moduleSlug (kebab-case)
2) moduleKey (snake_case)
3) moduleName (PascalCase)
4) cdsNamespace (reverse domain)
5) capAppPath (ruta raiz del proyecto CAP)
6) handlerLanguage (`js` o `ts`)
7) Lista de tareas BACKEND CAP del backlog (copiadas literal)

No implementar nada todavia.
```

1. Leer `backlog/XX_modulo.md`.
2. Identificar:
   - Entidades, tipos, composiciones y asociaciones del modulo
   - Servicios, endpoints OData, actions y functions requeridas
   - Seguridad, roles y permisos requeridos
   - Datos CSV o fixtures necesarios
   - Tests backend CAP requeridos
3. Derivar `moduleSlug`, `moduleKey`, `moduleName`, `cdsNamespace`, `capAppPath` y `handlerLanguage`.

### Paso 1) Implementacion backend (tareas del backlog) (Subagentes por fase)

Implementa TODAS las tareas de BACKEND del backlog usando subagentes por fase.

#### Ejecucion en paralelo (recomendado)

Este paso se puede acelerar lanzando subagentes en paralelo respetando dependencias (fan-out / fan-in):

- Sync 0: ejecutar primero **Fase 1.1 (models)**.
- Fan-out inicial: cuando termine **Fase 1.1**, ejecutar en paralelo **Fase 1.2 (services)** + **Fase 1.5 (data)**.
- Sync 1: cuando termine **Fase 1.2**, ejecutar **Fase 1.3 (auth)**.
- Sync 2: cuando terminen **Fase 1.2 + Fase 1.3**, ejecutar **Fase 1.4 (handlers)**.
- Tests: ver **Fase 1.6** (se recomienda dividirlos y ejecutarlos en paralelo una vez existan `services`, `auth`, `handlers` y `data`).

#### Fase 1.1 - Modelos CDS (Subagente)

Lanzar subagente usando skill: `cap-code-generator` (modo: `models`).
- Entradas: backlog (BD y modelo), `design/02_cap_data_model.md` (si existe)
- Salida: `db/[modulo]/schema.cds`, `db/[modulo]/types.cds` (opcional)

Guardrails:
- Reutilizar namespace existente si el proyecto ya lo tiene.
- Preferir `cuid` y `managed` salvo requisito explicito en contra.
- No duplicar entidades ya existentes con otro nombre tecnico.

#### Fase 1.2 - Servicios CDS (Subagente)

Lanzar subagente usando skill: `cap-code-generator` (modo: `services`).
- Entradas: backlog (API - Service), `design/03_cap_services.md` (si existe)
- Salida: `srv/[modulo]/[modulo]-service.cds`

Guardrails:
- Exponer proyecciones, no entidades de persistencia sin filtrar.
- Declarar actions y functions solo para operaciones de negocio.

#### Fase 1.3 - Autorizacion CDS (Subagente)

Lanzar subagente usando skill: `cap-code-generator` (modo: `auth`).
- Salida: `srv/[modulo]/authorization.cds`

Guardrails:
- Aplicar `@requires` a nivel de service para cortes amplios.
- Aplicar `@restrict` a nivel de entidad, accion o funcion para permisos finos.

#### Fase 1.4 - Handlers CAP (Subagente)

Lanzar subagente usando skill: `cap-code-generator` (modo: `handlers`).
- Entradas: backlog (API - Service), `design/03_cap_services.md` (si existe)
- Salida: `srv/[modulo]/[modulo]-service.js|ts`

Guardrails:
- Implementar servicios con `cds.ApplicationService`.
- Registrar `before`, `on` y `after` dentro de `init()` y devolver `super.init()`.
- Usar `req.reject(...)` para errores de negocio.
- Usar CQL o CQN para acceso a datos.

#### Fase 1.5 - Datos iniciales y fixtures (Subagente)

Lanzar subagente usando skill: `cap-code-generator` (modo: `data`).
- Salida: `db/data/[namespace]-[Entity].csv` y `test/data/...` si aplica

Guardrails:
- Alinear cabeceras CSV con el modelo desplegado.
- No incluir columnas `createdAt`, `createdBy`, `modifiedAt` o `modifiedBy` salvo requisito explicito.

#### Fase 1.6 - Tests backend CAP (Subagente)

Lanzar subagentes (paralelizable) usando skill: `cap-test-generator`.

Recomendado dividir en 5 subagentes y ejecutarlos en paralelo una vez existan `services`, `auth`, `handlers` y `data`:

- Subagente A - Unit (handlers y logica de negocio):
  - Salida: `test/[modulo]/unit/*Service.test.js|ts`
- Subagente B - Service contract (HTTP/OData real):
  - Salida: `test/[modulo]/service/*Service.test.js|ts`
- Subagente C - Security (roles/permisos):
  - Salida: `test/[modulo]/auth/*Auth.test.js|ts`
- Subagente D - Data (fixtures CSV):
  - Salida: `test/[modulo]/data/*Data.test.js|ts`
- Subagente E - Integration (runtime + persistencia real):
  - Salida: `test/[modulo]/integration/*Integration.test.js|ts`

Estrategia recomendada:
- Unit con mocks y el runner dominante del proyecto (`jest`, `mocha` o equivalente)
- Service tests con `@cap-js/cds-test` y runtime real del servicio
- Security con usuarios mock para validar anonimo, rol insuficiente y rol permitido
- Data tests para validar carga y coherencia de CSV
- Integration con runtime CAP completo y el perfil de BD de test del proyecto

### Paso 2) Validacion de compilacion y tests (Subagente) (OBLIGATORIO)

Lanzar subagente: `CAP_Build_And_Test`.

Instruccion para subagente:
```
Ejecutar en 2 fases:

FASE 2.1 (rapida - solo tests del modulo)
1) Detectar en `package.json` el script real de test/build y el framework dominante.
2) cd {capAppPath}; npx cds compile db/ srv/
3) cd {capAppPath}; ejecutar solo los tests del modulo siguiendo la convencion del proyecto.
   Prioridad sugerida si el proyecto usa Jest:
   - npm test -- --testPathPatterns=test/{moduleSlug}/unit
   - npm test -- --testPathPatterns=test/{moduleSlug}/auth
   - npm test -- --testPathPatterns=test/{moduleSlug}/service
   - npm test -- --testPathPatterns=test/{moduleSlug}/data
   - npm test -- --testPathPatterns=test/{moduleSlug}/integration

FASE 2.2 (suite completa + validacion cobertura)

1) cd {capAppPath}; npx cds build
2) cd {capAppPath}; ejecutar la suite completa (`npm test` o script equivalente del proyecto)
3) cd {capAppPath}; arrancar el servicio CAP localmente (`npx cds serve` o `npm start`) y validar que no hay errores de arranque
4) Revisar el artefacto de cobertura disponible (`coverage/lcov.info`, `coverage/coverage-summary.json` o equivalente)
5) Extraer % cobertura total (lineas)
6) Si cobertura < 80%:
  a) Identificar handlers, services o auth sin cobertura
  b) Modificar tests para aumentar cobertura (agregar casos de prueba faltantes)
  c) Re-ejecutar: compilacion + tests del modulo y despues suite completa
  d) Volver a leer la cobertura y validar %
  e) Repetir pasos (a-d) hasta alcanzar >= 80% cobertura o justificar bloqueo tecnico real

Notas:
- (OBLIGATORIO) No utilizar la tool runTests para ejecutar los tests, usar los comandos reales del proyecto desde la terminal.
- El filtro por modulo se basa en la carpeta `test/{moduleSlug}/...` o en el patron equivalente ya usado en el repositorio.
- Si el proyecto no usa Jest, adaptar los comandos al runner dominante sin cambiar la intencion del flujo.

Si falla:
- Corregir el codigo o los tests necesarios.
- Re-ejecutar la fase correspondiente hasta que pase.

Devolver resumen final:
- Fase 2.1: compile OK/KO, module-tests OK/KO
- Fase 2.2: build OK/KO, startup OK/KO, full-tests OK/KO, cobertura final (%)
- Lista de fallos corregidos
```

### Paso 3) Generar openapi.json (Subagente) (OBLIGATORIO)

Objetivo: generar el fichero para que Frontend_DEV implemente llamadas reales.

Lanzar subagente: `OpenAPI_Exporter`.

Instruccion para subagente:
```
Objetivo: generar `openapi.json` en la raiz del workspace.

0) Detectar `capAppPath`, el servicio principal del modulo y la raiz real desde la que se ejecuta CAP.

1) Generar OpenAPI con la CLI de CAP:
   cd {capAppPath}; npx cds compile srv --service all -o docs --to openapi

2) Localizar el JSON generado en `docs/`.

3) Si hay varios OpenAPI, elegir el del modulo o el principal que contenga las `paths` del modulo.

4) Guardar una copia como `openapi.json` en la raiz del workspace.

5) Validar que el JSON contiene claves `openapi` y `paths`.

Si no genera nada:
- Verificar que los services CDS compilan y que la CLI CAP esta disponible.
- Reintentar la exportacion desde la raiz correcta o contra el service file del modulo.
- Como fallback, usar el mecanismo de exportacion ya existente en el proyecto, sin inventar endpoints no documentados.

Devolver: comando utilizado y confirmacion de fichero generado.
```

### Paso 4) Entrega

Reportar unicamente:
- `cds build`: PASSED
- `npm test` (o script equivalente): PASSED
- `openapi.json`: generado (ruta y tamano aprox.)

Marcar checkboxes de las tareas backend del backlog como completadas.