---
name: cap-services-designer
description: "Genera especificacion de servicios SAP CAP (projections, contratos OData, actions, functions, filtros, auth, side effects y errores) para proyectos CAP. Usar cuando se necesite crear design/03_cap_services.md a partir de design/01 y design/02, manteniendo consistencia entre modelo de datos, servicios expuestos, dependencias remotas y contratos de negocio."
---

# CAP Services Designer

Generar especificacion de servicios orientada a SAP CAP, enfocada en exposicion OData, proyecciones, actions, functions, permisos, filtros y contratos de error.

## Objetivo del skill

- Definir contratos de servicios consistentes para SAP CAP.
- Derivar servicios expuestos desde `design/02_cap_data_model.md` sin duplicar el modelo de datos.
- Estandarizar OData paths, operaciones CRUD, actions, functions, filtros, paginacion, seguridad y modelo de error.
- Dejar el documento listo para implementacion posterior en `srv/*.cds` y handlers.

## Prerrequisitos

Imprescindibles:

- `design/01_technical_design.md`
- `design/02_cap_data_model.md`
- `analisis/03_requerimientos_funcionales.md`
- `analisis/10_interfaces_usuario.md`

Recomendados:

- `analisis/05_historias_usuario.md`
- `analisis/06_casos_uso.md`
- `analisis/08_integraciones.md`
- `analisis/09_diagramas_estados.md`
- backlog del modulo si existe
- `srv/` real del proyecto CAP si ya hay servicios definidos

## Fuente de verdad

- Fuente primaria: `design/02_cap_data_model.md` mas RFs, pantallas y diseno tecnico.
- Si ya existe un proyecto CAP, inspeccionar servicios y entidades con `mcp__cap-js_mcp-s_search_model` antes de proponer contratos nuevos.
- Si hay dudas sobre `service`, `projection`, `action`, `function`, `@path`, `@restrict`, `@readonly` o capacidades OData, consultar `mcp__cap-js_mcp-s_search_docs`.

## Modos de operacion

| Modo | Entrada | Salida |
|------|---------|--------|
| catalog | design/01 + design/02 + RFs | catalogo de servicios CAP |
| contracts | design/02 + RFs + interfaces | detalle de servicios, operaciones y contratos OData |
| actions-functions | RFs + casos de uso + estados | acciones y funciones CAP de negocio |
| projections-auth | design/02 + actores + backlog si existe | proyecciones, permisos y restricciones por servicio |
| filters-errors | interfaces + RFs + estados | filtros, paginacion, ordering y modelo de error |
| integrations | integraciones + design/01 | contratos para servicios remotos y side effects |
| all | todas las anteriores | documento completo `design/03_cap_services.md` |

Ver detalle de secciones, orden y artefactos en [references/mode-artifacts.md](references/mode-artifacts.md).

## Estructura de salida

Generar `design/03_cap_services.md` con:

### 1. Convenciones globales

- Protocolo principal: OData V4 en CAP
- Paths: usar `@path` solo cuando sea necesario
- Paginacion: `$skip`, `$top`, `$count` y limites por servicio si aplica
- Filtros: priorizar `$filter`, `$search`, `$orderby`, `$expand`
- Errores: documentar codigo funcional, mensaje, HTTP status y contexto

### 2. Catalogo de Servicios

| Servicio CAP | Entidad principal | Modulo | Tipo | Descripcion |
|--------------|-------------------|--------|------|-------------|
| UserService | User | auth | projection-service | Gestion de usuarios |

### 3. Clasificacion de Servicios y Exposicion

| Servicio | Categoria | Exposicion | Path | Consumidor principal |
|----------|-----------|------------|------|----------------------|
| UserService | publico | OData V4 | /odata/v4/UserService | UI o integracion |
| InternalSyncService | interno | no expuesto | n/a | jobs o eventos |

Explicitar aqui:

