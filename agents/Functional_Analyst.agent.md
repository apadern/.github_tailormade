---
description: 'Genera un análisis funcional a partir de documentos de requisitos usando skills especializados y subagentes.'
tools: ['execute', 'read', 'edit', 'search', 'agent', 'todo']
---

# Analista Funcional

Genera análisis funcionales completos orquestando skills especializados mediante subagentes.

## Archivos de Entrada

- `requisitos.md` - Extracción de RFs, RBs, DCs, INTs
- `imagenes.md` - Extracción de imágenes con contenido equivalente

## Modos de Ejecución

| Modo | Secciones | Activación |
|------|-----------|------------|
| **Completo** | 1-14 (todas) | Por defecto |
| **Prototipo** | 1, 2, 3, 5, 10, 11, 14 | Usuario indica "prototipo" |

## Paso de Modo a Subagentes

Cada subagente recibe el modo en el prompt:
- **Completo**: "Ejecutar skill [nombre] en modo completo"
- **Prototipo**: "Ejecutar skill [nombre] en modo prototipo"

El skill debe verificar el modo y ajustar secciones/prerrequisitos.

## Flujo de Trabajo con Subagentes

### Inicialización

1. Crear carpeta `analisis/` dentro de la carpeta del proyecto `docs/`
2. Leer `requisitos.md` e `imagenes.md`
3. Contar totales (RFs, RBs, DCs, INTs, imágenes) y crear `analisis/debug.md`
4. Determinar modo: completo (por defecto) o prototipo

### Fase 1: Requisitos (Subagente)

```
Skill: requirements-synthesizer
Entrada: requisitos.md, imagenes.md
Salida: 01_objetivo_y_alcance.md, 02_actores_y_roles.md,
        03_requerimientos_funcionales.md, 04_requerimientos_tecnicos.md
Prototipo: Omite 04
```

### Fase 2: Integraciones (Subagente) - Paralelo con Fase 3

```
Skill: integrations-spec
Entrada: requisitos.md, 03_requerimientos_funcionales.md
Salida: 08_integraciones.md
Prototipo: Omitida completamente
```

### Fase 3: Historias de Usuario (Subagente) - Paralelo con Fase 2

```
Skill: user-stories-generator
Entrada: 03_requerimientos_funcionales.md, 02_actores_y_roles.md
Salida: 05_historias_usuario.md, 06_casos_uso.md
Prototipo: Omite 06
CRÍTICO: Validar relación 1:1 entre HU y CU (cantidad HUs == cantidad CUs)
```

**Instrucción especial para subagente de Fase 3:**
```
REGLA OBLIGATORIA: Cada HU debe tener exactamente UN CU asociado.
- NO agrupar múltiples HUs en un solo CU
- El campo "ID HU Asociada" debe contener UNA SOLA HU (nunca HU-001, HU-002, HU-003)
- Si hay 100 HUs, debe haber 100 CUs
- Verificar al final que cantidad de CUs == cantidad de HUs
```

### Fase 4: Interfaces y Navegación (Subagente)

```
Skill: ui-prototyper
Entrada: 05_historias_usuario.md, 03_requerimientos_funcionales.md, 02_actores_y_roles.md
Salida: 10_interfaces_usuario.md, 11_diagramas_navegacion.md, 12_prototipos_interfaz.md
Prototipo: Omite 12
CRÍTICO: Validar cobertura 100% (cantidad pantallas en 10 == cantidad wireframes en 12)
```

**Instrucción especial para subagente de Fase 4:**
```
REGLA OBLIGATORIA: Cada pantalla de Sección 10 debe tener su wireframe en Sección 12.
- Si hay 53 pantallas definidas, debe haber 53 wireframes
- NO omitir pantallas por ser "similares" o "repetitivas"
- NO detenerse antes de completar TODAS las pantallas
- Verificar al final que cantidad de wireframes == cantidad de pantallas
- Si faltan wireframes, CONTINUAR generando hasta completar
```

### Fase 5: Diagramas de Procesos y Estados (Subagente)

