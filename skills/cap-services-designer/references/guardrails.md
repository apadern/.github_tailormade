# CAP Service Design Guardrails

Usar esta referencia para mantener consistencia entre el modelo de datos CAP y los servicios que se exponen.

## 1. Servicios y proyecciones

- Exponer proyecciones cuando la API no deba publicar la entidad persistente completa.
- Documentar `@path` solo cuando diverja del path por defecto.
- Distinguir entre servicio propio CAP y servicio remoto consumido via `cds.requires`.

No hacer:

- No tratar una entidad persistente como contrato publico por defecto.
- No mezclar en la misma tabla entidades base y proyecciones sin aclararlo.

## 2. Actions y Functions

- Usar `action` cuando hay side effects o mutacion de estado.
- Usar `function` cuando solo hay lectura, consulta o calculo sin side effects.
- Documentar si la operacion es bound o unbound.
- Definir entrada, salida, precondiciones y restricciones por estado o rol.

No hacer:

- No usar `action` como CRUD disfrazado sin justificarlo.
- No dejar operaciones custom sin trazabilidad a RF o caso de uso.

## 3. Auth y restricciones

- Reflejar `@requires`, `@restrict`, `@readonly`, `@insertonly` u otras restricciones relevantes.
- Diferenciar restricciones por rol, por estado y por ownership.
- Documentar si una proyeccion existe precisamente para separar permisos o visibilidad.

No hacer:

- No asumir que toda lectura y escritura comparte las mismas reglas.
- No omitir restricciones importantes esperando que solo vivan en handlers.

## 4. Query options y volumen

- Documentar `$filter`, `$search`, `$orderby`, `$expand`, `$skip`, `$top` y limites si aplican.
- Documentar profundidad maxima de `expand` si es relevante.
- Documentar orden por defecto si el contrato depende de ello.

No hacer:

- No dejar paginacion ilimitada sin justificacion.
- No publicar `expand` profundos sin advertir limites o coste.

## 5. Errores y side effects

- Documentar errores funcionales clave con codigo, status y contexto.
- Documentar side effects como eventos, auditoria, integraciones o recalculos.
- Distinguir error de validacion, autorizacion, conflicto y error tecnico.

No hacer:

- No devolver una tabla plana de endpoints sin semantica de negocio.
- No ocultar side effects relevantes de una action.

## 6. Checklist final

- catalogo de servicios completo
- detalle por servicio con OData, auth y operaciones
- actions y functions clasificadas correctamente
- filtros y paginacion explicitados
- errores relevantes documentados
- trazabilidad servicio-RF cubierta