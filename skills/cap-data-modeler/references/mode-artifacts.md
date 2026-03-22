# Modes And Artifacts

Usar esta referencia para decidir que construir en cada modo de cap-data-modeler.

## Orden recomendado

1. `conceptual`
2. `structural`
3. `enum-consolidation`
4. `mapping`
5. `dependencies`

## Modo `conceptual`

Entradas:

- `analisis/03_requerimientos_funcionales.md`
- `analisis/10_interfaces_usuario.md`
- `design/01_technical_design.md`

Salida:

- secciones 1 a 4 de `design/02_cap_data_model.md`

Incluye:

- catalogo de entidades
- detalle inicial por entidad
- diagrama ER
- matriz de relaciones

## Modo `structural`

Entradas:

- salida conceptual
- `design/01_technical_design.md`
- `db/` existente si hay proyecto CAP

Salida:

- seccion 5 de `design/02_cap_data_model.md`

Incluye:

- namespaces
- entities persistentes, virtuales o proyecciones
- aspects comunes y modulares
- organizacion prevista de archivos CDS

## Modo `enum-consolidation`

Entradas:

- analisis funcional
- detalle por entidad

Salida:

- seccion 6 de `design/02_cap_data_model.md`

Incluye:

- enums unicos
- types reutilizables
- ubicacion sugerida en `types.cds`

## Modo `mapping`

Entradas:

- structural
- `design/03_data_services.md` si existe

Salida:

- enriquecer seccion 2 y seccion 5 del documento

Incluye:

- mapeo entity/type/aspect
- uso de `cuid`, `managed`, `localized` o code lists
- origen del dato y persistencia CAP

## Modo `dependencies`

Entradas:

- modelo ya estructurado
- backlog si existe

Salida:

- seccion 7 de `design/02_cap_data_model.md`

Incluye:

- dependencias de modulos
- orden de implementacion
- riesgos de ciclos o shared domains

## Modo `all`

Ejecutar todas las fases y reportar:

- entidades
- relaciones
- enums o types
- namespaces
- modulos y orden propuesto