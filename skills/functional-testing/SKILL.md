---
name: functional-testing
description: Genera casos de prueba funcionales exhaustivos que cubran todos los flujos de negocio. Usar cuando se necesite generar la sección 13 de un análisis funcional.
---

# Functional Testing

Genera casos de prueba funcionales basados en CUs y HUs.

## Modos

| Modo | Acción |
|------|--------|
| **Completo** | Generar sección 13 |
| **Prototipo** | **Omitir completamente** |

## Prerrequisitos

- `analisis/05_historias_usuario.md` (HUs)
- `analisis/06_casos_uso.md` (CUs)
- `analisis/10_interfaces_usuario.md` (Pantallas)

## Sección 13: Pruebas Funcionales

Generar casos de prueba que cubran:
- Flujos principales de cada CU
- Flujos alternativos
- Casos de error

```markdown
## 13. Pruebas Funcionales

### 13.x. <Módulo>

| ID Prueba | HU / CU | Pantalla(s) | Actor | Criterios de Aceptación | Resultado Esperado |
| :-------- | :------ | :---------- | :---- | :---------------------- | :----------------- |
| **PF-001** | HU-01 / CU-01 | `P-WEB-01` | Cliente | Completar formulario con datos válidos | Sistema crea registro y muestra confirmación |
| **PF-002** | HU-01 / CU-01 | `P-WEB-01` | Cliente | Enviar formulario con campo vacío | Sistema muestra error de validación |
```

### Convención de IDs

- `PF-xxx` - Prueba funcional numerada secuencialmente

### Tipos de prueba por CU

1. **Flujo principal** - Camino feliz completo
2. **Flujo alternativo** - Cada bifurcación documentada
3. **Validación** - Campos obligatorios, formatos
4. **Permisos** - Acceso por rol
5. **Límites** - Valores extremos

Guardar como: `analisis/13_pruebas_funcionales.md`

## Reglas

- Mínimo una prueba por flujo principal de cada CU
- Incluir pruebas de error/validación
- Referenciar pantallas específicas
- Criterios medibles y verificables
- **NO incluir resúmenes, conclusiones ni secciones adicionales al final del documento**

## Escritura Incremental (Documentos Extensos)

**CRÍTICO**: Para evitar errores de límite de output:

### Proceso para `13_pruebas_funcionales.md`
1. Crear archivo con encabezado: `## 13. Pruebas Funcionales`
2. Generar y escribir pruebas módulo por módulo
3. Máximo 15-20 pruebas por operación de escritura
4. Append siguiente bloque usando `replace_string_in_file`

### Respuesta del Skill
Al finalizar, reportar solo:
```
Archivo 13_pruebas_funcionales.md generado: X pruebas en Y módulos
```
**NO devolver el contenido completo del archivo.**
