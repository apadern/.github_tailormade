# Modes And Artifacts

Usar esta referencia para decidir que generar en cada modo de testing CAP y donde debe vivir cada artefacto.

## Orden recomendado

1. `unit`
2. `auth`
3. `service`
4. `data`
5. `integration`

## Modo `unit`

Entradas:

- `backlog/XX_[modulo].md`
- `srv/[modulo]/[modulo]-service.js|ts`

Artefactos:

- `test/[modulo]/unit/*Service.test.js|ts`
- helpers locales si el modulo los necesita

Runner recomendado:

- usar `jest` o `mocha` segun la convencion ya establecida en el proyecto
- si no hay convencion previa, usar `jest`
- no levantar `cds.test()` salvo que el test deje de ser unitario y pase a `service` o `integration`

Incluye:

- validaciones de negocio
- transformaciones de datos
- errores funcionales
- mocks de dependencias externas

## Modo `auth`

Entradas:

- `backlog/XX_[modulo].md`
- `srv/[modulo]/authorization.cds`
- `srv/[modulo]/[modulo]-service.cds`

Artefactos:

- `test/[modulo]/auth/*Auth.test.js|ts`

Incluye:

- matriz por rol
- anonimo, rol insuficiente y rol correcto
- actions y functions protegidas

## Modo `service`

Entradas:

- `srv/[modulo]/[modulo]-service.cds`
- handlers si existen
- datos de prueba o fixtures basicos

Artefactos:

- `test/[modulo]/service/*Service.test.js|ts`

Incluye:

- requests HTTP o OData reales
- CRUD o lecturas principales
- query options
- acciones y functions

## Modo `data`

Entradas:

- `db/` y `db/data/`
- `test/data/` si existe
- backlog del modulo

Artefactos:

- `test/[modulo]/data/*Data.test.js|ts`

Incluye:

- validacion de cabeceras CSV
- validacion de estados y relaciones minimas
- carga de datos por perfil cuando aplique

## Modo `integration`

Entradas:

- modelo, servicios, handlers, auth y datos del modulo

Artefactos:

- `test/[modulo]/integration/*Integration.test.js|ts`

Incluye:

- flujos completos
- persistencia real
- efectos tras escrituras
- reglas de negocio relevantes

## Modo `all`

Ejecutar la secuencia completa y reportar:

- archivos creados por carpeta
- usuarios o roles probados
- fixtures usados o generados
- validaciones ejecutadas
- limitaciones abiertas