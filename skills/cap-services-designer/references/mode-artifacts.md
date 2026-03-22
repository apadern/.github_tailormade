# Modes And Artifacts

Usar esta referencia para decidir que construir en cada modo de cap-services-designer.

## Orden recomendado

1. `catalog`
2. `contracts`
3. `actions-functions`
4. `projections-auth`
5. `filters-errors`
6. `integrations`

## Modo `catalog`

Entradas:

- `design/01_technical_design.md`
- `design/02_cap_data_model.md`
- RFs

Salida:

- secciones 1 y 2 del documento

Incluye:

- catalogo de servicios
- entidad principal
- modulo
- tipo de servicio o projection

## Modo `contracts`

Entradas:

- `design/02_cap_data_model.md`
- RFs
- interfaces

Salida:

- seccion 3 del documento

Incluye:

- operaciones OData
- eventos CAP implicitos
- paths
- notas de contrato

## Modo `actions-functions`

Entradas:

- RFs
- casos de uso
- estados

Salida:

- parte de seccion 3 y seccion 4

Incluye:

- acciones de negocio
- funciones de consulta o calculo
- bound o unbound

## Modo `projections-auth`

Entradas:

- design/02
- actores o roles
- backlog si existe

Salida:

- seccion 5 del documento

Incluye:

- proyecciones por caso de uso
- roles y restricciones
- capacidades por servicio

## Modo `filters-errors`

Entradas:

- interfaces
- RFs
- estados

Salida:

- seccion 6 del documento

Incluye:

- filtros
- paginacion
- ordering
- modelo de error

## Modo `integrations`

Entradas:

- analisis de integraciones
- design/01

Salida:

- enriquecer seccion 3 y seccion 6

Incluye:

- contratos de servicios remotos
- side effects
- dependencias de servicios externos

## Modo `all`

Ejecutar la secuencia completa y reportar:

- servicios
- operaciones
- actions y functions
- restricciones
- errores documentados