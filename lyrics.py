from lyricsgenius import Genius

numbers = [str(i) for i in range(0,10)]

def extract_lyrics(name,artist):
    genius = Genius("TOKEN")
    song = genius.search_song(name,artist)
    if song == None:
        return None
    else:
        result = ""
        limit = 0
        url = song.url
        title = song.title
        lyrics = song.lyrics.split("Lyrics")[1].split("Embed")[0].replace("You might also like","")
        if lyrics[len(lyrics)-1] in numbers:
            for i in range(len(lyrics)-1,-1,-1):
                if lyrics[i] in numbers and lyrics[i-1] not in numbers:
                    limit = i
                    break
            if limit != 0:
                for i in range(0,limit):
                    result += lyrics[i]
                return {"lyrics":result.split("\n"),"url":url,"title":title}
        else:
            return {"lyrics":lyrics.split("\n"),"url":url,"title":title}