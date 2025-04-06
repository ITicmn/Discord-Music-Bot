import discord
from discord import FFmpegPCMAudio
from discord import app_commands, Webhook
from discord.ext import commands
from discord.ui import View, Select
from discord.utils import get
import asyncio
import nest_asyncio
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import ffmpeg
import time
import os
import vt
nest_asyncio.apply()

from util import *
from server import *
from tracks import *
from downloader import *
from file_downloader import *
from file_uploader import *
from recommendation import *
from lyrics import *
from easter_egg import *

BOT_FOLDER = '/music bot/'
AUDIO = '/music bot/Audio/'
YOUTUBE = '/music bot/Audio/Youtube/'
SPOTIFY = '/music bot/Audio/Spotify/'
APPLE_MUSIC = '/music bot/Audio/Apple Music/'
ASSETS = '/music bot/assets/'
FILES = '/music bot/Virus Check File/'
FILES_SAVE = '/music bot/File Save/'
FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
HELP_INFO = json.load(open(fr'{BOT_FOLDER}help.json','r',encoding="utf-8",errors="ignore"))

youtube_icon = discord.File(f"{ASSETS}youtube icon.png", filename="yt_icon.png")
bot_icon = discord.File(f"{ASSETS}GuoYiTing.jpg", filename="bot_icon.png")

activity = discord.Activity(type=discord.ActivityType.listening, name="Pursuit ~ Lying Coldly", url="https://open.spotify.com/track/2WmchKjNtDdNdf88NRpy0N?si=08320f2c38a7447a", details="Umm...Actually", large_image_url="https://i.makeagif.com/media/4-16-2020/6iH555.mp4")

bot = commands.Bot(command_prefix="!", intents = discord.Intents.all(), activity=activity, status=discord.Status.idle)

@bot.event
async def on_ready():
    print("Bot is up and ready")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

########################################################################## Selenium Setup
service = Service()
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_experimental_option("detach", True)
#options.add_argument('--headless')
driver = webdriver.Chrome(service=service, options=options)
########################################################################## VirusTotal Setup
virustotal = vt.Client("TOKEN")
########################################################################## Button
class play_view(discord.ui.View):
    def __init__(self,server):
        super().__init__(timeout=None)
        self.autoplay = [x for x in self.children if x.custom_id=="autoplay"][0]
        self.loop = [x for x in self.children if x.custom_id=="loop"][0]
        if server.repeat == "None":
            self.loop.label = "無"
        elif server.repeat == "One Song":
            self.loop.label = "單首"
        elif server.repeat == "All":
            self.loop.label = "全部"
        if [*server.autoplay][0] != "None":
            self.autoplay.emoji = "✅"
            self.autoplay.style = discord.ButtonStyle.green
        else:
            self.autoplay.emoji = "❌"
            self.autoplay.style = discord.ButtonStyle.red
        
    @discord.ui.button(label=f"", row=0, style=discord.ButtonStyle.gray, custom_id = "back", emoji="⏮")
    async def back_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        if interaction.guild.voice_client == None or interaction.user.voice == None or interaction.user.voice.channel != interaction.guild.voice_client.channel:
            return await interaction.response.send_message("你必須與機器人同個語音房才可使用按鈕")
        server = Server(str(interaction.guild_id))
        if len(server.queue) == 0:
            return await interaction.response.send_message("歌單裡沒有歌曲")
        voice = get(bot.voice_clients,guild=interaction.guild)
        if server.repeat == "None":
            await interaction.response.send_message(f"前一首歌不存在(或許你應該試著將循環播放設成**All**)")
        elif server.repeat == "One Song":
            voice.pause()
            time.sleep(1)
            voice.stop()
            await interaction.response.send_message(f"已重播目前這首歌(或許你應該試著將循環播放設成**All**)")
        elif server.repeat == "All":
            previous_track(server.queue)
            previous_track(server.queue)
            server.save_data()
            voice.pause()
            time.sleep(1)
            voice.stop()
            await interaction.response.edit_message(view=self)
    
    @discord.ui.button(label=f"", row=0, style=discord.ButtonStyle.gray, custom_id = "pause", emoji="⏯")
    async def pause_resume_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        if interaction.guild.voice_client == None or interaction.user.voice == None or interaction.user.voice.channel != interaction.guild.voice_client.channel:
            return await interaction.response.send_message("你必須與機器人同個語音房才可使用按鈕")
        server = Server(str(interaction.guild_id))
        voice = get(bot.voice_clients,guild=interaction.guild)
        server.save_data()
        if voice.is_playing():
            voice.pause()
            await interaction.response.edit_message(view=self)
        else:
            if voice.is_paused():
                voice.resume()
                await interaction.response.edit_message(view=self)
                title = [*server.queue[0]][0]
                length = song_length(list(server.queue[0].values())[0]["length"])
                platform = list(server.queue[0].values())[0]["platform"]
                #
                thumbnail = thumbnail_easter_egg(title,list(server.queue[0].values())[0]["thumbnail"])
                #
                count = list(server.queue[0].values())[0]["length"]
                platform_icon = discord.File(f"{ASSETS}{platform} icon.png", filename="platform_icon.png")
                bot_icon = discord.File(f"{ASSETS}GuoYiTing.jpg", filename="bot_icon.png")
                while server.time < count-1 and len(server.queue) > 0 and voice.is_playing():
                    time.sleep(1)
                    try:
                        server = Server(str(interaction.guild_id))
                    except:
                        pass
                    c = int(server.time*(18/count))
                    duration = song_length(server.time)
                    embed = discord.Embed(title=f"**{title}**", url=list(server.queue[0].values())[0]["url"], color=0xbf70ff)
                    embed.set_author(name=platform,icon_url="attachment://platform_icon.png")
                    embed.set_footer(text="GuoYiTing Is Singing",icon_url="attachment://bot_icon.png")
                    embed.add_field(name="**∥ 正在撥放：**",value=f'\n                                           ♫\n▶︎ ● ｜{c*"<:bar:1289648502489747570>"}<:dot:1289644466860458048>{(18-c)*"<:bar:1289648502489747570>"}\n\n {duration[1]}:{duration[2]} / {length[1]}:{length[2]} \n',inline=False)
                    if len(server.queue) > 1:
                        embed.add_field(name="→【下一首歌曲】",value=f"**{[*server.queue[1]][0]}**",inline=False)
                    embed.set_thumbnail(url=thumbnail)
                    await interaction.message.edit(embed=embed)
            else:
                await interaction.response.send_message("目前沒有音樂在播放")
    
    @discord.ui.button(label=f"", row=0, style=discord.ButtonStyle.gray, custom_id = "skip", emoji="⏭")
    async def skip_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        if interaction.guild.voice_client == None or interaction.user.voice == None or interaction.user.voice.channel != interaction.guild.voice_client.channel:
            return await interaction.response.send_message("你必須與機器人同個語音房才可使用按鈕")
        server = Server(str(interaction.guild_id))
        if len(server.queue) == 0:
            return await interaction.response.send_message("歌單裡沒有歌曲")
        voice = get(bot.voice_clients,guild=interaction.guild)
        server.save_data()
        voice.pause()
        time.sleep(1)
        voice.stop()
        await interaction.response.edit_message(view=self)
    
    @discord.ui.button(label=f"", row=0, style=discord.ButtonStyle.gray, custom_id = "replay", emoji="🔄")
    async def replay_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        if interaction.guild.voice_client == None or interaction.user.voice == None or interaction.user.voice.channel != interaction.guild.voice_client.channel:
            return await interaction.response.send_message("你必須與機器人同個語音房才可使用按鈕")
        server = Server(str(interaction.guild_id))
        if len(server.queue) == 0:
            return await interaction.response.send_message("歌單裡沒有歌曲")
        voice = get(bot.voice_clients,guild=interaction.guild)
        if server.repeat == "None":
            song = server.queue[0]
            server.queue.insert(0,song)
        elif server.repeat == "All":
            previous_track(server.queue)
        server.save_data()
        voice.pause()
        time.sleep(1)
        voice.stop()
        await interaction.response.edit_message(view=self)
    
    @discord.ui.button(label=f"無", row=0, style=discord.ButtonStyle.gray, custom_id = "loop", emoji="🔁")
    async def loop_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        if interaction.user.voice == None or interaction.user.voice.channel != interaction.guild.voice_client.channel:
            return await interaction.response.send_message("你必須與機器人同個語音房才可使用按鈕")
        server = Server(str(interaction.guild_id))
        if server.repeat == "One Song":
            server.repeat = "All"
            button.label = "全部"
        elif server.repeat == "All":
            server.repeat = "None"
            button.label = "無"
        elif server.repeat == "None":
            server.repeat = "One Song"
            button.label = "單首"
        server.save_data()
        await interaction.response.edit_message(view=self)
    
    @discord.ui.button(label=f"隨機播放", row=1, style=discord.ButtonStyle.gray, custom_id = "shuffle", emoji="🔀")
    async def shuffle_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        if interaction.guild.voice_client == None or interaction.user.voice == None or interaction.user.voice.channel != interaction.guild.voice_client.channel:
            return await interaction.response.send_message("你必須與機器人同個語音房才可使用按鈕")
        server = Server(str(interaction.guild_id))
        server.queue = shuffle_track(server.queue)
        server.save_data()
        await interaction.response.send_message(f"已打散歌曲佇列裡所有的歌曲")
    
    @discord.ui.button(label=f"目前歌單", row=1, style=discord.ButtonStyle.gray, custom_id = "queue", emoji="▶️")
    async def queue_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        if interaction.guild.voice_client == None or interaction.user.voice == None or interaction.user.voice.channel != interaction.guild.voice_client.channel:
            return await interaction.response.send_message("你必須與機器人同個語音房才可使用按鈕")
        server = Server(str(interaction.guild_id))
        bot_icon = discord.File(f"{ASSETS}GuoYiTing.jpg", filename="bot_icon.png")
        embed=discord.Embed(title="**歌曲佇列**", description=f"length:{len(server.queue)}", color=0xbf70ff)
        if len(server.queue) > 5:
            for i in range(0,5):
                song = server.queue[i]
                length = song_length(list(song.values())[0]["length"])
                embed.add_field(name=f"**{i+1}** | **{[*song][0]}** - **{length[1]}:{length[2]}**", value="", inline=False)
        else:
            for i in range(0,len(server.queue)):
                song = server.queue[i]
                length = song_length(list(song.values())[0]["length"])
                embed.add_field(name=f"**{i+1}** | **{[*song][0]}** - **{length[1]}:{length[2]}**", value="", inline=False)
        embed.set_footer(text="GuoYiTing Is Singing",icon_url="attachment://bot_icon.png")
        view = page_view(server,None,"queue")
        await interaction.response.send_message(files=[bot_icon],embed=embed,view=view,ephemeral=True)
    
    @discord.ui.button(label=f"歌詞", row=1, style=discord.ButtonStyle.gray, custom_id = "lyrics", emoji="📜")
    async def lyrics_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        if interaction.guild.voice_client == None or interaction.user.voice == None or interaction.user.voice.channel != interaction.guild.voice_client.channel:
            return await interaction.response.send_message("你必須與機器人同個語音房才可使用按鈕")
        server = Server(str(interaction.guild_id))
        song = server.queue[0]
        lyric = extract_lyrics([*song][0],list(song.values())[0]["artist"])
        if lyric == None:
            await interaction.response.send_message("抱歉，查不到這首歌的歌詞")
        else:
            section = False
            line = False
            stitle = ""
            sline = ""
            embed = discord.Embed(title=f"**{lyric["title"]}**", url=lyric["url"], color=0xbf70ff)
            for i in range(0,len(lyric["lyrics"])):
                if lyric["lyrics"][i] == "":
                    section = True
                elif section == True:
                    stitle = lyric["lyrics"][i]
                    section = False
                    line = True
                elif line == True:
                    sline += lyric["lyrics"][i] + "\n"
                    if i+1 >= len(lyric["lyrics"]) or lyric["lyrics"][i+1] == "":
                        embed.add_field(name=f"**{stitle}**",value=sline,inline=False)
                        line = False
            genius_icon = discord.File(f"{ASSETS}Genius.jpg", filename="genius_icon.png")
            embed.set_footer(text="歌詞可能會有點不正確，請見諒。來源: Genius",icon_url="attachment://genius_icon.png")
            await interaction.response.send_message(file=genius_icon,embed=embed,ephemeral=True)
    
    @discord.ui.button(label=f"清除佇列", row=2, style=discord.ButtonStyle.gray, custom_id = "clear", emoji="🧹")
    async def clear_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        if interaction.guild.voice_client == None or interaction.user.voice == None or interaction.user.voice.channel != interaction.guild.voice_client.channel:
            return await interaction.response.send_message("你必須與機器人同個語音房才可使用按鈕")
        server = Server(str(interaction.guild_id))
        voice = get(bot.voice_clients,guild=interaction.guild)
        if voice.is_playing():
            server.queue = [server.queue[0]]
            server.save_data()
        else:
            server.queue = clear_track(server.queue)
            server.save_data()
            voice.stop()
        await interaction.response.send_message(f"已清除歌曲佇列裡所有的歌")
    
    @discord.ui.button(label=f"自動播放", row=2, style=discord.ButtonStyle.red, custom_id = "autoplay", emoji="✅")
    async def autoplay_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        if interaction.user.voice == None or interaction.user.voice.channel != interaction.guild.voice_client.channel:
            return await interaction.response.send_message("你必須與機器人同個語音房才可使用按鈕")
        server = Server(str(interaction.guild_id))
        if server.autoplay[0] == False:
            if [*server.autoplay[1]][0] == "None":
                return await interaction.response.send_message("你還未設定自動撥放的歌單")
            server.autoplay[0] = True
            button.style = discord.ButtonStyle.green
            button.emoji = "✅"
        else:
            server.autoplay[0] = False
            button.style = discord.ButtonStyle.red
            button.emoji = "❌"
        server.save_data()
        await interaction.response.edit_message(view=self)
    
    @discord.ui.button(label=f"中斷連線", row=2, style=discord.ButtonStyle.red, custom_id = "leave", emoji="👋")
    async def leave_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        if interaction.user.voice == None or interaction.user.voice.channel != interaction.guild.voice_client.channel:
            return await interaction.response.send_message("你必須與機器人同個語音房才可使用按鈕")
        voice = get(bot.voice_clients,guild=interaction.guild)
        server = Server(str(interaction.guild_id))
        if voice and voice.is_connected():
            if interaction.user.voice.channel == interaction.guild.voice_client.channel:
                voice.pause()
                time.sleep(1)
                server.queue = clear_track(server.queue)
                server.save_data()
                await interaction.guild.voice_client.disconnect()
                await interaction.response.send_message(content=f"記住我右邊的心跳...")
            else:
                await interaction.response.send_message(f"你需要跟我同一個通話才能請我出去")
        else:
            await interaction.response.send_message(f"我根本還沒進通話???")
            
