def is_url(text):
    text = text.split("/")
    if "https:" in text[0]:
        return True
    return False

def media_type(url):
    url = url.split("/")
    url = url[2].split(".")
    for u in url:
        if u == "apple":
            return "apple music"
        elif u == "spotify":
            return "spotify"
        elif u == "youtu" or u == "youtube":
            return "youtube"
        elif u == "nicovideo":
            return "niconico"
        
def song_length(second):
    minute = second//60
    second -= minute*60
    hour = minute//60
    minute -= hour*60
    if second / 10 < 1:
        second = f"0{second}"
    if minute / 10 < 1:
        minute = f"0{minute}"
    if hour / 10 < 1:
        hour = f"0{hour}"
    return (str(hour),str(minute),str(second))

def valid_song_name(name):
    non_valid = ['*',"\\","/",":","|","?",'"',"<",">"]
    result = ""
    name = list(name)
    for n in non_valid:
        for i in range(0,name.count(n)):
            name.remove(n)
    for n in name:
        result += n
    return result

#"：","＊","？","：","｜","＼","／"