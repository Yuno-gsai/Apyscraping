from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

# Archivos de cookies
COOKIES_INSTAGRAM = "cookies_instagram.txt"
COOKIES_YOUTUBE = "cookies_youtube.txt"

@app.route("/get_video", methods=["POST"])
def get_video():
    data = request.json
    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # Detectar la plataforma
    if "instagram.com" in url:
        cookies_file = COOKIES_INSTAGRAM
    elif "youtube.com" in url or "youtu.be" in url:
        cookies_file = COOKIES_YOUTUBE
    else:
        return jsonify({"error": "Unsupported URL"}), 400

    try:
        # Ejecutar yt-dlp para obtener el link directo
        result = subprocess.run(
            ["yt-dlp", "--cookies", cookies_file, "-g", url],
            capture_output=True, text=True
        )

        if result.returncode != 0:
            return jsonify({"error": result.stderr.strip()}), 500

        return jsonify({"video_url": result.stdout.strip()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Render detecta el puerto con la variable de entorno PORT
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
