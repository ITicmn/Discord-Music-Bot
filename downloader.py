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

SPOTIFY = '/music bot/Audio/Spotify/'
APPLE_MUSIC = '/music bot/Audio/Apple Music/'
YOUTUBE = '/music bot/Audio/Youtube/'
NICONICO = '/music bot/Audio/NicoNico/'

ydl_opts = {'format': 'bestaudio', 'noplaylist':'True','outtmpl': f'{YOUTUBE}temporary/song.%(ext)s',"windowsfilenames":'True'}
nc_opts = {'format': 'bestaudio', 'noplaylist':'True','outtmpl': f'{NICONICO}temporary/song.%(ext)s',"windowsfilenames":'True'}
    
def youtube_download(url):
    info = youtube_info_extract(url)
    title = info["title"]
    valid_title = valid_song_name(title)
    artist = info["uploader"]
    length = info["duration"]
    thumbnail = info["thumbnail"]
    result = {"title":title,"artist":artist,"length":int(length),"valid_title":valid_title,"thumbnail":thumbnail}
    if os.path.isfile(f"{YOUTUBE}{valid_title}.mp4") == False:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        for file in os.listdir(f"{YOUTUBE}temporary/"):
            if file.startswith("song"):
                os.rename(f"{YOUTUBE}temporary/{file}",f"{YOUTUBE}{valid_title}.mp4")
    return result
        
def youtube_info_extract(url):
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url,download=False)
    return info

def spotify_download(url):
    subprocess.run(["py","-m","spotdl","--output",f"{SPOTIFY}temporary",url])
    info = []
    for name in os.listdir(f"{SPOTIFY}temporary"):
        stat = TinyTag.get(fr"{SPOTIFY}temporary/{name}",image=True)
        valid_title = valid_song_name(f"{stat.artist} - {stat.title}")
        info.append({"title":stat.title,"artist":stat.artist,"length":int(stat.duration),"valid_title":valid_title})
        if os.path.isfile(f"{SPOTIFY}{valid_title}.mp4"):
            os.remove(f"{SPOTIFY}temporary/{name}")
            continue
        image = stat.get_image()
        image = Image.open(BytesIO(image))
        image.save(fr'{SPOTIFY}{valid_title}.png')
        os.rename(f"{SPOTIFY}temporary/{name}",f"{SPOTIFY}{valid_title}.mp4")
    return info
    #os.system(f"py -m spotdl {url}")

def apple_music_download(url):
    subprocess.run(["py","-m","gamdl","-c","/music bot/apple_music_cookie/cookies.txt","-o",f"{APPLE_MUSIC}temporary","--template-folder-album","","--template-folder-compilation","","--no-synced-lyrics",url])
    info = []
    for name in os.listdir(f"{APPLE_MUSIC}temporary"):
        stat = TinyTag.get(fr"{APPLE_MUSIC}temporary/{name}",image=True)
        valid_title = valid_song_name(f"{stat.artist} - {stat.title}")
        info.append({"title":stat.title,"artist":stat.artist,"length":int(stat.duration),"valid_title":valid_title})
        if os.path.isfile(f"{APPLE_MUSIC}{valid_title}.mp4"):
            os.remove(f"{APPLE_MUSIC}temporary/{name}")
            continue
        image = stat.get_image()
        image = Image.open(BytesIO(image))
        image.save(fr'{APPLE_MUSIC}{valid_title}.png')
        os.rename(f"{APPLE_MUSIC}temporary/{name}",f"{APPLE_MUSIC}{valid_title}.mp4")
    return info
    
def niconico_download(url):
    with YoutubeDL(nc_opts) as ydl:
        ydl.download([url])
        
def soundcloud_download(url):
    pass

def check_file_exist(name):
    pass
