from moviepy.editor import *
import os

def video_converter(file_path,output_path,output_format):
    video = VideoFileClip(file_path)
    filename = os.path.basename(file_path).split(".")[0]
    output = video.copy()
    output.write_videofile(f"{output_path}/{filename}.{output_format}",temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")
    video.close()
    output.close()
    
def audio_converter(file_path,output_path,output_format):
    audio = AudioFileClip(file_path)
    filename = os.path.basename(file_path).split(".")[0]
    output = audio.copy()
    output.write_audiofile(f"{output_path}/{filename}.{output_format}")
    audio.close()
    output.close()
    
def video_to_audio(file_path,output_path,output_format):
    video = VideoFileClip(file_path)
    audio = video.audio
    filename = os.path.basename(file_path).split(".")[0]
    audio.write_audiofile(f"{output_path}/{filename}.{output_format}")
    video.close()
    audio.close()