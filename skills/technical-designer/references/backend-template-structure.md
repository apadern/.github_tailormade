# Estructura Base del Backend (Spring Boot)

Esta referencia define la **plantilla de estructura** y convenciones mínimas para el backend Java del MVP.

## Árbol de Directorios (Backend)

```
backend/
├── pom.xml
├── docker-compose.yml
└── src/
  ├── main/
  │   ├── java/
  │   │   └── com/nttdata/backend/
  │   │       ├── BackendApplication.java
  │   │       ├── config/                      # Configuración (Security, OpenAPI, CORS)
  │   │       │   ├── CorsConfig.java
  │   │       │   ├── OpenAPIConfig.java
  │   │       │   └── SecurityConfig.java
  │   │       ├── security/                    # Security/JWT + UserDetails
  │   │       │   ├── jwt/
  │   │       │   │   ├── JwtAuthenticationEntryPoint.java
  │   │       │   │   ├── JwtAuthenticationFilter.java
  │   │       │   │   └── JwtTokenProvider.java
  │   │       │   ├── SecurityUser.java
  │   │       │   └── UserDetailsServiceImpl.java
  │   │       ├── common/                      # DTOs compartidos + manejo de errores
  │   │       │   ├── dto/
  │   │       │   │   ├── ApiResponse.java
  │   │       │   │   ├── ErrorResponse.java
  │   │       │   │   └── PageResponse.java
  │   │       │   └── exception/
  │   │       │       ├── BusinessException.java
  │   │       │       ├── GlobalExceptionHandler.java
  │   │       │       ├── ResourceNotFoundException.java
  │   │       │       └── UnauthorizedException.java
  │   │       ├── auth/                        # Módulo auth
  │   │       │   ├── controller/AuthController.java
  │   │       │   ├── dto/                     # LoginRequest/LoginResponse/RegisterRequest
  │   │       │   └── service/AuthService.java
  │   │       ├── user/                        # Módulo administración de usuarios/roles/permisos
  │   │       │   ├── controller/              # UserController/RoleController/PermissionController
  │   │       │   ├── dto/                     # requests + DTOs
  │   │       │   ├── model/                   # entidades JPA (User/Role/Permission)
  │   │       │   ├── repository/              # repositorios Spring Data
  │   │       │   └── service/                 # lógica de negocio
  │   │       └── audit/                       # Módulo de auditoría (AOP + Log)
  │   │           ├── aspect/AuditAspect.java  # Interceptor de auditoría
  │   │           ├── controller/AuditLogController.java
  │   │           ├── dto/                     # AuditLogResponse/ChangeDetailDTO
  │   │           ├── model/AuditLog.java      # Entidad de persistencia de logs
  │   │           ├── repository/AuditLogRepository.java
  │   │           └── service/AuditLogService.java
  │   └── resources/
  │       ├── application.yml
  │       ├── application-dev.yml
  │       ├── application-prod.yml
  │       └── db/migration/                    # Flyway (V1__*.sql, V2__*.sql, ...)
  └── test/
    ├── java/
    │   └── com/nttdata/backend/
    │       ├── BackendApplicationTests.java
    │       ├── integration/PostgresTestContainer.java
    │       ├── auth/controller/AuthControllerTest.java
    │       ├── user/
    │       │   ├── controller/              # RoleControllerTest/UserControllerTest
    │       │   ├── security/                # UserControllerSecurityTest
    │       │   └── service/                 # RoleServiceTest/UserServiceTest
    │       └── audit/
    │           ├── controller/AuditLogControllerTest.java
    │           ├── service/AuditLogServiceTest.java
    │           └── integration/AuditIntegrationTest.java
    └── resources/
      └── application-test.yml
```

## Capas (alto nivel)

- **Web (controller)**: Controllers REST, validación de entrada, códigos HTTP, anotaciones OpenAPI.
- **Service**: orquestación/casos de uso y reglas de negocio.
- **Repository**: persistencia con Spring Data JPA.
- **Model**: entidades JPA.
- **Security**: Spring Security + JWT + method security (`@PreAuthorize`).
- **Common**: envelopes de respuesta y manejo centralizado de excepciones.

## Convenciones

- **Base path API**: `/api` vía `server.servlet.context-path` (ver `application.yml`).
  - Ejemplo: `@RequestMapping("/auth")` expone endpoints como `/api/auth/**`.
- **Documentación**: OpenAPI/Swagger habilitado.
- **Seguridad**: Spring Security con JWT y autorización por roles (p.ej. `ROLE_ADMIN`).
- **Migraciones**: Flyway en `src/main/resources/db/migration`.
- **Modelo de error**: consistente (p.ej. `ProblemDetail` o envelope `{ success, message, data }`).

## Reglas de consistencia (diseño)

- Un **módulo funcional** (del análisis) debe corresponder a:
  - una carpeta de frontend en `frontend/src/modules/[module]` y
  - un paquete backend (preferente) en `backend/src/main/java/.../[module]` (o equivalente si el repo ya está creado).
- Evitar endpoints sueltos sin módulo; si aparece un transversal (auth, catálogos), declararlo como tal en el diseño.
