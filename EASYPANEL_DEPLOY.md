# 🚀 Guía de Despliegue en EasyPanel

## Requisitos Previos

1. **Servidor con EasyPanel instalado**
2. **Repositorio GitHub** con tu código
3. **Dominio** (opcional pero recomendado)

## Pasos para el Despliegue

### 1. Preparar el Repositorio

Asegúrate de que tu repositorio tenga estos archivos:
- ✅ `main.py` - Aplicación FastAPI principal
- ✅ `youtube_processor.py` - Lógica de procesamiento
- ✅ `requirements.txt` - Dependencias
- ✅ `Dockerfile` - Configuración de Docker
- ✅ `.dockerignore` - Archivos excluidos
- ✅ `README.md` - Documentación

### 2. Acceder a EasyPanel

1. Abre tu panel de EasyPanel en el navegador
2. Inicia sesión con tus credenciales

### 3. Crear un Nuevo Proyecto

1. Haz clic en **"+ New Project"**
2. Asigna un nombre como `youtube-summary`
3. Haz clic en **"Create Project"**

### 4. Agregar un Servicio de Aplicación

1. Dentro del proyecto, haz clic en **"+ Add Service"**
2. Selecciona **"App Service"**
3. Asigna un nombre como `api`

### 5. Configurar el Source

1. En la sección **"Source"**, selecciona:
   - **Source Type**: `Github Repository`
   - **Repository**: `tu-usuario/YoutubeSummary`
   - **Branch**: `main`
   - **Build Path**: `/` (raíz del repositorio)

### 6. Configurar Environment Variables

En la sección **"Environment"**, agrega:

```bash
API_USERNAME=tu_usuario_personalizado
API_PASSWORD=tu_contraseña_segura
HOST=0.0.0.0
PORT=8000
```

### 7. Configurar Domains & Proxy

1. En **"Domains & Proxy"**:
   - **Proxy Port**: `8000`
   - **Domain**: `tu-dominio.com` (o usa el dominio gratuito de EasyPanel)
   - **HTTPS**: ✅ Habilitado (automático con Let's Encrypt)

### 8. Configurar Mounts (Opcional)

Para persistir los archivos generados:

1. En **"Mounts"**, agrega:
   - **Type**: `Volume`
   - **Name**: `outputs`
   - **Mount Path**: `/app/outputs`

### 9. Deploy Settings

1. En **"Deploy Settings"**:
   - **Replicas**: `1` (para empezar)
   - **Command**: Dejar vacío (usará el CMD del Dockerfile)

### 10. Desplegar

1. Haz clic en **"Deploy"**
2. Espera a que termine el build (puede tomar varios minutos)
3. Verifica en la sección **"Logs"** que no haya errores

## 🧪 Probar la API

Una vez desplegado, puedes probar:

### 1. Endpoint de Salud
```bash
curl https://tu-dominio.com/health
```

### 2. Procesar un Video
```bash
curl -X POST "https://tu-dominio.com/process" \
  -H "Content-Type: application/json" \
  -u "tu_usuario:tu_contraseña" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

### 3. Documentación Automática
- Swagger UI: `https://tu-dominio.com/docs`
- ReDoc: `https://tu-dominio.com/redoc`

## 🔧 Configuraciones Adicionales

### Auto Deploy

1. En **"Auto Deploy"**, habilita la opción
2. Esto configurará un webhook en GitHub
3. Cada push a la rama `main` desplegará automáticamente

### Escalado

Para manejar más tráfico:
1. Aumenta **"Replicas"** en Deploy Settings
2. Considera usar múltiples workers de uvicorn

### Monitoreo

1. Ve a la sección **"Logs"** para ver los logs en tiempo real
2. Usa **"Console"** para acceder al container si necesitas debuggear

## 🔒 Seguridad

### Variables de Entorno Seguras

```bash
# Genera contraseñas seguras
API_USERNAME=admin_$(date +%s)
API_PASSWORD=$(openssl rand -base64 32)

# Para production, usa valores más descriptivos
API_USERNAME=youtube_api_admin
API_PASSWORD=tu_contraseña_muy_segura_123!
```

### HTTPS Automático

EasyPanel configura automáticamente:
- ✅ Certificados SSL/TLS gratuitos con Let's Encrypt
- ✅ Redirección automática de HTTP a HTTPS
- ✅ Renovación automática de certificados

## 🚨 Troubleshooting

### Error en el Build

Si el build falla:
1. Revisa los **"Logs"** del build
2. Verifica que el `Dockerfile` sea correcto
3. Asegúrate de que `requirements.txt` esté actualizado

### Error de Conexión

Si la API no responde:
1. Verifica que el **"Proxy Port"** sea `8000`
2. Revisa los logs del servicio
3. Verifica que las variables de entorno estén configuradas

### Problemas con YouTube

Si hay errores al procesar videos:
1. Los logs mostrarán errores específicos de yt-dlp
2. Algunos videos pueden tener restricciones geográficas
3. Verifica que el video tenga subtítulos disponibles

## 📊 Costos y Recursos

### Recursos Recomendados

- **RAM**: 512MB - 1GB (para empezar)
- **CPU**: 1 vCPU
- **Storage**: 10GB (para logs y archivos temporales)

### Optimización

Para reducir costos:
1. Configura limpieza automática de archivos antiguos
2. Usa compresión en las respuestas
3. Implementa cache si necesario

## 🔄 Actualizaciones

### Automatic Updates

Con **"Auto Deploy"** habilitado:
1. Haz push a GitHub
2. EasyPanel detecta los cambios
3. Rebuild y redeploy automático

### Manual Updates

1. Ve a la sección **"Source"**
2. Haz clic en **"Deploy"**
3. EasyPanel reconstruirá la imagen

## 🆘 Soporte

Si necesitas ayuda:
- [EasyPanel Discord](https://discord.gg/9bcDSXcZQ7)
- [EasyPanel Documentation](https://easypanel.io/docs)
- [GitHub Issues](https://github.com/tu-usuario/YoutubeSummary/issues)

---

¡Listo! Tu API de YouTube Summary debería estar funcionando en EasyPanel. 🎉
