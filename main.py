from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, HttpUrl
import secrets
import os
from typing import Optional
import uvicorn
from youtube_processor import YouTubeProcessor
import uuid
from datetime import datetime

app = FastAPI(
    title="YouTube Summary API",
    description="API para generar resúmenes de videos de YouTube",
    version="1.0.0"
)

security = HTTPBasic()

# Configuración de autenticación básica
USERNAME = os.getenv("API_USERNAME", "admin")
PASSWORD = os.getenv("API_PASSWORD", "password123")

class YouTubeRequest(BaseModel):
    url: str
    output_format: Optional[str] = "txt"  # txt o json

class YouTubeResponse(BaseModel):
    success: bool
    message: str
    file_id: Optional[str] = None
    video_id: Optional[str] = None
    download_url: Optional[str] = None

def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    """Autentica al usuario usando HTTP Basic Auth"""
    is_correct_username = secrets.compare_digest(credentials.username, USERNAME)
    is_correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/")
async def root():
    """Endpoint de salud de la API"""
    return {
        "message": "YouTube Summary API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "process": "/process",
            "download": "/download/{file_id}",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/process", response_model=YouTubeResponse)
async def process_youtube_video(
    request: YouTubeRequest,
    username: str = Depends(authenticate_user)
):
    """
    Procesa un video de YouTube y genera el archivo de resumen
    """
    try:
        # Inicializar el procesador
        processor = YouTubeProcessor()
        
        # Extraer ID del video
        video_id = processor.extract_youtube_id(request.url)
        if not video_id:
            raise HTTPException(
                status_code=400,
                detail="URL de YouTube no válida"
            )
        
        # Generar ID único para el archivo
        file_id = str(uuid.uuid4())
        
        # Procesar el video
        result = processor.process_video(video_id, file_id, request.output_format)
        
        if not result["success"]:
            error_message = result["message"]
            
            # Detectar tipos específicos de errores
            if "bot" in error_message.lower() or "cookies" in error_message.lower():
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "YouTube bot detection",
                        "message": "YouTube está bloqueando las solicitudes. Intenta con otro video o vuelve a intentar más tarde.",
                        "suggestions": [
                            "Probar con videos más populares y públicos",
                            "Intentar de nuevo en unos minutos",
                            "Verificar que el video tenga subtítulos disponibles"
                        ]
                    }
                )
            elif "private" in error_message.lower() or "unavailable" in error_message.lower():
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "Video not accessible",
                        "message": "El video no está disponible, es privado o no existe.",
                        "suggestions": [
                            "Verificar que la URL sea correcta",
                            "Asegurarse de que el video sea público",
                            "Comprobar que el video no haya sido eliminado"
                        ]
                    }
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "Processing failed",
                        "message": error_message,
                        "suggestions": [
                            "Verificar que el video tenga subtítulos disponibles",
                            "Intentar con otro video",
                            "Contactar soporte si el problema persiste"
                        ]
                    }
                )
        
        return YouTubeResponse(
            success=True,
            message="Video procesado exitosamente",
            file_id=file_id,
            video_id=video_id,
            download_url=f"/download/{file_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@app.get("/download/{file_id}")
async def download_file(
    file_id: str,
    username: str = Depends(authenticate_user)
):
    """
    Descarga el archivo generado por su ID
    """
    try:
        # Verificar que el archivo existe
        txt_file = f"outputs/output_{file_id}.txt"
        json_file = f"outputs/output_{file_id}.json"
        
        if os.path.exists(txt_file):
            return FileResponse(
                path=txt_file,
                filename=f"youtube_summary_{file_id}.txt",
                media_type="text/plain"
            )
        elif os.path.exists(json_file):
            return FileResponse(
                path=json_file,
                filename=f"youtube_summary_{file_id}.json",
                media_type="application/json"
            )
        else:
            raise HTTPException(
                status_code=404,
                detail="Archivo no encontrado"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al descargar el archivo: {str(e)}"
        )

@app.get("/files")
async def list_files(username: str = Depends(authenticate_user)):
    """
    Lista todos los archivos generados
    """
    try:
        if not os.path.exists("outputs"):
            return {"files": []}
        
        files = []
        for filename in os.listdir("outputs"):
            if filename.startswith("output_"):
                file_path = os.path.join("outputs", filename)
                file_stats = os.stat(file_path)
                
                # Extraer file_id del nombre del archivo
                file_id = filename.replace("output_", "").replace(".txt", "").replace(".json", "")
                
                files.append({
                    "file_id": file_id,
                    "filename": filename,
                    "size": file_stats.st_size,
                    "created": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                    "download_url": f"/download/{file_id}"
                })
        
        return {"files": files}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al listar archivos: {str(e)}"
        )

@app.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    username: str = Depends(authenticate_user)
):
    """
    Elimina un archivo por su ID
    """
    try:
        txt_file = f"outputs/output_{file_id}.txt"
        json_file = f"outputs/output_{file_id}.json"
        
        deleted = False
        
        if os.path.exists(txt_file):
            os.remove(txt_file)
            deleted = True
            
        if os.path.exists(json_file):
            os.remove(json_file)
            deleted = True
        
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Archivo no encontrado"
            )
        
        return {"message": f"Archivo {file_id} eliminado exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar el archivo: {str(e)}"
        )

if __name__ == "__main__":
    # Crear directorio de outputs si no existe
    os.makedirs("outputs", exist_ok=True)
    
    # Configurar servidor
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        access_log=True
    )