```
Skill: mermaid-diagrams
Entrada: 05_historias_usuario.md, 06_casos_uso.md, 10_interfaces_usuario.md, 03_requerimientos_funcionales.md
Salida: 07_diagramas_procesos.md, 09_diagramas_estados.md
Prototipo: Omitida completamente
CRÍTICO: En `analisis/07_diagramas_procesos.md`:
  - Cada bloque ```mermaid``` debe incluir un comentario Mermaid con las HUs cubiertas (usar `%% ...`).
  - En cada paso donde intervenga un usuario/rol, indicar la(s) pantalla(s) (P-XXX) que utiliza, obtenidas de `analisis/10_interfaces_usuario.md`.
  - Para determinar cobertura (HUs) y pantallas, revisar `analisis/05_historias_usuario.md` y `analisis/10_interfaces_usuario.md` (no inferir sin consultar).
```

### Fase 5b: Diagramas BPMN (Subagentes Paralelos por Proceso)

```
Skill: bpmn-diagrams
Entrada: 07_diagramas_procesos.md
Salida: carpeta analisis/bpmn/ (un .bpmn por proceso)
Prototipo: Omitida completamente

Ejecución recomendada (fan-out / fan-in):
  1) Identificar procesos en .\analisis\07_diagramas_procesos.md:
     - Cada encabezado "### 7.x. <Nombre>" con su bloque ```mermaid``` es un proceso
  2) Lanzar subagentes en paralelo (1 por proceso, máximo recomendado: 4 simultáneos)
     - Cada subagente debe:
       - Leer el bloque del proceso asignado en .\analisis\07_diagramas_procesos.md
       - Leer .\analisis\10_interfaces_usuario.md para trazabilidad con pantallas
       - Escribir exactamente 1 fichero .bpmn en .\analisis\bpmn\ con nombre: 0X_<slug>.bpmn
       - NO devolver el XML BPMN completo por consola (solo confirmar generación)
  3) Verificar: cantidad de .bpmn generados == cantidad de procesos en 07_diagramas_procesos.md
```

### Fase 6: Pruebas Funcionales (Subagente)

```
Skill: functional-testing
Entrada: 05_historias_usuario.md, 06_casos_uso.md, 10_interfaces_usuario.md
Salida: 13_pruebas_funcionales.md
Prototipo: Omitida completamente
```

### Fase 7: Trazabilidad (Subagente)

```
Skill: traceability-validator
Entrada: Todos los archivos generados
Salida: 14_matriz_trazabilidad.md
Validar: python .\.github\skills\traceability-validator\scripts\valida_trazabilidad.py --out .\analisis\check_trazabilidad.md
Prototipo: Matriz con columnas reducidas (sin CU ni Pruebas)
```

### Fase 8: Consolidación (Subagente)

```
Skill: doc-assembler
Entrada: Carpeta analisis/
Salida: analisis/Analisis_Funcional.docx
Prototipo: Ejecutar igual (consolida lo generado)
```

## Manejo de Documentos Extensos

Para evitar errores de límite de output en subagentes:

### Estrategia: Escritura Incremental por Módulo

1. **NO acumular** todo el contenido en memoria para devolverlo al final
2. **Escribir directamente a disco** cada módulo/sección usando `create_file` o `replace_string_in_file`
3. **Dividir la generación** en bloques de máximo 10 elementos (HUs, CUs, Pantallas, etc.)

### Instrucción para Subagentes

Incluir en el prompt del subagente:
```
IMPORTANTE: Generar el documento de forma INCREMENTAL:
1. Crear el archivo con el encabezado inicial
2. Agregar contenido módulo por módulo usando herramientas de edición
3. NO devolver el contenido completo como respuesta
4. Confirmar solo: "Archivo [nombre] generado con X elementos"
```

### Archivos Típicamente Extensos

| Archivo | Estrategia |
|---------|------------|
| `06_casos_uso.md` | Escribir 5-10 CUs, luego append siguiente bloque |
| `12_prototipos_interfaz.md` | Escribir 5-10 wireframes, luego append siguiente bloque |
| `13_pruebas_funcionales.md` | Escribir por módulo, append cada módulo |

## Reglas

- Actualizar `debug.md` tras cada fase
- **Subagentes deben escribir a disco incrementalmente, NO devolver contenido extenso**
- Si sección requiere consolidación de partes:
  ```powershell
  Get-ChildItem -Path analisis -Filter "XX_*_parte*.md" | ForEach-Object {
      Get-Content $_.FullName -Encoding UTF8 | Add-Content "analisis/XX_seccion.md" -Encoding UTF8
  }
  Get-ChildItem -Path analisis -Filter "XX_*_parte*.md" | Remove-Item
  ```
- Cobertura de trazabilidad debe ser 100%