class page_view(discord.ui.View):
    def __init__(self,server,playlist,mode):
        super().__init__()
        self.mode = mode
        if mode == "queue":
            queue = server.queue
        elif mode == "playlist":
            self.playlist = playlist
            queue = server.playlist[playlist]
        elif mode == "playlists":
            queue = [*server.playlist]
        self.page = 1
        self.back = [x for x in self.children if x.custom_id=="back_page"][0]
        self.back.disabled = True
        self.next = [x for x in self.children if x.custom_id=="next_page"][0]
        if len(queue) / 5 <= 1:
            self.next.disabled = True
        
    @discord.ui.button(label=f"", row=0, style=discord.ButtonStyle.gray, custom_id = "back_page", emoji="⬅️")
    async def back_page_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        server = Server(str(interaction.guild_id))
        if self.mode == "queue":
            queue = server.queue
            out = "歌曲佇列"
        elif self.mode == "playlist":
            queue = server.playlist[self.playlist]
            out = f"{self.playlist}裡的歌曲"
        elif self.mode == "playlists":
            queue = [*server.playlist]
            out = "歌單"
        self.page -= 1
        bot_icon = discord.File(f"{ASSETS}GuoYiTing.jpg", filename="bot_icon.png")
        embed=discord.Embed(title=f"**{out}**", description=f"length:{len(server.queue)}", color=0xbf70ff)
        for i in range((self.page-1)*5,self.page*5):
            if self.mode == "playlists":
                playlist = server.playlist[queue[i]]
                length = len(list(playlist.values())[i])
                embed.add_field(name=f"**{i+1}** | **{queue[i]}** - **{length}**", value="", inline=False)
            else:
                song = queue[i]
                length = song_length(list(song.values())[0]["length"])
                embed.add_field(name=f"**{i+1}** | **{[*song][0]}** - **{length[1]}:{length[2]}**", value="", inline=False)
        if self.page == 1:
            self.back.disabled = True
        if len(queue)-self.page*5 > 0:
            self.next.disabled = False
        else:
            self.next.disabled = True
        embed.set_footer(text="GuoYiTing Is Singing",icon_url="attachment://bot_icon.png")
        await interaction.response.edit_message(attachments=[bot_icon],embed=embed,view=self)
    
    @discord.ui.button(label=f"", row=0, style=discord.ButtonStyle.gray, custom_id = "next_page", emoji="➡️")
    async def next_page_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        server = Server(str(interaction.guild_id))
        if self.mode == "queue":
            queue = server.queue
            out = "歌曲佇列"
        elif self.mode == "playlist":
            queue = server.playlist[self.playlist]
            out = f"{self.playlist}裡的歌曲"
        elif self.mode == "playlists":
            queue = [*server.playlist]
            out = "歌單"
        bot_icon = discord.File(f"{ASSETS}GuoYiTing.jpg", filename="bot_icon.png")
        embed=discord.Embed(title=f"**{out}**", description=f"length:{len(server.queue)}", color=0xbf70ff)
        if len(queue)-self.page*5 > 5:
            for i in range(self.page*5,(self.page+1)*5):
                if self.mode == "playlists":
                    playlist = server.playlist[queue[i]]
                    length = len(list(playlist.values())[i])
                    embed.add_field(name=f"**{i+1}** | **{queue[i]}** - **{length}**", value="", inline=False)
                else:
                    song = queue[i]
                    length = song_length(list(song.values())[0]["length"])
                    embed.add_field(name=f"**{i+1}** | **{[*song][0]}** - **{length[1]}:{length[2]}**", value="", inline=False)
        else:
            for i in range(self.page*5,len(queue)):
                if self.mode == "playlists":
                    playlist = server.playlist[queue[i]]
                    length = len(list(playlist.values())[i])
                    embed.add_field(name=f"**{i+1}** | **{queue[i]}** - **{length}**", value="", inline=False)
                else:
                    song = queue[i]
                    length = song_length(list(song.values())[0]["length"])
                    embed.add_field(name=f"**{i+1}** | **{[*song][0]}** - **{length[1]}:{length[2]}**", value="", inline=False)
            self.next.disabled = True
        self.back.disabled = False
        self.page += 1
        embed.set_footer(text="GuoYiTing Is Singing",icon_url="attachment://bot_icon.png")
        await interaction.response.edit_message(attachments=[bot_icon],embed=embed,view=self)
