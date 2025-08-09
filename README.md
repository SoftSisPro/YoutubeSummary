# YouTube Summary FastAPI

API REST para generar resúmenes de videos de YouTube con autenticación básica, diseñada para despliegue en Easy Panel.

## Características

- ✅ Autenticación HTTP Basic
- ✅ Extracción automática de transcripciones de YouTube
- ✅ Soporte para múltiples idiomas (ES/EN)
- ✅ Generación de prompts para resumir videos
- ✅ Salida en formato TXT o JSON
- ✅ API REST completa
- ✅ Gestión de archivos (listar, descargar, eliminar)
- ✅ Compatible con Easy Panel

## Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Configurar variables de entorno (opcional):
```bash
export API_USERNAME=tu_usuario
export API_PASSWORD=tu_contraseña
export PORT=8000
export HOST=0.0.0.0
```

## Uso

### Ejecutar localmente
```bash
python main.py
```

La API estará disponible en `http://localhost:8000`

### Documentación
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

### `POST /process`
Procesa un video de YouTube y genera el archivo de resumen.

**Request:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "output_format": "txt"  // opcional: "txt" o "json"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Video procesado exitosamente",
  "file_id": "uuid-generado",
  "video_id": "VIDEO_ID",
  "download_url": "/download/uuid-generado"
}
```

### `GET /download/{file_id}`
Descarga el archivo generado por su ID.

### `GET /files`
Lista todos los archivos generados.

### `DELETE /files/{file_id}`
Elimina un archivo por su ID.

### `GET /health`
Verificación de salud de la API.

## Autenticación

Todos los endpoints (excepto `/` y `/health`) requieren autenticación HTTP Basic.

**Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: `password123`

## Despliegue en Easy Panel

1. Crear un nuevo servicio en Easy Panel
2. Configurar las siguientes variables de entorno:
   - `API_USERNAME`: Tu usuario personalizado
   - `API_PASSWORD`: Tu contraseña personalizada
   - `PORT`: 8000 (o el puerto que configure Easy Panel)
   - `HOST`: 0.0.0.0

3. Comando de inicio: `python main.py`

## Ejemplo de uso con curl

```bash
# Procesar un video
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -u "admin:password123" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# Descargar archivo generado
curl -X GET "http://localhost:8000/download/FILE_ID" \
  -u "admin:password123" \
  -o "resumen.txt"

# Listar archivos
curl -X GET "http://localhost:8000/files" \
  -u "admin:password123"
```

## Estructura del proyecto

```
.
├── main.py                 # Aplicación FastAPI principal
├── youtube_processor.py    # Lógica de procesamiento de YouTube
├── requirements.txt        # Dependencias
├── outputs/               # Directorio de archivos generados
└── README.md              # Este archivo
```

## Notas

- Los archivos se almacenan en el directorio `outputs/`
- Cada archivo tiene un ID único (UUID)
- La API maneja automáticamente la creación del directorio de salida
- Compatible con videos en español e inglés
- Soporte para subtítulos automáticos y manuales
