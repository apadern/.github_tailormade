---
name: cap-code-generator
description: "Genera codigo backend SAP CAP Node.js o TypeScript desde backlog y diseno tecnico: modelos CDS, tipos, servicios, handlers, autorizaciones, datos CSV y tests. Usar cuando haya que implementar o ampliar un modulo CAP en db/, srv/ y test/, manteniendo buenas practicas enterprise de modelado, OData, seguridad, validacion y estructura modular."
---

# CAP Code Generator

Generar codigo SAP CAP a partir de backlog y diseno tecnico, con foco en Node.js, CDS y proyectos enterprise.

## Modos de operacion

| Modo | Entrada | Salida |
|------|---------|--------|
| models | backlog/XX_[modulo].md (primaria) + design/02_data_model.md (acelerador) | db/[modulo]/schema.cds + db/[modulo]/types.cds opcional |
| services | models + backlog/XX_[modulo].md + design/03_data_services.md opcional | srv/[modulo]/[modulo]-service.cds |
| handlers | services + backlog/XX_[modulo].md | srv/[modulo]/[modulo]-service.js o .ts |
| auth | backlog/XX_[modulo].md + services | srv/[modulo]/authorization.cds |
| data | models + backlog/XX_[modulo].md | db/data/[namespace]-[Entity].csv |
| tests | services + handlers + auth | test/[modulo]/*.test.js o .ts |
| all | backlog/XX_[modulo].md (primaria) + design/02 + design/03 (opcionales) | Todos los anteriores |

Ver detalle de artefactos y orden de generacion en [references/mode-artifacts.md](references/mode-artifacts.md).

## Fuente de verdad

- Fuente primaria obligatoria: backlog/XX_[modulo].md.
- design/02_data_model.md y design/03_data_services.md son aceleradores opcionales.
- No sustituir el backlog por el diseno. Si hay conflicto, prevalece el backlog y se documenta la discrepancia.

## Flujo obligatorio

1. Leer el backlog completo del modulo.
2. Derivar y usar de forma consistente:
	 - moduleSlug: kebab-case para carpetas y rutas.
	 - moduleKey: snake_case para identificadores tecnicos.
	 - moduleName: PascalCase para services, entities y actions.
	 - namespace: reverse domain o namespace ya existente del proyecto.
3. Si el proyecto ya es CAP, inspeccionar entidades y servicios existentes con `mcp__cap-js_mcp-s_search_model` antes de crear artefactos nuevos.
4. Si hay dudas de APIs, anotaciones o runtime CAP, consultar `mcp__cap-js_mcp-s_search_docs` antes de asumir un patron.
5. Buscar colisiones con nombres de entities, services, actions y archivos antes de generar.
6. Generar en este orden: models -> services -> auth -> handlers -> data -> tests.
7. Validar el resultado con build, test y arranque local antes de cerrar el trabajo.

## Guardrails criticos

- Preferir `cuid` y `managed` de `@sap/cds/common` salvo que el backlog imponga otra clave.
- No exponer entidades de persistencia directamente si la API requiere una vista distinta. Usar proyecciones en servicios.
- No usar SQL raw en handlers. Usar CQL o CQN.
- No duplicar autorizacion en CDS y handlers sin motivo. Priorizar `@requires` y `@restrict` en CDS.
- No activar drafts por defecto. Solo hacerlo si el backlog lo exige de forma explicita.
- No introducir `@cds.persistence.skip` sin definir quien llena los datos y como se valida.
- No asumir compatibilidad entre SQLite y PostgreSQL. Si hay logica dependiente de BD, dejarla explicita.
- No crear CSV de seed con cabeceras o nombres de entidad incorrectos. El nombre del archivo debe coincidir con la entidad desplegada.

Leer [references/guardrails.md](references/guardrails.md) para checklists, anti-errores y validaciones detalladas.

## Parametros opcionales

- `module` (string): nombre funcional del modulo. Debe extraerse del backlog si no se pasa.
- `namespace` (string): namespace CDS. Reutilizar el del proyecto si existe.
- `handlerLanguage` (string): `js` o `ts`. Default: seguir el lenguaje dominante del proyecto.
- `databaseProfile` (string): `sqlite`, `postgres` u otro perfil CAP definido en el proyecto.
- `includeManaged` (boolean): aplicar `managed` en entidades persistentes. Default: `true`.
- `includeCuid` (boolean): aplicar `cuid` en entidades persistentes. Default: `true`.
- `enableDraft` (boolean): habilitar draft solo si el backlog lo exige. Default: `false`.
- `generateTestData` (boolean): crear CSV iniciales y datos para tests. Default: `true`.
- `minTestRecords` (number): minimo de registros por entidad principal. Default: `10`.
- `servicePath` (string): path OData custom si el proyecto no usa el default.

## Prerrequisitos

Fuente primaria obligatoria:
- backlog/XX_[modulo].md

Aceleradores opcionales:
- design/02_data_model.md
- design/03_data_services.md

Infra obligatoria:
- Proyecto SAP CAP existente o previamente scaffolded.
- package.json con `@sap/cds` y entorno de ejecucion configurado.
- Estructura base CAP con `db/`, `srv/` y `test/` cuando aplique.

## Modo: models

Transformar backlog y modelo de datos en artefactos CDS persistentes.

### Salida

- db/[modulo]/schema.cds
- db/[modulo]/types.cds cuando existan enums, tipos reutilizables o aspects propios del modulo

### Convenciones

- Declarar namespace al inicio del archivo.
- Importar `cuid` y `managed` desde `@sap/cds/common` cuando aplique.
- Usar entities en PascalCase, elementos en camelCase y services en PascalCase terminados en `Service`.
- Expresar restricciones basicas en CDS: nullability, precision, escala, enums y longitudes.
- Separar tipos reutilizables en `types.cds` si se usan en mas de una entidad.

## Modo: services

Definir la superficie OData o REST del modulo sobre el modelo CDS.

### Salida

- srv/[modulo]/[modulo]-service.cds

### Convenciones

- Exponer proyecciones, no tablas fisicas sin filtro de API.
- Declarar actions y functions solo para operaciones de negocio, no para CRUD generico.
- Mantener paths, nombres de entidades publicas y nombres de acciones coherentes con el backlog.
- Anotar capacidades de solo lectura, insercion o actualizacion cuando el caso lo requiera.

## Modo: auth

Definir seguridad en CDS antes de implementar logica imperativa.

### Salida

- srv/[modulo]/authorization.cds

### Convenciones

- Aplicar `@requires` a nivel de service para cortes amplios.
- Aplicar `@restrict` a nivel de entidad o accion para permisos finos.
- Reutilizar nombres de rol del backlog o del proyecto, sin inventar roles paralelos.

## Modo: handlers

Implementar la logica de negocio y las validaciones que no pertenezcan al modelo declarativo.

### Salida

- srv/[modulo]/[modulo]-service.js o srv/[modulo]/[modulo]-service.ts

### Convenciones

- Implementar servicios con `cds.ApplicationService`.
- Registrar `before`, `on` y `after` en `init()`.
- Usar `req.reject(...)` para errores de negocio y `await` en todas las operaciones async.
- Usar CQL o CQN para acceso a datos.
- Mantener los handlers del modulo junto a su service CDS.

## Modo: data

Generar datos iniciales y de prueba compatibles con CAP.

### Salida

- db/data/[namespace]-[Entity].csv
- test/data/... si el proyecto separa fixtures por perfil

### Convenciones

- Alinear cabeceras CSV con los nombres efectivos de los elementos desplegados.
- No incluir columnas `createdAt`, `createdBy`, `modifiedAt` o `modifiedBy` salvo que el proyecto las requiera de forma explicita.
- Generar variedad suficiente para filtros, estados y permisos.

## Modo: tests

Generar pruebas de integracion, autorizacion y acciones de negocio.

### Salida

- test/[modulo]/[modulo]-service.test.js o .ts
- test/[modulo]/[modulo]-auth.test.js o .ts

### Convenciones

- Preferir `@cap-js/cds-test` para levantar el servicio y poblar datos.
- Probar happy path, validaciones, autorizacion y acciones custom.
- Validar respuestas HTTP o CQN segun el tipo de prueba.

## Instrucciones de ejecucion

1. Leer backlog y diseno disponible.
2. Identificar entidades, reglas de negocio, roles y operaciones.
3. Revisar el CAP existente con MCP antes de crear archivos nuevos.
4. Generar el modo solicitado o ejecutar `all` en orden.
5. Validar con build y tests.
6. Reportar los archivos creados, decisiones relevantes y validaciones ejecutadas.

## Restricciones

- No generar codigo si no existe backlog/XX_[modulo].md.
- No modificar configuracion global del proyecto CAP sin necesidad explicita.
- No crear servicios o entidades duplicadas cuando ya exista un artefacto equivalente.
- No exponer datos sensibles por defecto.
- No meter reglas de negocio estructurales en CSV o anotaciones de UI.
- No asumir drafts, multitenancy o integraciones remotas si el backlog no lo pide.

## Criterio de finalizacion

El trabajo se considera completado cuando:

✅ Los archivos CDS compilan correctamente  
✅ El servicio CAP arranca sin errores  
✅ Las autorizaciones y handlers siguen el backlog  
✅ Los datos CSV cargan en el perfil objetivo  
✅ Las pruebas relevantes pasan o quedan justificadas  

## Salida esperada del skill

### Modo: models
```
✅ Models generados: N archivos CDS en db/[modulo]/
	- schema.cds
	- types.cds (opcional)
```

### Modo: services
```
✅ Services generados: N archivos CDS en srv/[modulo]/
	- [modulo]-service.cds
```

### Modo: auth
```
✅ Seguridad generada: N archivos CDS en srv/[modulo]/
	- authorization.cds
```

### Modo: handlers
```
✅ Handlers generados: N archivos en srv/[modulo]/
	- [modulo]-service.js|ts
```

### Modo: data
```
✅ Datos iniciales generados: N archivos CSV en db/data/
	- [namespace]-[Entity].csv
```

### Modo: tests
```
✅ Tests generados: N archivos en test/[modulo]/
	- [modulo]-service.test.js|ts
	- [modulo]-auth.test.js|ts
```

### Modo: all
```
✅ Generacion completa del modulo [modulo]:
	 ✅ N archivos CDS de modelo
	 ✅ N archivos CDS de servicio y seguridad
	 ✅ N handlers
	 ✅ N archivos CSV
	 ✅ N tests
	 ✅ Validacion CAP ejecutada
```