########################################################################## Autocomplete
async def search_autocomplete(interaction:discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
    result = []
    driver.get(f"https://www.youtube.com")
    box = driver.find_element(By.XPATH,'/html/body/ytd-app/div[1]/div/ytd-masthead/div[4]/div[2]/ytd-searchbox/form/div[1]/div[1]/input')
    box.send_keys(current)
    box.send_keys(" "+Keys.BACKSPACE)
    driver.implicitly_wait(0.3)
    option = driver.find_elements(By.CLASS_NAME,'sbqs_c')
    for i in range(0,len(option)):
        result.append(app_commands.Choice(name=option[i].text, value=option[i].text))
        if len(result) == 15:
            break
    return result

async def playlist_autocomplete(interaction:discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
    server = Server(str(interaction.guild_id))
    result = []
    for name in [*server.playlist]:
        if current in name:
            result.append(app_commands.Choice(name=name, value=name))
        if len(result) == 15:
            break
    return result

async def prediction_topic_autocomplete(interaction:discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
    server = Server(str(interaction.guild_id))
    result = []
    for name in [*server.prediction]:
        if current in name:
            result.append(app_commands.Choice(name=name, value=name))
        if len(result) == 15:
            break
    return result

async def prediction_option_autocomplete(interaction:discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
    server = Server(str(interaction.guild_id))
    result = []
    topic = interaction.namespace.topic
    for name in [*server.prediction[topic]["options"]]:
        if current in name:
            result.append(app_commands.Choice(name=name, value=name))
        if len(result) == 15:
            break
    return result

async def wheel_topic_autocomplete(interaction:discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
    server = Server(str(interaction.guild_id))
    result = []
    for name in [*server.wheel]:
        if current in name:
            result.append(app_commands.Choice(name=name, value=name))
        if len(result) == 15:
            break
    return result

async def wheel_option_autocomplete(interaction:discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
    server = Server(str(interaction.guild_id))
    result = []
    topic = interaction.namespace.topic
    for name in server.wheel[topic]["options"]:
        if current in name:
            result.append(app_commands.Choice(name=name, value=name))
        if len(result) == 15:
            break
    return result

async def text_autocomplete(interaction:discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
    result = []
    async for message in interaction.channel.history(limit=100):
        if current in message.content:
            result.append(app_commands.Choice(name=message.content, value=str(message.id)))
        if len(result) == 15:
            break
    return result

async def help_autocomplete(interaction:discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
    result = []
    for info in [*HELP_INFO["Chinese"]]:
        if current in info:
            result.append(app_commands.Choice(name=info, value=info))
        if len(result) == 25:
            break
    return result

async def autoplay_mode_autocomplete(interaction:discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
    mode = ["weekly most stream","daily most stream","custom","server playlist","None"]
    result = []
    for info in mode:
        if current in info:
            result.append(app_commands.Choice(name=info, value=info))
        if len(result) == 25:
            break
    return result

async def autoplay_location_autocomplete(interaction:discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
    if interaction.namespace.mode != "server playlist" and interaction.namespace.mode != "None" and interaction.namespace.mode != "custom":
        mode = ["Global","Taiwan","America","Japan"]
    elif interaction.namespace.mode == "None":
        mode = ["None"]
    elif interaction.namespace.mode == "server playlist":
        server = Server(str(interaction.guild_id))
        mode = [*server.playlist]
    result = []
    for info in mode:
        if current in info:
            result.append(app_commands.Choice(name=info, value=info))
        if len(result) == 25:
            break
    return result

async def suggestion_mode_autocomplete(interaction:discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
    mode = ["weekly most stream","daily most stream","custom","server playlist"]
    result = []
    for info in mode:
        if current in info:
            result.append(app_commands.Choice(name=info, value=info))
        if len(result) == 25:
            break
    return result

async def suggestion_location_autocomplete(interaction:discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
    if interaction.namespace.mode != "server playlist" and interaction.namespace.mode != "custom":
        mode = ["Global","Taiwan","America","Japan"]
    if interaction.namespace.mode == "server playlist":
        server = Server(str(interaction.guild_id))
        mode = [*server.playlist]
    result = []
    for info in mode:
        if current in info:
            result.append(app_commands.Choice(name=info, value=info))
        if len(result) == 25:
            break
    return result

async def file_platform_autocomplete(interaction:discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
    platform = ["Youtube","Spotify","Apple Music","Niconico"]
    result = []
    for info in platform:
        if current in info:
            result.append(app_commands.Choice(name=info, value=info))
        if len(result) == 25:
            break
    return result

async def file_type_autocomplete(interaction:discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
    if interaction.namespace.platform == "Spotify" or interaction.namespace.platform == "Apple Music":
        type = ["Audio"]
    else:
        type = ["Video","Audio"]
    result = []
    for info in type:
        if current in info:
            result.append(app_commands.Choice(name=info, value=info))
        if len(result) == 25:
            break
    return result

async def file_filetype_autocomplete(interaction:discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
    if interaction.namespace.type == "Audio":
        filetype = ["mp3","webm","m4a"]
    elif interaction.namespace.type == "Video":
        filetype = ["mp4","webm","wav","mov"]
    result = []
    for info in filetype:
        if current in info:
            result.append(app_commands.Choice(name=info, value=info))
        if len(result) == 25:
            break
    return result
########################################################################## Event
@bot.event
async def on_voice_state_update(member:discord.Member,before:discord.VoiceState,after:discord.VoiceState):
    server = Server(str(member.guild.id))
    if before.channel:
        voice = get(bot.voice_clients,guild=member.guild)
        if voice and voice.is_connected():
            if voice.channel == before.channel:
                if len(before.channel.members) == 1:
                    time.sleep(10)
                    if len(before.channel.members) == 1:
                        voice.pause()
                        time.sleep(1)
                        server = Server(str(member.guild.id))
                        server.queue = clear_track(server.queue)
                        server.save_data()
                        await voice.disconnect()
        if before.channel.id in server.temporary_voice_channel["temporary"]:
            if len(before.channel.members) == 0:
                server.temporary_voice_channel["temporary"].remove(before.channel.id)
                server.save_management()
                await before.channel.delete()
    if after.channel:
        if after.channel.id == server.temporary_voice_channel["default"] and member.id != bot.user.id:
            if member.nick == None:
                channel = await member.guild.create_voice_channel(name=f"{member.display_name}的頻道",category=after.channel.category)
            else:
                channel = await member.guild.create_voice_channel(name=f"{member.nick}的頻道",category=after.channel.category)
            await channel.edit(sync_permissions=True)
            await member.move_to(channel)
            server.temporary_voice_channel["temporary"].append(channel.id)
            server.save_management()
        if member.id == bot.user.id and before.channel != after.channel:
            voice = get(bot.voice_clients,guild=member.guild)
            if voice:
                if before.channel:
                    voice.pause()
                    time.sleep(1)
                    server = Server(str(member.guild.id))
                    server.queue = clear_track(server.queue)
                    server.save_data()
                    await voice.disconnect()
                    
@bot.event
async def on_member_join(member:discord.Member):
    server = Server(str(member.guild.id))
    if server.welcome_channel != "":
        channel = bot.get_channel(server.welcome_channel)
        await channel.send(f"歡迎<@{member.id}>來到**{member.guild.name}**")
  
@bot.event  
async def on_member_remove(member:discord.Member):
    if member.id != bot.application_id:
        server = Server(str(member.guild.id))
        if server.leave_channel != "":
            channel = bot.get_channel(server.leave_channel)
            await channel.send(f"<@{member.id}>離開了**{member.guild.name}** o7")
        
@bot.event         
async def on_reaction_add(reaction:discord.Reaction, user:discord.Member):
    server = Server(str(user.guild.id))
    if reaction.emoji == "✅" and reaction.message.id == server.role_message:
        if server.basic_role != "":
            role = user.guild.get_role(server.basic_role)
            await user.add_roles(role)
    elif reaction.emoji == "📥" and user.id in server.emote_save:
        message = reaction.message.content
        embeds = reaction.message.embeds
        attachments = reaction.message.attachments
        files = []
        for attachment in attachments:
            files.append(await attachment.to_file())
        message += f"\n-{reaction.message.author.name}(**User ID**: {reaction.message.author.id})(**Guild**: {reaction.message.guild.name}, **Channel**: {reaction.message.channel.name})(**Time Sent**: {reaction.message.created_at})"
        if user.dm_channel != None:
            await user.dm_channel.send(message,embeds=embeds,files=files)
        else:
            await user.create_dm()
            await user.dm_channel.send(message,embeds=embeds,files=files)
                    
@bot.event         
async def on_reaction_remove(reaction:discord.Reaction, user:discord.Member):
    server = Server(str(user.guild.id))
    if reaction.emoji == "✅" and reaction.message.id == server.role_message:
        if server.basic_role != "":
            role = user.guild.get_role(server.basic_role)
            await user.remove_roles(role)
                    
@bot.event
async def on_message(message:discord.Message):
    if message.author.id != bot.user.id:
        test_list = ['.com', '.ru', '.net', '.org', '.info', '.biz', '.io', '.co', "https://", "http://"]
        link_matches = [ele for ele in test_list if(ele in message.content)]
        if "https://" in link_matches or "http://" in link_matches and len(link_matches) > 1:
            server = Server(str(message.guild.id))
            if server.scam_prevent["URL"] != "None":
                if server.scam_prevent["URL"] == "Low":
                    threshold = 3
                elif server.scam_prevent["URL"] == "Medium":
                    threshold = 1
                else:
                    threshold = 0
                link = message.content.split(link_matches[len(link_matches)-1])[1].split(link_matches[0])[0]
                link = f"{link_matches[len(link_matches)-1]}{link}{link_matches[0]}"
                analysis = await virustotal.scan_url_async(link,wait_for_completion=True)
                stats = analysis.get("stats")
                if stats["malicious"] > threshold or stats["suspicious"] > threshold:
                    await message.delete()
                    if message.author.dm_channel != None:
                        return await message.author.dm_channel.send("您剛剛傳送的連結不安全，注意您帳號是否安全")
                    else:
                        await message.author.create_dm()
                        return await message.author.dm_channel.send("您剛剛傳送的連結不安全，注意您帳號是否安全")
        if len(message.attachments) != 0:
            server = Server(str(message.guild.id))
            if server.scam_prevent["File"] != "None":
                if server.scam_prevent["File"] == "Low":
                    threshold = 3
                elif server.scam_prevent["File"] == "Medium":
                    threshold = 1
                else:
                    threshold = 0
                for file in message.attachments:
                    if file.content_type == None or "image" not in file.content_type and "video" not in file.content_type and "audio" not in file.content_type:
                        await file.save(f"{FILES}{file.filename}")
                        analysis = await virustotal.scan_file_async(open(f"{FILES}{file.filename}", "rb"), wait_for_completion=True)
                        stats = analysis.get("stats")
                        if stats["malicious"] > threshold or stats["suspicious"] > threshold:
                            await message.delete()
                            os.remove(f"{FILES}{file.filename}")
                            if message.author.dm_channel != None:
                                return await message.author.dm_channel.send("您剛剛傳送的檔案不安全，注意您帳號是否安全")
                            else:
                                await message.author.create_dm()
                                return await message.author.dm_channel.send("您剛剛傳送的檔案不安全，注意您帳號是否安全")
        if type(message.channel) == discord.DMChannel:
            if "新年快樂" in message.content:
                if message.author.dm_channel != None:
                    return await message.author.dm_channel.send("新年快樂!")
                else:
                    await message.author.create_dm()
                    return await message.author.dm_channel.send("新年快樂!")
    if bot.user.mentioned_in(message):
        text = message.content.lower()
        if "search" in text:
            text = text.split("search")[1]
            service = Service()
            options = webdriver.ChromeOptions()
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            options.add_experimental_option("detach", True)
            #options.add_argument('--headless')
            driver = webdriver.Chrome(service=service, options=options)
            driver.get(f"https://www.google.com")
            box = driver.find_element(By.XPATH,'/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/textarea')
            box.send_keys(text)
            box.send_keys(Keys.ENTER)
            website = driver.find_element(By.CLASS_NAME,'LC20lb MBeuO DKV0Md')
            print(website)

@bot.event
async def on_guild_remove(guild:discord.Guild):
    os.remove(f"{BOT_FOLDER}/Server/{guild.id}.json")
                 
@bot.tree.error
async def on_error(interaction:discord.Interaction,error:discord.app_commands.AppCommandError):
    print(error)
    await interaction.followup.send(content="機器人好像出了點差錯!可以再試幾次，如果還是不行可以向我們反映")
    
########################################################################## Listener
@bot.listen("on_reaction_add")         
async def role_message_reaction(reaction:discord.Reaction, user:discord.Member):
    server = Server(str(user.guild.id))
    if reaction.emoji == "✅" and reaction.message.id == server.role_message:
        if server.basic_role != "":
            role = user.guild.get_role(server.basic_role)
            await user.add_roles(role)
    elif reaction.emoji == "📥" and user.id in server.emote_save:
        message = reaction.message.content
        embeds = reaction.message.embeds
        attachments = reaction.message.attachments
        files = []
        for attachment in attachments:
            files.append(await attachment.to_file())
        message += f"\n-{reaction.message.author.name}(**User ID**: {reaction.message.author.id})(**Guild**: {reaction.message.guild.name}, **Channel**: {reaction.message.channel.name})(**Time Sent**: {reaction.message.created_at})"
        if user.dm_channel != None:
            await user.dm_channel.send(message,embeds=embeds,files=files)
        else:
            await user.create_dm()
            await user.dm_channel.send(message,embeds=embeds,files=files)
########################################################################## MUSIC BOT TRACKING
def ending_track(interaction:discord.Interaction,message):
    server = Server(str(interaction.guild_id))
    next_track(server.queue,server.repeat)
    server.save_data()
    if len(server.queue) == 0:
        if server.autoplay[0] == True and server.repeat == "None" and interaction.guild.voice_client.is_connected():
            if [*server.autoplay[1]][0] == "server playlist":
                try:
                    x = random.randint(0,len(server.playlist[list(server.autoplay[1].values())[0]])-1)
                    suggestion = server.playlist[server.autoplay[1].values()[0]][x]
                    server.queue.append(suggestion)
                except:
                    server.autoplay = [False,{"None":"None"}]
                    asyncio.run_coroutine_threadsafe(interaction.channel.send("自動撥放的歌單已不存在"), bot.loop)
            elif [*server.autoplay[1]][0] == "custom":
                try:
                    suggestion = auto_suggestion([*server.autoplay[1]][0],list(server.autoplay[1].values())[0])
                    infos = spotify_download(suggestion)
                    for info in infos:
                        title = f"{info["artist"]} - {info["title"]}"
                        valid_title = info["valid_title"]
                        artist = info["artist"]
                        length = info["length"]
                        thumbnail = f"attachment://song_icon.png"
                        server.queue.append({valid_title:{"platform":"Spotify","title":title,"length":length,"artist":artist,"url":suggestion,"thumbnail":thumbnail}})
                except:
                    server.autoplay = [False,{"None":"None"}]
                    asyncio.run_coroutine_threadsafe(interaction.channel.send("自動撥放的歌單已不存在"), bot.loop)
            else:
                try:
                    suggestion = auto_suggestion([*server.autoplay[1]][0],list(server.autoplay[1].values())[0])
                    infos = spotify_download(suggestion)
                    for info in infos:
                        title = f"{info["artist"]} - {info["title"]}"
                        valid_title = info["valid_title"]
                        artist = info["artist"]
                        length = info["length"]
                        thumbnail = f"attachment://song_icon.png"
                        server.queue.append({valid_title:{"platform":"Spotify","title":title,"length":length,"artist":artist,"url":suggestion,"thumbnail":thumbnail}})
                except:
                    server.autoplay = [False,{"None":"None"}]
                    asyncio.run_coroutine_threadsafe(interaction.channel.send("自動撥放的歌單已不存在"), bot.loop)
            server.save_data()
    if len(server.queue) != 0:
        voice = get(bot.voice_clients,guild=interaction.guild)
        platform = list(server.queue[0].values())[0]["platform"]
        title = [*server.queue[0]][0]
        length = song_length(list(server.queue[0].values())[0]["length"])
        platform = list(server.queue[0].values())[0]["platform"]
        #
        thumbnail = thumbnail_easter_egg(title,list(server.queue[0].values())[0]["thumbnail"])
        #
        count = list(server.queue[0].values())[0]["length"]
        platform_icon = discord.File(f"{ASSETS}{platform} icon.png", filename="platform_icon.png")
        bot_icon = discord.File(f"{ASSETS}GuoYiTing.jpg", filename="bot_icon.png")
        embed = discord.Embed(title=f"**{title}**", url=list(server.queue[0].values())[0]["url"], color=0xbf70ff)
        embed.add_field(name="**∥ 正在撥放：**",value=f'\n                                           ♫\n▶︎ ● ｜{0*"<:bar:1289648502489747570>"}<:dot:1289644466860458048>{18*"<:bar:1289648502489747570>"}\n\n 00:00 / {length[1]}:{length[2]} \n',inline=False)
        if len(server.queue) > 1:
            embed.add_field(name="→【下一首歌曲】",value=f"**{[*server.queue[1]][0]}**",inline=False)
        embed.set_author(name=platform,icon_url="attachment://platform_icon.png")
        embed.set_footer(text="GuoYiTing Is Singing",icon_url="attachment://bot_icon.png")
        if platform == "Youtube":
            embed.set_thumbnail(url=thumbnail)
            asyncio.run_coroutine_threadsafe(message.edit(content=f"正在播放**{title}({length[1]}:{length[2]})**",embed=embed,attachments=[bot_icon,platform_icon]), bot.loop)
        else:
            song_icon = discord.File(f"{AUDIO}{platform}/{title}.png", filename=f"song_icon.png")
            embed.set_thumbnail(url=thumbnail)
            asyncio.run_coroutine_threadsafe(message.edit(content=f"正在播放**{title}({length[1]}:{length[2]})**",embed=embed,attachments=[bot_icon,platform_icon,song_icon]), bot.loop)
        source = AudioSourceTracked(FFmpegPCMAudio(executable=f"{BOT_FOLDER}ffmpeg/bin/ffmpeg.exe", source=f"{AUDIO}{platform}/{title}.mp4"),server)
        voice.play(source,after = lambda e: ending_track(interaction,message))
        time.sleep(1)
        server.time = 0
        while server.time < count-1 and len(server.queue) > 0 and voice.is_playing():
            time.sleep(1)
            try:
                server = Server(str(interaction.guild_id))
            except:
                pass
            c = int(server.time*(18/count))
            duration = song_length(server.time)
            embed = discord.Embed(title=f"**{title}**", url=list(server.queue[0].values())[0]["url"], color=0xbf70ff)
            embed.set_author(name=platform,icon_url="attachment://platform_icon.png")
            embed.set_footer(text="GuoYiTing Is Singing",icon_url="attachment://bot_icon.png")
            embed.add_field(name="**∥ 正在撥放：**",value=f'\n                                           ♫\n▶︎ ● ｜{c*"<:bar:1289648502489747570>"}<:dot:1289644466860458048>{(18-c)*"<:bar:1289648502489747570>"}\n\n {duration[1]}:{duration[2]} / {length[1]}:{length[2]} \n',inline=False)
            if len(server.queue) > 1:
                embed.add_field(name="→【下一首歌曲】",value=f"**{[*server.queue[1]][0]}**",inline=False)
            embed.set_thumbnail(url=thumbnail)
            asyncio.run_coroutine_threadsafe(message.edit(embed=embed), bot.loop)
    else:
        time.sleep(1)
        asyncio.run_coroutine_threadsafe(message.edit(content="歌單已結束",embed=None,view=None,attachments=[]), bot.loop)
        
class AudioSourceTracked(discord.AudioSource):
    def __init__(self, source, server):
        self._source = source
        self.count_20ms = 0
        self.server = server

    def read(self) -> bytes:
        data = self._source.read()
        if data:
            self.count_20ms += 1
            if self.count_20ms % 50 == 0:
                self.server.time = int(self.count_20ms * 0.02)
                self.server.save_time()
        return data
########################################################################## MUSIC BOT
@bot.tree.command(name="join", description="加入你所在的頻道")
async def join(interaction:discord.Interaction):
    await interaction.response.defer()
    await asyncio.sleep(0)
    voice = get(bot.voice_clients,guild=interaction.guild)
    if interaction.user.voice == None:
        await interaction.followup.send(f"你必須處在通話裡才可邀請我進去")
    else:
        channel = interaction.user.voice.channel
        if voice and voice.channel == channel:
            return await interaction.followup.send(f"早已加入**{channel.name}**")
        if voice and voice.is_connected() and voice.channel != channel:
            await voice.move_to(channel)
        else:
            await channel.connect()
        await interaction.followup.send(f"已加入**{channel.name}**")
        
@bot.tree.command(name="leave", description="離開並清空歌曲佇列")
async def leave(interaction:discord.Interaction):
    await interaction.response.defer()
    await asyncio.sleep(0)
    voice = get(bot.voice_clients,guild=interaction.guild)
    server = Server(str(interaction.guild_id))
    if voice and voice.is_connected():
        if interaction.user.voice != None:
            if interaction.user.voice.channel == interaction.guild.voice_client.channel:
                voice.pause()
                time.sleep(1)
                server.queue = clear_track(server.queue)
                server.save_data()
                await interaction.guild.voice_client.disconnect()
                await interaction.followup.send(f"記住我右邊的心跳...")
            else:
                await interaction.followup.send(f"你需要跟我同一個通話才能請我出去")
        else:
            await interaction.followup.send(f"你需要跟我同一個通話才能請我出去")
    else:
        await interaction.followup.send(f"我根本還沒進通話???")

@bot.tree.command(name="play", description="撥放歌曲")
@app_commands.describe(search="name or url of track")
#@app_commands.autocomplete(search = search_autocomplete)
async def play(interaction:discord.Interaction, search:str):
    await interaction.response.defer()
    await asyncio.sleep(0)
    voice = get(bot.voice_clients,guild=interaction.guild)
    if interaction.user.voice == None:
        return await interaction.followup.send(f"你必須處在通話裡才可邀請我進去")
    server = Server(str(interaction.guild_id))
    original_queue = len(server.queue)
    if is_url(search):
        media = media_type(search)
        if media == "apple music":
            infos = apple_music_download(search)
            for info in infos:
                title = f"{info["artist"]} - {info["title"]}"
                valid_title = info["valid_title"]
                artist = info["artist"]
                length = info["length"]
                thumbnail = f"attachment://song_icon.png"
                server.queue.append({valid_title:{"platform":"Apple Music","title":title,"length":length,"artist":artist,"url":search,"thumbnail":thumbnail}})
        elif media == "spotify":
            infos = spotify_download(search)
            for info in infos:
                title = f"{info["artist"]} - {info["title"]}"
                valid_title = info["valid_title"]
                artist = info["artist"]
                length = info["length"]
                thumbnail = f"attachment://song_icon.png"
                server.queue.append({valid_title:{"platform":"Spotify","title":title,"length":length,"artist":artist,"url":search,"thumbnail":thumbnail}})
        elif media == "youtube":
            if "playlist" in search:
                list_info = youtube_info_extract(search)
                for i in range(0,list_info["playlist_count"]):
                    url = list_info['entries'][i]["webpage_url"]
                    info = youtube_download(url)
                    title = info["title"]
                    valid_title = info["valid_title"]
                    artist = info["artist"]
                    length = info["length"]
                    thumbnail = info["thumbnail"]
                    server.queue.append({valid_title:{"platform":"Youtube","title":title,"length":length,"artist":artist,"url":url,"thumbnail":thumbnail}})
            else:
                info = youtube_download(search)
                title = info["title"]
                valid_title = info["valid_title"]
                artist = info["artist"]
                length = info["length"]
                thumbnail = info["thumbnail"]
                server.queue.append({valid_title:{"platform":"Youtube","title":title,"length":length,"artist":artist,"url":search,"thumbnail":thumbnail}})
    else:
        ytdl_options = {'noplaylist': True,'default_search': 'auto'}
        with YoutubeDL(ytdl_options) as ydl:
            video = ydl.extract_info(f"ytsearch1:{search}", download = False)
        result = video["entries"][0]["webpage_url"]
        info = youtube_download(result)
        title = info["title"]
        valid_title = info["valid_title"]
        artist = info["artist"]
        length = info["length"]
        thumbnail = info["thumbnail"]
        server.queue.append({valid_title:{"platform":"Youtube","title":title,"length":length,"artist":artist,"url":result,"thumbnail":thumbnail}})
    server.save_data()
    channel = interaction.user.voice.channel
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        await channel.connect()
    voice = get(bot.voice_clients,guild=interaction.guild)
    if original_queue > 0:
        length = song_length(length)
        await interaction.followup.send(f"**{title}({length[1]}:{length[2]})**已被加入到**{len(server.queue)}**的位置")
    else:
        title = [*server.queue[0]][0]
        length = song_length(list(server.queue[0].values())[0]["length"])
        platform = list(server.queue[0].values())[0]["platform"]
        #
        thumbnail = thumbnail_easter_egg(title,list(server.queue[0].values())[0]["thumbnail"])
        #
        count = list(server.queue[0].values())[0]["length"]
        platform_icon = discord.File(f"{ASSETS}{platform} icon.png", filename="platform_icon.png")
        bot_icon = discord.File(f"{ASSETS}GuoYiTing.jpg", filename="bot_icon.png")
        embed = discord.Embed(title=f"**{title}**", url=list(server.queue[0].values())[0]["url"], color=0xbf70ff)
        embed.add_field(name="**∥ 正在撥放：**",value=f'\n                                           ♫\n▶︎ ● ｜{0*"<:bar:1289648502489747570>"}<:dot:1289644466860458048>{18*"<:bar:1289648502489747570>"}\n\n 00:00 / {length[1]}:{length[2]} \n',inline=False)
        if len(server.queue) > 1:
            embed.add_field(name="→【下一首歌曲】",value=f"**{[*server.queue[1]][0]}**",inline=False)
        embed.set_author(name=platform,icon_url="attachment://platform_icon.png")
        embed.set_footer(text="GuoYiTing Is Singing",icon_url="attachment://bot_icon.png")
        view = play_view(server)
        if platform == "Youtube":
            embed.set_thumbnail(url=thumbnail)
            message = await interaction.followup.send(f"正在播放**{title}({length[1]}:{length[2]})**",files=[bot_icon,platform_icon],embed=embed,view=view)
        else:
            song_icon = discord.File(f"{AUDIO}{platform}/{title}.png", filename=f"song_icon.png")
            embed.set_thumbnail(url=thumbnail)
            message = await interaction.followup.send(f"正在播放**{title}({length[1]}:{length[2]})**",files=[bot_icon,platform_icon,song_icon],embed=embed,view=view)
        source = AudioSourceTracked(FFmpegPCMAudio(executable=f"{BOT_FOLDER}ffmpeg/bin/ffmpeg.exe",source=f"{AUDIO}{platform}/{title}.mp4"), server)
        voice.play(source, after=lambda e: ending_track(interaction,message))
        time.sleep(1)
        server.time = 0
        while server.time < count-1 and len(server.queue) > 0 and voice.is_playing():
            time.sleep(1)
            try:
                server = Server(str(interaction.guild_id))
            except:
                pass
            c = int(server.time*(18/count))
            duration = song_length(server.time)
            embed = discord.Embed(title=f"**{title}**", url=list(server.queue[0].values())[0]["url"], color=0xbf70ff)
            embed.set_author(name=platform,icon_url="attachment://platform_icon.png")
            embed.set_footer(text="GuoYiTing Is Singing",icon_url="attachment://bot_icon.png")
            embed.add_field(name="**∥ 正在撥放：**",value=f'\n                                           ♫\n▶︎ ● ｜{c*"<:bar:1289648502489747570>"}<:dot:1289644466860458048>{(18-c)*"<:bar:1289648502489747570>"}\n\n {duration[1]}:{duration[2]} / {length[1]}:{length[2]} \n',inline=False)
            if len(server.queue) > 1:
                embed.add_field(name="→【下一首歌曲】",value=f"**{[*server.queue[1]][0]}**",inline=False)
            embed.set_thumbnail(url=thumbnail)
            await message.edit(embed=embed)
            
@bot.tree.command(name="playfile", description="撥放檔案音訊")
@app_commands.describe(file="the file you want to play")
async def playfile(interaction:discord.Interaction,file:discord.Attachment):
    await interaction.response.defer()
    await asyncio.sleep(0)
    if interaction.user.voice == None or interaction.guild.voice_client == None or interaction.user.voice.channel != interaction.guild.voice_client.channel:
        return await interaction.followup.send("你必須與機器人同個語音房才可使用此指令")
    server = Server(str(interaction.guild_id))
    server.save_data()
    await interaction.followup.send(file=file)
    
@bot.tree.command(name="skip", description="跳過當前歌曲")
async def skip(interaction:discord.Interaction):
    await interaction.response.defer()
    await asyncio.sleep(0)
    if interaction.user.voice == None or interaction.guild.voice_client == None or interaction.user.voice.channel != interaction.guild.voice_client.channel:
        return await interaction.followup.send("你必須與機器人同個語音房才可使用此指令")
    server = Server(str(interaction.guild_id))
    if len(server.queue) == 0:
        return await interaction.followup.send("歌單裡沒有歌曲")
    voice = get(bot.voice_clients,guild=interaction.guild)
    song = server.queue[0]
    length = song_length(list(song.values())[0]["length"])
    server.save_data()
    voice.pause()
    time.sleep(1)
    voice.stop()
    await interaction.followup.send(f"已跳過**{[*song][0]}({length[1]}:{length[2]})**")
    
@bot.tree.command(name="back", description="撥放前一首歌曲")
async def back(interaction:discord.Interaction):
    await interaction.response.defer()
    await asyncio.sleep(0)
    if interaction.user.voice == None or interaction.guild.voice_client == None or interaction.user.voice.channel != interaction.guild.voice_client.channel:
        return await interaction.followup.send("你必須與機器人同個語音房才可使用此指令")
    server = Server(str(interaction.guild_id))
    if len(server.queue) == 0:
        return await interaction.followup.send("歌單裡沒有歌曲")
    voice = get(bot.voice_clients,guild=interaction.guild)
    if server.repeat == "None":
        await interaction.followup.send(f"前一首歌不存在(或許你應該試著將循環播放設成**All**)")
    elif server.repeat == "One Song":
        voice.stop()
        await interaction.followup.send(f"已重播目前這首歌(或許你應該試著將循環播放設成**All**)")
    elif server.repeat == "All":
        previous_track(server.queue)
        previous_track(server.queue)
        voice.pause()
        time.sleep(1)
        voice.stop()
        server.save_data()
        await interaction.followup.send(f"正在播放上一首歌")
    
@bot.tree.command(name="clear", description="清空歌曲佇列")
async def clear(interaction:discord.Interaction):
    await interaction.response.defer()
    await asyncio.sleep(0)
    if interaction.user.voice == None or interaction.guild.voice_client == None or interaction.user.voice.channel != interaction.guild.voice_client.channel:
        return await interaction.followup.send("你必須與機器人同個語音房才可使用此指令")
    server = Server(str(interaction.guild_id))
    voice = get(bot.voice_clients,guild=interaction.guild)
    if voice.is_playing():
        server.queue = [server.queue[0]]
        server.save_data()
    else:
        server.queue = clear_track(server.queue)
        server.save_data()
        voice.stop()
    await interaction.followup.send(f"已清除歌曲佇列裡所有的歌")
    
@bot.tree.command(name="delete", description="刪除歌曲")
@app_commands.describe(track="number of the track you want to delete")
async def delete(interaction:discord.Interaction, track:int):
    await interaction.response.defer()
    await asyncio.sleep(0)
    if interaction.user.voice == None or interaction.guild.voice_client == None or interaction.user.voice.channel != interaction.guild.voice_client.channel:
        return await interaction.followup.send("你必須與機器人同個語音房才可使用此指令")
    server = Server(str(interaction.guild_id))
    if track < 0 or track > len(server.queue):
        await interaction.followup.send(f"你給予的數字已超過歌曲佇列的大小了")
    else:
        voice = get(bot.voice_clients,guild=interaction.guild)
        if track == 0:
            if voice.is_playing():
                return await interaction.followup.send("你無法刪除正在播放的曲目")
            else:
                if server.repeat == "None":
                    voice.stop()
                elif server.repeat == "One Song":
                    delete_track(server.queue,track)
                    server.save_data()
                    voice.stop()
                elif server.repeat == "All":
                    previous_track(server.queue)
                    server.queue.pop(1)
                    server.save_data()
                    voice.stop()
        else:
            delete_track(server.queue,track)
            server.save_data()
        await interaction.followup.send(f"已刪除第**{track}**首歌")
    
@bot.tree.command(name="jump", description="跳至指定歌曲")
@app_commands.describe(track="number of the track you want to jump to")
async def jump(interaction:discord.Interaction, track:int):
    await interaction.response.defer()
    await asyncio.sleep(0)
    if interaction.user.voice == None or interaction.guild.voice_client == None or interaction.user.voice.channel != interaction.guild.voice_client.channel:
        return await interaction.followup.send("你必須與機器人同個語音房才可使用此指令")
    server = Server(str(interaction.guild_id))
    if track > len(server.queue):
        await interaction.followup.send(f"你給予的數字已超過歌曲佇列的大小了")
    else:
        voice = get(bot.voice_clients,guild=interaction.guild)
        jump_track(server.queue,track,server.repeat)
        if server.repeat == "One Song":
            server.queue.pop(0)
        server.save_data()
        voice.pause()
        time.sleep(1)
        voice.stop()
        await interaction.followup.send(f"跳到第**{track}**首歌")
    
@bot.tree.command(name="queue", description="歌曲佇列")
async def queue(interaction:discord.Interaction):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    bot_icon = discord.File(f"{ASSETS}GuoYiTing.jpg", filename="bot_icon.png")
    embed=discord.Embed(title="**歌曲佇列**", description=f"length:{len(server.queue)}", color=0xbf70ff)
    if len(server.queue) > 5:
        for i in range(0,5):
            song = server.queue[i]
            length = song_length(list(song.values())[0]["length"])
            embed.add_field(name=f"**{i+1}** | **{[*song][0]}** - **{length[1]}:{length[2]}**", value="", inline=False)
    else:
        for i in range(0,len(server.queue)):
            song = server.queue[i]
            length = song_length(list(song.values())[0]["length"])
            embed.add_field(name=f"**{i+1}** | **{[*song][0]}** - **{length[1]}:{length[2]}**", value="", inline=False)
    embed.set_footer(text="GuoYiTing Is Singing",icon_url="attachment://bot_icon.png")
    view = page_view(server,None,"queue")
    await interaction.followup.send(files=[bot_icon],embed=embed,view=view)
    
@bot.tree.command(name="loop", description="改變循環播放樣式")
async def loop(interaction:discord.Interaction):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    if server.repeat == "One Song":
        server.repeat = "All"
        output = "全部"
    elif server.repeat == "All":
        server.repeat = "None"
        output = "無"
    elif server.repeat == "None":
        server.repeat = "One Song"
        output = "單首"
    server.save_data()
    await interaction.followup.send(f"循環播放**{output}**")
    
@bot.tree.command(name="replay", description="重播")
async def replay(interaction:discord.Interaction):
    await interaction.response.defer()
    await asyncio.sleep(0)
    if interaction.user.voice == None or interaction.guild.voice_client == None or interaction.user.voice.channel != interaction.guild.voice_client.channel:
        return await interaction.followup.send("你必須與機器人同個語音房才可使用此指令")
    server = Server(str(interaction.guild_id))
    if len(server.queue) == 0:
        return await interaction.followup.send("歌單裡沒有歌曲")
    voice = get(bot.voice_clients,guild=interaction.guild)
    if server.repeat == "None":
        song = server.queue[0]
        server.queue.insert(0,song)
        server.save_data()
        voice.pause()
        time.sleep(1)
        voice.stop()
        await interaction.followup.send(f"已重播**{[*server.queue[0]][0]}**")
    elif server.repeat == "All" and len(server.queue) > 1:
        previous_track(server.queue)
        server.save_data()
        voice.pause()
        time.sleep(1)
        voice.stop()
        await interaction.followup.send(f"已重播**{[*server.queue[1]][0]}**")
    else:
        voice.pause()
        time.sleep(1)
        voice.stop()
        await interaction.followup.send(f"已重播**{[*server.queue[0]][0]}**")
    
@bot.tree.command(name="nowplay", description="目前正在播放的歌曲")
async def nowplay(interaction:discord.Interaction):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    voice = get(bot.voice_clients,guild=interaction.guild)
    if len(server.queue) == 0:
        await interaction.followup.send(f"目前沒有在播放歌曲")
    else:
        title = [*server.queue[0]][0]
        length = song_length(list(server.queue[0].values())[0]["length"])
        platform = list(server.queue[0].values())[0]["platform"]
        #
        thumbnail = thumbnail_easter_egg(title,list(server.queue[0].values())[0]["thumbnail"])
        #
        count = list(server.queue[0].values())[0]["length"]
        platform_icon = discord.File(f"{ASSETS}{platform} icon.png", filename="platform_icon.png")
        bot_icon = discord.File(f"{ASSETS}GuoYiTing.jpg", filename="bot_icon.png")
        embed = discord.Embed(title=f"**{title}**", url=list(server.queue[0].values())[0]["url"], color=0xbf70ff)
        embed.add_field(name="**∥ 正在撥放：**",value=f'\n                                           ♫\n▶︎ ● ｜{0*"<:bar:1289648502489747570>"}<:dot:1289644466860458048>{18*"<:bar:1289648502489747570>"}\n\n 00:00 / {length[1]}:{length[2]} \n',inline=False)
        if len(server.queue) > 1:
            embed.add_field(name="→【下一首歌曲】",value=f"**{[*server.queue[1]][0]}**",inline=False)
        embed.set_author(name=platform,icon_url="attachment://platform_icon.png")
        embed.set_footer(text="GuoYiTing Is Singing",icon_url="attachment://bot_icon.png")
        view = play_view(server)
        if platform == "Youtube":
            embed.set_thumbnail(url=thumbnail)
            message = await interaction.followup.send(f"正在播放**{title}({length[1]}:{length[2]})**",files=[bot_icon,platform_icon],embed=embed,view=view)
        else:
            song_icon = discord.File(f"{AUDIO}{platform}/{title}.png", filename=f"song_icon.png")
            embed.set_thumbnail(url=thumbnail)
            message = await interaction.followup.send(f"正在播放**{title}({length[1]}:{length[2]})**",files=[bot_icon,platform_icon,song_icon],embed=embed,view=view)
        while server.time < count-1 and len(server.queue) > 0 and voice.is_playing():
            time.sleep(1)
            try:
                server = Server(str(interaction.guild_id))
            except:
                pass
            c = int(server.time*(18/count))
            duration = song_length(server.time)
            embed = discord.Embed(title=f"**{title}**", url=list(server.queue[0].values())[0]["url"], color=0xbf70ff)
            embed.set_author(name=platform,icon_url="attachment://platform_icon.png")
            embed.set_footer(text="GuoYiTing Is Singing",icon_url="attachment://bot_icon.png")
            embed.add_field(name="**∥ 正在撥放：**",value=f'\n                                           ♫\n▶︎ ● ｜{c*"<:bar:1289648502489747570>"}<:dot:1289644466860458048>{(18-c)*"<:bar:1289648502489747570>"}\n\n {duration[1]}:{duration[2]} / {length[1]}:{length[2]} \n',inline=False)
            if len(server.queue) > 1:
                embed.add_field(name="→【下一首歌曲】",value=f"**{[*server.queue[1]][0]}**",inline=False)
            embed.set_thumbnail(url=thumbnail)
            await message.edit(embed=embed)
    
@bot.tree.command(name="pause", description="暫停播放歌曲")
async def pause(interaction:discord.Interaction):
    await interaction.response.defer()
    await asyncio.sleep(0)
    if interaction.user.voice == None or interaction.guild.voice_client == None or interaction.user.voice.channel != interaction.guild.voice_client.channel:
        return await interaction.followup.send("你必須與機器人同個語音房才可使用此指令")
    server = Server(str(interaction.guild_id))
    voice = get(bot.voice_clients,guild=interaction.guild)
    if voice.is_playing():
        voice.pause()
        await interaction.followup.send("已暫停")
    else:
        await interaction.followup.send("目前沒有音樂在播放")
    
@bot.tree.command(name="resume", description="繼續播放歌曲")
async def resume(interaction:discord.Interaction):
    await interaction.response.defer()
    await asyncio.sleep(0)
    if interaction.user.voice == None or interaction.guild.voice_client == None or interaction.user.voice.channel != interaction.guild.voice_client.channel:
        return await interaction.followup.send("你必須與機器人同個語音房才可使用此指令")
    server = Server(str(interaction.guild_id))
    voice = get(bot.voice_clients,guild=interaction.guild)
    if voice.is_paused():
        voice.resume()
        await interaction.followup.send("已重新開始播放")
    else:
        await interaction.followup.send("目前沒有音樂被暫停")
    
@bot.tree.command(name="autoplay", description="自動播放歌曲")
@app_commands.autocomplete(mode = autoplay_mode_autocomplete)
@app_commands.autocomplete(location = autoplay_location_autocomplete)
async def autoplay(interaction:discord.Interaction,mode:str,location:str):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    if mode == "custom":
        if playlist_exist(location) == False:
            return await interaction.followup.send(f"歌單ID不存在")
    if mode == "None":
        server.autoplay[0] = False
        server.autoplay[1] = {mode: location}
    else:
        server.autoplay[0] = True
        server.autoplay[1] = {mode: location}
    server.save_data()
    await interaction.followup.send(f"自動播放已被設為**{mode}:{location}**")
    
@bot.tree.command(name="lyrics", description="找尋歌曲的歌詞")
async def lyrics(interaction:discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    if len(server.queue) == 0:
        return await interaction.followup.send("歌單裡沒有歌曲")
    song = server.queue[0]
    lyric = extract_lyrics([*song][0],list(song.values())[0]["artist"])
    if lyric == None:
        await interaction.followup.send("抱歉，查不到這首歌的歌詞")
    else:
        section = False
        line = False
        stitle = ""
        sline = ""
        embed = discord.Embed(title=f"**{lyric["title"]}**", url=lyric["url"], color=0xbf70ff)
        for i in range(0,len(lyric["lyrics"])):
            if lyric["lyrics"][i] == "":
                section = True
            elif section == True:
                stitle = lyric["lyrics"][i]
                section = False
                line = True
            elif line == True:
                sline += lyric["lyrics"][i] + "\n"
                if i+1 >= len(lyric["lyrics"]) or lyric["lyrics"][i+1] == "":
                    embed.add_field(name=f"**{stitle}**",value=sline,inline=False)
                    line = False
        genius_icon = discord.File(f"{ASSETS}Genius.jpg", filename="genius_icon.png")
        embed.set_footer(text="歌詞可能會有點不正確，請見諒。來源: Genius",icon_url="attachment://genius_icon.png")
        await interaction.followup.send(file=genius_icon,embed=embed)
    
@bot.tree.command(name="removedupe", description="刪除歌曲佇列中重複的歌曲")
async def removedupe(interaction:discord.Interaction):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    removedupe_track(server.queue)
    server.save_data()
    await interaction.followup.send(f"已清除歌曲佇列裡重複的歌曲")
    
@bot.tree.command(name="shuffle", description="打散歌曲佇列的歌曲")
async def shuffle(interaction:discord.Interaction):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    server.queue = shuffle_track(server.queue)
    server.save_data()
    await interaction.followup.send(f"已打散歌曲佇列裡所有的歌曲")
    
@bot.tree.command(name="playlist_create", description="創建歌單")
@app_commands.describe(name="name of your playlist")
async def playlist_create(interaction:discord.Interaction,name:str):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    if name in [*server.playlist]:
        await interaction.followup.send(f"你已經有名為**{name}**的歌單了")
    else:
        server.playlist[name] = []
        server.save_data()
        await interaction.followup.send(f"歌單:**{name}**已被創建")

@bot.tree.command(name="playlist_show", description="查詢歌單裡的歌曲")
@app_commands.describe(playlist="name of your playlist")
@app_commands.autocomplete(playlist = playlist_autocomplete)
async def playlist_show(interaction:discord.Interaction,playlist:str):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    bot_icon = discord.File(f"{ASSETS}GuoYiTing.jpg", filename="bot_icon.png")
    embed=discord.Embed(title=f"**{playlist}裡的歌曲**", description=f"length:{len(server.playlist[playlist])}", color=0xbf70ff)
    if len(server.playlist[playlist]) > 5:
        for i in range(0,5):
            song = server.playlist[playlist][i]
            length = song_length(list(song.values())[0]["length"])
            embed.add_field(name=f"**{i+1}** | **{[*song][0]}** - **{length[1]}:{length[2]}**", value="", inline=False)
    else:
        for i in range(0,len(server.playlist[playlist])):
            song = server.playlist[playlist][i]
            length = song_length(list(song.values())[0]["length"])
            embed.add_field(name=f"**{i+1}** | **{[*song][0]}** - **{length[1]}:{length[2]}**", value="", inline=False)
    embed.set_footer(text="GuoYiTing Is Singing",icon_url="attachment://bot_icon.png")
    view = page_view(server,playlist,"playlist")
    await interaction.followup.send(files=[bot_icon],embed=embed,view=view)
    
@bot.tree.command(name="playlist_showall", description="查詢歌單")
async def playlist_showall(interaction:discord.Interaction):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    bot_icon = discord.File(f"{ASSETS}GuoYiTing.jpg", filename="bot_icon.png")
    embed=discord.Embed(title=f"**歌單**", description=f"length:{len([*server.playlist])}", color=0xbf70ff)
    if len([*server.playlist]) > 5:
        for i in range(0,5):
            length = len(list(server.playlist.values())[i])
            embed.add_field(name=f"**{i+1}** | **{[*server.playlist][i]}** - **{length}**", value="", inline=False)
    else:
        for i in range(0,len([*server.playlist])):
            length = len(list(server.playlist.values())[i])
            embed.add_field(name=f"**{i+1}** | **{[*server.playlist][i]}** - **{length}**", value="", inline=False)
    embed.set_footer(text="GuoYiTing Is Singing",icon_url="attachment://bot_icon.png")
    view = page_view(server,None,"playlists")
    await interaction.followup.send(files=[bot_icon],embed=embed,view=view)
    
@bot.tree.command(name="playlist_add", description="在歌單中加入歌曲")
@app_commands.describe(playlist="name of your playlist")
@app_commands.autocomplete(playlist = playlist_autocomplete)
@app_commands.describe(search="name or url of track")
#@app_commands.autocomplete(search = search_autocomplete)
async def playlist_add(interaction:discord.Interaction,playlist:str,search:str):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    if is_url(search):
        media = media_type(search)
        if media == "apple music":
            infos = apple_music_download(search)
            for info in infos:
                title = f"{info["artist"]} - {info["title"]}"
                valid_title = info["valid_title"]
                artist = info["artist"]
                length = info["length"]
                thumbnail = f"attachment://song_icon.png"
                server.playlist[playlist].append({valid_title:{"platform":"Apple Music","title":title,"length":length,"artist":artist,"url":search,"thumbnail":thumbnail}})
        elif media == "spotify":
            infos = spotify_download(search)
            for info in infos:
                title = f"{info["artist"]} - {info["title"]}"
                valid_title = info["valid_title"]
                artist = info["artist"]
                length = info["length"]
                thumbnail = f"attachment://song_icon.png"
                server.playlist[playlist].append({valid_title:{"platform":"Spotify","title":title,"length":length,"artist":artist,"url":search,"thumbnail":thumbnail}})
        elif media == "youtube":
            if "playlist" in search:
                list_info = youtube_info_extract(search)
                for i in range(0,list_info["playlist_count"]):
                    url = list_info['entries'][i]["webpage_url"]
                    info = youtube_download(url)
                    title = info["title"]
                    valid_title = info["valid_title"]
                    artist = info["artist"]
                    length = info["length"]
                    thumbnail = info["thumbnail"]
                    server.playlist[playlist].append({valid_title:{"platform":"Youtube","title":title,"length":length,"artist":artist,"url":url,"thumbnail":thumbnail}})
            else:
                info = youtube_download(search)
                title = info["title"]
                valid_title = info["valid_title"]
                artist = info["artist"]
                length = info["length"]
                thumbnail = info["thumbnail"]
                server.playlist[playlist].append({valid_title:{"platform":"Youtube","title":title,"length":length,"artist":artist,"url":search,"thumbnail":thumbnail}})
    else:
        ytdl_options = {'noplaylist': True,'default_search': 'auto'}
        with YoutubeDL(ytdl_options) as ydl:
            video = ydl.extract_info(f"ytsearch1:{search}", download = False)
        result = video["entries"][0]["webpage_url"]
        info = youtube_download(result)
        title = info["title"]
        valid_title = info["valid_title"]
        artist = info["artist"]
        length = info["length"]
        thumbnail = info["thumbnail"]
        server.playlist[playlist].append({valid_title:{"platform":"Youtube","title":title,"length":length,"artist":artist,"url":result,"thumbnail":thumbnail}})
    length = song_length(length)
    server.save_data()
    await interaction.followup.send(f"**{title}({length[1]}:{length[2]})**已被加入歌單:**{playlist}**中第**{len(server.playlist[playlist])}**的位置")
    
@bot.tree.command(name="playlist_delete", description="刪除歌單裡的曲目")
@app_commands.describe(playlist="name of your playlist")
@app_commands.autocomplete(playlist = playlist_autocomplete)
@app_commands.describe(index="the index of the track you want to delete from your playlist")
async def playlist_delete(interaction:discord.Interaction,playlist:str,index:int):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    if index <= 0 or index > len(server.playlist[playlist]):
        await interaction.followup.send(f"你給予的數字已超過歌單的大小了")
    else:
        delete_track(server.playlist[playlist],index)
        server.save_data()
        await interaction.followup.send(f"已刪除歌單:**{playlist}**中第**{index}**首歌")
    
@bot.tree.command(name="playlist_play", description="播放歌單")
@app_commands.describe(playlist = "name of your playlist")
@app_commands.autocomplete(playlist = playlist_autocomplete)
async def playlist_play(interaction:discord.Interaction,playlist:str):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    original_queue = len(server.queue)
    voice = get(bot.voice_clients,guild=interaction.guild)
    if interaction.user.voice == None:
        await interaction.followup.send(f"你必須處在通話裡才可邀請我進去")
    else:
        for song in server.playlist[playlist]:
            server.queue.append(song)
        server.save_data()
        channel = interaction.user.voice.channel
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            await channel.connect()
        voice = get(bot.voice_clients,guild=interaction.guild)
        if original_queue > 0:
            await interaction.followup.send(f"歌單:**{playlist}**中的**{len(server.playlist[playlist])}**首歌已被加入歌曲佇列")
        else:
            title = [*server.queue[0]][0]
            length = song_length(list(server.queue[0].values())[0]["length"])
            platform = list(server.queue[0].values())[0]["platform"]
            #
            thumbnail = thumbnail_easter_egg(title,list(server.queue[0].values())[0]["thumbnail"])
            #
            count = list(server.queue[0].values())[0]["length"]
            platform_icon = discord.File(f"{ASSETS}{platform} icon.png", filename="platform_icon.png")
            bot_icon = discord.File(f"{ASSETS}GuoYiTing.jpg", filename="bot_icon.png")
            embed = discord.Embed(title=f"**{title}**", url=list(server.queue[0].values())[0]["url"], color=0xbf70ff)
            embed.add_field(name="**∥ 正在撥放：**",value=f'\n                                           ♫\n▶︎ ● ｜{0*"<:bar:1289648502489747570>"}<:dot:1289644466860458048>{18*"<:bar:1289648502489747570>"}\n\n 00:00 / {length[1]}:{length[2]} \n',inline=False)
            if len(server.queue) > 1:
                embed.add_field(name="→【下一首歌曲】",value=f"**{[*server.queue[1]][0]}**",inline=False)
            embed.set_author(name=platform,icon_url="attachment://platform_icon.png")
            embed.set_footer(text="GuoYiTing Is Singing",icon_url="attachment://bot_icon.png")
            view = play_view(server)
            if platform == "Youtube":
                embed.set_thumbnail(url=thumbnail)
                message = await interaction.followup.send(f"正在播放**{title}({length[1]}:{length[2]})**",files=[bot_icon,platform_icon],embed=embed,view=view)
            else:
                song_icon = discord.File(f"{AUDIO}{platform}/{title}.png", filename=f"song_icon.png")
                embed.set_thumbnail(url=thumbnail)
                message = await interaction.followup.send(f"正在播放**{title}({length[1]}:{length[2]})**",files=[bot_icon,platform_icon,song_icon],embed=embed,view=view)
            source = AudioSourceTracked(FFmpegPCMAudio(executable=f"{BOT_FOLDER}ffmpeg/bin/ffmpeg.exe",source=f"{AUDIO}{platform}/{title}.mp4"), server)
            voice.play(source, after=lambda e: ending_track(interaction,message))
            server.time = 0
            while server.time < count-1 and len(server.queue) > 0 and voice.is_playing():
                time.sleep(1)
                try:
                    server = Server(str(interaction.guild_id))
                except:
                    pass
                c = int(server.time*(18/count))
                duration = song_length(server.time)
                embed = discord.Embed(title=f"**{title}**", url=list(server.queue[0].values())[0]["url"], color=0xbf70ff)
                embed.set_author(name=platform,icon_url="attachment://platform_icon.png")
                embed.set_footer(text="GuoYiTing Is Singing",icon_url="attachment://bot_icon.png")
                embed.add_field(name="**∥ 正在撥放：**",value=f'\n                                           ♫\n▶︎ ● ｜{c*"<:bar:1289648502489747570>"}<:dot:1289644466860458048>{(18-c)*"<:bar:1289648502489747570>"}\n\n {duration[1]}:{duration[2]} / {length[1]}:{length[2]} \n',inline=False)
                if len(server.queue) > 1:
                    embed.add_field(name="→【下一首歌曲】",value=f"**{[*server.queue[1]][0]}**",inline=False)
                embed.set_thumbnail(url=thumbnail)
                await message.edit(embed=embed)
    
@bot.tree.command(name="playlist_remove", description="刪除歌單")
@app_commands.describe(playlist = "name of your playlist")
@app_commands.autocomplete(playlist = playlist_autocomplete)
async def playlist_remove(interaction:discord.Interaction,playlist:str):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    server.playlist.pop(playlist)
    server.save_data()
    await interaction.followup.send(f"已移除歌單:**{playlist}**")
    
@bot.tree.command(name="playlist_clear", description="清空歌單")
@app_commands.describe(playlist="name of your playlist")
@app_commands.autocomplete(playlist = playlist_autocomplete)
async def playlist_clear(interaction:discord.Interaction,playlist:str):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    server.playlist[playlist] = clear_track(server.playlist[playlist])
    server.save_data()
    await interaction.followup.send(f"已清除歌單:**{playlist}**中的所有歌曲")
    
@bot.tree.command(name="playlist_removedupe", description="刪除歌單中重複的歌曲")
@app_commands.describe(playlist="name of your playlist")
@app_commands.autocomplete(playlist = playlist_autocomplete)
async def playlist_removedupe(interaction:discord.Interaction,playlist:str):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    removedupe_track(server.playlist[playlist])
    server.save_data()
    await interaction.followup.send(f"已清除歌單:**{playlist}**中重複的歌曲")
    
@bot.tree.command(name="playlist_shuffle", description="打散歌單中的歌曲")
@app_commands.describe(playlist="name of your playlist")
@app_commands.autocomplete(playlist = playlist_autocomplete)
async def playlist_shuffle(interaction:discord.Interaction,playlist:str):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    server.playlist[playlist] = shuffle_track(server.playlist[playlist])
    server.save_data()
    await interaction.followup.send(f"已打散歌單:**{playlist}**中所有的歌曲")
    
@bot.tree.command(name="queue_extract", description="將當前的歌曲佇列加入歌單")
@app_commands.describe(playlist = "name of your playlist")
@app_commands.autocomplete(playlist = playlist_autocomplete)
async def queue_extract(interaction:discord.Interaction,playlist:str):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    for song in server.queue:
        server.playlist[playlist].append(song)
    server.save_data()
    await interaction.followup.send(f"已將歌曲佇列中的所有歌曲加入歌單:**{playlist}**")
    
@bot.tree.command(name="song_extract", description="將當前的歌曲加入歌單")
@app_commands.describe(playlist = "name of your playlist")
@app_commands.autocomplete(playlist = playlist_autocomplete)
async def song_extract(interaction:discord.Interaction,playlist:str):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    song = server.queue[0]
    length = song_length(list(server.queue[0].values())[0]["length"])
    server.playlist[playlist].append(song)
    server.save_data()
    await interaction.followup.send(f"已將目前播放的**{[*song][0]}({length[1]}:{length[2]})**加入歌單:**{playlist}**")
    
@bot.tree.command(name="suggestion", description="將熱門歌曲加入歌單")
@app_commands.autocomplete(mode = suggestion_mode_autocomplete)
@app_commands.autocomplete(location = suggestion_location_autocomplete)
async def song_suggestion(interaction:discord.Interaction,mode:str,location:str):
    await interaction.response.defer()
    await asyncio.sleep(0)
    voice = get(bot.voice_clients,guild=interaction.guild)
    if interaction.user.voice == None:
        return await interaction.followup.send(f"你必須處在通話裡才可使用此指令")
    server = Server(str(interaction.guild_id))
    original_queue = len(server.queue)
    if mode == "server playlist":
        x = random.randint(0,len(server.playlist[location])-1)
        suggestion = server.playlist[location][x]
        server.queue.append(suggestion)
    elif mode == "custom":
        try:
            suggestion = auto_suggestion(mode,location)
            infos = spotify_download(suggestion)
            for info in infos:
                title = f"{info["artist"]} - {info["title"]}"
                valid_title = info["valid_title"]
                artist = info["artist"]
                length = info["length"]
                thumbnail = f"attachment://song_icon.png"
                server.queue.append({valid_title:{"platform":"Spotify","title":title,"length":length,"artist":artist,"url":suggestion,"thumbnail":thumbnail}})
        except:
            return await interaction.followup.send("自動撥放的歌單已不存在")
    else:
        try:
            suggestion = auto_suggestion(mode,location)
            infos = spotify_download(suggestion)
            for info in infos:
                title = f"{info["artist"]} - {info["title"]}"
                valid_title = info["valid_title"]
                artist = info["artist"]
                length = info["length"]
                thumbnail = f"attachment://song_icon.png"
                server.queue.append({valid_title:{"platform":"Spotify","title":title,"length":length,"artist":artist,"url":suggestion,"thumbnail":thumbnail}})
        except:
            return await interaction.followup.send("自動撥放的歌單已不存在")
    server.save_data()
    channel = interaction.user.voice.channel
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        await channel.connect()
    voice = get(bot.voice_clients,guild=interaction.guild)
    if original_queue > 0:
        length = song_length(length)
        await interaction.followup.send(f"**{title}({length[1]}:{length[2]})**已被加入到**{len(server.queue)}**的位置")
    else:
        title = [*server.queue[0]][0]
        length = song_length(list(server.queue[0].values())[0]["length"])
        platform = list(server.queue[0].values())[0]["platform"]
        #
        thumbnail = thumbnail_easter_egg(title,list(server.queue[0].values())[0]["thumbnail"])
        #
        count = list(server.queue[0].values())[0]["length"]
        platform_icon = discord.File(f"{ASSETS}{platform} icon.png", filename="platform_icon.png")
        bot_icon = discord.File(f"{ASSETS}GuoYiTing.jpg", filename="bot_icon.png")
        embed = discord.Embed(title=f"**{title}**", url=list(server.queue[0].values())[0]["url"], color=0xbf70ff)
        embed.add_field(name="**∥ 正在撥放：**",value=f'\n                                           ♫\n▶︎ ● ｜{0*"<:bar:1289648502489747570>"}<:dot:1289644466860458048>{18*"<:bar:1289648502489747570>"}\n\n 00:00 / {length[1]}:{length[2]} \n',inline=False)
        if len(server.queue) > 1:
            embed.add_field(name="→【下一首歌曲】",value=f"**{[*server.queue[1]][0]}**",inline=False)
        embed.set_author(name=platform,icon_url="attachment://platform_icon.png")
        embed.set_footer(text="GuoYiTing Is Singing",icon_url="attachment://bot_icon.png")
        view = play_view(server)
        if platform == "Youtube":
            embed.set_thumbnail(url=thumbnail)
            message = await interaction.followup.send(f"正在播放**{title}({length[1]}:{length[2]})**",files=[bot_icon,platform_icon],embed=embed,view=view)
        else:
            song_icon = discord.File(f"{AUDIO}{platform}/{title}.png", filename=f"song_icon.png")
            embed.set_thumbnail(url=thumbnail)
            message = await interaction.followup.send(f"正在播放**{title}({length[1]}:{length[2]})**",files=[bot_icon,platform_icon,song_icon],embed=embed,view=view)
        source = AudioSourceTracked(FFmpegPCMAudio(executable=f"{BOT_FOLDER}ffmpeg/bin/ffmpeg.exe",source=f"{AUDIO}{platform}/{title}.mp4"), server)
        voice.play(source, after=lambda e: ending_track(interaction,message))
        time.sleep(1)
        server.time = 0
        while server.time < count-1 and len(server.queue) > 0 and voice.is_playing():
            time.sleep(1)
            try:
                server = Server(str(interaction.guild_id))
            except:
                pass
            c = int(server.time*(18/count))
            duration = song_length(server.time)
            embed = discord.Embed(title=f"**{title}**", url=list(server.queue[0].values())[0]["url"], color=0xbf70ff)
            embed.set_author(name=platform,icon_url="attachment://platform_icon.png")
            embed.set_footer(text="GuoYiTing Is Singing",icon_url="attachment://bot_icon.png")
            embed.add_field(name="**∥ 正在撥放：**",value=f'\n                                           ♫\n▶︎ ● ｜{c*"<:bar:1289648502489747570>"}<:dot:1289644466860458048>{(18-c)*"<:bar:1289648502489747570>"}\n\n {duration[1]}:{duration[2]} / {length[1]}:{length[2]} \n',inline=False)
            if len(server.queue) > 1:
                embed.add_field(name="→【下一首歌曲】",value=f"**{[*server.queue[1]][0]}**",inline=False)
            embed.set_thumbnail(url=thumbnail)
            await message.edit(embed=embed)

@bot.tree.command(name="play_others", description="播放別人正在聽的Spotify歌曲")
async def play_others(interaction:discord.Interaction,member:discord.Member):
    await interaction.response.defer()
    await asyncio.sleep(0)
    if interaction.user.voice == None:
        return await interaction.followup.send(f"你必須處在通話裡才可邀請我進去")
    member = interaction.guild.get_member(member.id)
    activities = member.activities
    url = None
    for activity in activities:
        if activity.name == "Spotify":
            url = activity.track_url
            break
    if url == None:
        return await interaction.followup.send("該使用者沒在聽歌")
    server = Server(str(interaction.guild_id))
    original_queue = len(server.queue)
    infos = spotify_download(url)
    for info in infos:
        title = f"{info["artist"]} - {info["title"]}"
        valid_title = info["valid_title"]
        artist = info["artist"]
        length = info["length"]
        thumbnail = f"attachment://song_icon.png"
        server.queue.append({valid_title:{"platform":"Spotify","title":title,"length":length,"artist":artist,"url":url,"thumbnail":thumbnail}})
    server.save_data()
    channel = interaction.user.voice.channel
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        await channel.connect()
    voice = get(bot.voice_clients,guild=interaction.guild)
    if original_queue > 0:
        length = song_length(length)
        await interaction.followup.send(f"**{title}({length[1]}:{length[2]})**已被加入到**{len(server.queue)}**的位置")
    else:
        title = [*server.queue[0]][0]
        length = song_length(list(server.queue[0].values())[0]["length"])
        platform = list(server.queue[0].values())[0]["platform"]
        #
        thumbnail = thumbnail_easter_egg(title,list(server.queue[0].values())[0]["thumbnail"])
        #
        count = list(server.queue[0].values())[0]["length"]
        platform_icon = discord.File(f"{ASSETS}{platform} icon.png", filename="platform_icon.png")
        bot_icon = discord.File(f"{ASSETS}GuoYiTing.jpg", filename="bot_icon.png")
        embed = discord.Embed(title=f"**{title}**", url=list(server.queue[0].values())[0]["url"], color=0xbf70ff)
        embed.add_field(name="**∥ 正在撥放：**",value=f'\n                                           ♫\n▶︎ ● ｜{0*"<:bar:1289648502489747570>"}<:dot:1289644466860458048>{18*"<:bar:1289648502489747570>"}\n\n 00:00 / {length[1]}:{length[2]} \n',inline=False)
        if len(server.queue) > 1:
            embed.add_field(name="→【下一首歌曲】",value=f"**{[*server.queue[1]][0]}**",inline=False)
        embed.set_author(name=platform,icon_url="attachment://platform_icon.png")
        embed.set_footer(text="GuoYiTing Is Singing",icon_url="attachment://bot_icon.png")
        view = play_view(server)
        if platform == "Youtube":
            embed.set_thumbnail(url=thumbnail)
            message = await interaction.followup.send(f"正在播放**{title}({length[1]}:{length[2]})**",files=[bot_icon,platform_icon],embed=embed,view=view)
        else:
            song_icon = discord.File(f"{AUDIO}{platform}/{title}.png", filename=f"song_icon.png")
            embed.set_thumbnail(url=thumbnail)
            message = await interaction.followup.send(f"正在播放**{title}({length[1]}:{length[2]})**",files=[bot_icon,platform_icon,song_icon],embed=embed,view=view)
        source = AudioSourceTracked(FFmpegPCMAudio(executable=f"{BOT_FOLDER}ffmpeg/bin/ffmpeg.exe",source=f"{AUDIO}{platform}/{title}.mp4"), server)
        voice.play(source, after=lambda e: ending_track(interaction,message))
        time.sleep(1)
        server.time = 0
        while server.time < count-1 and len(server.queue) > 0 and voice.is_playing():
            time.sleep(1)
            try:
                server = Server(str(interaction.guild_id))
            except:
                pass
            c = int(server.time*(18/count))
            duration = song_length(server.time)
            embed = discord.Embed(title=f"**{title}**", url=list(server.queue[0].values())[0]["url"], color=0xbf70ff)
            embed.set_author(name=platform,icon_url="attachment://platform_icon.png")
            embed.set_footer(text="GuoYiTing Is Singing",icon_url="attachment://bot_icon.png")
            embed.add_field(name="**∥ 正在撥放：**",value=f'\n                                           ♫\n▶︎ ● ｜{c*"<:bar:1289648502489747570>"}<:dot:1289644466860458048>{(18-c)*"<:bar:1289648502489747570>"}\n\n {duration[1]}:{duration[2]} / {length[1]}:{length[2]} \n',inline=False)
            if len(server.queue) > 1:
                embed.add_field(name="→【下一首歌曲】",value=f"**{[*server.queue[1]][0]}**",inline=False)
            embed.set_thumbnail(url=thumbnail)
            await message.edit(embed=embed)
########################################################################## MANAGER BOT
@bot.tree.command(name="set_temporary_channel", description="設定臨時語音房")
async def set_temporary_channel(interaction:discord.Interaction,channel:discord.VoiceChannel):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    server.temporary_voice_channel["default"] = channel.id
    server.save_management()
    await interaction.followup.send(f"臨時語音已被設成<#{channel.id}>")
    
@bot.tree.command(name="reset_temporary_channel", description="重設臨時語音房")
async def reset_temporary_channel(interaction:discord.Interaction):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    server.temporary_voice_channel["default"] = ""
    server.save_management()
    await interaction.followup.send(f"臨時語音已被重設")
    
@bot.tree.command(name="set_welcome_channel", description="設定歡迎頻道")
async def set_welcome_channel(interaction:discord.Interaction,channel:discord.TextChannel):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    server.welcome_channel = channel.id
    server.save_management()
    await interaction.followup.send(f"加入頻道已被設成<#{channel.id}>")
    
@bot.tree.command(name="reset_welcome_channel", description="重設歡迎頻道")
async def reset_welcome_channel(interaction:discord.Interaction):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    server.welcome_channel = ""
    server.save_management()
    await interaction.followup.send(f"加入頻道已被重設")
    
@bot.tree.command(name="set_leave_channel", description="設定離開頻道")
async def set_leave_channel(interaction:discord.Interaction,channel:discord.TextChannel):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    server.leave_channel = channel.id
    server.save_management()
    await interaction.followup.send(f"退出頻道已被設成<#{channel.id}>")
    
@bot.tree.command(name="reset_leave_channel", description="重設離開頻道")
async def reset_leave_channel(interaction:discord.Interaction):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    server.leave_channel = ""
    server.save_management()
    await interaction.followup.send(f"退出頻道已被重設")
    
@bot.tree.command(name="role_message", description="設定身分組認領的訊息")
@app_commands.describe(message="給使用者的訊息")
async def role_message(interaction:discord.Interaction,message:str,role:discord.Role):
    await interaction.response.defer()
    await asyncio.sleep(0)
    member = interaction.guild.get_member(bot.user.id)
    roles = member.roles
    higher = False
    for r in roles:
        if interaction.guild.roles.index(r) < interaction.guild.roles.index(role):
            higher = True
            break
    if higher == False:
        return await interaction.followup.send("機器人需要更高的權限")
    server = Server(str(interaction.guild_id))
    server.basic_role = role.id
    embed = discord.Embed(title=f"**{message}**", color=0xbf70ff)
    msg = await interaction.followup.send(embed=embed)
    server.role_message = msg.id
    server.save_management()
########################################################################## SERVER STAT BOT
@bot.tree.command(name="avatar", description="取得用戶頭像")
async def avatar(interaction:discord.Interaction,user:discord.User):
    await interaction.response.defer()
    await asyncio.sleep(0)
    if user.avatar == None:
        return await interaction.followup.send(f"**{user.name}沒有設定頭像**")
    icon = user.avatar.url
    embed = discord.Embed(title=f"**{user.name}的頭像**")
    embed.set_image(url=icon)
    await interaction.followup.send(embed=embed)
    
@bot.tree.command(name="banner", description="取得用戶橫幅")
async def banner(interaction:discord.Interaction,user:discord.User):
    await interaction.response.defer()
    await asyncio.sleep(0)
    user = await bot.fetch_user(user.id)
    if user.banner == None:
        return await interaction.followup.send(f"**{user.name}沒有設定橫幅**")
    icon = user.banner.url
    embed = discord.Embed(title=f"**{user.name}的橫幅**")
    embed.set_image(url=icon)
    await interaction.followup.send(embed=embed)
    
@bot.tree.command(name="server_icon", description="取得伺服器頭像")
async def server_icon(interaction:discord.Interaction):
    await interaction.response.defer()
    await asyncio.sleep(0)
    if interaction.guild.icon == None:
        return await interaction.followup.send(f"**{interaction.guild.name}沒有設定封面**")
    icon = interaction.guild.icon.url
    embed = discord.Embed(title=f"**{interaction.guild.name}的封面**")
    embed.set_image(url=icon)
    await interaction.followup.send(embed=embed)
    
@bot.tree.command(name="server_banner", description="取得伺服器橫幅")
async def server_banner(interaction:discord.Interaction):
    await interaction.response.defer()
    await asyncio.sleep(0)
    if interaction.guild.banner == None:
        return await interaction.followup.send(f"**{interaction.guild.name}沒有設定橫幅**")
    icon = interaction.guild.banner.url
    embed = discord.Embed(title=f"**{interaction.guild.name}的橫幅**")
    embed.set_image(url=icon)
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="random_user", description="取得隨機用戶")
@app_commands.choices(type=[app_commands.Choice(name="Bot", value="Bot"),app_commands.Choice(name="User", value="User"),app_commands.Choice(name="All", value="All")])
async def random_user(interaction:discord.Interaction,type:app_commands.Choice[str]):
    await interaction.response.defer()
    await asyncio.sleep(0)
    while True:
        x = random.randint(0,len(interaction.guild.members)-1)
        member = interaction.guild.members[x]
        if type.name == "Bot":
            if member.bot:
                break
        elif type.name == "User":
            if not member.bot:
                break
        else:
            break
    await interaction.followup.send(f"選到了<@{member.id}>")

@bot.tree.command(name="random_channel", description="取得隨機頻道")
@app_commands.choices(type=[app_commands.Choice(name="Text Channel", value="Text Channel"),app_commands.Choice(name="Voice Channel", value="Voice Channel"),app_commands.Choice(name="Category", value="Category"),app_commands.Choice(name="All", value="All")])
async def random_channel(interaction:discord.Interaction,type:app_commands.Choice[str]):
    await interaction.response.defer()
    await asyncio.sleep(0)
    if type.name == "Text Channel":
        x = random.randint(0,len(interaction.guild.text_channels)-1)
        channel = interaction.guild.text_channels[x]
    elif type.name == "Voice Channel":
        x = random.randint(0,len(interaction.guild.voice_channels)-1)
        channel = interaction.guild.voice_channels[x]
    elif type.name == "Category":
        x = random.randint(0,len(interaction.guild.categories)-1)
        channel = interaction.guild.categories[x]
    elif type.name == "All":
        x = random.randint(0,len(interaction.guild.channels)-1)
        channel = interaction.guild.channels[x]
    await interaction.followup.send(f"選到了<#{channel.id}>")
########################################################################## Gadget BOT
@bot.tree.command(name="create_prediction", description="建立預測")
@app_commands.describe(topic="主題",option1="選項一",option2="選項二",time="時間限制")
async def create_prediction(interaction:discord.Interaction,topic:str,option1:str,option2:str,time:str|None):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    server.prediction[topic] = {"creator":interaction.user.id,"options":{option1:[],option2:[]},"voted":[],"time":time}
    options = server.prediction[topic]["options"]
    server.save_management()
    embed = discord.Embed(title=f"**{topic}**", color=0x2b2b2b)
    embed.add_field(name=f"**{option1}**", value=f"{len(options[option1])}%", inline=False)
    embed.add_field(name=f"**{option2}**", value=f"{len(options[option2])}%", inline=False)
    await interaction.followup.send(embed=embed)
    
@bot.tree.command(name="end_prediction", description="結束預測")
@app_commands.autocomplete(topic = prediction_topic_autocomplete,option = prediction_option_autocomplete)
@app_commands.describe(option="預測結果")
async def end_prediction(interaction:discord.Interaction,topic:str,option:str):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    if interaction.user.id != server.prediction[topic]["creator"]:
        return await interaction.followup.send("你沒有權限修改")
    options = server.prediction[topic]["options"]
    success = ""
    for suc in options[option]:
        success += f"<@{suc}> "
    embed = discord.Embed(title=f"**{topic}**", color=0x2b2b2b)
    for opt in [*options]:
        if len(server.prediction[topic]["voted"]) == 0:
            embed.add_field(name=f"**{opt}**", value=f"{len(options[opt])}%", inline=False)
        else:
            embed.add_field(name=f"**{opt}**", value=f"{round(len(options[opt])/len(server.prediction[topic]["voted"])*100,1)}%", inline=False)
    server.prediction.pop(topic)
    server.save_management()
    if len(success) != 0:
        await interaction.followup.send(f"**{topic}**已結束\n{success}預測成功",embed=embed)
    else:
        await interaction.followup.send(f"**{topic}**已結束\n無人預測成功",embed=embed)
    
@bot.tree.command(name="edit_prediction", description="編輯預測")
@app_commands.autocomplete(topic = prediction_topic_autocomplete, option = prediction_option_autocomplete)
@app_commands.describe(topic="要修改的主題",option="要修改的選項",edit_topic="修改主題",edit_option="修改選項",add_option="新增選項")
async def edit_prediction(interaction:discord.Interaction,topic:str,option:str|None,edit_topic:str|None,edit_option:str|None,add_option:str|None):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    if interaction.user.id != server.prediction[topic]["creator"]:
        return await interaction.followup.send("你沒有權限修改")
    if edit_topic != None:
        if edit_topic in [*server.prediction]:
            return await interaction.followup.send("已有這個名稱的主題")
        else:
            server.prediction[edit_topic] = server.prediction[topic]
            server.prediction.pop(topic)
            topic = edit_topic
    if option != None and edit_option != None:
        if edit_option in [*server.prediction[topic]["options"]]:
            return await interaction.followup.send("已有重複名稱的選項")
        else:
            server.prediction[topic]["options"][edit_option] = server.prediction[topic]["options"][option]
            server.prediction[topic]["options"].pop(option)
    if add_option != None:
        if add_option in [*server.prediction[topic]["options"]]:
            return await interaction.followup.send("已有重複名稱的選項")
        else:
            server.prediction[topic]["options"][add_option] = []
    server.save_management()
    options = server.prediction[topic]["options"]
    embed = discord.Embed(title=f"**{topic}**", color=0x2b2b2b)
    for opt in [*options]:
        if len(server.prediction[topic]["voted"]) == 0:
            embed.add_field(name=f"**{opt}**", value=f"{len(options[opt])}%", inline=False)
        else:
            embed.add_field(name=f"**{opt}**", value=f"{round(len(options[opt])/len(server.prediction[topic]["voted"])*100,1)}%", inline=False)
    await interaction.followup.send(embed=embed)
    
@bot.tree.command(name="vote_prediction", description="預測投票")
@app_commands.autocomplete(topic = prediction_topic_autocomplete,option = prediction_option_autocomplete)
async def vote_prediction(interaction:discord.Interaction,topic:str,option:str):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    if interaction.user.id in server.prediction[topic]["voted"]:
        return await interaction.followup.send("你已參與過")
    server.prediction[topic]["options"][option].append(interaction.user.id)
    server.prediction[topic]["voted"].append(interaction.user.id)
    server.save_management()
    options = server.prediction[topic]["options"]
    embed = discord.Embed(title=f"**{topic}**", color=0x2b2b2b)
    for opt in [*options]:
        if len(server.prediction[topic]["voted"]) == 0:
            embed.add_field(name=f"**{opt}**", value=f"{len(options[opt])}%", inline=False)
        else:
            embed.add_field(name=f"**{opt}**", value=f"{round(len(options[opt])/len(server.prediction[topic]["voted"])*100,1)}%", inline=False)
    await interaction.followup.send(embed=embed)
    
@bot.tree.command(name="check_prediction", description="檢視預測")
@app_commands.autocomplete(topic = prediction_topic_autocomplete)
async def check_prediction(interaction:discord.Interaction,topic:str):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    options = server.prediction[topic]["options"]
    embed = discord.Embed(title=f"**{topic}**", color=0x2b2b2b)
    for opt in [*options]:
        if len(server.prediction[topic]["voted"]) == 0:
            embed.add_field(name=f"**{opt}**", value=f"{len(options[opt])}%", inline=False)
        else:
            embed.add_field(name=f"**{opt}**", value=f"{round(len(options[opt])/len(server.prediction[topic]["voted"])*100,1)}%", inline=False)
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="roll_dice", description="擲骰子")
@app_commands.describe(minimum="最小數字",maximum="最大數字",count="骰子數量")
async def roll_dice(interaction:discord.Interaction,minimum:int,maximum:int,count:int):
    await interaction.response.defer()
    await asyncio.sleep(0)
    result = 0
    for i in range(0,count):
        x = random.randint(minimum,maximum)
        result += x
    await interaction.followup.send(f"骰到的結果是**{result}**")

@bot.tree.command(name="create_wheel", description="建立輪盤")
@app_commands.describe(topic="主題",mode="模式")
@app_commands.choices(mode=[app_commands.Choice(name="Even", value="Even"),app_commands.Choice(name="Non-Even", value="Non-Even")])
async def create_wheel(interaction:discord.Interaction,topic:str,mode:app_commands.Choice[str]):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    server.wheel[topic] = {"creator":interaction.user.id,"options":[],"mode":mode.name}
    server.save_management()
    if mode.name == "Even":
        mode = "平均"
    else:
        mode = "不平均"
    await interaction.followup.send(f"已建立輪盤:**{topic}**(模式:{mode})")
    
@bot.tree.command(name="remove_wheel", description="刪除輪盤")
@app_commands.autocomplete(topic = wheel_topic_autocomplete)
@app_commands.describe(topic="主題")
async def remove_wheel(interaction:discord.Interaction,topic:str):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    if interaction.user.id != server.wheel[topic]["creator"]:
        return await interaction.followup.send("你沒有權限修改")
    server.wheel.pop(topic)
    server.save_management()
    await interaction.followup.send(f"已移除輪盤:**{topic}**")
    
@bot.tree.command(name="edit_wheel", description="編輯輪盤")
@app_commands.autocomplete(topic = wheel_topic_autocomplete, option = wheel_option_autocomplete)
@app_commands.describe(topic="要修改的主題",option="要修改的選項",edit_topic="修改主題",edit_option="修改選項",add_option="新增選項",percentage="百分比(只有在「不平均模式」下需填)")
async def edit_wheel(interaction:discord.Interaction,topic:str,option:str|None,edit_topic:str|None,edit_option:str|None,add_option:str|None,percentage:float|None):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    if interaction.user.id != server.wheel[topic]["creator"]:
        return await interaction.followup.send("你沒有權限修改")
    if edit_topic != None:
        if edit_topic in [*server.wheel]:
            return await interaction.followup.send("已有這個名稱的主題")
        else:
            server.wheel[edit_topic] = server.wheel[topic]
            server.wheel.pop(topic)
            topic = edit_topic
    if option != None and edit_option != None:
        if edit_option in server.wheel[topic]["options"]:
            return await interaction.followup.send("已有重複名稱的選項")
        else:
            server.wheel[topic]["options"].append(edit_option)
            server.wheel[topic]["options"].remove(option)
    if add_option != None:
        if add_option in server.wheel[topic]["options"]:
            return await interaction.followup.send("已有重複名稱的選項")
        else:
            if server.wheel[topic]["mode"] == "Non-Even" and percentage == None:
                return await interaction.followup.send("不平均模式下須填入占比")
            if server.wheel[topic]["mode"] == "Even":
                server.wheel[topic]["options"].append(add_option)
            else:
                server.wheel[topic]["options"].append((add_option,percentage))
    server.save_management()
    selections = server.wheel[topic]["options"]
    embed = discord.Embed(title=f"**{topic}**",description=f"模式:{server.wheel[topic]["mode"]}", color=0x2b2b2b)
    for sel in [*selections]:
        if server.wheel[topic]["mode"] == "Even":
            embed.add_field(name=f"**{sel}**", value=f"{round(1/len(selections)*100,1)}%", inline=False)
        else:
            embed.add_field(name=f"**{sel[0]}**", value=f"{sel[1]}%", inline=False)
    await interaction.followup.send(embed=embed)
    
@bot.tree.command(name="check_wheel", description="檢視輪盤")
@app_commands.autocomplete(topic = wheel_topic_autocomplete)
@app_commands.describe(topic="主題")
async def check_wheel(interaction:discord.Interaction,topic:str):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    selections = server.wheel[topic]["options"]
    embed = discord.Embed(title=f"**{topic}**",description=f"模式:{server.wheel[topic]["mode"]}", color=0x2b2b2b)
    for sel in [*selections]:
        if server.wheel[topic]["mode"] == "Even":
            embed.add_field(name=f"**{sel}**", value=f"{round(1/len(selections)*100,1)}%", inline=False)
        else:
            embed.add_field(name=f"**{sel[0]}**", value=f"{sel[1]}%", inline=False)
    await interaction.followup.send(embed=embed)
    
@bot.tree.command(name="spin_wheel", description="轉輪盤")
@app_commands.autocomplete(topic = wheel_topic_autocomplete)
@app_commands.describe(topic="主題")
async def spin_wheel(interaction:discord.Interaction,topic:str):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    wheel = server.wheel[topic]
    if wheel["mode"] == "Even":
        selection = wheel["options"]
    else:
        selection = []
        for s in wheel["options"]:
            for i in range(0,s[1]):
                selection.append(s[0])
    server.save_management()
    x = random.randint(0,len(selection)-1)
    await interaction.followup.send(f"選到了 **{selection[x]}**")
    
@bot.tree.command(name="switch_scam_prevent", description="更改伺服器防詐功能的狀態")
@app_commands.choices(type=[app_commands.Choice(name="File", value="File"),app_commands.Choice(name="URL", value="URL"),app_commands.Choice(name="Both", value="Both")])
@app_commands.choices(level=[app_commands.Choice(name="None", value="None"),app_commands.Choice(name="Low", value="Low"),app_commands.Choice(name="Medium", value="Medium"),app_commands.Choice(name="High", value="High")])
@app_commands.describe(type="種類",level="安全層級")
async def switch_scam_prevent(interaction:discord.Interaction,type:app_commands.Choice[str],level:app_commands.Choice[str]):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    if type.value == "File":
        output = "檔案"
        server.scam_prevent[type.value] = level.value
    elif type.value == "URL":
        output = "網址"
        server.scam_prevent[type.value] = level.value
    else:
        output = "檔案和網址"
        server.scam_prevent["File"] = level.value
        server.scam_prevent["URL"] = level.value
    if level.value == "None":
        status = "關閉"
    elif level.value == "Low":
        status = "低層級"
    elif level.value == "Medium":
        status = "中層級"
    elif level.value == "High":
        status = "高層級"
    server.save_management()
    await interaction.followup.send(f"**{output}**防詐功能已被設為**{status}**")
########################################################################## Save BOT
@bot.tree.command(name="switch_emoji_save", description="更改使用者私訊暫存功能的狀態")
async def switch_emoji_save(interaction:discord.Interaction):
    await interaction.response.defer()
    await asyncio.sleep(0)
    server = Server(str(interaction.guild_id))
    if interaction.user.id in server.emote_save:
        status = "關閉"
        server.emote_save.remove(interaction.user.id)
        server.save_save()
        await interaction.followup.send(f"表情符號儲存功能已被設為**{status}**")
    else:
        status = "開啟"
        server.emote_save.append(interaction.user.id)
        server.save_save()
        await interaction.followup.send(f"表情符號儲存功能已被設為**{status}**(可在訊息底下添加:inbox_tray:來儲存)")
    
@bot.tree.command(name="screenshot", description="截圖對話")
@app_commands.autocomplete(start = text_autocomplete, end = text_autocomplete)
@app_commands.choices(anonymous=[app_commands.Choice(name="True", value="True"),app_commands.Choice(name="False", value="False")])
@app_commands.describe(start="起始點",end="截止點",anonymous="是否匿名處理")
async def screenshot(interaction:discord.Interaction,start:str,end:str,anonymous:app_commands.Choice[str]):
    await interaction.response.defer()
    await asyncio.sleep(0)
    operation = False
    result = []
    async for message in interaction.channel.history(limit=100):
        if str(message.id) == end:
            operation = True
        if operation == True:
            result.append(message)
        if str(message.id) == start:
            break
    print(result)
    await interaction.followup.send(f"a")
########################################################################## Tool BOT
@bot.tree.command(name="download")
@app_commands.autocomplete(platform = file_platform_autocomplete)
@app_commands.autocomplete(type = file_type_autocomplete)
@app_commands.autocomplete(filetype = file_filetype_autocomplete)
@app_commands.describe(url="link")
async def download_link(interaction:discord.Interaction,url:str,platform:str,type:str,filetype:str|None):
    await interaction.response.defer()
    await asyncio.sleep(0)
    if not os.path.exists(f"{FILES_SAVE}/Download/{platform}/{interaction.user.id}"):
        os.mkdir(f"{FILES_SAVE}/Download/{platform}/{interaction.user.id}")
    if platform == "Youtube":
        info = file_youtube_download(url,type,filetype,str(interaction.user.id))
    elif platform == "Spotify":
        info = file_spotify_download(url,filetype,str(interaction.user.id))
    elif platform == "Apple Music":
        info = file_apple_music_download(url,filetype,str(interaction.user.id))
    elif platform == "Niconico":
        info = file_niconico_download(url,type,filetype,str(interaction.user.id))
    link = file_upload(info["path"],str(interaction.user.id))
    message = await interaction.followup.send(f"Your download link: {link}")
    time.sleep(10)
    try:
        file_delete(info["path"],str(interaction.user.id))
    except:
        pass
    await message.delete()
    
@bot.tree.command(name="convert")
@app_commands.choices(type=[app_commands.Choice(name="mp3", value="mp3"),app_commands.Choice(name="mp4", value="mp4"),app_commands.Choice(name="webm", value="webm"),app_commands.Choice(name="m4a", value="m4a"),app_commands.Choice(name="wav", value="wav"),app_commands.Choice(name="mov", value="mov")])
async def convert_file(interaction:discord.Interaction,file:discord.Attachment,type:app_commands.Choice[str]):
    await interaction.response.defer()
    await asyncio.sleep(0)
    if not os.path.exists(f"{FILES_SAVE}/Convert/{interaction.user.id}"):
        os.mkdir(f"{FILES_SAVE}/Convert/{interaction.user.id}")
    await interaction.followup.send(f"WIP")
########################################################################## GAME BOT

########################################################################## Context Menu
@bot.tree.context_menu(name="Get Avatar")
async def get_avatar(interaction:discord.Interaction,member:discord.Member):
    await interaction.response.defer()
    await asyncio.sleep(0)
    if member.avatar == None:
        return await interaction.followup.send(f"**{member.name}沒有設定頭像**")
    icon = member.avatar.url
    embed = discord.Embed(title=f"**{member.name}的頭像**")
    embed.set_image(url=icon)
    await interaction.followup.send(embed=embed)

@bot.tree.context_menu(name="Get Banner")
async def get_banner(interaction:discord.Interaction,member:discord.Member):
    await interaction.response.defer()
    await asyncio.sleep(0)
    user = await bot.fetch_user(member.id)
    if user.banner == None:
        return await interaction.followup.send(f"**{user.name}沒有設定橫幅**")
    icon = user.banner.url
    embed = discord.Embed(title=f"**{user.name}的橫幅**")
    embed.set_image(url=icon)
    await interaction.followup.send(embed=embed)
    
@bot.tree.context_menu(name="DM Save")
async def dm_save(interaction:discord.Interaction,message:discord.Message):
    await interaction.response.defer(ephemeral=True)
    await asyncio.sleep(0)
    user = interaction.user
    content = message.content
    embeds = message.embeds
    attachments = message.attachments
    files = []
    for attachment in attachments:
        files.append(await attachment.to_file())
    content += f"\n-{message.author.name}(**User ID**: {message.author.id})(**Guild**: {message.guild.name}, **Channel**: {message.channel.name})(**Time Sent**: {message.created_at})"
    if user.dm_channel != None:
        await user.dm_channel.send(content,embeds=embeds,files=files)
    else:
        await user.create_dm()
        await user.dm_channel.send(content,embeds=embeds,files=files)
    await interaction.followup.send(f"以儲存訊息至私訊",ephemeral=True)
    
@bot.tree.context_menu(name="Play Song")
async def play_song(interaction:discord.Interaction,member:discord.Member):
    await interaction.response.defer()
    await asyncio.sleep(0)
    if interaction.user.voice == None:
        return await interaction.followup.send(f"你必須處在通話裡才可邀請我進去")
    member = interaction.guild.get_member(member.id)
    activities = member.activities
    url = None
    for activity in activities:
        if activity.name == "Spotify":
            url = activity.track_url
            break
    if url == None:
        return await interaction.followup.send("該使用者沒在聽歌")
    server = Server(str(interaction.guild_id))
    original_queue = len(server.queue)
    infos = spotify_download(url)
    for info in infos:
        title = f"{info["artist"]} - {info["title"]}"
        valid_title = info["valid_title"]
        artist = info["artist"]
        length = info["length"]
        thumbnail = f"attachment://song_icon.png"
        server.queue.append({valid_title:{"platform":"Spotify","title":title,"length":length,"artist":artist,"url":url,"thumbnail":thumbnail}})
    server.save_data()
    channel = interaction.user.voice.channel
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        await channel.connect()
    voice = get(bot.voice_clients,guild=interaction.guild)
    if original_queue > 0:
        length = song_length(length)
        await interaction.followup.send(f"**{title}({length[1]}:{length[2]})**已被加入到**{len(server.queue)}**的位置")
    else:
        title = [*server.queue[0]][0]
        length = song_length(list(server.queue[0].values())[0]["length"])
        platform = list(server.queue[0].values())[0]["platform"]
        #
        thumbnail = thumbnail_easter_egg(title,list(server.queue[0].values())[0]["thumbnail"])
        #
        count = list(server.queue[0].values())[0]["length"]
        platform_icon = discord.File(f"{ASSETS}{platform} icon.png", filename="platform_icon.png")
        bot_icon = discord.File(f"{ASSETS}GuoYiTing.jpg", filename="bot_icon.png")
        embed = discord.Embed(title=f"**{title}**", url=list(server.queue[0].values())[0]["url"], color=0xbf70ff)
        embed.add_field(name="**∥ 正在撥放：**",value=f'\n                                           ♫\n▶︎ ● ｜{0*"<:bar:1289648502489747570>"}<:dot:1289644466860458048>{18*"<:bar:1289648502489747570>"}\n\n 00:00 / {length[1]}:{length[2]} \n',inline=False)
        if len(server.queue) > 1:
            embed.add_field(name="→【下一首歌曲】",value=f"**{[*server.queue[1]][0]}**",inline=False)
        embed.set_author(name=platform,icon_url="attachment://platform_icon.png")
        embed.set_footer(text="GuoYiTing Is Singing",icon_url="attachment://bot_icon.png")
        view = play_view(server)
        if platform == "Youtube":
            embed.set_thumbnail(url=thumbnail)
            message = await interaction.followup.send(f"正在播放**{title}({length[1]}:{length[2]})**",files=[bot_icon,platform_icon],embed=embed,view=view)
        else:
            song_icon = discord.File(f"{AUDIO}{platform}/{title}.png", filename=f"song_icon.png")
            embed.set_thumbnail(url=thumbnail)
            message = await interaction.followup.send(f"正在播放**{title}({length[1]}:{length[2]})**",files=[bot_icon,platform_icon,song_icon],embed=embed,view=view)
        source = AudioSourceTracked(FFmpegPCMAudio(executable=f"{BOT_FOLDER}ffmpeg/bin/ffmpeg.exe",source=f"{AUDIO}{platform}/{title}.mp4"), server)
        voice.play(source, after=lambda e: ending_track(interaction,message))
        time.sleep(1)
        server.time = 0
        while server.time < count-1 and len(server.queue) > 0 and voice.is_playing():
            time.sleep(1)
            try:
                server = Server(str(interaction.guild_id))
            except:
                pass
            c = int(server.time*(18/count))
            duration = song_length(server.time)
            embed = discord.Embed(title=f"**{title}**", url=list(server.queue[0].values())[0]["url"], color=0xbf70ff)
            embed.set_author(name=platform,icon_url="attachment://platform_icon.png")
            embed.set_footer(text="GuoYiTing Is Singing",icon_url="attachment://bot_icon.png")
            embed.add_field(name="**∥ 正在撥放：**",value=f'\n                                           ♫\n▶︎ ● ｜{c*"<:bar:1289648502489747570>"}<:dot:1289644466860458048>{(18-c)*"<:bar:1289648502489747570>"}\n\n {duration[1]}:{duration[2]} / {length[1]}:{length[2]} \n',inline=False)
            if len(server.queue) > 1:
                embed.add_field(name="→【下一首歌曲】",value=f"**{[*server.queue[1]][0]}**",inline=False)
            embed.set_thumbnail(url=thumbnail)
            await message.edit(embed=embed)
##########################################################################
@bot.tree.command(name="help", description="機器人的介紹和指令")
@app_commands.autocomplete(command = help_autocomplete)
async def bot_help(interaction:discord.Interaction,command:str):
    await interaction.response.defer()
    await asyncio.sleep(0)
    information = HELP_INFO["Chinese"][command]
    if command == "Other Feature":
        embed = discord.Embed(title=f"**{information["title"]}**",color=0xbf70ff)
        for info in [*information]:
            if info != "title":
                embed.add_field(name=f"{info}",value=f"{information[info]}",inline=False)
    elif command == "Bot Information":
        embed = discord.Embed(title=f"**{information["title"]}**",color=0xbf70ff)
        for info in [*information]:
            if info != "title":
                embed.add_field(name=f"{info}",value=f"{information[info]}",inline=False)
    else:
        embed = discord.Embed(title=f"**{command}**",color=0xbf70ff)
        embed.add_field(name=f"{information}",value="",inline=False)
    bot_icon = discord.File(f"{ASSETS}GuoYiTing.jpg", filename="bot_icon.png")
    embed.set_footer(text="GuoYiTing Is Singing",icon_url="attachment://bot_icon.png")
    await interaction.followup.send(files=[bot_icon],embed=embed)

@bot.tree.command(name="bot_send", description="send a message to a user through bot using their user_id")
async def bot_send(interaction:discord.Interaction,user_id:str,text:str):
    await interaction.response.defer(ephemeral=True)
    await asyncio.sleep(0)
    user = bot.get_user(int(user_id))
    if user.dm_channel:
        await user.dm_channel.send(text)
    else:
        await user.create_dm()
        await user.dm_channel.send(content=text)
    await interaction.followup.send(f"Successfully sent Message: {text} to User: <@{user_id}>")
    
@bot.tree.command(name="bot_check", description="check the bot's channel with a specific user using user_id")
async def bot_send(interaction:discord.Interaction,user_id:str):
    await interaction.response.defer(ephemeral=True)
    await asyncio.sleep(0)
    user = bot.get_user(int(user_id))
    if user.dm_channel:
        async for message in user.dm_channel.history(limit=100):
            print(message.content)
        await interaction.followup.send(f"There were messages sent to <@{user_id}>")
    else:
        await interaction.followup.send(f"There were no messages sent to <@{user_id}>")
    

    
bot.run("TOKEN")