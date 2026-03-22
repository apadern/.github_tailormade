# CAP Data Modeling Guardrails

Usar esta referencia para mantener consistencia entre el modelo conceptual y un futuro modelo CDS enterprise.

## 1. Entidades persistentes

- Preferir `entity Foo : cuid, managed` para entidades persistentes normales.
- Usar `UUID` como clave canonica salvo requisito explicito distinto.
- Definir `String(n)` y `Decimal(p,s)` con restricciones concretas.
- Diferenciar claramente entre entidad persistente y entidad derivada o virtual.

No hacer:

- No duplicar `createdAt`, `createdBy`, `modifiedAt` o `modifiedBy` si `managed` cubre el caso.
- No dejar claves o tipos ambiguos sin una razon de negocio.

## 2. Types y enums

- Consolidar enums reutilizados en `types.cds` o un area comun del modulo.
- Usar nombres de enum en PascalCase y valores en un estilo consistente.
- Reutilizar types comunes como `Country`, `Currency` o similares si encajan en el dominio.

No hacer:

- No repetir el mismo enum inline en varias entidades.
- No mezclar valores de negocio y literales tecnicos sin necesidad.

## 3. Asociaciones y composiciones

- Usar `association` para referencias.
- Usar `composition` solo cuando el hijo depende del ciclo de vida del padre.
- Documentar backlinks y cardinalidades cuando haya relaciones `to many`.
- Para N:M, documentar entidad puente.

No hacer:

- No usar `Composition of one` por defecto.
- No tratar una referencia simple como ownership real si no lo es.

## 4. Namespaces y modularidad

- Reutilizar namespace existente del proyecto antes de crear uno nuevo.
- Agrupar entidades, enums y aspects por modulo funcional.
- Separar aspectos y types reutilizables cuando sirvan a varios modulos.

No hacer:

- No dispersar entidades del mismo dominio sin criterio.
- No crear namespaces casi duplicados por variaciones minimas de nombre.

## 5. Consistencia documental

- Cada entidad del catalogo debe tener correspondencia con su detalle.
- Cada enum listado en una entidad debe aparecer una sola vez en el resumen de enums y types.
- Cada relacion importante debe aparecer tanto en el diagrama como en la matriz de relaciones.
- Cada modulo en dependencias debe existir en el diseno tecnico o quedar justificado.

## 6. Checklist final

- catalogo de entidades completo
- detalle por entidad con tipo CAP y mapeo CDS
- relaciones clasificadas como association o composition
- enums y types consolidados
- namespaces y aspects claros
- dependencias modulares sin ambiguedad