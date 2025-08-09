# Imagen base de Python
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para yt-dlp
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de requirements primero para aprovechar el cache de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Crear directorio outputs
RUN mkdir -p outputs

# Exponer el puerto
EXPOSE 8000

# Variables de entorno por defecto
ENV API_USERNAME=admin
ENV API_PASSWORD=password123
ENV HOST=0.0.0.0
ENV PORT=8000

# Comando para ejecutar la aplicación
CMD ["python", "main.py"]
