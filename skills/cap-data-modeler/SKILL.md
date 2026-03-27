---
name: cap-data-modeler
description: "Genera modelo de datos SAP CAP (conceptual + logico + mapeo a CDS) para proyectos CAP. Usar cuando se necesite crear un documento de modelo de datos orientado a CAP con entidades, atributos, relaciones, aspects, enums, namespaces, ownership y decisiones de persistencia a partir del analisis funcional y design/01."
---

# CAP Data Modeler

Generar modelo de datos orientado a SAP CAP, manteniendo trazabilidad desde analisis funcional hasta artefactos CDS futuros.

El objetivo es describir entidades, relaciones, enums, aspects y tipos de negocio, y dejar explicito como se traducen a un modelo CAP basado en namespaces, `entity`, `type`, `aspect`, `association` y `composition`, sin entrar todavia en implementacion completa de archivos `.cds`.

## Prerrequisitos

Imprescindibles:

- `design/01_technical_design.md` o equivalente tecnico del modulo
- `analisis/03_requerimientos_funcionales.md`
- `analisis/10_interfaces_usuario.md`

Recomendados:

- `analisis/05_historias_usuario.md`
- `analisis/06_casos_uso.md`
- `analisis/07_diagramas_procesos.md`
- `analisis/08_integraciones.md`
- `analisis/14_matriz_trazabilidad.md`
- cualquier `db/` existente del proyecto CAP, si ya existe modelado previo

## Fuente de verdad

- Fuente primaria: requisitos funcionales, pantallas y diseno tecnico.
- Si ya existe un proyecto CAP, inspeccionar el modelo real con `mcp__cap-js_mcp-s_search_model` antes de proponer entidades nuevas.
- Si hay dudas sobre patrones de modelado CDS, consultar `mcp__cap-js_mcp-s_search_docs` antes de asumir una estructura.

## Modos de operacion

| Modo | Entrada | Salida |
|------|---------|--------|
| conceptual | analisis + design/01 | catalogo de entidades y ER de alto nivel |
| structural | conceptual + design/01 | namespaces, entities, aspects y persistencia CAP |
| enum-consolidation | analisis + conceptual | resumen unico de enums y types reutilizables |
| mapping | structural + design/03 si existe | mapeo a CDS, persistencia, services y origen del dato |
| dependencies | structural + analisis + backlog si existe | dependencias entre modulos y orden de implementacion |
| all | todas las anteriores | documento completo de modelo de datos CAP |

Ver detalle de secciones, orden y artefactos en [references/mode-artifacts.md](references/mode-artifacts.md).

## Estructura de salida

Generar `design/02_cap_data_model.md` con estas secciones:

### 1. Catalogo de Entidades

| Entidad | Descripcion | Modulo | Tipo CAP |
|---------|-------------|--------|----------|
| User | Usuario del sistema | auth | persistent |
| Shipment | Embarque | logistics | persistent |

### 2. Detalle por Entidad

Para cada entidad:

```markdown
### [NombreEntidad]

**Descripcion:** Breve descripcion

**Tipo CAP:** `persistent` | `virtual` | `projection` | `aspect-composition`

**Namespace sugerido:** `com.myorg.[modulo]`

**Mapeo CDS (alto nivel):**
- Entity / Type / Aspect: `entity [NombreEntidad]`
- Reuse aspects: `cuid`, `managed` (si aplica)
- Persistencia: `db/[modulo]/schema.cds` o equivalente

**Origen del dato:** `manual` | `sync` | `derivado` | `externo-no-persistido`

**Atributos:**
| Campo | Tipo de negocio | Tipo CDS sugerido | Descripcion | Requerido |
|-------|------------------|-------------------|-------------|-----------|
| ID | string | UUID | Identificador unico | Si |
| status | enum | ShipmentStatus | Estado actual | Si |

**Relaciones CAP:**
| Campo | Tipo | Destino | Cardinalidad | Ownership |
|------|------|---------|--------------|-----------|
| items | Composition of many | ShipmentItem | 1:N | Padre-hijo |

**Enums asociados:**
- Listar solo nombres de enums usados
- Si no aplica: `- Ninguno`
```

### 3. Diagrama Entidad-Relacion

Usar Mermaid `erDiagram` y, debajo, aclarar el mapeo CAP cuando haya composiciones o asociaciones no triviales.

### 4. Matriz de Relaciones

| Entidad Origen | Relacion | Entidad Destino | Cardinalidad | Tipo CAP |
|----------------|----------|-----------------|--------------|----------|
| Shipment | contiene | ShipmentItem | 1:N | composition |

### 5. Namespaces, Aspects y Organizacion CAP

| Namespace | Modulo | Artefactos previstos | Notas |
|-----------|--------|----------------------|-------|
| com.nttdata.logistics | logistics | schema.cds, types.cds | dominio core |

Incluir aqui:

- aspects comunes reutilizables
- types comunes reutilizables
- decision de `cuid`, `managed`, `localized`, code lists y tipos comunes

### 6. Decisiones de Persistencia y Fuente de Verdad

| Entidad | Persistencia | Fuente de verdad | Motivo | Implicacion CAP |
|---------|--------------|------------------|--------|-----------------|
| Shipment | local | CAP DB | ownership completo del ciclo de vida | CRUD local completo |
| Supplier | replicada | sistema externo | cache o snapshot controlado | sincronizacion y reconciliacion |
| PurchaseOrder | no persistida | servicio remoto | lectura federada | projection o servicio de lectura |

Documentar explicitamente:

