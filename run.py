from youtube_transcript_api import YouTubeTranscriptApi
import pyperclip

def extract_youtube_id(url_input):
    """
    Extrae el ID de un video de YouTube de varios formatos de URL.

    Formatos soportados:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://youtu.be/VIDEO_ID?t=123

    Returns:
        str: El ID del video o None si la URL no es válida
    """
    # Eliminar espacios en blanco al inicio y final
    url_input = url_input.strip()

    # Verificar si es una URL válida de YouTube
    if "youtube.com/watch?v=" in url_input or "youtu.be/" in url_input:
        # Extraer ID desde formato youtu.be
        if "youtu.be/" in url_input:
            video_id = url_input.split("youtu.be/")[1]
        # Extraer ID desde formato youtube.com
        else:
            video_id = url_input.split("v=")[1]

        # Eliminar parámetros adicionales (timestamp, etc.)
        if "&" in video_id:
            video_id = video_id.split("&")[0]
        if "?" in video_id:
            video_id = video_id.split("?")[0]

        return video_id
    else:
        return None

def main():
    
    url_input = input("Por favor, ingresa la URL del video de YouTube: ")
    url = extract_youtube_id(url_input)
    try:
        transcript = YouTubeTranscriptApi.get_transcript(url, languages=['en'])
    except:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(url, languages=['es'])
        except:
            print("No se encontró transcripción en español ni en inglés")
            transcript = []

    transcript_text = '\n'.join(entry['text'] for entry in transcript)

    prompt = """
    I'm going to give you the full transcript of a YouTube video. Please read it and write a summary in Spanish that is clear, well-structured, and easy to understand for someone who hasn't watched the video. It doesn't need to be super short; instead, focus on fully developing the main ideas, key points, and any final conclusions or takeaways. If possible, organize the summary into thematic sections or parts of the content, so it's easier to follow.

    Full transcript:
    """ + transcript_text

    pyperclip.copy(prompt)
    print("Copiado...")

if __name__ == "__main__":
    main()