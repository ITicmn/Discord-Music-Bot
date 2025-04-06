from yt_dlp import YoutubeDL
import gamdl
import spotify_dl
import spotdl
from tinytag import TinyTag
from io import BytesIO
from PIL import Image
import requests
import os
import subprocess

from util import valid_song_name

DLSPOTIFY = '/music bot/File Save/Download/Spotify/'
DLAPPLE_MUSIC = '/music bot/File Save/Download/Apple Music/'
DLYOUTUBE = '/music bot/File Save/Download/Youtube/'
DLNICONICO = '/music bot/File Save/Download/Niconico/'

def file_youtube_download(url,type,filetype,id):
    info = file_youtube_info_extract(url)
    title = info["title"]
    valid_title = valid_song_name(title)
    artist = info["uploader"]
    length = info["duration"]
    thumbnail = info["thumbnail"]
    title = valid_song_name(f"Youtube {valid_title}({artist})")
    if type == "Video":
        if filetype == None:
            filetype = "mp4"
        if not os.path.exists(f"{DLYOUTUBE}{id}/{filetype}"):
            os.mkdir(f"{DLYOUTUBE}{id}/{filetype}")
        with YoutubeDL({'noplaylist':'True','outtmpl': f'{DLYOUTUBE}{id}/{filetype}/{title}.%(ext)s',"windowsfilenames":'True'}) as ydl:
            ydl.download([url])
        for file in os.listdir(f"{DLYOUTUBE}{id}/{filetype}/"):
            if not file.endswith(filetype):
                os.rename(f"{DLYOUTUBE}{id}/{filetype}/{file}",f"{DLYOUTUBE}{id}/{filetype}/{title}.{filetype}")
    elif type == "Audio":
        if filetype == None:
            filetype = "mp3"
        if not os.path.exists(f"{DLYOUTUBE}{id}/{filetype}"):
            os.mkdir(f"{DLYOUTUBE}{id}/{filetype}")
        with YoutubeDL({'format': 'bestaudio', 'noplaylist':'True','outtmpl': f'{DLYOUTUBE}{id}/{filetype}/{title}.%(ext)s',"windowsfilenames":'True'}) as ydl:
            ydl.download([url])
        for file in os.listdir(f"{DLYOUTUBE}{id}/{filetype}/"):
            if not file.endswith(filetype):
                os.rename(f"{DLYOUTUBE}{id}/{filetype}/{file}",f"{DLYOUTUBE}{id}/{filetype}/{title}.{filetype}")
    result = {"title":title,"artist":artist,"length":int(length),"thumbnail":thumbnail,"path":f"{DLYOUTUBE}{id}/{filetype}/{title}.{filetype}"}
    return result
        
def file_youtube_info_extract(url):
    with YoutubeDL({'format': 'bestaudio', 'noplaylist':'True','outtmpl': f'{DLYOUTUBE}%(title)s.%(ext)s',"windowsfilenames":'True'}) as ydl:
        info = ydl.extract_info(url,download=False)
    return info

def file_spotify_download(url,filetype,id):
    if filetype == None:
        filetype = "mp3"
    if not os.path.exists(f"{DLSPOTIFY}{id}/{filetype}"):
        os.mkdir(f"{DLSPOTIFY}{id}/{filetype}")
    subprocess.run(["py","-m","spotdl","--output",f"{DLSPOTIFY}{id}/{filetype}/",url])
    for name in os.listdir(f"{DLSPOTIFY}{id}/{filetype}/"):
        if name.split(" ")[0] != "Spotify":
            stat = TinyTag.get(fr"{DLSPOTIFY}{id}/{filetype}/{name}",image=True)
            title = valid_song_name(f"Spotify {stat.title}({stat.artist})")
            info = {"title":title,"artist":stat.artist,"length":int(stat.duration),"path":f"{DLSPOTIFY}{id}/{filetype}/{title}.{filetype}"}
            os.rename(f"{DLSPOTIFY}{id}/{filetype}/{name}",f"{DLSPOTIFY}{id}/{filetype}/{title}.{filetype}")
            break
    return info
    #os.system(f"py -m spotdl {url}")

