---
name: doc-assembler
description: Unifica documentos markdown parciales en un documento maestro y genera entregables en formato DOCX. Usar al finalizar la generación de análisis funcional para consolidar la documentación.
---

# Document Assembler

Este skill consolida la documentación de la carpeta `analisis/` en el entregable final en formato DOCX.

## Procedimiento

### Generar Entregable DOCX

Utilizar el script de conversión incluido en el skill.
El script acepta la carpeta `analisis/` como entrada, procesa todos los archivos numerados (`01_*.md`, `02_*.md`) en orden y genera un único documento de Word.

```powershell
python .\.github\skills\doc-assembler\scripts\md2docx.py analisis/ analisis/Analisis_Funcional.docx
```

### Entregables Generados

- `analisis/Analisis_Funcional.docx`: Documento final formateado para entrega.
