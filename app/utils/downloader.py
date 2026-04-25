import yt_dlp
import os
import time

def obtener_info_video(url):
    """Obtiene metadatos y la lista REAL de calidades disponibles."""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            if not info:
                return None

            formatos = info.get('formats', [])
            # Filtrar alturas únicas y solo de video que contengan datos reales
            alturas = sorted(list(set(
                f.get('height') for f in formatos 
                if f.get('height') is not None and f.get('height') >= 144
            )), reverse=True)

            if not alturas:
                alturas = [720, 480, 360]

            return {
                'url': url,
                'titulo': info.get('title', 'Video sin título'),
                'thumbnail': info.get('thumbnail', ''),
                'duracion': info.get('duration_string', '0:00'),
                'max_res': alturas[0],
                'lista_calidades': alturas,
                'fuente': info.get('extractor_key', 'YouTube')
            }
        except Exception as e:
            print(f"Error al analizar video: {e}")
            return None

def descargar_media(url, tipo, calidad):
    """Descarga Audio o Video con gestión de calidad estricta."""
    download_folder = os.path.abspath('downloads')
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    project_root = os.path.abspath('.')

    ydl_opts = {
        'nocheckcertificate': True,
        'quiet': False,
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
        'restrictfilenames': True,
        'ffmpeg_location': project_root,
        'noplaylist': True,
    }

    if tipo == 'audio':
        # USAMOS LA VARIABLE CALIDAD (128, 192, 320)
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': str(calidad), # <-- CORREGIDO: Antes estaba fijo en 320
            }],
        })
    else:
        # FORMATO DE VIDEO ESTRICTO
        # Buscamos mp4 con la altura exacta o la inmediatamente inferior
        ydl_opts.update({
            'format': f'bestvideo[height<={calidad}][ext=mp4]+bestaudio[ext=m4a]/best[height<={calidad}][ext=mp4]/best[height<={calidad}]',
            'merge_output_format': 'mp4',
        })

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            # Obtenemos el nombre del archivo final procesado
            temp_filename = ydl.prepare_filename(info)
            
            # Ajustar la extensión según el proceso de post-procesado
            base = os.path.splitext(temp_filename)[0]
            ext_final = ".mp3" if tipo == 'audio' else ".mp4"
            final_path = base + ext_final

            # Verificación inmediata
            if os.path.exists(final_path):
                return os.path.abspath(final_path)

            # Si FFmpeg cambió el nombre (por caracteres especiales), buscamos el más reciente
            time.sleep(1)
            for f in os.listdir(download_folder):
                full_f = os.path.join(download_folder, f)
                if f.endswith(ext_final) and (time.time() - os.path.getmtime(full_f)) < 30:
                    return os.path.abspath(full_f)

            return None
        except Exception as e:
            print(f"Error crítico en la descarga: {e}")
            return None