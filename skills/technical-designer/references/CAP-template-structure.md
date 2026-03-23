# Estructura Base del Backend (SAP CAP Node.js)

Esta referencia define la **plantilla de estructura** y convenciones mínimas para el backend SAP CAP del MVP con foco enterprise.

La referencia es **completa por diseño**: incluye módulos base y módulos opcionales que deben contemplarse cuando el alcance lo requiera. No todos los proyectos CAP necesitan todas las carpetas o capacidades del árbol.

## Árbol de Directorios (Backend CAP)

```
backend/
├── package.json
├── .cdsrc.json                       # Configuración CAP por perfiles (alternativa: .cdsrc.yaml)
├── .env                              # Variables locales/no sensibles por perfil (opcional)
├── xs-security.json                  # Scopes/roles para despliegues en SAP BTP cuando aplique
├── mta.yaml                          # Descriptor de despliegue en SAP BTP (opcional)
├── eslint.config.mjs                 # Linting (opcional pero recomendado)
├── docs/                             # OpenAPI exportado, ADRs y documentación operativa (opcional)
│   ├── openapi/
│   └── adr/
├── scripts/                          # Automatizaciones de build, seed, smoke checks (opcional)
│   └── ...
├── db/
│   ├── schema.cds                    # Modelo raíz o agregador de imports
│   ├── common/                       # Tipos, aspects y catálogos reutilizables
│   │   ├── types.cds
│   │   └── code-lists.cds
│   ├── modules/                      # Modelo por módulo funcional
│   │   ├── auth.cds
│   │   ├── users.cds
│   │   └── audit.cds
│   ├── integration/                  # Definiciones para servicios remotos, eventos o replicación (opcional)
│   │   ├── s4.cds
│   │   └── external-events.cds
│   └── data/                         # Datos iniciales CSV por entidad
│       ├── sap.common-Currencies.csv
│       └── my.app-Users.csv
├── srv/
│   ├── common/
│   │   ├── annotations.cds          # Anotaciones técnicas/UI y restricciones transversales
│   │   └── authorization.cds        # @requires/@restrict separados del contrato principal
│   ├── auth/
│   │   ├── auth-service.cds         # Servicio expuesto (@path, projections, actions/functions)
│   │   └── auth-service.js          # before/on/after hooks y orquestación
│   ├── user/
│   │   ├── user-service.cds
│   │   └── user-service.js
│   ├── audit/
│   │   ├── audit-service.cds
│   │   └── audit-service.js
│   ├── integration/                  # Conectores a destinos/servicios remotos (opcional)
│   │   ├── remote-services.cds
│   │   └── remote-services.js
│   ├── messaging/                    # Eventos de dominio, suscripciones y publicación (opcional)
│   │   ├── messaging-service.cds
│   │   └── messaging-service.js
│   ├── jobs/                         # Procesos batch, reconciliaciones y tareas programadas (opcional)
│   │   └── scheduled-jobs.js
│   ├── health/                       # Health/readiness checks específicos de negocio (opcional)
│   │   └── health-service.js
│   ├── plugins/                      # Plugins o extensiones cross-cutting del runtime (opcional)
│   │   └── ...
│   └── server.js                    # Bootstrap/custom middleware solo si es necesario
├── app/                              # Opcional: anotaciones UI o aplicaciones servidas por CAP
│   └── ...
├── approuter/                        # Opcional: SAP Application Router para BTP/full-stack
│   ├── package.json
│   └── xs-app.json
├── test/
│   ├── integration/
│   │   ├── auth-service.test.js
│   │   ├── user-service.test.js
│   │   └── http-api.test.js
│   ├── security/
│   │   └── authorization.test.js
│   ├── messaging/                    # Validación de eventos, outbox y colas (opcional)
│   │   └── messaging.test.js
│   ├── jobs/                         # Validación de procesos batch o scheduling (opcional)
│   │   └── jobs.test.js
│   ├── contract/                     # Tests de contrato/OpenAPI/OData metadata (opcional)
│   │   └── metadata.test.js
│   ├── data/                        # Datos específicos de test cargables por perfil
│   │   └── my.app-Users.csv
│   └── helpers/
│       └── test-users.js
└── mtx/
    └── sidecar/                     # Opcional: multitenancy, extensibility y feature toggles
        ├── package.json
        ├── .cdsrc.json
        └── server.js
```

## Módulos y Capacidades Opcionales

- **Siempre esperables en cualquier CAP**: `package.json`, `db/`, `srv/`, `test/` y configuración CAP (`.cdsrc.json` o equivalente).
- **Comunes en proyectos productivos**: `xs-security.json`, `docs/`, `app/`, `approuter/`, `srv/audit/`, `srv/health/`.
- **Necesarios solo si el alcance lo exige**:
  - `srv/integration/` y `db/integration/` para destinos SAP/BTP, APIs externas o réplicas.
  - `srv/messaging/` y `test/messaging/` para eventos, Event Mesh, colas o integración asíncrona.
  - `srv/jobs/` y `test/jobs/` para lotes, reconciliaciones o procesos diferidos.
  - `mtx/sidecar/` para multitenancy, extensibilidad por tenant y feature toggles.
  - `approuter/` para despliegues BTP con enrutado centralizado y autenticación unificada.
- **No convertir en obligatorios módulos opcionales**: si un proyecto no tiene integración, mensajería, jobs o MTX, la estructura puede omitirse sin salirse del estándar.

## Capas (alto nivel)

