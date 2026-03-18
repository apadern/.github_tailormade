---
name: traceability-validator
description: Genera la matriz de trazabilidad y valida cobertura 100% de requisitos. Incluye script de validación automática. Usar cuando se necesite generar la sección 14 de un análisis funcional o validar trazabilidad.
---

# Traceability Validator

Genera y valida la matriz de trazabilidad del análisis funcional.

## Modos

| Modo | Columnas de Matriz | Prerrequisitos |
|------|-------------------|----------------|
| **Completo** | RF, HU, CU, Pantalla, Prueba | 03, 05, 06, 10, 13 |
| **Prototipo** | RF, HU, Pantalla | 03, 05, 10 |

## Prerrequisitos

### Modo Completo
- `analisis/03_requerimientos_funcionales.md`
- `analisis/05_historias_usuario.md`
- `analisis/06_casos_uso.md`
- `analisis/10_interfaces_usuario.md`
- `analisis/13_pruebas_funcionales.md`

### Modo Prototipo
- `analisis/03_requerimientos_funcionales.md`
- `analisis/05_historias_usuario.md`
- `analisis/10_interfaces_usuario.md`

## Sección 14: Matriz de Trazabilidad

Trazar cada RF contra HUs, CUs, Pantallas y Pruebas:

```markdown
## 14. Matriz de Trazabilidad

| Requisito | Historia(s) de Usuario | Caso(s) de Uso | Pantalla(s) | Prueba(s) |
| :-------- | :--------------------- | :------------- | :---------- | :-------- |
| **RF-001:** <título> | HU-001, HU-002 | CU-01, CU-02 | `P-001` | PF-001, PF-002 |
```

### Modo prototipo

Eliminar columnas `Caso(s) de Uso` y `Prueba(s)`:

```markdown
| Requisito | Historia(s) de Usuario | Pantalla(s) |
| :-------- | :--------------------- | :---------- |
```

Guardar como: `analisis/14_matriz_trazabilidad.md`

## Validación Automática

### Paso 1: Ejecutar Script

```powershell
python .\.github\skills\traceability-validator\scripts\valida_trazabilidad.py --out .\analisis\check_trazabilidad.md
```

El script valida:
- Cada RF tiene al menos una HU, CU, Pantalla y Prueba (según modo)
- Las HUs referenciadas existen y declaran relación con el RF
- Las pantallas existen y están asociadas a las HUs correctas
- Detecta IDs huérfanos o duplicados

### Paso 2: Revisar Errores

Abrir `analisis/check_trazabilidad.md` y verificar la sección **Resumen**:

```markdown
| Discrepancias (ERROR) | X |
```

**CRÍTICO**: Si `Discrepancias (ERROR) > 0`, la validación NO está completa.

### Paso 3: Corregir Errores

Para cada ERROR en la tabla **Discrepancias detectadas**:

| Tipo Error | Descripción | Acción de Corrección |
|------------|-------------|---------------------|
| **RF** | RF no existe o título no coincide | Verificar ID en `14_matriz_trazabilidad.md` coincida con `03_requerimientos_funcionales.md` |
| **RF_HU** | La HU no declara relación con el RF | Actualizar campo `ID Requerimientos relacionados` en `05_historias_usuario.md` agregando el RF |
| **RF_UI** | Pantalla no asociada a ninguna HU del RF | Agregar HUs faltantes en fila del RF en `14_matriz_trazabilidad.md` O actualizar columna HU asociadas en `10_interfaces_usuario.md` |
| **HU** | HU referenciada no existe o fila sin HUs | Corregir ID en `14_matriz_trazabilidad.md` o agregar HU en `05_historias_usuario.md` |
| **UI** | Pantalla referenciada no existe o fila sin pantallas | Corregir ID en `14_matriz_trazabilidad.md` o agregar Pantalla en `10_interfaces_usuario.md` |
| **NO_APLICA** | Inconsistencia entre matriz y requerimientos | Sincronizar estado NO APLICA entre `14_matriz_trazabilidad.md` y `03_requerimientos_funcionales.md` |
| **COBERTURA** | RF/HU/Pantalla definido pero no aparece en matriz | Agregar fila correspondiente en `14_matriz_trazabilidad.md` |

### Paso 4: Re-ejecutar Validación

Tras cada corrección, volver a ejecutar el script:

```powershell
python .\.github\skills\traceability-validator\scripts\valida_trazabilidad.py --out .\analisis\check_trazabilidad.md
```

**Repetir hasta que `Discrepancias (ERROR) = 0`** y `Observaciones (WARN) = 0` **o** todas las advertencias están justificadas (1 a 1)

### Paso 5: Criterio de Finalización

La validación se considera **COMPLETA** únicamente cuando:

✅ `Discrepancias (ERROR) = 0`  
✅ `Observaciones (WARN) = 0` **o** todas las advertencias están justificadas (1 a 1)
✅ `Filas RF en matriz = RF definidos en 03_requerimientos_funcionales.md`  
✅ Cobertura 100% de todos los RFs

## Reglas

- **OBLIGATORIO**: Corregir todos los errores (ERROR) antes de finalizar
- Cada warning no corregido requiere justificación individual (una entrada por warning).
- No se permite avanzar al siguiente backlog/módulo con gates incompletos.
- Cobertura 100% de RFs es obligatoria
- Documentar RFs no cubiertos o excepciones en `debug.md`
- No dar por terminada la tarea si existen discrepancias de tipo ERROR
- **NO incluir resúmenes, conclusiones ni secciones adicionales al final del documento**

## Escritura Incremental (Documentos Extensos)

**CRÍTICO**: Para evitar errores de límite de output:

### Proceso para `14_matriz_trazabilidad.md`
1. Crear archivo con encabezado y cabecera de tabla
2. Generar y escribir filas en bloques de 20-30 RFs
3. Append siguiente bloque usando `replace_string_in_file`
4. **NO acumular toda la matriz en memoria**

### Respuesta del Skill
Al finalizar, reportar solo:
```
Archivo 14_matriz_trazabilidad.md generado: X filas de trazabilidad
Validación: Y errores, Z advertencias
```
**NO devolver el contenido completo del archivo.**
