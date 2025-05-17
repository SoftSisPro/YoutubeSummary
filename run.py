from youtube_transcript_api import YouTubeTranscriptApi
import pyperclip
import re
import tkinter as tk
from tkinter import messagebox
import traceback

def extract_youtube_id(url_input):
    """
    Extrae el ID de un video de YouTube de varios formatos de URL.
    """

    if not url_input:
        return None

    # Eliminar espacios en blanco al inicio y final
    url_input = str(url_input).strip()

    # Verificar si es una URL válida de YouTube usando expresiones regulares
    youtube_regex = r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:(?:watch|live)\?v=|live/)|youtu\.be/)([a-zA-Z0-9_-]+)(?:[?&#]|$)'
    match = re.search(youtube_regex, url_input)

    if match:
        return match.group(1)
    else:
        return None

def main():
    # Crear una ventana tkinter oculta para poder mostrar mensajes
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal

    # Obtener el contenido del portapapeles
    clipboard_content = pyperclip.paste()

    # Extraer ID de YouTube
    video_id = extract_youtube_id(clipboard_content)


    if not video_id:
        messagebox.showerror("Error", "No tienes un link de YouTube en tu portapapeles")
        root.destroy()
        return

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id=video_id,languages=['en', 'es'])
    except:
        messagebox.showerror("Error", "No se encontró transcripción para este video")
        #transcript = YouTubeTranscriptApi.get_transcript(video_id)
        traceback.print_exc()
        root.destroy()
        return

    # Unir todas las líneas de la transcripción
    transcript_text = ' '.join(entry['text'] for entry in transcript)

    # Crear el prompt para Claude
    prompt = f"""
    I'm going to give you the full transcript of a YouTube video. Please read it and write a summary in Spanish that is clear, well-structured, and easy to understand for someone who hasn't watched the video. It doesn't need to be super short; instead, focus on fully developing the main ideas, key points, and any final conclusions or takeaways. If possible, organize the summary into thematic sections or parts of the content, so it's easier to follow.

    Full transcript:
    {transcript_text}
    """

    # Copiar el prompt al portapapeles
    pyperclip.copy(prompt)
    #messagebox.showinfo("Éxito", "Se ha copiado el prompt con la transcripción del video al portapapeles")

    root.destroy()

if __name__ == "__main__":
    main()
