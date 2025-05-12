from flask import Flask, request, render_template, send_file, jsonify
from yt_dlp import YoutubeDL
import os, shutil, subprocess, re


app = Flask(__name__)
os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"
DOWNLOAD_FOLDER = 'downloads'
os.environ["FFMPEG_BINARY"] = r"C:\ffmpeg\bin\ffmpeg.exe"

from yt_dlp import YoutubeDL
import os

def download_video(link, resolution_str, path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)

        with YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(link, download=False)
            video_id = info['id']
            formats = info['formats']

        target_height = int(resolution_str.replace('p', ''))
        video_format = next(
            (f for f in formats if f.get("vcodec") != "none" and f.get("acodec") == "none" and f.get("height") == target_height),
            None
        )
        if not video_format:
            raise Exception(f"{resolution_str} çözünürlüğünde video bulunamadı.")
        video_format_id = video_format['format_id']

        audio_format = max(
            (f for f in formats if f.get("acodec") != "none" and f.get("vcodec") == "none"),
            key=lambda f: f.get('abr') or 0
        )
        audio_format_id = audio_format['format_id']

        print(f"Kullanıcı seçimi: {resolution_str} -> video format: {video_format_id}, audio format: {audio_format_id}")

        video_path = os.path.join(path, f"{video_id}.video.mp4")
        with YoutubeDL({
            'format': str(video_format_id),
            'outtmpl': video_path,
            'quiet': False
        }) as ydl:
            ydl.download([link])

        audio_path = os.path.join(path, f"{video_id}.audio.m4a")
        with YoutubeDL({
            'format': str(audio_format_id),
            'outtmpl': audio_path,
            'quiet': False
        }) as ydl:
            ydl.download([link])

        output_path = os.path.join(path, f"{video_id}_{resolution_str}.mp4")
        subprocess.run([
            r"C:\ffmpeg\bin\ffmpeg.exe", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            output_path
        ], check=True)

        return output_path

    except Exception as e:
        print(f"🔥 Bir hata oluştu: {e}")
        return None

    

def download_audio(link, path):
    try:
        if not link.strip():
            raise ValueError("Boş link verildi.")

        base_link = link.strip().split("&")[0]

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(path, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': False,
            'ffmpeg_location': r'C:\ffmpeg\bin\ffmpeg.exe',
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(base_link, download=True)
            filename = ydl.prepare_filename(info)
            final_path = os.path.splitext(filename)[0] + '.mp3'

            print(f"✔ MP3 indirildi: {final_path}")
            return final_path

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        link = request.form.get('link', '').strip()
        choice = request.form.get('choice')
        resolution = request.form.get('resolution', None)

        if not link:
            return "No link provided", 400
        if not os.path.exists(DOWNLOAD_FOLDER):
            os.makedirs(DOWNLOAD_FOLDER)

        if choice == '1':
            if not resolution:
                return "Resolution not selected", 400
            file_path = download_video(link, resolution, DOWNLOAD_FOLDER)
        elif choice == '2':
            file_path = download_audio(link, DOWNLOAD_FOLDER)
        else:
            return "Invalid choice", 400
        print(">>> FORM VERİSİ:")
        print("Link:", repr(link))
        print("Choice:", choice)
        print("Resolution:", resolution)
        if file_path:
            return send_file(file_path, as_attachment=True)
        else:
            return "An error occurred during download"

    return render_template('index.html')

from yt_dlp import YoutubeDL

@app.route('/resolutions', methods=['POST'])
def resolutions():
    data = request.get_json()
    link = data['link']
    print(f"Fetching resolutions for: {link}")
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'force_generic_extractor': False
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            formats = info.get('formats', [])
            resolutions = list({f"{f['height']}p" for f in formats if f.get('height')})
            resolutions.sort(key=lambda x: int(x.replace("p", "")), reverse=True)
            print(f"Available resolutions: {resolutions}")
            return jsonify(resolutions=resolutions)
    except Exception as e:
        print(f"yt-dlp error: {e}")
        return jsonify(error=str(e)), 500


if __name__ == "__main__":
    app.run(debug=True)
