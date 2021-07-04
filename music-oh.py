import discord
import asyncio
import youtube_dl
import pprint
from apiclient.discovery import build
from multiprocessing import Process
from collections import deque

from discord.ext import commands

TOKEN = 'TOKEN'
YOUTUBE_API_KEY = 'KEY'
client = discord.Client()
youtube = build("youtube","v3",developerKey=YOUTUBE_API_KEY)

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}
#映像無しで出力するためのオプション

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


url=deque()


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

    @client.event
    async def on_message(message):
        game = discord.Game("/help でコード一覧")
        await client.change_presence(status=discord.Status.online, activity=game)

        if message.content.startswith("/play"):
            Searchword=message.content.replace("/play","")
            if Searchword.startswith(":"):
                search_response = youtube.search().list(
                part='snippet',
                #検索したい文字列を指定
                q=Searchword,
                #関連度数
                order='relevance',
                #type='video',
                ).execute()
                #  検索全部見えちゃうマンpprint.pprint(search_response)
                ual='https://www.youtube.com/watch?v=' + search_response['items'][0]['id']['videoId']
                url.append(ual)
                print(url)
                await message.channel.send(":nerd: **検索された曲**")
                await message.channel.send("ーーーーーーーーーーーーーーーーーーーーーーー"+"\n■ "+ual+"\nーーーーーーーーーーーーーーーーーーーーーーー")
            else:
                await message.channel.send("`:`← を忘れていませんか？　もしくは無効なワードです。")

        if message.content.startswith("/url:"):
            uaL=message.content.replace("/url:","")
            if uaL.startswith("https"):
                url.append(uaL)
                print(url)
                await message.channel.send(":nerd: **検索された曲**")
                await message.channel.send("ーーーーーーーーーーーーーーーーーーーーーーー"+"\n■ "+uaL+"\nーーーーーーーーーーーーーーーーーーーーーーー")

            else:
                await message.channel.send("**URLが指定されていません。**")




        if message.content == "/stop":#動作確認済み
            voice_client = message.guild.voice_client
            voice_client.pause()
            await message.channel.send("**Pause now** :pause_button:")
            #一時停止？

        if message.content == "/restart":#動作確認済み
            voice_client = message.guild.voice_client
            voice_client.resume()
            await message.channel.send("**Restart** :arrow_forward:")


        if message.content == "/end":#動作確認済み
            voice_client = message.guild.voice_client
            voice_client.stop()
            await message.channel.send("**END** :stop_button:")


        if message.content == "/join":#動作確認済み
            vc = message.author.voice.channel
            await vc.connect()
            await message.channel.send(":candle: **joined**:candle: ")



        if message.content == "/disconnect":#動作確認済み
            voice_client = message.guild.voice_client
            await message.channel.send(":boom: **切断成功**")
            await voice_client.disconnect()


        if message.content.startswith("/help"):#動作確認済み
             m="**```再生コード\n/play:検索ワード   音楽再生（検索版）\n/url:URLをここに   音楽再生（URLから）\n/stop             一時停止\n/restart          リスタート\n/end              停止\n\nbotを入れるコード\n/join             接続\n/disconnect       切断\n\n※必ず/joinしてください。```**"
             await message.channel.send(m)

        if message.content=="/st":
            try:
                URL=url.popleft()
                voice_client = message.guild.voice_client
                #ボイスチャンネルの場所は　voice_client

                player = await YTDLSource.from_url(URL,loop=client.loop)
                voice_client.play(player)
                print(url)
                print("now"+URL)
                await message.channel.send(":face_with_hand_over_mouth: **流れます♪**")
                await message.channel.send("ーーーーーーーーーーーーーーーーーーーーーーー"+"\n■ "+URL+"\nーーーーーーーーーーーーーーーーーーーーーーー")
            except:
                try:
                    await message.channel.send(":face_with_monocle:  ***現在再生中です*** \n\n ***次に流れる曲***")
                    await message.channel.send("ーーーーーーーーーーーーーーーーーーーーーーー"+"\n■ "+URL+"\nーーーーーーーーーーーーーーーーーーーーーーー")
                    url.appendleft(URL)
                    print(url)
                except:
                    await message.channel.send(":scream: ***もうかける曲ないよ***")









client.run(TOKEN)
