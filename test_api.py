#!/usr/bin/env python3
"""
Script de prueba para la API de YouTube Summary
"""

import requests
import json
import base64
from typing import Dict, Any

class YouTubeAPITester:
    def __init__(self, base_url: str = "http://localhost:8000", username: str = "admin", password: str = "password123"):
        self.base_url = base_url
        self.auth = (username, password)
        
    def test_health(self) -> Dict[str, Any]:
        """Prueba el endpoint de salud"""
        print("🔍 Probando endpoint de salud...")
        response = requests.get(f"{self.base_url}/health")
        print(f"Status: {response.status_code}")
        return response.json()
    
    def test_root(self) -> Dict[str, Any]:
        """Prueba el endpoint raíz"""
        print("🔍 Probando endpoint raíz...")
        response = requests.get(f"{self.base_url}/")
        print(f"Status: {response.status_code}")
        return response.json()
    
    def test_process_video(self, url: str, output_format: str = "txt") -> Dict[str, Any]:
        """Prueba el procesamiento de un video"""
        print(f"🔍 Probando procesamiento de video: {url}")
        
        data = {
            "url": url,
            "output_format": output_format
        }
        
        response = requests.post(
            f"{self.base_url}/process",
            json=data,
            auth=self.auth
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Video procesado exitosamente")
            print(f"   File ID: {result.get('file_id')}")
            print(f"   Video ID: {result.get('video_id')}")
            return result
        else:
            print(f"❌ Error: {response.text}")
            return {"error": response.text}
    
    def test_download_file(self, file_id: str) -> bool:
        """Prueba la descarga de un archivo"""
        print(f"🔍 Probando descarga de archivo: {file_id}")
        
        response = requests.get(
            f"{self.base_url}/download/{file_id}",
            auth=self.auth
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            # Guardar el archivo
            filename = f"test_download_{file_id}.txt"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ Archivo descargado: {filename}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    
    def test_list_files(self) -> Dict[str, Any]:
        """Prueba la lista de archivos"""
        print("🔍 Probando lista de archivos...")
        
        response = requests.get(
            f"{self.base_url}/files",
            auth=self.auth
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            files = result.get('files', [])
            print(f"✅ Encontrados {len(files)} archivos")
            for file_info in files:
                print(f"   - {file_info.get('filename')} (ID: {file_info.get('file_id')})")
            return result
        else:
            print(f"❌ Error: {response.text}")
            return {"error": response.text}
    
    def test_delete_file(self, file_id: str) -> bool:
        """Prueba la eliminación de un archivo"""
        print(f"🔍 Probando eliminación de archivo: {file_id}")
        
        response = requests.delete(
            f"{self.base_url}/files/{file_id}",
            auth=self.auth
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Archivo eliminado exitosamente")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    
    def test_unauthorized_access(self) -> bool:
        """Prueba acceso sin autenticación"""
        print("🔍 Probando acceso sin autenticación...")
        
        response = requests.post(
            f"{self.base_url}/process",
            json={"url": "https://www.youtube.com/watch?v=test"}
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Autenticación funcionando correctamente")
            return True
        else:
            print("❌ Error: Debería requerir autenticación")
            return False

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas de la API YouTube Summary")
    print("=" * 50)
    
    # Inicializar tester
    tester = YouTubeAPITester()
    
    # Pruebas básicas
    print("\n1. Pruebas básicas")
    print("-" * 20)
    tester.test_root()
    tester.test_health()
    tester.test_unauthorized_access()
    
    # Prueba de procesamiento de video
    print("\n2. Prueba de procesamiento")
    print("-" * 30)
    
    # URL de prueba (video corto y popular)
    test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # "Me at the zoo" - primer video de YouTube
    
    result = tester.test_process_video(test_url, "txt")
    
    if "file_id" in result:
        file_id = result["file_id"]
        
        # Prueba de descarga
        print("\n3. Prueba de descarga")
        print("-" * 20)
        tester.test_download_file(file_id)
        
        # Prueba de lista de archivos
        print("\n4. Prueba de lista de archivos")
        print("-" * 30)
        tester.test_list_files()
        
        # Prueba de eliminación (opcional)
        print(f"\n5. ¿Eliminar archivo de prueba {file_id}? (y/n): ", end="")
        if input().lower() == 'y':
            tester.test_delete_file(file_id)
    
    print("\n✅ Pruebas completadas")

if __name__ == "__main__":
    main()
