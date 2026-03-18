---
name: backend-test-generator
description: Genera tests backend Java Spring Boot por capas (unit/service con Mockito, controller tests con PostgresTestContainer+MockMvc, security 401/403/JWT con @SpringBootTest, e integración con Testcontainers+Flyway). Úsalo en la fase de tests backend o para corregir fallos típicos (Flyway checksum, ApplicationContext, 401/403).
---

# Backend Test Generator

Generar tests backend siguiendo una estrategia por capas para minimizar flakiness y reducir acoplamiento.

## Principio clave (OBLIGATORIO)

Separar los tests por intención:

1. **Unit (Service)**: lógica de negocio pura (Mockito). Sin Spring.
2. **Controller contract (MockMvc + PostgresTestContainer)**: contrato HTTP (status/JSON/validaciones/query params) con stack real (Spring + Security) y BD Postgres efímera.
3. **Security**: 401/403, roles y autenticación JWT. Spring completo (sin BD si no aporta valor).
4. **Integration (DB)**: repositorios + migraciones + persistencia real (Testcontainers + Flyway).

No mezclar (ej: `@SpringBootTest` + mocks + excluir Flyway/JPA para todos los tests) salvo como fallback puntual.

## Modos

- `unit`: genera solo tests unitarios (services) con Mockito.
- `controller`: genera solo controller contract tests usando `PostgresTestContainer`.
- `security`: genera solo tests de seguridad (401/403/JWT).
- `integration`: genera solo tests de integración con Testcontainers.
- `all`: genera todo lo anterior.

## Entradas esperadas

- `backlog/XX_[modulo].md` (fuente principal)
- Código ya generado/implementado:
  - Controllers en `backend/src/main/java/com/nttdata/backend/[modulePackage]/controller/`
  - Services en `backend/src/main/java/com/nttdata/backend/[modulePackage]/service/`
  - Security config en `backend/src/main/java/com/nttdata/backend/config/` y/o `.../[modulePackage]/security/`

## Salidas

- Unit: `backend/src/test/java/com/nttdata/backend/[modulePackage]/service/*Test.java`
- Controller: `backend/src/test/java/com/nttdata/backend/[modulePackage]/controller/*ControllerTest.java`
- Security: `backend/src/test/java/com/nttdata/backend/[modulePackage]/security/*Test.java`
- Integration: `backend/src/test/java/com/nttdata/backend/[modulePackage]/integration/*IntegrationTest.java`

## Reglas de generación (anti-errores)

### A) Context path `/api` (CRÍTICO)

Si el proyecto usa `server.servlet.context-path=/api`, en MockMvc:

- Usar ruta externa con prefijo `/api`.
- Y además setear `.contextPath("/api")`.

Ejemplo: `get("/api/auth/me").contextPath("/api")`.

### B) Controller contract tests (OBLIGATORIO: PostgresTestContainer)

En este proyecto, los tests de controller deben usar PostgresTestContainer (patrón existente en el repo, por ejemplo `.../user/controller/UserControllerTest.java`).

Plantilla recomendada:

- `@SpringBootTest`
- `@AutoConfigureMockMvc`
- `@ActiveProfiles("test")`
- `@Transactional` (si se crean datos)
- `extends PostgresTestContainer`
- `@DynamicPropertySource` llamando a `registerProperties(registry)`
- Autenticación/roles con `@WithMockUser(...)` cuando aplique

Objetivo: validar contrato HTTP real (status/JSON/validaciones), con filtros de seguridad activos y BD efímera.

### C) Security tests

Usar `@SpringBootTest` + `@AutoConfigureMockMvc` (filtros activos) para validar:

- 401 sin JWT en endpoints protegidos
- 403 cuando autenticado sin rol

**Nota 401 vs 403:**
- Endpoints con `@PreAuthorize`: sin autenticación suelen devolver 403 (AccessDenied) según configuración.
- Endpoints protegidos por `.authenticated()`: sin autenticación suelen devolver 401.

### D) Integration tests (DB)

Usar Testcontainers para Postgres y Flyway activo.

- Objetivo: validar migraciones + repositorios + persistencia real.
- Evitar asserts frágiles sobre callbacks JPA (timestamps) si no son requisito de negocio.
- Si se validan callbacks: usar `saveAndFlush()` y re-consultar (`findById`).

### E) Paginación

Si se construye `PageImpl` en unit tests:

- `content`: sublista de la página solicitada
- `totalElements`: total global

Asserts recomendados:
- `getTotalElements()` == total global
- `getNumberOfElements()` == `content.size()`
- `getNumber()` == page

## Fallback: perfil `test-no-flyway`

Solo usarlo si el contexto de seguridad/JWT o beans del proyecto hacen el test frágil y el test NO necesita BD:

- `@ActiveProfiles("test-no-flyway")`
- `backend/src/test/resources/application-test-no-flyway.yml` excluyendo DataSource/JPA/Flyway

## Checklist de calidad (antes de finalizar)

- Tests compilan.
- Controller slice tests no requieren BD.
- Security tests cubren 401 y 403 según configuración real.
- Integration tests usan Testcontainers y pasan en limpio.

## Ejecución sugerida

- `mvn -q -Dtest="*ServiceTest" test`
- `mvn -q -Dtest="*ControllerTest" test`
- `mvn -q -Dtest="*Security*Test" test`
- `mvn -q -Dtest="*IntegrationTest" test`

Opcional (solo tests de un módulo por paquete, si aplica):
- `mvn -q -Dtest="com/nttdata/backend/[modulePackage]/**/*Test,com/nttdata/backend/[modulePackage]/**/*IntegrationTest" test`
