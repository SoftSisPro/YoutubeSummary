import yt_dlp
import requests
import re
import traceback
import xml.etree.ElementTree as ET
import sys

def extract_youtube_id(url_input):
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

def descargar_y_parsear_subtitulos(url):
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
        
        print(f"� Encontrados {len(segment_urls)} segmentos de subtítulos")
        
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

def obtener_transcripcion(video_id):
    """
    Obtiene la transcripción de un video de YouTube usando yt-dlp.
    Intenta en este orden:
        1) auto-generated Spanish (es)
        2) auto-generated English (en)
        3) manual Spanish (es)
        4) manual English (en)
    Devuelve una lista de líneas de texto, o None si no hay transcript.
    """
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['es', 'en'],
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=False)
    except Exception as e:
        print(f"❌ Error al extraer info del video: {e}")
        traceback.print_exc()
        return None

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
                    return descargar_y_parsear_subtitulos(url)

    print("❌ No se encontró transcripción en ningún idioma soportado.")
    return None

def extraer_texto_de_p(lineas):
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

def main():

    # Verificar si se proporcionó un enlace como argumento
    if len(sys.argv) != 2:
        print("Uso: python run.py <link>")
        return

    # Extraer ID desde el argumento de línea de comandos
    url_input = sys.argv[1]
    video_id = extract_youtube_id(url_input)
    if not video_id:
        print("No hay un enlace de YouTube válido en el argumento proporcionado.")
        return

    # Obtener la transcripción
    print(f"🎬 Procesando video ID: {video_id}")
    transcript = obtener_transcripcion(video_id)
    if not transcript:
        print("❌ No se encontró transcripción para este video.")
        return

    print(f"📄 Transcripción inicial: {len(transcript)} líneas")
    transcript = extraer_texto_de_p(transcript)
    
    if not transcript:
        print("❌ No se pudo extraer texto de la transcripción.")
        return

    # Unir líneas y crear prompt
    transcript_text = ' '.join(transcript)
    print(f"📝 Texto final: {len(transcript_text)} caracteres")
    
    if len(transcript_text.strip()) == 0:
        print("⚠️  El texto extraído está vacío.")
        return
    prompt = f"""
I'm going to give you the full transcript of a YouTube video. Please read it and write a summary in Spanish that is clear, well-structured, and easy to understand for someone who hasn't watched the video. It doesn't need to be super short; instead, focus on fully developing the main ideas, key points, and any final conclusions or takeaways. If possible, organize the summary into thematic sections or parts of the content, so it's easier to follow.

Full transcript:
{transcript_text}
"""

    with open('output.txt', 'w', encoding='utf-8') as f:
        f.write(prompt)
    print("Prompt copiado al portapapeles.")

if __name__ == "__main__":
    main()
