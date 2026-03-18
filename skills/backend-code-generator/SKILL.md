---
name: backend-code-generator
description: Genera código backend Java Spring Boot (migraciones Flyway, entities JPA, repositories, DTOs, services, controllers) desde backlog/diseño.
---

# Backend Code Generator

Genera código Java Spring Boot desde especificaciones de diseño técnico para MVPs.

## Modos de Operación

| Modo | Entrada | Salida |
|------|---------|--------|
| migrations | backlog/XX_[modulo].md (primaria) + design/02_data_model.md (acelerador) | backend/src/main/resources/db/migration/VXX__*.sql |
| entities | backlog/XX_[modulo].md (primaria) + design/02_data_model.md (acelerador) | backend/src/main/java/com/nttdata/backend/[modulePackage]/model/*.java |
| repositories | entities + backlog/XX_[modulo].md | backend/src/main/java/com/nttdata/backend/[modulePackage]/repository/*.java |
| dtos | backlog/XX_[modulo].md (primaria) + design/02_data_model.md (acelerador) | backend/src/main/java/com/nttdata/backend/[modulePackage]/dto/*.java |
| services | backlog/XX_[modulo].md (primaria) + design/03_data_services.md (acelerador) + DTOs | backend/src/main/java/com/nttdata/backend/[modulePackage]/service/*.java |
| controllers | services + (design/03_data_services.md opcional) | backend/src/main/java/com/nttdata/backend/[modulePackage]/controller/*.java |
| all | backlog/XX_[modulo].md (primaria) + design/02 + design/03 (opcionales) | Todos los anteriores |

## Fuente de verdad (IMPORTANTE)

- **Fuente primaria obligatoria:** `backlog/XX_[modulo].md`.
- `design/02_data_model.md` y `design/03_data_services.md` son **aceleradores opcionales** (si existen, ayudan a completar constraints/contratos), pero no sustituyen el backlog.

## Guardrails anti-errores

### 1) Colisiones de beans Spring (ConflictingBeanDefinition / BeanDefinitionOverride)

Problema típico: dos clases con el mismo nombre (p.ej. `FooService`, `FooRepository`) en distintos paquetes generan el mismo bean name por defecto.

Regla:
- Antes de crear `*Service` / `*Repository`, buscar si ya existe un homónimo en el repo.
  - Si existe fuera del módulo: preferir **renombrar la clase** con prefijo/sufijo del módulo.
  - Si no se puede renombrar: asignar bean name explícito (`@Service("...")`, `@Repository("...")`) y, si hay inyección ambigua, usar `@Qualifier`.

### 2) Colisiones de entidades JPA (DuplicateMappingException)

Problema típico: dos entidades con el mismo nombre JPA por defecto (class name) en distintos paquetes.

Regla:
- Si existe otra entidad con el mismo class name en el repo, añadir `@Entity(name = "...")` único (por ejemplo sufijo del módulo).

### 3) Mismatch BD <-> JPA (Schema-validation wrong column type)

Reglas rápidas:
- Columnas `numeric` en PostgreSQL: mapear a `BigDecimal` (no `Double`) y, si aplica, usar `@Column(columnDefinition = "numeric")`.
- Si una columna usa un **dominio** Postgres (p.ej. `tipo_busqueda`, `version_sclv`, etc.): reflejarlo en la entity con `@Column(columnDefinition = "<dominio>")`.
- Para enums persistidos como string: `@Enumerated(EnumType.STRING)` (y mantener coherencia con el tipo real definido en migraciones).

### 4) Flyway checksum mismatch

Regla:
- No modificar migraciones ya creadas/aplicadas. Para cualquier cambio, crear una nueva migración `VXX__...sql`.

## Normalización del módulo (OBLIGATORIO)

A partir del nombre del módulo en el backlog, derivar y usar de forma consistente:

- `moduleSlug`: kebab-case para rutas/URL (ej: `maestro-posiciones`).
- `moduleKey`: snake_case para migraciones y nombres de tablas/archivos (ej: `maestro_posiciones`).
- `modulePackage`: segmento de package Java en minúsculas (ej: `maestroposiciones`).

Regla recomendada:
- `moduleSlug`: minúsculas, espacios/underscore → `-`.
- `moduleKey`: minúsculas, espacios/guiones → `_`.
- `modulePackage`: eliminar separadores y dejar solo `[a-z0-9]`.

## Parámetros opcionales

- `module` (string): nombre del módulo (ej: "maestroposiciones", "auth").
  - **REQUERIDO**: debe extraerse del backlog o diseño.
- `startVersion` (number): versión inicial para migraciones Flyway.
  - Default: buscar en `backend/src/main/resources/db/migration/` la última versión y autoincrement.
- `basePackage` (string): paquete base Java.
  - Default: `com.nttdata.backend`
- `includeAudit` (boolean): añade campos de auditoría (createdAt, updatedAt, createdBy, updatedBy).
  - Default: `true`
- `includeSoftDelete` (boolean): implementa soft delete con campo deletedAt.
  - Default: `false`
- `generateTestData` (boolean): genera datos de prueba (inserts) en migraciones de seed.
  - Default: `true`
- `minTestRecords` (number): mínimo de registros en datos de prueba.
  - Default: `10`

## Prerrequisitos

Fuente primaria (OBLIGATORIO):
- `backlog/XX_[modulo].md` - Backlog del módulo siguiendo el template detallado.

Aceleradores (OPCIONAL):
- `design/02_data_model.md` - Modelo de datos con entidades (si existe, usarlo para completar tipos/constraints).
- `design/03_data_services.md` - Especificación de servicios/API (si existe, usarlo para contratos y seguridad).

Infra (OBLIGATORIO):
- Proyecto Spring Boot ya scaffolded con estructura base
- `pom.xml` con dependencias: Spring Web, Spring Data JPA, Flyway, Spring Security, Validation, Lombok

## Modo: Migrations

Transforma entidades del modelo de datos en migraciones SQL para Flyway.

### Salida

Archivos en `backend/src/main/resources/db/migration/`. 

Revisar migraciones existentes para consistencia en el numero de versión (VXX) a generar. Si el ultimo fichero de migración es `V8__xxxx`, se debe generar `V9__xxxx` (incremento secuencial), ignorando cualquier versión discrepante indicada en el backlog. El estado actual de la carpeta de migraciones prevalece sobre la documentación para determinar la numeración correcta.

Generar un unico fichero seed de datos iniciales (opcional) por módulo, con un nombre estándar (`VXX__{moduleKey}_seed_data.sql`), en lugar de múltiples migraciones de seed.

Convención de nombres: Flyway usa `V{n}__{description}.sql` (doble guion bajo **solo** entre versión y descripción). Dentro de `description` usar guion bajo simple.

- **VXX__{moduleKey}_create_enums.sql** - Todos los enums del modulo
- **VXX__{moduleKey}_create_{tabla}.sql** - Tabla con PK, FKs, constraints, campos auditoría
- **VXX__{moduleKey}_seed_data.sql** - Datos iniciales (opcional)

Ejemplo:
- `V5__maestro_posiciones_create_posiciones.sql`

### Convenciones

- Usar tipos SQL estándar: `BIGSERIAL`, `VARCHAR`, `TIMESTAMP`, `BOOLEAN`
- **PKs (CANÓNICO):** `id BIGSERIAL PRIMARY KEY`
  - Solo usar `*_id` si el backlog/diseño lo exige explícitamente.
  - Si se usa `*_id`, las entities deben mapearlo con `@Column(name = "*_id")` y los FKs deben referenciar esa columna.
- FKs: `CONSTRAINT fk_[tabla]_[ref] FOREIGN KEY ([columna]) REFERENCES [tabla_ref]([columna_ref])`
- Índices: `CREATE INDEX idx_[tabla]_[columna] ON [tabla]([columna])`
- **Auditoría (por defecto):** `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP`, `updated_at TIMESTAMP`
  - `created_by` y `updated_by` SOLO si existe campo equivalente en la entity (o si el template del proyecto incluye una BaseEntity con esos campos).

### Reglas anti-errores (IMPORTANTE)

- **No adivinar nombres de tabla/columna:** si el backlog o `design/02_data_model.md` define el nombre de tabla/columna, usarlo tal cual.
- **Nombres de tabla:** la clase entity puede ser singular, pero la tabla debe seguir el nombre del modelo (frecuentemente plural en snake_case). Evitar variaciones tipo `auditoria_accion` vs `auditoria_acciones`.
- **FKs:** referenciar SIEMPRE la PK real de la tabla referenciada (por defecto `id`).
- **Flyway:** NO editar migraciones ya ejecutadas en un entorno persistente.
  - Si hay que cambiar el esquema: crear una nueva migración (ALTER/RENAME).
  - Si una migración ya se ejecutó y se cambia el archivo, puede aparecer `checksum mismatch`; preferir recrear el entorno o ejecutar `flyway repair` conscientemente.

## Modo: Entities

Transforma entidades en clases JPA con anotaciones, validaciones y Lombok.

### Salida

- Clases en `backend/src/main/java/com/nttdata/backend/[modulo]/model/*.java`

### Convenciones

- Anotaciones obligatorias: `@Entity`, `@Table(name = "nombre_tabla")`, `@Data`, `@Builder`, `@NoArgsConstructor`, `@AllArgsConstructor`
- PK: `@Id @GeneratedValue(strategy = GenerationType.IDENTITY)`
- FK: `@ManyToOne @JoinColumn(name = "[columna]_id")`
- Validaciones: `@NotNull`, `@NotBlank`, `@Size`, según diseño
- Usar `java.time.LocalDateTime` para fechas

### Reglas anti-errores (IMPORTANTE)

- **Columna PK:** por defecto mapear a `id` (sin sufijo). Si el SQL usa otro nombre, añadir `@Column(name = "...")` en el campo `id` o renombrar el campo para que sea consistente.
- **Auditoría:** si las migraciones solo crean `created_at`/`updated_at`, las entities no deben declarar `createdBy/updatedBy`.

## Modo: Repositories

Genera interfaces JPA Repository con métodos derivados y queries custom.

### Salida

- Interfaces en `backend/src/main/java/com/nttdata/backend/[modulo]/repository/*.java`

### Convenciones

- Extender `JpaRepository<Entity, Long>`
- Métodos derivados para búsquedas: `findBy[Campo]`, `findBy[Campo1]And[Campo2]`
- Queries custom con `@Query` cuando sea necesario
- Usar `@EntityGraph` para evitar N+1

## Modo: DTOs

Genera DTOs (Request/Response/Filters) con Lombok y validaciones.

### Salida

- DTOs en `backend/src/main/java/com/nttdata/backend/[modulo]/dto/*.java`

### Convenciones

- **Request DTOs**: validaciones `@NotNull`, `@NotBlank`, `@Size`
- **Response DTOs**: sin validaciones, solo Lombok
- **Filter DTOs**: campos opcionales para búsqueda/paginación
- Usar `@Data`, `@Builder`, `@NoArgsConstructor`, `@AllArgsConstructor`

## Modo: Services

Genera Services con lógica de negocio, transacciones, logging y manejo de errores.

### Salida

- Services en `backend/src/main/java/com/nttdata/backend/[modulo]/service/*.java`

### Convenciones

- Anotaciones: `@Service`, `@Slf4j`, `@Transactional` (cuando modifica datos)
- Inyección de dependencias por constructor
- Métodos deben mapear Entity ↔ DTO
- Logging en puntos críticos: inicio, errores, operaciones de negocio
- Validaciones de negocio: lanzar `BusinessException` (template) si inválido
- No encontrado: lanzar `ResourceNotFoundException` (template)

## Modo: Controllers

Genera Controllers REST con OpenAPI, seguridad, paginación y validación desde la especificación de servicios.

### Entrada

- `design/03_data_services.md` - Especificación de endpoints REST

### Salida

- Controllers en `backend/src/main/java/com/nttdata/backend/[modulo]/controller/*.java`

### Convenciones

- Anotaciones: `@RestController`, `@RequestMapping("/[moduleSlug]")`, `@Slf4j`
- Nota: el prefijo `/api` lo aporta `server.servlet.context-path=/api` (no duplicar).
- Seguridad: `@PreAuthorize("hasRole('[ROLE]')")` según diseño
- Validación: `@Valid` en Request DTOs
- Paginación: usar `Pageable` y `Page<T>` para listados
- Respuestas HTTP: **usar wrapper estándar** `ResponseEntity<ApiResponse<T>>` (o `ApiResponse<Void>`), con códigos adecuados (200, 201, 204, 400, 404, 500)
- OpenAPI: `@Operation`, `@ApiResponse` para documentación

## Instrucciones de Ejecución

1. Leer backlog del módulo (ej: `backlog/02_maestro_posiciones.md`)
2. Extraer nombre del módulo y entidades
3. Invocar skill en orden: migrations → entities → repositories → dtos → services → controllers
4. Validar: `mvn clean compile`

## Convenciones de Código

### Nomenclatura
- **Clases:** PascalCase (ej: `PosicionService`, `PosicionController`)
- **Atributos:** camelCase (ej: `posicionId`, `empleadoNombre`)
- **Tablas DB:** snake_case (ej: `posiciones`, `historico_sincronizacion_posiciones`)
- **Columnas DB:** snake_case (ej: `posicion_id`, `empleado_nombre`)

### Anotaciones
- **Lombok:** `@Data`, `@Builder`, `@NoArgsConstructor`, `@AllArgsConstructor` en DTOs
- **JPA:** `@Entity`, `@Table`, `@Id`, `@GeneratedValue`, `@Column` en entities
- **Validation:** `@NotNull`, `@NotBlank`, `@Size`, `@Min`, `@Max` en DTOs y entities
- **Spring:** `@Service`, `@Repository`, `@RestController`, `@Transactional`
- **Security:** `@PreAuthorize("hasRole('...')")` en controllers

### Logging
- Usar `@Slf4j` de Lombok
- Niveles:
  - `log.error()` para excepciones
  - `log.warn()` para situaciones anómalas
  - `log.info()` para flujos principales
  - `log.debug()` para detalles técnicos

### Excepciones
- Usar las excepciones estándar del template:
  - `BusinessException` para reglas/validaciones de negocio
  - `ResourceNotFoundException` cuando no existe un recurso
  - `UnauthorizedException` si aplica
- Evitar `IllegalArgumentException` como mecanismo principal (puede degradar a 500 si no está mapeada explícitamente)

### Wrapper de respuestas

- Usar `com.nttdata.backend.common.dto.ApiResponse<T>` como contrato estándar.
- Para errores, confiar en `GlobalExceptionHandler` (`ErrorResponse`).


## Restricciones

- NO generar código en módulos existentes sin instrucción explícita de actualización
- NO modificar archivos de configuración global (`application.yml`, `SecurityConfig.java`) sin validación
- NO generar migraciones con versiones duplicadas (verificar última versión existente)
- NO incluir lógica de negocio en controllers (delegar a services)
- NO usar queries N+1 (usar `@EntityGraph` o fetch joins cuando sea necesario)

## Prohibiciones

- NUNCA generar código si no existe `backlog/XX_[modulo].md` o si no contiene las secciones requeridas.
- NUNCA asumir diseño si falta: si `design/02` y/o `design/03` no existen, usar exclusivamente el backlog como fuente.
- NUNCA usar tipos Java antiguos (`Date`, `Calendar`) → usar `java.time.*`
- NUNCA exponer entities directamente en controllers → usar DTOs
- NUNCA hardcodear valores de configuración → usar `@Value` o `application.yml`
- NUNCA ignorar excepciones (log y propagar o manejar apropiadamente)

## Criterio de Finalización

El modo se considera **COMPLETADO** cuando:

✅ Todos los archivos generados compilan sin errores (`mvn compile`)  
✅ Migraciones Flyway son válidas (sintaxis SQL correcta)  
✅ Código sigue convenciones de nomenclatura y anotaciones  
✅ Logging implementado en puntos críticos

## Salida Esperada del Skill

Al finalizar cada modo, el skill debe reportar:

### Modo: migrations
```
✅ Migraciones generadas: N archivos SQL en backend/src/main/resources/db/migration/
  - VXX__{moduleKey}_create_enums.sql (creación de enums)
  - VXX__{moduleKey}_create_{tabla}.sql (creación de tablas)
  - VXX__{moduleKey}_seed_data.sql (datos iniciales, opcional)
```

### Modo: entities
```
✅ Entities generadas: N clases en backend/src/main/java/com/nttdata/backend/[modulePackage]/model/
   - [Entity].java (una por entidad del diseño)
```

### Modo: repositories
```
✅ Repositories generadas: N interfaces en backend/src/main/java/com/nttdata/backend/[modulePackage]/repository/
   - [Entity]Repository.java (una por entity)
```

### Modo: dtos
```
✅ DTOs generados: N clases en backend/src/main/java/com/nttdata/backend/[modulePackage]/dto/
   - [Entity]Response.java
   - [Entity]Request.java
   - [Entity]FiltersRequest.java (para búsquedas)
```

### Modo: services
```
✅ Services generados: N clases en backend/src/main/java/com/nttdata/backend/[modulePackage]/service/
   - [Entity]Service.java (una por entity principal)
```

### Modo: controllers
```
✅ Controllers generados: N clases en backend/src/main/java/com/nttdata/backend/[modulo]/controller/
   - [Entity]Controller.java (una por entity principal)
```

### Modo: all
```
✅ Generación completa del módulo [modulo]:
   ✅ N migraciones SQL
   ✅ N entities
   ✅ N repositories
   ✅ N DTOs
   ✅ N services
   ✅ N controllers
   ✅ Compilación exitosa: mvn clean compile
```