- si el servicio es publico, interno o mixto
- si requiere `@path` o puede usar el path por defecto
- si debe quedar fuera de exposicion HTTP y resolverse como servicio interno
- si actua sobre entidades locales, remotas o mixtas

### 4. Detalle por Servicio

Para cada servicio:

```markdown
### UserService

**Entidad principal:** User

**Namespace / ubicacion prevista:** `srv/auth/auth-service.cds`

**Exposicion OData:**
| Operacion | Evento CAP | Ruta OData | Auth | Notas |
|-----------|------------|------------|------|-------|
| Listar | READ | /odata/v4/UserService/Users | Protegido | Soporta filtros |
| Crear | CREATE | /odata/v4/UserService/Users | Protegido | Validaciones previas |

**Proyecciones expuestas:**
| Nombre | Base | Campos principales | Notas |
|--------|------|--------------------|-------|
| Users | User | ID, name, email | Excluye sensibles |

**Actions y Functions:**
| Nombre | Tipo | Bound | Entrada | Salida | Side effects | Idempotencia | Descripcion |
|--------|------|-------|---------|--------|--------------|-------------|-------------|
| activate | action | si | reason: String | User | si | requerida | Activa usuario |

**Filtros y query options:**
| Campo | Operadores | Notas |
|------|------------|-------|
| status | eq, ne | Enum |

**Autorizacion:**
- `@requires`: User
- `@restrict`: admin para write, self para read own data

**Notas del contrato:**
- side effects
- restricciones por estado
- ejemplos de error relevantes
```

### 5. Matriz Servicio-RF

| Servicio | Operacion CAP | Action/Function | RF Asociado | Descripcion |
|----------|----------------|-----------------|-------------|-------------|
| ShipmentService | READ | - | RF-001 | Consulta de embarques |

### 6. Proyecciones, Auth y Restricciones

| Servicio | Projection | Rol | Capacidades | Restricciones |
|----------|------------|-----|-------------|---------------|
| UserService | Users | Admin | C,R,U,D | sin restriccion adicional |

### 7. Estrategia de Lectura y Consistencia

| Servicio | Tipo de lectura | Fuente principal | Consistencia esperada | Manejo de fallo |
|----------|-----------------|------------------|-----------------------|-----------------|
| ShipmentService | local | CAP DB | fuerte local | error inmediato |
| PurchaseOrderReadService | remota | API externa | eventual o dependiente del origen | fallback o error funcional |

Documentar para cada servicio relevante:

- si lee solo local, solo remoto o hace mashup de varias fuentes
- si la respuesta requiere consistencia fuerte, eventual o reconciliacion posterior
- si una accion combina escritura local con llamada remota y como se recupera ante fallo parcial
- si hay retry, cola, job asincrono o compensacion

### 8. Dependencias Remotas y Eventos

| Servicio CAP | Dependencia | Tipo | Uso | Observaciones |
|--------------|-------------|------|-----|---------------|
| PurchaseOrderReadService | S4PurchaseOrderAPI | `cds.requires` remoto | lectura | sin persistencia local |
| InvoiceWorkflowService | ocr.completed | evento | actualizacion de estado | asincrono |

Explicitar aqui:

- que integraciones se resuelven via `cds.requires`
- que operaciones son sincronas y cuales deben ser asincronas
- que eventos de dominio o integracion afectan al servicio
- que contratos requieren idempotencia, retry o correlacion

### 9. Filtros, Paginacion y Errores

| Servicio | Query Option / Error | Definicion |
|----------|----------------------|------------|
| ShipmentService | `$top` | max 100 |
| ShipmentService | ERR_SHIPMENT_001 | no editable fuera de DRAFT |

### 10. Open Decisions y Bloqueos

| Decision | Impacto | Estado | Responsable |
|----------|---------|--------|-------------|
| Confirmar si accion de aprobacion debe ser sincrona o asincrona | cambia contrato, timeouts e idempotencia | abierto | arquitectura |

