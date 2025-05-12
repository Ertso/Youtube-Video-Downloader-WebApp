# Youtube-Video-Downloader-WebApp
A web version of my previous script which does not work thanks to ###YOUTUBE CHANGING ITS ALGORITHM AND BREAKING PYTUBE ENTIRELY

## Setup
Enter these commands on your terminal:

pip install flask

pip install yt_dlp

Download: ffmpeg from: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip

Extract the contents to a folder such as:
C:\ffmpeg

#Add FFmpeg to System PATH
Open System Properties (Win + R → sysdm.cpl)

Go to Advanced → Environment Variables

Under System Variables, find and edit Path

Add the following:
C:\ffmpeg\bin
(or path of wherever you extracted)

## Using
Enter this command on your terminal:

python app.py

Or just double-click on the app.py to run it

After running it, you will see a localhost URL. Copy it and paste it into your web browser (chrome, opera, etc), or just Ctrl+leftclick it idc

have fun
