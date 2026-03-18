---
name: text-extractor
description: Extrae requisitos funcionales, reglas de negocio, decisiones e integraciones de documentos técnicos (PDF, DOCX, TXT). Usar cuando se necesite procesar documentos de entrada para extraer RFs, RBs, DCs, INTs y contexto general.
---

# Text Extractor

Extrae y estructura requisitos de documentos técnicos.

## Uso

Ejecutar el script sobre los documentos de entrada:

```powershell
python .\.githubTailormade\skills\text-extractor\scripts\extractor_de_requisitos.py "[DOCUMENTO1]" "[DOCUMENTO2]" -o requisitos.md --tesseract-path "C:\Users\apadernr\AppData\Local\Programs\Tesseract-OCR\tesseract.exe" --include-context
```

## Salida

Genera `requisitos.md` con secciones:
- **RF**: Requerimientos Funcionales
- **RB**: Reglas de Negocio  
- **DC**: Decisiones/Condiciones
- **INT**: Integraciones
- **OBS**: Observaciones
- **Contexto General**: Texto bruto por fuente

También crea carpeta `images/` con imágenes extraídas para análisis visual posterior.

## Parámetros

| Parámetro | Descripción |
|-----------|-------------|
| `documentos` | Archivos de entrada (PDF, DOCX, TXT, imágenes) |
| `-o` | Archivo de salida (default: requisitos.md) |
| `--tesseract-path` | Ruta a tesseract.exe para OCR |
| `--include-context` | Incluir texto bruto completo |
