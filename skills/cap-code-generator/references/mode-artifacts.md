# Modes And Artifacts

Usar esta referencia para decidir que generar en cada modo y en que orden hacerlo.

## Orden recomendado

1. `models`
2. `services`
3. `auth`
4. `handlers`
5. `data`
6. `tests`

## Modo `models`

Entradas:

- backlog/XX_[modulo].md
- design/02_data_model.md si existe

Artefactos:

- db/[modulo]/schema.cds
- db/[modulo]/types.cds opcional

Incluye:

- namespace
- entities
- aspects del modulo
- enums y tipos reutilizables

## Modo `services`

Entradas:

- backlog/XX_[modulo].md
- design/03_data_services.md si existe
- models ya generados o existentes

Artefactos:

- srv/[modulo]/[modulo]-service.cds

Incluye:

- service principal
- projections
- actions y functions
- paths o anotaciones de capacidad si aplican

## Modo `auth`

Entradas:

- backlog/XX_[modulo].md
- services ya generados o existentes

Artefactos:

- srv/[modulo]/authorization.cds

Incluye:

- `@requires`
- `@restrict`
- permisos sobre entidades y acciones

## Modo `handlers`

Entradas:

- backlog/XX_[modulo].md
- services ya generados o existentes

Artefactos:

- srv/[modulo]/[modulo]-service.js o .ts

Incluye:

- clase que extiende `cds.ApplicationService`
- handlers `before`, `on`, `after`
- validaciones de negocio
- acceso a datos via CQL o CQN

## Modo `data`

Entradas:

- backlog/XX_[modulo].md
- models ya generados o existentes

Artefactos:

- db/data/[namespace]-[Entity].csv
- test/data/[namespace]-[Entity].csv opcional

Incluye:

- filas para happy path
- filas para filtros o estados
- datos compatibles con roles o restricciones si se prueban permisos

## Modo `tests`

Entradas:

- services
- handlers
- auth
- data

Artefactos:

- test/[modulo]/[modulo]-service.test.js o .ts
- test/[modulo]/[modulo]-auth.test.js o .ts

Incluye:

- bootstrap con `@cap-js/cds-test`
- pruebas CRUD o de lectura principal
- pruebas de acciones o functions custom
- pruebas de autorizacion

## Modo `all`

Ejecutar la secuencia completa y reportar:

- archivos creados por carpeta
- decisiones de modelado relevantes
- roles aplicados
- validaciones ejecutadas
- limitaciones abiertas