import os
from mediafire.client import (MediaFireClient, File, Folder)

client = MediaFireClient()
client.login(email='email',
    password='password',
    app_id='id')

def file_upload(file_path,user_id):
    client.create_folder(f"mf:/Discord User Download/{user_id}")
    file_name = os.path.basename(file_path)
    result = client.upload_file(file_path, f"mf:/Discord User Download/{user_id}/{file_name}")
    return f"https://www.mediafire.com/file/{result.quickkey}"

def file_delete(file_path,user_id):
    file_name = os.path.basename(file_path)
    os.remove(file_path)
    client.delete_file(f"mf:/Discord User Download/{user_id}/{file_name}")