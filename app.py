from flask import Flask, request, render_template, send_file, jsonify
from pytube import YouTube
import os
from moviepy.editor import *
from moviepy.audio.io.AudioFileClip import AudioFileClip

app = Flask(__name__)

DOWNLOAD_FOLDER = 'downloads'

def download_video(link, resolution, path):
    try:
        yutub = YouTube(link)
        video_stream = yutub.streams.filter(res=resolution, adaptive=True).first()
        audio_stream = yutub.streams.filter(only_audio=True).first()

        video_path = video_stream.download(output_path=path, filename="video.mp4")
        audio_path = audio_stream.download(output_path=path, filename="audio.mp4")

        video_clip = VideoFileClip(video_path)
        audio_clip = AudioFileClip(audio_path)
        final_clip = video_clip.set_audio(audio_clip)
        final_clip_path = os.path.join(path, f"{yutub.title}.mp4")
        final_clip.write_videofile(final_clip_path)

        video_clip.close()
        audio_clip.close()
        os.remove(video_path)
        os.remove(audio_path)

        return final_clip_path
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def download_audio(link, path):
    try:
        yutub = YouTube(link)
        ys = yutub.streams.filter(only_audio=True).first()

        audio_file = ys.download(output_path=path)
        base, ext = os.path.splitext(audio_file)
        new_file = base + '.mp3'

        audio_clip = AudioFileClip(audio_file)
        audio_clip.write_audiofile(new_file)
        audio_clip.close()

        os.remove(audio_file)

        return new_file
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        link = request.form['link']
        choice = request.form['choice']
        resolution = request.form.get('resolution')

        if not os.path.exists(DOWNLOAD_FOLDER):
            os.makedirs(DOWNLOAD_FOLDER)

        if choice == '1':
            file_path = download_video(link, resolution, DOWNLOAD_FOLDER)
        elif choice == '2':
            file_path = download_audio(link, DOWNLOAD_FOLDER)
        else:
            return "Invalid choice"

        if file_path:
            return send_file(file_path, as_attachment=True)
        else:
            return "An error occurred during download"

    return render_template('index.html')

@app.route('/resolutions', methods=['POST'])
def resolutions():
    data = request.get_json()
    link = data['link']
    print(f"Fetching resolutions for: {link}")
    yutub = YouTube(link)
    video_streams = yutub.streams.filter(adaptive=True).order_by('resolution').desc()
    resolutions = [stream.resolution for stream in video_streams if stream.resolution]
    unique_resolutions = list(dict.fromkeys(resolutions))
    print(f"Available resolutions: {unique_resolutions}")
    return jsonify(resolutions=unique_resolutions)

if __name__ == "__main__":
    app.run(debug=True)
