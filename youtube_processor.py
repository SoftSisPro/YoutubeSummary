import yt_dlp
import requests
import re
import traceback
import xml.etree.ElementTree as ET
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class YouTubeProcessor:
    def __init__(self):
        self.output_dir = "outputs"
        os.makedirs(self.output_dir, exist_ok=True)

    def extract_youtube_id(self, url_input: str) -> Optional[str]:
        """
        Extrae el ID de un video de YouTube de varios formatos de URL.
        """
        if not url_input:
            return None
        url_input = str(url_input).strip()
        youtube_regex = (
            r'(?:https?://)?(?:www\.)?'
            r'(?:youtube\.com/(?:watch\?v=|live\?v=|shorts/)|youtu\.be/)'
            r'([A-Za-z0-9_-]{11})'
        )
        match = re.search(youtube_regex, url_input)
        return match.group(1) if match else None

    def descargar_y_parsear_subtitulos(self, url: str) -> Optional[List[str]]:
        """
        Descarga un archivo de subtítulos VTT o SRT desde la URL y lo parsea.
        Maneja playlists M3U8 descargando los segmentos individuales.
        Devuelve una lista de líneas de texto.
        """
        try:
            print(f"🔄 Descargando subtítulos desde: {url}")
            resp = requests.get(url)
            resp.raise_for_status()
            print(f"✅ Descarga exitosa. Tamaño: {len(resp.text)} caracteres")
        except Exception as e:
            print(f"❌ Error al descargar subtítulos: {e}")
            traceback.print_exc()
            return None

        content = resp.text
        
        # Si es una playlist M3U8, extraer las URLs de los segmentos
        if content.startswith('#EXTM3U') or '.m3u8' in url:
            print("📋 Detectada playlist M3U8, extrayendo segmentos...")
            segment_urls = []
            lines = content.splitlines()
            
            for line in lines:
                line = line.strip()
                if line.startswith('https://') and 'timedtext' in line:
                    segment_urls.append(line)
            
            print(f"🔗 Encontrados {len(segment_urls)} segmentos de subtítulos")
            
            # Descargar todos los segmentos
            all_transcript = []
            for i, segment_url in enumerate(segment_urls):
                try:
                    print(f"📥 Descargando segmento {i+1}/{len(segment_urls)}...")
                    seg_resp = requests.get(segment_url)
                    seg_resp.raise_for_status()
                    
                    # Parsear el contenido VTT del segmento
                    segment_lines = seg_resp.text.splitlines()
                    for line in segment_lines:
                        line = line.strip()
                        # Omitir líneas vacías, numeración, timestamps y metadatos VTT
                        if (not line or line.startswith('WEBVTT') or 
                            re.match(r'^\d+$', line) or '-->' in line or 
                            re.match(r'^\d{2}:\d{2}:\d{2}\.', line) or
                            line.startswith('NOTE')):
                            continue
                        all_transcript.append(line)
                            
                except Exception as e:
                    print(f"⚠️  Error descargando segmento {i+1}: {e}")
                    continue
            
            transcript = all_transcript
        else:
            # Procesamiento normal para archivos VTT/SRT directos
            lines = content.splitlines()
            transcript = []
            for line in lines:
                line = line.strip()
                # Omitir líneas vacías, numeración, timestamps y metadatos VTT
                if (not line or line.startswith('WEBVTT') or 
                    re.match(r'^\d+$', line) or '-->' in line or 
                    re.match(r'^\d{2}:\d{2}:\d{2}\.', line) or
                    line.startswith('NOTE')):
                    continue
                transcript.append(line)
        
        print(f"✅ Extraídas {len(transcript)} líneas de texto")
        return transcript

    def obtener_transcripcion(self, video_id: str) -> Optional[List[str]]:
        """
        Obtiene la transcripción de un video de YouTube usando yt-dlp.
        Intenta múltiples estrategias para evitar bloqueos de bot.
        """
        
        # Estrategia 1: Configuración estándar con headers
        strategies = [
            {
                'name': 'Standard with headers',
                'opts': {
                    'skip_download': True,
                    'writesubtitles': True,
                    'writeautomaticsub': True,
                    'subtitleslangs': ['es', 'en'],
                    'quiet': True,
                    'no_warnings': True,
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-us,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                    },
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android', 'web'],
                            'player_skip': ['configs'],
                        }
                    }
                }
            },
            {
                'name': 'Android client only',
                'opts': {
                    'skip_download': True,
                    'writesubtitles': True,
                    'writeautomaticsub': True,
                    'subtitleslangs': ['es', 'en'],
                    'quiet': True,
                    'no_warnings': True,
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android'],
                        }
                    }
                }
            },
            {
                'name': 'Basic configuration',
                'opts': {
                    'skip_download': True,
                    'writesubtitles': True,
                    'writeautomaticsub': True,
                    'subtitleslangs': ['es', 'en'],
                    'quiet': True,
                    'no_warnings': True,
                }
            }
        ]

        for strategy in strategies:
            try:
                print(f"🔄 Intentando estrategia: {strategy['name']}")
                with yt_dlp.YoutubeDL(strategy['opts']) as ydl:
                    info = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=False)
                
                # Si llegamos aquí, la extracción fue exitosa
                print(f"✅ Estrategia exitosa: {strategy['name']}")
                break
                
            except Exception as e:
                print(f"❌ Estrategia '{strategy['name']}' falló: {e}")
                if strategy == strategies[-1]:  # Última estrategia
                    print("❌ Todas las estrategias fallaron")
                    traceback.print_exc()
                    return None
                continue

        # Fuentes en orden: auto-generated, luego manual
        for source in ('automatic_captions', 'subtitles'):
            captions = info.get(source) or {}
            for lang in ['es', 'en']:
                if lang in captions:
                    entries = captions[lang]
                    # Elegir la primera pista .vtt/.srt/ttml
                    entry = next((c for c in entries if c.get('ext') in ('vtt', 'srt', 'ttml')), entries[0])
                    url = entry.get('url')
                    if url:
                        print(f"✅ Transcripción encontrada ({source}) en: {lang}")
                        return self.descargar_y_parsear_subtitulos(url)

        print("❌ No se encontró transcripción en ningún idioma soportado.")
        return None

    def extraer_texto_de_p(self, lineas: List[str]) -> List[str]:
        """
        Dada una lista de líneas, extrae el texto útil.
        Maneja tanto formato XML como texto plano.
        """
        textos = []
        print(f"🔍 Procesando {len(lineas)} líneas para extraer texto...")
        
        for linea in lineas:
            linea = linea.strip()
            if not linea:
                continue
                
            # Si la línea contiene etiquetas XML, intentar parsearla
            if '<' in linea and '>' in linea:
                try:
                    # Intentar parsear como XML
                    elemento = ET.fromstring(linea)
                    if elemento.text:
                        textos.append(elemento.text.strip())
                except ET.ParseError:
                    # Si no es XML válido, extraer texto entre > y <
                    texto_extraido = re.sub(r'<[^>]*>', '', linea).strip()
                    if texto_extraido:
                        textos.append(texto_extraido)
            else:
                # Si no tiene etiquetas XML, es texto plano
                if linea and not re.match(r'^\d+$', linea) and '-->' not in linea:
                    textos.append(linea)
        
        print(f"✅ Extraídos {len(textos)} fragmentos de texto")
        if textos:
            print(f"📝 Muestra del primer fragmento: {textos[0][:100]}...")
        
        return textos

    def process_video(self, video_id: str, file_id: str, output_format: str = "txt") -> Dict:
        """
        Procesa un video de YouTube y genera el archivo de salida
        """
        try:
            # Obtener la transcripción
            print(f"🎬 Procesando video ID: {video_id}")
            transcript = self.obtener_transcripcion(video_id)
            if not transcript:
                return {
                    "success": False,
                    "message": "No se encontró transcripción para este video."
                }

            print(f"📄 Transcripción inicial: {len(transcript)} líneas")
            transcript = self.extraer_texto_de_p(transcript)
            
            if not transcript:
                return {
                    "success": False,
                    "message": "No se pudo extraer texto de la transcripción."
                }

            # Unir líneas y crear prompt
            transcript_text = ' '.join(transcript)
            print(f"📝 Texto final: {len(transcript_text)} caracteres")
            
            if len(transcript_text.strip()) == 0:
                return {
                    "success": False,
                    "message": "El texto extraído está vacío."
                }

            prompt = f"""I'm going to give you the full transcript of a YouTube video. Please read it and write a summary in Spanish that is clear, well-structured, and easy to understand for someone who hasn't watched the video. It doesn't need to be super short; instead, focus on fully developing the main ideas, key points, and any final conclusions or takeaways. If possible, organize the summary into thematic sections or parts of the content, so it's easier to follow.

Full transcript:
{transcript_text}"""

            # Preparar datos para guardar
            output_data = {
                "video_id": video_id,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "processed_at": datetime.now().isoformat(),
                "transcript_length": len(transcript_text),
                "prompt": prompt,
                "transcript_lines": len(transcript),
                "file_id": file_id
            }

            # Guardar según el formato solicitado
            if output_format.lower() == "json":
                output_file = os.path.join(self.output_dir, f"output_{file_id}.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, ensure_ascii=False, indent=2)
            else:
                output_file = os.path.join(self.output_dir, f"output_{file_id}.txt")
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(prompt)

            print(f"✅ Archivo guardado: {output_file}")

            return {
                "success": True,
                "message": "Video procesado exitosamente",
                "file_path": output_file,
                "data": output_data
            }

        except Exception as e:
            print(f"❌ Error procesando video: {e}")
            traceback.print_exc()
            return {
                "success": False,
                "message": f"Error procesando video: {str(e)}"
            }
