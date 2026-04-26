from flask import Flask, render_template, request, jsonify, send_file, after_this_request
import os
import time
from app.utils.downloader import obtener_info_video, descargar_media

app = Flask(__name__,
            template_folder='app/templates',
            static_folder='app/static')

# Configuración de rutas absolutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, 'downloads')

# Asegurar que la carpeta de descargas existe
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analizar', methods=['POST'])
def analizar():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"error": "No se envió una URL"}), 400

        url = data.get('url')
        info = obtener_info_video(url)

        if info:
            return render_template('opciones.html', info=info)

        return jsonify({"error": "No se pudo analizar el video o el link es inválido."}), 404
    except Exception as e:
        print(f"Error en /analizar: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route('/descargar', methods=['POST'])
def descargar():
    url = request.form.get('url')
    tipo = request.form.get('tipo')
    calidad = request.form.get('calidad')

    if not url:
        return "Error: URL faltante", 400

    try:
        path_archivo = descargar_media(url, tipo, calidad)

        if path_archivo and os.path.exists(path_archivo):
            nombre_final = os.path.basename(path_archivo)

            mimetype_dict = {
                'audio': 'audio/mpeg',
                'video': 'video/mp4'
            }
            content_type = mimetype_dict.get(tipo, 'application/octet-stream')

            time.sleep(1)

            @after_this_request
            def remove_file(response):
                try:
                    pass
                except Exception as error:
                    app.logger.error(f"Error eliminando archivo: {error}")
                return response

            return send_file(
                path_archivo,
                as_attachment=True,
                download_name=nombre_final,
                mimetype=content_type
            )
        else:
            return f"Error: No se encontró el archivo en {calidad}p. Intenta otra calidad.", 404

    except Exception as e:
        print(f"Error crítico en /descargar: {e}")
        return f"Error al procesar la descarga: {e}", 500


@app.route('/limpiar')
def limpiar_descargas():
    """Ruta de mantenimiento para vaciar la carpeta downloads"""
    try:
        count = 0
        for filename in os.listdir(DOWNLOAD_FOLDER):
            file_path = os.path.join(DOWNLOAD_FOLDER, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
                count += 1
        return f"Carpeta limpia. Se eliminaron {count} archivos."
    except Exception as e:
        return f"Error al limpiar: {str(e)}", 500


if __name__ == '__main__':
    # Ejecución del servidor
    app.run(debug=True, port=5000)
