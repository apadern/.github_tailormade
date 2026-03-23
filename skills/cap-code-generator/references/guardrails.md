# Guardrails CAP

Usar esta referencia cuando haya que decidir como modelar, exponer o validar un modulo CAP sin degradar seguridad, consistencia o mantenibilidad.

## 1. Modelado CDS

- Preferir `entity Foo : cuid, managed` para entidades persistentes normales.
- Usar `UUID` como clave canonica salvo requisito explicito en contra.
- Definir `String(n)` y `Decimal(p,s)` con longitud y precision explicitas.
- Separar enums y tipos reutilizables en `types.cds` si aparecen en varias entidades.
- Usar `Composition of many` solo cuando exista ownership real del ciclo de vida.
- Evitar `Composition of one` salvo justificacion explicita.
- Mantener backlinks claros en asociaciones `to many`.
- Reutilizar namespace existente del proyecto antes de crear uno nuevo.

No hacer:

- No duplicar entidades ya existentes con otro nombre tecnico.
- No modelar campos de auditoria manuales si `managed` cubre el caso.
- No usar tipos genericos sin restricciones cuando el backlog define limites.

## 2. Servicios y API

- Exponer proyecciones en `srv/`, no entidades de persistencia sin filtrar.
- Declarar actions y functions solo para operaciones de negocio.
- Mantener nombres publicos estables y coherentes con el backlog.
- Limitar capacidades CRUD con anotaciones si la API no debe ser completamente editable.
- Revisar asociaciones expuestas para evitar sobreexposicion accidental.

No hacer:

- No usar `as select from` si lo que se necesita es una proyeccion de servicio normal.
- No publicar entidades sensibles por defecto.
- No trasladar restricciones de seguridad a la UI esperando que CAP las aplique.

## 3. Seguridad

- Priorizar `@requires` y `@restrict` en CDS.
- Aplicar permisos finos a entidades, acciones y funciones.
- Reutilizar nombres de rol existentes en el dominio o backlog.
- Probar permisos con usuarios mock o perfiles de test.

No hacer:

- No duplicar la misma autorizacion en CDS y handler sin una razon concreta.
- No mezclar reglas de negocio y reglas de autorizacion si pueden separarse.

## 4. Handlers

- Implementar servicios con `cds.ApplicationService`.
- Registrar handlers en `init()` y devolver `super.init()`.
- Usar `await` en todas las operaciones async.
- Usar `req.reject(...)` para errores funcionales y mensajes claros.
- Usar CQL o CQN para lecturas y escrituras.
- Mantener handlers del modulo junto a su service.

No hacer:

- No usar SQL raw salvo requisito excepcional documentado.
- No modificar `req.data` en `after` sin necesidad extrema.
- No registrar hooks asincronos tardios que puedan perder eventos.

## 5. Datos CSV

- Nombrar archivos como `[namespace]-[Entity].csv`.
- Alinear cabeceras con la entidad desplegada, no con nombres internos obsoletos.
- Generar datasets variados para estados, filtros y permisos.
- Separar `db/data` y `test/data` si el proyecto usa perfiles distintos.

No hacer:

- No cargar columnas gestionadas automaticamente sin motivo.
- No usar valores irreales que rompan validaciones basicas.

## 6. Tests

- Preferir `@cap-js/cds-test`.
- Cubrir happy path, validaciones, autorizacion y acciones custom.
- Validar tanto la respuesta como el efecto persistente cuando aplique.
- Probar al menos un caso de denegacion por rol cuando exista seguridad.

No hacer:

- No limitarse a probar HTTP 200 en operaciones con efectos complejos.
- No dejar sin prueba una action o function de negocio nueva.

## 7. Validacion final

Ejecutar como minimo:

- compilacion de modelos CDS
- arranque del servicio CAP
- carga de datos del perfil objetivo
- tests del modulo generado

Si alguna validacion no puede ejecutarse, dejar constancia explicita del motivo.