# CAP Testing Guardrails

Usar esta referencia cuando haya que decidir como probar handlers, servicios, seguridad, datos o integraciones en SAP CAP sin introducir flakiness ni falsas garantias.

## 1. Unit tests

- Probar logica de negocio aislada sin levantar CAP completo si no hace falta.
- Mockear dependencias externas y acceso a datos cuando el objetivo sea una funcion o handler concreto.
- Limpiar mocks y estado global entre tests.
- Verificar `req.reject(...)`, transformaciones y ramas de error.
- Elegir `jest` o `mocha` segun el runner dominante del proyecto. La documentacion CAP no impone un runner unico para unit tests puros.
- Si el proyecto no define runner, usar `jest` como default para minimizar curva de entrada.

No hacer:

- No usar runtime completo para una validacion puramente local.
- No dejar `cds.model`, mocks o stubs compartidos entre casos.

## 2. Service contract tests

- Preferir `@cap-js/cds-test` para levantar el servicio y usar helpers HTTP.
- Tratar `@cap-js/cds-test` como la referencia documental principal cuando el test necesita runtime CAP real.
- Si no hay convencion previa de runner, envolver estas suites en `jest` y usar `@cap-js/cds-test` como helper CAP.
- Probar rutas OData o endpoints reales del servicio.
- Validar status, payload y efectos observables.
- Cubrir query options, acciones y functions cuando existan.

No hacer:

- No simular respuestas HTTP a mano si el runtime CAP puede responder de verdad.
- No asumir formato o metadata sin probarla.

## 3. Security tests

- Probar usuarios anonimos, usuarios con rol insuficiente y usuarios con rol correcto.
- Ajustar asserts 401 o 403 a la configuracion real del proyecto.
- Cubrir `@requires`, `@restrict` y chequeos manuales con `req.user`.
- Reutilizar usuarios mock del proyecto o generarlos de forma explicita en test.

No hacer:

- No probar solo el caso exitoso de seguridad.
- No hardcodear roles que el modelo no define.

## 4. Data tests

- Validar que los CSV cargan con cabeceras correctas y datos compatibles con el modelo.
- Cubrir estados, filtros y relaciones minimas.
- Separar datos de desarrollo y datos de test si el proyecto distingue perfiles.

No hacer:

- No usar fixtures que violen constraints del modelo por descuido.
- No asumir que `db/data` y `test/data` se comportan igual en todos los perfiles.

## 5. Integration tests

- Usar runtime CAP real y persistencia real del perfil de test.
- Resetear o reconstruir datos cuando el estado afecte al resultado.
- Verificar efectos persistentes tras escrituras.
- Mantener las pruebas de integracion enfocadas en flujos reales, no en detalles internos de implementacion.

No hacer:

- No mezclar demasiadas responsabilidades en una sola prueba gigante.
- No confiar solo en status codes si hay mutacion de datos.

## 6. Validacion final

Comprobar como minimo:

- compilacion del proyecto de tests
- arranque del runtime CAP en test
- carga correcta de fixtures relevantes
- cobertura de seguridad y casos de error clave
- limpieza o aislamiento razonable entre casos

Si algo no puede ejecutarse, dejarlo documentado de forma explicita.