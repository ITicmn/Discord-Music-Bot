import json
import os

SERVER_PATH = 'C:/Users/USER/Desktop/code/Game Development/little projects/music bot/Server/'

class Server():
    def __init__(self, id):
        if os.path.isfile(f"{SERVER_PATH}{id}.json"):
            with open(fr'{SERVER_PATH}{id}.json', 'r',encoding="utf-8",errors="ignore") as file:
                data = json.load(file)
            self.server_id = id
            self.queue = data[id]["music bot"]["queue"]
            self.playlist = data[id]["music bot"]["playlist"]
            self.repeat = data[id]["music bot"]["repeat"]
            self.autoplay = data[id]["music bot"]["autoplay"]
            self.time = data[id]["music bot"]["time"]
            self.temporary_voice_channel = data[id]["manager bot"]["temporary voice channel"]
            self.welcome_channel = data[id]["manager bot"]["welcome channel"]
            self.leave_channel = data[id]["manager bot"]["leave channel"]
            self.basic_role = data[id]["manager bot"]["basic role"]
            self.role_message = data[id]["manager bot"]["role message"]
            self.prediction = data[id]["manager bot"]["prediction"]
            self.wheel = data[id]["manager bot"]["wheel"]
            self.scam_prevent = data[id]["manager bot"]["scam prevent"]
            self.emote_save = data[id]["save bot"]["enable emote-save"]
        else:
            setup = {
                id:{
                "music bot":{
                    "queue": [],
                    "playlist": {},
                    "repeat": "None",
                    "autoplay": [False,{"None":"None"}],
                    "time": 0
                },
                "manager bot":{
                    "temporary voice channel":{
                        "default":"",
                        "temporary":[]
                    },
                    "welcome channel": "",
                    "leave channel": "",
                    "basic role": "",
                    "role message": "",
                    "prediction":{},
                    "wheel":{},
                    "scam prevent":{"File":False,"URL":False}
                },
                "save bot":{
                    "enable emote-save":[]
                }
                }
            }
            with open(fr'{SERVER_PATH}{id}.json', 'w', encoding="utf-8", errors="ignore") as file:
                file.write(json.dumps(setup, indent=4, ensure_ascii=False))
            with open(fr'{SERVER_PATH}{id}.json', 'r', encoding="utf-8", errors="ignore") as file:
                data = json.load(file)
            self.server_id = id
            self.queue = data[id]["music bot"]["queue"]
            self.playlist = data[id]["music bot"]["playlist"]
            self.repeat = data[id]["music bot"]["repeat"]
            self.autoplay = data[id]["music bot"]["autoplay"]
            self.time = data[id]["music bot"]["time"]
            self.temporary_voice_channel = data[id]["manager bot"]["temporary voice channel"]
            self.welcome_channel = data[id]["manager bot"]["welcome channel"]
            self.leave_channel = data[id]["manager bot"]["leave channel"]
            self.basic_role = data[id]["manager bot"]["basic role"]
            self.role_message = data[id]["manager bot"]["role message"]
            self.prediction = data[id]["manager bot"]["prediction"]
            self.wheel = data[id]["manager bot"]["wheel"]
            self.scam_prevent = data[id]["manager bot"]["scam prevent"]
            self.emote_save = data[id]["save bot"]["enable emote-save"]
            
    def save_data(self):
        with open(fr'{SERVER_PATH}{self.server_id}.json', 'r', encoding="utf-8", errors="ignore") as file:
            data = json.load(file)
        data[self.server_id]["music bot"]["queue"] = self.queue
        data[self.server_id]["music bot"]["playlist"] = self.playlist
        data[self.server_id]["music bot"]["repeat"] = self.repeat
        data[self.server_id]["music bot"]["autoplay"] = self.autoplay
        with open(fr'{SERVER_PATH}{self.server_id}.json', 'w', encoding="utf-8", errors="ignore") as file:
            file.write(json.dumps(data, indent=4, ensure_ascii=False))
            
    def save_time(self):
        with open(fr'{SERVER_PATH}{self.server_id}.json', 'r', encoding="utf-8", errors="ignore") as file:
            data = json.load(file)
        data[self.server_id]["music bot"]["time"] = self.time
        with open(fr'{SERVER_PATH}{self.server_id}.json', 'w', encoding="utf-8", errors="ignore") as file:
            file.write(json.dumps(data, indent=4, ensure_ascii=False))
            
    def save_management(self):
        with open(fr'{SERVER_PATH}{self.server_id}.json', 'r', encoding="utf-8", errors="ignore") as file:
            data = json.load(file)
        data[self.server_id]["manager bot"]["temporary voice channel"] = self.temporary_voice_channel
        data[self.server_id]["manager bot"]["welcome channel"] = self.welcome_channel
        data[self.server_id]["manager bot"]["leave channel"] = self.leave_channel
        data[self.server_id]["manager bot"]["basic role"] = self.basic_role
        data[self.server_id]["manager bot"]["role message"] = self.role_message
        data[self.server_id]["manager bot"]["prediction"] = self.prediction
        data[self.server_id]["manager bot"]["wheel"] = self.wheel
        data[self.server_id]["manager bot"]["scam prevent"] = self.scam_prevent
        with open(fr'{SERVER_PATH}{self.server_id}.json', 'w', encoding="utf-8", errors="ignore") as file:
            file.write(json.dumps(data, indent=4, ensure_ascii=False))
            
    def save_save(self):
        with open(fr'{SERVER_PATH}{self.server_id}.json', 'r', encoding="utf-8", errors="ignore") as file:
            data = json.load(file)
        data[self.server_id]["save bot"]["enable emote-save"] = self.emote_save
        with open(fr'{SERVER_PATH}{self.server_id}.json', 'w', encoding="utf-8", errors="ignore") as file:
            file.write(json.dumps(data, indent=4, ensure_ascii=False))
