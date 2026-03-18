# Template MVP v1.4

## PASO 0: PREREQUISITOS
Configurar los siguientes MCP Server en VS Code:

```
{
	"inputs": [],
	"servers": {
		"chrome-devtools": {
			"command": "npx",
			"args": [
				"-y",
				"chrome-devtools-mcp@latest"
			],
			"type": "stdio"
		},
		"image-extractor": {
			"command": "npx",
			"args": ["mcp-image-extractor@latest"]
		}
	}
}
```
## PASO 1: EXTRAER LOS REQUISITOS DE LA DOCUMENTACIÓN
Ejecutar el agente `Requirements_Extractor` para extraer los requisitos de la documentación. Ejemplo de prompt:

```
Extraer requisitos de "03 - Situaciones administrativas 6.0 (Corregido).pdf" y "Infotipos PSE.docx"
```

* NOTA: Para extraer el texto de las imágenes con OCR se requiere instalar Tesseract https://github.com/UB-Mannheim/tesseract/wiki y actualizar la ruta en el fichero `.github\agents\Requirements_Extractor.agent.md`

## PASO 2: GENERAR EL ANÁLISIS FUNCIONAL 
Ejecutar el agente `Functional_Analyst` para generar el análisis funcional del MVP (carpeta `analisis/`). Ejemplo de prompt:

```
Generar análisis funcional para un sistema que cubra toda la funcionalidad del CRM Comercial.
```

## PASO 3: GENERAR DISEÑO TÉCNICO Y PLANIFICACIÓN
Ejecutar el agente `MVP_Design.agent` para generar el diseño técnico (`design/01_technical_design.md`), modelo de datos (`design/02_data_model.md`), servicios (`design/03_data_services.md`) y backlog (`backlog/XX_[Nombre_Modulo].md`). Ejemplo de prompt:

```
Generar diseño técnico y planificación.
```

## PASO 4: COLORES Y TIPOGRAFÍA (OPCIONAL) 
Ejecutar el siguiente prompt para personalizar los colores y la tipografía del MVP conforme a la identidad visual del cliente. Ejemplo de prompt:

```
1. Usar Chrome para navegar a https://www.cliente.com/
2. Actualizar el fichero "estilos.md" con los "Background Colours", "Text Colours" y "Typography" obtenidas de la web.
```

## PASO 5: IMPLEMENTAR MVP (BACKEND)
Ejecutar el agente `Backend_DEV` para implementar el backend de los distintos módulos del MVP. Ejemplo de prompt:

```
Implementar módulo de Administración
```

## PASO 6: IMPLEMENTAR MVP (FRONTEND)
Ejecutar el agente `Frontend_DEV` para implementar el frontend de los distintos módulos del MVP. Ejemplo de prompt:

```
Implementar módulo de Administración
```

---

## CHANGE REQUEST

### PASO 1: CREAR CHANGE REQUEST (CR)
Existe un skill creado para facilitar la creación del Change Request. Ejemplo de prompt:

```
Crear CR para un nuevo módulo de gestión de Usuarios, Roles y Permisos
```

### PASO 2: PLANIFICACIÓN DEL CHANGE REQUEST (CR)
Ejecutar el agente `CR_Planner` para generar el backlog del Change Request. Ejemplo de prompt:

```
Planificar CR-001
```

## PASO 3: IMPLEMENTAR CHANGE REQUEST (BACKEND)
Ejecutar el agente `Backend_DEV` para implementar el backend del Change Request. Ejemplo de prompt:

```
Implementar Gestión de Usuarios, Roles y Permisos (CR-001)
```

## PASO 4: IMPLEMENTAR CHANGE REQUEST (FRONTEND)
Ejecutar el agente `Frontend_DEV` para implementar el frontend del Change Request. Ejemplo de prompt:

```
Implementar Gestión de Usuarios, Roles y Permisos (CR-001)
```

**NOTA** Se recomienda utilizar Claude Sonnet 4.5 para ejecutar todos los agentes.
