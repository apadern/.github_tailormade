---
name: requirements-synthesizer
description: Sintetiza requisitos funcionales (RFs), actores, alcance y requisitos técnicos a partir de documentos de extracción bruta (requisitos.md, imagenes.md). Usar cuando se necesite generar las secciones 1-4 de un análisis funcional.
---

# Requirements Synthesizer

Sintetiza y estructura requisitos a partir de datos brutos extraídos.

## Modos

| Modo | Secciones a generar |
|------|--------------------|
| **Completo** | 1, 2, 3, 4 |
| **Prototipo** | 1, 2, 3 (omitir sección 4) |

## Flujo de Trabajo

1. Leer `requisitos.md` e `imagenes.md` del directorio raíz
2. Analizar TODOS los RFs, RBs, DCs, INTs e imágenes (contar totales)
3. Generar secciones en orden, guardando cada una en `analisis/`
4. En modo prototipo, omitir sección 4
5. Actualizar `analisis/debug.md` con conteos por sección

## Sección 1: Objetivo y Alcance

Analizar RFs y DCs de alto nivel para derivar:

```markdown
## 1. Objetivo y Alcance

### 1.1 Objetivo general
<uno o dos párrafos breves>

### 1.2 Alcance del sistema
<lista de viñetas con funcionalidades, módulos y procesos>

### 1.3 Límites del sistema (Fuera de Alcance)
<lista de viñetas con exclusiones e interacciones externas>
```

Guardar como: `analisis/01_objetivo_y_alcance.md`

## Sección 2: Actores y Roles

Identificar actores (humanos y sistemas) de los requisitos e imágenes:

```markdown
## 2. Actores y Roles

| Actor / Rol | Descripción | Permisos / Responsabilidades |
| :---------- | :---------- | :--------------------------- |
<filas>
```

Guardar como: `analisis/02_actores_y_roles.md`

## Sección 3: Requerimientos Funcionales

**NO copiar** RFs de `requisitos.md`. **Sintetizar** nuevos RFs formales agrupados por módulo:

```markdown
## 3. Requerimientos Funcionales

### 3.x Módulo: <Nombre>
| ID | Requerimiento | Descripción |
| :-- | :-- | :-- |
<filas>
```

- Usar IDs consecutivos: RF-001, RF-002...
- Documentar módulos identificados en `debug.md`
- Guardar como: `analisis/03_requerimientos_funcionales.md`

## Sección 4: Requerimientos Técnicos

Derivar de RFs e integraciones. Mantener estructura concisa y enfocada:

```markdown
## 4. Requerimientos Técnicos

### 4.1 Infraestructura

Servidor o hosting requerido, sistema operativo, base de datos y entorno de ejecución.

### 4.2 Software

Frameworks y librerías principales, compatibilidad con navegadores, dependencias externas.

### 4.3 Seguridad

Autenticación, cifrado de datos y cumplimiento normativo.

### 4.4 Rendimiento

Tiempos de respuesta, concurrencia esperada y disponibilidad mínima (SLA).
```

**IMPORTANTE**: Mantener contenido breve y relevante. NO expandir con subsecciones adicionales (4.5, 4.6, 4.7, 4.8...). Solo incluir información derivada explícitamente de los documentos fuente.

Guardar como: `analisis/04_requerimientos_tecnicos.md`

## Reglas

- Nunca resumir ni simplificar contenido
- Si excede 35000 caracteres, dividir en partes y consolidar con PowerShell
- Todo contenido debe derivar de los documentos fuente
- Actualizar `debug.md` tras cada sección