- si la entidad es local, replicada, cacheada, derivada o solo remota
- si CAP es sistema de registro o solo sistema de proceso
- si la escritura ocurre en CAP, en sistema remoto o en ambos con compensacion
- si existen snapshots, eventos, jobs o reconciliacion posterior

### 7. Ownership y Control de Acceso

| Entidad | Owner funcional | Scope de acceso | Regla principal | Impacto en modelo |
|---------|-----------------|-----------------|-----------------|-------------------|
| Shipment | creador o buyer | own, team, tenant | solo owner edita en DRAFT | campos owner/status obligatorios |

Explicitar aqui:

- que entidad requiere ownership explicito para soportar restricciones por instancia
- que claims o atributos de identidad deberan existir para autorizar lecturas o escrituras
- cuando el control de acceso depende de estado, sociedad, organizacion o buyer group
- cuando una relacion necesita evitar cascadas peligrosas por separar ownership y referencia

### 8. Resumen de Enums y Types

| Enum o Type | Tipo CDS | Valores o estructura | Ubicacion sugerida |
|-------------|----------|----------------------|--------------------|
| ShipmentStatus | String enum | DRAFT, CONFIRMED, DELIVERED | db/logistics/types.cds |

### 9. Dependencias entre Modulos

| Modulo | Depende de | Requerido por | Orden | Justificacion |
|--------|------------|---------------|-------|---------------|
| auth | - | todos | 01 | base de seguridad |

### 10. Open Decisions y Bloqueos

| Decision | Impacto | Estado | Responsable |
|----------|---------|--------|-------------|
| Definir si PurchaseOrder se persiste o se consume remoto | cambia entidades, claves y servicios | abierto | arquitectura |

Registrar aqui cualquier punto que impida cerrar el modelo sin asumir de forma optimista una decision tecnica o funcional.

## Proceso

1. Leer requisitos, pantallas y diseno tecnico.
2. Identificar sustantivos clave y distinguir entidades, code lists, enums y datos derivados.
3. Revisar si el proyecto CAP ya tiene namespaces, entities o types reutilizables.
4. Construir el catalogo de entidades.
5. Definir detalle por entidad con mapeo a CDS de alto nivel.
6. Determinar para cada entidad persistencia, fuente de verdad y estrategia de sincronizacion si aplica.
7. Inferir relaciones y clasificar cada una como `association` o `composition`.
8. Identificar ownership, restricciones por instancia y claims necesarios para soportarlas.
9. Consolidar enums y types reutilizables sin duplicados.
10. Definir namespaces, aspects, dependencias modulares y decisiones abiertas.
11. Generar `design/02_cap_data_model.md`.

## Guardrails criticos

- Preferir `cuid` y `managed` para entidades persistentes normales salvo requisito explicito en contra.
- No usar `composition` si no existe ownership real del ciclo de vida.
- Evitar `Composition of one` salvo justificacion fuerte.
- No duplicar campos de auditoria si un aspect comun ya los cubre.
- Consolidar enums y types si se reutilizan en mas de una entidad.
- No modelar N:M como si CAP lo resolviera implicitamente; documentar entidad puente.
- Distinguir siempre entre entidad persistente, proyeccion, tipo y entidad virtual.
- Si ya existe un namespace o una code list compatible, reutilizarla antes de inventar otra.
- No asumir que toda entidad funcional debe persistirse en CAP; justificar cuando es remota, replicada o derivada.
- No mezclar en la misma entidad atributos cuyo sistema de registro pertenece a dominios distintos sin explicar sincronizacion y consistencia.
- No introducir ownership implicito; si el acceso depende de usuario, organizacion o estado, modelarlo de forma verificable.
- No convertir relaciones de referencia a `composition` para simplificar borrados o navegacion.
- Si una decision de persistencia o claves no esta cerrada, registrarla en open decisions en lugar de fijarla arbitrariamente.

Leer [references/guardrails.md](references/guardrails.md) para decisiones detalladas, anti-patrones y checklist de consistencia.

## Restricciones

- No generar todavia codigo `.cds` completo salvo snippets ilustrativos.
- No generar clases Java, interfaces TypeScript ni DDL SQL completo.
- No mezclar modelo conceptual con decisiones de UI o autorizacion fuera de lo necesario para el dato.
- No omitir el tipo CAP de cada relacion importante.
- No dejar enums duplicados o ambiguos.

## Escritura incremental

Para documentos extensos, generar el archivo de forma incremental:

1. Crear encabezado y secciones 1-2.
2. Anadir entidades al catalogo en bloques pequenos.
3. Anadir detalle por entidad en bloques de 3-5 entidades.
4. Anadir diagrama ER y matriz de relaciones.
5. Anadir namespaces, aspects, enums y dependencias.

No devolver el contenido completo del documento en la respuesta final. Solo confirmar resumen cuantitativo.

## Criterio de finalizacion

El trabajo se considera completado cuando:

✅ El documento `design/02_cap_data_model.md` esta generado  
✅ Las entidades y relaciones cubren los requisitos funcionales relevantes  
✅ Cada entidad tiene tipo CAP y mapeo CDS de alto nivel  
✅ Cada entidad relevante tiene declarada su fuente de verdad y estrategia de persistencia  
✅ Los supuestos de ownership o acceso por instancia quedan explicitados  
✅ Los enums y types quedan consolidados sin duplicados  
✅ Las dependencias modulares, namespaces y decisiones abiertas quedan explicitados  

## Salida esperada del skill

```
Archivo design/02_cap_data_model.md generado:
- Entidades: X
- Relaciones: Y
- Enums o types: E
- Namespaces: N
- Modulos: M
- Decisiones de persistencia: P
- Open decisions: O
```
