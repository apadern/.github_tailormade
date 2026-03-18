## Bitácora de errores (OBLIGATORIO)
Objetivo: capturar soluciones reutilizables a fallos recurrentes (tests, build, runtime, Flyway/Testcontainers, Spring Context, OpenAPI, E2E, lint).

Archivo: `bitacora_errores.md`.

Reglas:
1) Antes de corregir, busca si ya existe una entrada equivalente:
	 - **Backend**: Maven/Spring/Flyway/Testcontainers/OpenAPI
	 - **Frontend**: Playwright/Vite/lint/build/servicios/API
2) Si es un error conocido registra en la bitacora que se utilizo para corregir el problema, incrementando en 1 el valor de `Errores similares` 
3) Si es un error nuevo y queda resuelto, registra una entrada breve en el bloque correcto.
4) Prioriza la reutilización: sin narrativa, solo lo necesario para repetir la solución.

Plantilla (pegar tal cual):
```
- Contexto: ...
	Error: ...
	Causa: ...
	Solución: ...
	Verificación: ...
	Errores similares: 0
```