- **Model (db)**: modelos CDS, aspects reutilizables, catálogos y validaciones declarativas (`@mandatory`, `@assert`, `cuid`, `managed`).
- **Service Definition (srv/*.cds)**: proyecciones, acciones, funciones y eventos expuestos; define `@path`, protocolos y restricciones declarativas.
- **Service Implementation (srv/*.js)**: lógica de negocio y orquestación mediante `cds.ApplicationService` y handlers `before/on/after`.
- **Persistence & Integration**: acceso a datos e integraciones mediante CQL/CQN, `srv.run(...)` y `cds.connect.to(...)`; CAP no usa repositorios manuales como capa obligatoria.
- **Security & Cross-Cutting**: autenticación configurable, autorización en CDS, audit logging, outbox, mensajería, health checks y observabilidad.
- **Testing**: pruebas de servicio, HTTP, seguridad, contrato, jobs y eventos con `@cap-js/cds-test`, perfiles de datos y base local/in-memory para validar comportamiento funcional y de seguridad.

## Convenciones

- **Base path API**: CAP expone servicios por protocolo, normalmente en rutas como `/odata/v4/<service>` y `/rest/<service>` cuando REST está habilitado.
  - Usar `@path` para definir rutas estables y legibles por consumidor; evitar hardcodear rutas HTTP dentro de handlers.
- **Documentación**: el contrato fuente vive en CDS y `/$metadata` se genera automáticamente.
  - Si se requiere OpenAPI, generarlo explícitamente con `cds compile srv --service all -o docs --to openapi`; Swagger UI solo debe habilitarse de forma explícita.
- **Seguridad**: configurar autenticación en `cds.requires.auth` y autorización declarativa con `@requires` y `@restrict`.
  - Los endpoints públicos deben declararse de forma explícita, por ejemplo con `@requires: 'any'`.
- **Integraciones remotas**: centralizar los contratos externos y destinos en módulos de integración separados.
  - Evitar mezclar handlers de dominio con conectividad a S/4, SAP Graph, SuccessFactors o APIs terceras si esa conectividad no pertenece al dominio principal.
- **Mensajería y outbox**: si existe integración asíncrona, tratarla como capacidad de primer nivel y no como código auxiliar disperso.
  - Mantener eventos, consumidores y configuración de canales en módulos dedicados; habilitar persistent outbox cuando haya garantías de entrega o audit logging.
- **Persistencia**: el modelo es **model-first** en `db/*.cds`; los datos iniciales viven en `db/data` y, cuando aplique, en `test/data` por perfil.
  - Evitar migraciones SQL manuales como patrón por defecto; priorizar `cds build`, `cds deploy` y las capacidades del adaptador de base de datos (SQLite/PostgreSQL/HANA).
- **Modelo de error**: reutilizar la estructura estándar de errores CAP/OData y usar `req.reject(...)` para errores funcionales.
  - Evitar envelopes HTTP propios que rompan la semántica del protocolo expuesto.
- **Configuración por entorno**: centralizar perfiles en `.cdsrc.json` o en la sección `cds` de `package.json`.
  - En desarrollo, priorizar SQLite y autenticación mock; en productivo, PostgreSQL/HANA, IAS/XSUAA y outbox/audit si están en alcance.
- **Observabilidad**: mantener logging estructurado y habilitar persistent outbox para mensajería y audit logging cuando el caso de uso lo requiera.
  - Reservar `srv/server.js` para bootstrap y middleware transversal; no usarlo como contenedor de lógica de negocio por módulo.
- **Operación y despliegue**: `docs/`, `scripts/`, `approuter/` y `mtx/` forman parte de la referencia, pero se materializan solo cuando hay exigencias operativas, SaaS o despliegue BTP.
  - La referencia debe cubrirlos para diseño, aunque el repositorio concreto no los implemente todos.

## Reglas de consistencia (diseño)

- Un **módulo funcional** (del análisis) debe corresponder a:
  - una carpeta de frontend en `frontend/src/modules/[module]` y
  - uno o varios modelos en `backend/db/modules/[module].cds` (o equivalente si el repo ya está creado) y
  - un servicio CAP en `backend/srv/[module]/[module]-service.cds` con su implementación `backend/srv/[module]/[module]-service.js`.
- Evitar exponer entidades de persistencia directamente desde `db/`; la API pública debe quedar definida en `srv/` mediante proyecciones y contratos explícitos.
- Evitar servicios o handlers sueltos sin módulo; si aparece un transversal (auth, catálogos, auditoría), declararlo como tal y mantenerlo separado del dominio funcional.
- Separar, cuando el módulo crezca, el contrato de servicio y la seguridad en ficheros distintos (`*-service.cds` y `authorization.cds` o `*-auth.cds`).
- Mantener la lógica de negocio dentro de handlers y servicios CAP; evitar trasladarla a `server.js`, middleware ad hoc o llamadas HTTP locales entre servicios del mismo proceso.
- Si existe una capacidad opcional relevante para el alcance (integraciones, mensajería, jobs, MTX, approuter, health checks), debe aparecer explícitamente en el diseño aunque luego se marque como `Opcional / No aplica` para ese proyecto.
- Si una capacidad no aplica, omitir su implementación física es válido; omitirla del análisis de arquitectura no lo es.
- Si existen composiciones o entidades auto-expuestas navegables, revisar autorización en el root expuesto para no abrir accesos implícitos no deseados.
- No incluir artefactos generados (`gen/`, `node_modules/`) en la estructura de referencia; la plantilla debe reflejar solo código fuente y configuración mantenible.