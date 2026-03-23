---
name: cap-test-generator
description: "Genera tests backend SAP CAP Node.js o TypeScript por capas: unit con mocks, service contract con @cap-js/cds-test, seguridad con usuarios mock y autorizacion CDS, validacion de datos CSV e integracion con runtime y persistencia real. Usar en la fase de testing CAP o para corregir fallos tipicos de aislamiento, permisos, seeds y handlers."
---

# CAP Test Generator

Generar tests CAP siguiendo una estrategia por capas para minimizar flakiness, aislar correctamente el runtime y validar seguridad, datos y contratos OData.

## Principio clave (OBLIGATORIO)

Separar los tests por intencion:

1. `unit`: logica de handlers y funciones puras. Sin runtime CAP completo ni BD real.
2. `service`: contrato HTTP o OData con `@cap-js/cds-test` y servidor real de CAP.
3. `auth`: autorizacion y autenticacion con usuarios mock, `@requires`, `@restrict` y checks de `req.user`.
4. `data`: carga y validacion de fixtures CSV, integridad basica y cobertura de estados.
5. `integration`: runtime CAP completo con persistencia real del perfil de test y efectos sobre datos.

No mezclar todo en un unico test lento salvo en `all` o como fallback puntual.

## Posicion documental sobre unit tests en CAP

La documentacion CAP para Node.js no impone un unico framework obligatorio para unit tests puros.

- `@cap-js/cds-test` y `cds.test()` son la referencia documental para tests que levantan el runtime CAP, el servidor o la API HTTP u OData.
- `cds.test()` esta documentado como compatible con `Jest` y `Mocha`.
- Para unit tests puros, la documentacion no obliga a usar `cds.test()` ni a levantar el runtime completo.
- Para unit tests puros, usar mocks y el runner dominante del proyecto, normalmente `Jest` o `Mocha`.
- Para assertions, CAP documenta bien el uso de `chai` a traves de `cds.test`, pero eso no obliga a usar `chai` en unit tests aislados si el proyecto ya tiene otra convencion valida.

Regla operativa del skill:

- `unit` = mocks + framework dominante del proyecto (`jest`, `mocha` o equivalente ya presente)
- `service`, `auth` e `integration` = preferir `@cap-js/cds-test` cuando se prueba runtime real, HTTP, OData, auth mock o persistencia

Regla por defecto si el proyecto no define framework de tests:

- usar `Jest` como default para los tests generados
- usar `@cap-js/cds-test` dentro de suites `Jest` cuando haya que probar runtime CAP real
- cambiar a `Mocha` solo si el proyecto ya lo usa o si existe una restriccion tecnica concreta del equipo

## Modos

- `unit`: genera solo tests unitarios para handlers y logica de negocio aislada.
- `service`: genera solo tests de contrato de servicio con `@cap-js/cds-test`.
- `auth`: genera solo tests de seguridad y permisos.
- `data`: genera solo tests sobre fixtures y datos de prueba.
- `integration`: genera solo tests de integracion end-to-end del modulo.
- `all`: genera todo lo anterior en orden.

Ver detalle de rutas, orden y artefactos en [references/mode-artifacts.md](references/mode-artifacts.md).

## Entradas esperadas

- `backlog/XX_[modulo].md` (fuente principal)
- Codigo ya generado o implementado:
	- Servicios CDS en `srv/[modulo]/[modulo]-service.cds`
	- Handlers en `srv/[modulo]/[modulo]-service.js` o `.ts`
	- Seguridad en `srv/[modulo]/authorization.cds` si aplica
	- Modelo y datos en `db/` y `db/data/`

## Salidas

- Unit: `test/[modulo]/unit/*Service.test.js|ts`
- Service: `test/[modulo]/service/*Service.test.js|ts`
- Auth: `test/[modulo]/auth/*Auth.test.js|ts`
- Data: `test/[modulo]/data/*Data.test.js|ts`
- Integration: `test/[modulo]/integration/*Integration.test.js|ts`

## Flujo obligatorio

1. Leer el backlog del modulo completo.
2. Detectar el lenguaje dominante del proyecto de tests: JavaScript o TypeScript.
3. Inspeccionar el modelo y servicios existentes con `mcp__cap-js_mcp-s_search_model` antes de generar tests.
4. Si hay dudas sobre `cds.test`, auth mock, perfiles o convenciones CAP, consultar `mcp__cap-js_mcp-s_search_docs`.
5. Buscar tests existentes del modulo para no duplicar patrones o helpers.
6. Generar en este orden: `unit -> auth -> service -> data -> integration`.
7. Validar compilacion, arranque del servicio en test y ejecucion de la suite generada.

## Reglas de generacion (anti-errores)

### A) Aislamiento del runtime CAP (CRITICO)

- Si se usa `cds.test()`, resetear datos entre tests con `test.data.reset` cuando el estado importe.
- No compartir estado mutable entre tests.
- No dejar mocks, `cds.model` o stubs vivos entre casos.
- Si el test es unitario, evitar levantar todo CAP sin necesidad.

### B) Service contract tests (OBLIGATORIO: `@cap-js/cds-test`)