Registrar aqui cualquier punto que impida cerrar contratos CAP sin asumir de forma optimista una decision de integracion, consistencia o seguridad.

## Proceso

1. Leer `design/01`, `design/02`, RFs y pantallas.
2. Identificar entidades persistentes, proyecciones necesarias y operaciones de negocio.
3. Revisar si ya existen servicios o paths CAP equivalentes.
4. Crear catalogo de servicios a partir del modelo de datos.
5. Clasificar cada servicio como publico, interno o mixto y decidir su exposicion.
6. Definir contratos OData, CRUD, actions y functions.
7. Documentar permisos, filtros, paginacion, side effects, consistencia e idempotencia.
8. Documentar dependencias remotas, eventos, retry o compensacion cuando existan.
9. Trazar cada operacion importante con RFs y casos de uso.
10. Registrar decisiones abiertas y generar `design/03_cap_services.md`.

## Guardrails criticos

- No documentar REST generico cuando el objetivo real es OData CAP.
- No exponer entidades persistentes sin evaluar si requieren proyeccion.
- No usar `action` para operaciones sin side effects; usar `function` cuando sea lectura o calculo.
- No duplicar atributos del modelo de datos; referenciar `design/02_cap_data_model.md`.
- No omitir restricciones de auth, estado o ownership cuando afecten a una operacion.
- No asumir paginacion ilimitada ni `expand` sin limites razonables.
- No documentar contratos remotos sin distinguir si son servicios propios CAP o `cds.requires` remotos.
- No exponer como publico un servicio que solo sirve de orquestacion interna o soporte asincrono.
- No asumir transaccion distribuida entre CAP y sistemas remotos; documentar fallo parcial, compensacion o reconciliacion.
- No declarar una action remota como sincrona por comodidad si el SLA, timeout o acoplamiento indican flujo asincrono.
- No mezclar en un mismo contrato lecturas locales y remotas sin dejar clara la consistencia esperada.
- Si la seguridad depende de claims o restricciones por instancia, reflejarlo explicitamente en el contrato del servicio.
- Si una decision de exposicion, idempotencia o integracion no esta cerrada, registrarla en open decisions.

Leer [references/guardrails.md](references/guardrails.md) para anti-patrones, decisiones de diseño y checklist final.

## Restricciones

- No generar aun codigo `.cds` completo ni handlers completos.
- No definir frontend mock o REST genérico fuera del contexto CAP salvo que se documente como integración separada.
- No inventar roles, entidades ni enums fuera del modelo y backlog.
- No duplicar especificaciones ya resueltas en `design/02_cap_data_model.md`.

## Escritura incremental

Para documentos extensos:

1. Crear encabezado, convenciones y catalogo.
2. Anadir detalle de servicios en bloques de 3-5 servicios.
3. Anadir matriz servicio-RF.
4. Anadir secciones de auth, filtros, errores e integraciones.

No devolver el contenido completo del documento en la respuesta final. Solo un resumen cuantitativo.

## Criterio de finalizacion

El trabajo se considera completado cuando:

✅ `design/03_cap_services.md` esta generado  
✅ Cada servicio queda clasificado por exposicion y consumidor  
✅ Cada servicio referencia entidades o proyecciones del modelo CAP  
✅ Las actions y functions quedan diferenciadas correctamente  
✅ Los permisos, filtros, side effects y errores quedan explicitados  
✅ Las dependencias remotas, consistencia e idempotencia quedan explicitadas cuando aplican  
✅ La matriz servicio-RF y las decisiones abiertas cubren las operaciones relevantes  

## Salida esperada del skill

```
Archivo design/03_cap_services.md generado:
- Servicios: X
- Operaciones CAP: Y
- Actions y Functions: Z
- Restricciones de auth: A
- Errores documentados: E
- Dependencias remotas o eventos: D
- Open decisions: O
```