def file_apple_music_download(url,filetype,id):
    if filetype == None:
        filetype = "mp3"
    if not os.path.exists(f"{DLAPPLE_MUSIC}{id}/{filetype}"):
        os.mkdir(f"{DLAPPLE_MUSIC}{id}/{filetype}")
    subprocess.run(["py","-m","gamdl","-c","C:/Users/USER/Desktop/code/Game Development/little projects/music bot/apple_music_cookie/cookies.txt","-o",f"{DLAPPLE_MUSIC}{id}/{filetype}/","--template-folder-album","","--no-synced-lyrics",url])
    for name in os.listdir(f"{DLAPPLE_MUSIC}{id}/{filetype}/"):
        if name.split(" ")[0] != "Apple_Music":
            stat = TinyTag.get(fr"{DLAPPLE_MUSIC}{id}/{filetype}/{name}",image=True)
            title = valid_song_name(f"Apple_Music {stat.title}({stat.artist})")
            info = {"title":title,"artist":stat.artist,"length":int(stat.duration),"path":f"{DLAPPLE_MUSIC}{id}/{filetype}/{title}.{filetype}"}
            os.rename(f"{DLAPPLE_MUSIC}{id}/{filetype}/{name}",f"{DLAPPLE_MUSIC}{id}/{filetype}/{title}.{filetype}")
            break
    return info
    #subprocess.run(["py","-m","gamdl","-c","C:/Users/USER/Desktop/code/Game Development/little projects/music bot/apple_music_cookie/","-o","C:/Users/USER/Desktop/code/Game Development/little projects/music bot/Audio/",url])
    
def file_niconico_download(url,type,filetype,id):
    if type == "Video":
        if filetype == None:
            filetype = "mp4"
        if not os.path.exists(f"{DLNICONICO}{id}/{filetype}"):
            os.mkdir(f"{DLNICONICO}{id}/{filetype}")
        with YoutubeDL({'noplaylist':'True','outtmpl': f'{DLNICONICO}{id}/{filetype}/%(title)s.%(ext)s',"windowsfilenames":'True'}) as ydl:
            ydl.download([url])
        for file in os.listdir(f"{DLNICONICO}{id}/{filetype}/"):
            if file.split(" ")[0] != "Niconico":
                stat = TinyTag.get(fr"{DLNICONICO}{id}/{filetype}/{file}",image=True)
                title = valid_song_name(f"Niconico {stat.title}({stat.artist})")
                info = {"title":title,"artist":stat.artist,"length":int(stat.duration),"path":f"{DLNICONICO}{id}/{filetype}/{title}.{filetype}"}
                os.rename(f"{DLNICONICO}{id}/{filetype}/{file}",f"{DLNICONICO}{id}/{filetype}/{title}.{filetype}")
                break
    elif type == "Audio":
        if filetype == None:
            filetype = "mp3"
        if not os.path.exists(f"{DLNICONICO}{id}/{filetype}"):
            os.mkdir(f"{DLNICONICO}{id}/{filetype}")
        with YoutubeDL({'format': 'bestaudio', 'noplaylist':'True','outtmpl': f'{DLNICONICO}{id}/{filetype}/%(title)s.%(ext)s',"windowsfilenames":'True'}) as ydl:
            ydl.download([url])
        for file in os.listdir(f"{DLNICONICO}{id}/{filetype}/"):
            if file.split(" ")[0] != "Niconico":
                stat = TinyTag.get(fr"{DLNICONICO}{id}/{filetype}/{file}",image=True)
                title = valid_song_name(f"Niconico {stat.title}({stat.artist})")
                info = {"title":title,"artist":stat.artist,"length":int(stat.duration),"path":f"{DLNICONICO}{id}/{filetype}/{title}.{filetype}"}
                os.rename(f"{DLNICONICO}{id}/{filetype}/{file}",f"{DLNICONICO}{id}/{filetype}/{title}.{filetype}")
                break
        return info

#youtube_download("","video")
#youtube_download("","audio")
#spotify_download("")
#apple_music_download("")
#niconico_download("","video")