En CAP, los tests de contrato deben usar el runtime real del servicio cuando se validan rutas, OData, status codes, acciones o functions.

Plantilla recomendada:

- `const test = cds.test(...)`
- helpers `GET`, `POST`, `PUT`, `DELETE` ligados al servidor
- autenticacion mock con `{ auth: { username, password } }` o helpers equivalentes del proyecto
- validacion de status, payload y side effects cuando aplique

Objetivo: validar contrato HTTP u OData real con seguridad y datos activos.

### C) Security tests

Usar usuarios mock y perfiles de desarrollo o test para validar:

- acceso anonimo rechazado cuando corresponda
- acceso con rol insuficiente rechazado
- acceso con rol correcto permitido
- permisos sobre actions, functions y entidades con `@requires` y `@restrict`

Nota 401 vs 403:

- En CAP puede variar segun estrategia de auth mock y configuracion del proyecto.
- No asumir uno u otro a ciegas. Ajustar asserts a la configuracion real del servicio.

### D) Integration tests

Usar runtime CAP real con persistencia del perfil de test.

- Objetivo: validar handlers, persistencia, datos y restricciones de negocio reales.
- Preferir BD efimera o perfil SQLite de test cuando el proyecto lo soporte.
- Si el proyecto ya prueba Postgres u otra BD real, seguir el patron existente.
- Validar tanto respuesta como estado persistido cuando haya escrituras.

### E) Fixtures y CSV

Los datos iniciales en CAP son parte del comportamiento probado.

- Validar nombres de archivo `[namespace]-[Entity].csv`.
- Validar cabeceras alineadas con el modelo desplegado.
- Cubrir estados, filtros y permisos relevantes.
- Separar `db/data` y `test/data` si el proyecto usa perfiles distintos.

## Fallback: perfil ligero de test

Solo usarlo si el test no necesita runtime completo, auth real ni persistencia real:

- usar tests unitarios con mocks
- o usar un perfil de test simplificado del proyecto

No convertir todos los tests a fallback por comodidad.

## Parametros opcionales

- `module` (string): nombre funcional del modulo.
- `handlerLanguage` (string): `js` o `ts`. Default: seguir el proyecto.
- `testFramework` (string): `jest`, `mocha` o el framework dominante del proyecto para tests unitarios y suites no acopladas a `cds.test`. Si el proyecto no define ninguno, default: `jest`.
- `databaseProfile` (string): perfil CAP objetivo para integracion.
- `generateFixtures` (boolean): crear fixtures adicionales de test. Default: `true`.
- `minRecords` (number): minimo de registros por entidad relevante. Default: `5`.
- `includeAuthMatrix` (boolean): generar matriz completa de permisos por rol. Default: `true`.

## Checklist de calidad (antes de finalizar)

- Tests compilan.
- Los unit no levantan runtime completo sin necesidad.
- Los service tests usan `@cap-js/cds-test` o el helper real del proyecto.
- Los auth tests cubren anonimo, rol insuficiente y rol correcto cuando aplique.
- Los integration tests validan persistencia o efectos reales.
- Los datos de prueba son coherentes con el modelo CDS.

Leer [references/guardrails.md](references/guardrails.md) para patrones detallados, checklists y anti-patrones.

## Ejecucion sugerida

- `npm test -- --testPathPatterns=test/[modulo]/unit`
- `npm test -- --testPathPatterns=test/[modulo]/auth`
- `npm test -- --testPathPatterns=test/[modulo]/service`
- `npm test -- --testPathPatterns=test/[modulo]/data`
- `npm test -- --testPathPatterns=test/[modulo]/integration`

Adaptar el comando si el proyecto usa `jest`, `mocha`, `vitest` o scripts propios.

## Criterio de finalizacion

El modo se considera COMPLETADO cuando:

✅ Los tests generados compilan  
✅ La suite del modo corre o queda justificada si no puede ejecutarse  
✅ Los permisos y contratos reflejan el backlog  
✅ Los fixtures no rompen el despliegue del modelo  
✅ El reporte final indica archivos creados y validaciones ejecutadas  

## Salida esperada del skill

### Modo: unit
```
✅ Unit tests generados: N archivos en test/[modulo]/unit/
	- *Service.test.js|ts
```

### Modo: service
```
✅ Service contract tests generados: N archivos en test/[modulo]/service/
	- *Service.test.js|ts
```

### Modo: auth
```
✅ Security tests generados: N archivos en test/[modulo]/auth/
	- *Auth.test.js|ts
```

### Modo: data
```
✅ Data tests generados: N archivos en test/[modulo]/data/
	- *Data.test.js|ts
```

### Modo: integration
```
✅ Integration tests generados: N archivos en test/[modulo]/integration/
	- *Integration.test.js|ts
```

### Modo: all
```
✅ Generacion completa de tests CAP para [modulo]:
	 ✅ N unit tests
	 ✅ N service tests
	 ✅ N auth tests
	 ✅ N data tests
	 ✅ N integration tests
	 ✅ Validacion de testing CAP ejecutada
```
