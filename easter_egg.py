import random

special = {
    "lying coldly":["https://media1.tenor.com/m/qZF9bnx5WJYAAAAC/aceattorney-dance.gif","https://media.tenor.com/GT-4lEL2RHYAAAAM/miles-edgeworth.gif"],
    "turnabout sisters":["https://media1.tenor.com/m/n4Dak88VJpcAAAAd/maya-fey-ace-attorney.gif"],
    "cornered":["https://media1.tenor.com/m/DP615vqUzeAAAAAC/ace-attorney-phoenix-wright.gif"],
    "ライアーダンサー":["https://media1.tenor.com/m/Gqlc1tuZfwEAAAAC/liar-liar-dancer.gif","https://media1.tenor.com/m/50CnVr3q0nwAAAAC/liar-dancer-kasane-teto.gif","https://media1.tenor.com/m/TTXZQ2KXweEAAAAC/kasane-teto-teto.gif"],
    "never gonna give you up":["https://media1.tenor.com/m/x8v1oNUOmg4AAAAd/rickroll-roll.gif"]
}

def thumbnail_easter_egg(song_name,original):
    song_name = song_name.lower()
    y = random.randint(0,100)
    if y <= 30:
        for s in [*special]:
            if s in song_name:
                gif = special[s]
                x = random.randint(0,len(gif)-1)
                return gif[x]
    return original