from flask import Flask, request, jsonify
import subprocess
import os
import time

app = Flask(__name__)

# Archivos de cookies
if "COOKIES_INSTAGRAM" in os.environ:
    with open("cookies_instagram.txt", "w") as f:
        f.write(os.environ["COOKIES_INSTAGRAM"])

if "COOKIES_YOUTUBE" in os.environ:
    with open("cookies_youtube.txt", "w") as f:
        f.write(os.environ["COOKIES_YOUTUBE"])


@app.route("/get_video", methods=["POST"])
def get_video():
    data = request.json
    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # Detectar la plataforma
    if "instagram.com" in url:
        cookies_file = "cookies_instagram.txt"
        platform = "instagram"
    elif "youtube.com" in url or "youtu.be" in url:
        cookies_file = "cookies_youtube.txt"
        platform = "youtube"
    else:
        return jsonify({"error": "Unsupported URL"}), 400

    try:
        app.logger.info(f"Procesando URL: {url} (plataforma: {platform})")

        start_time = time.time()

        result = subprocess.run(
            ["yt-dlp", "--cookies", cookies_file, "-g", url],
            capture_output=True, text=True, timeout=60  # máximo 60s
        )

        elapsed = time.time() - start_time
        app.logger.info(f"yt-dlp terminó en {elapsed:.2f} segundos")
        app.logger.info(f"STDOUT: {result.stdout.strip()}")
        app.logger.info(f"STDERR: {result.stderr.strip()}")

        if result.returncode != 0:
            return jsonify({
                "error": "yt-dlp failed",
                "stderr": result.stderr.strip(),
                "stdout": result.stdout.strip(),
                "elapsed_seconds": elapsed
            }), 500

        return jsonify({
            "video_url": result.stdout.strip(),
            "elapsed_seconds": elapsed
        })

    except subprocess.TimeoutExpired:
        return jsonify({"error": "yt-dlp timeout (exceeded 60s)"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
