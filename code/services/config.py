
import re
from pymongo import MongoClient
def getMongo():
    return MongoClient("mongodb+srv://SCP:Geneavianina@scp16cluseter.foubt.mongodb.net/myFirstDatabase?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")

cluster = getMongo()
DiscordGuild = cluster["discord"]["guilds"]
levelling = cluster["discord"]["levelling"]
mulah = cluster["discord"]["mulah"]
BotGuilds = cluster["discord"]["botguilds"]




def GetFirstKey(dict:dict):
    for x in dict:
        return x


def removeDupes(testlist:list):
    res = []
    for x in testlist:
        if x not in res:
            res.append(x)
    return res

def get_guild_count():
    guild_count = DiscordGuild.find().sort("id", -1)
    count=0
    for x in guild_count:
        count+=1
    return count

def get_guild_ids():
    guild_count = DiscordGuild.find().sort("id", -1)
    ids = []
    for x in guild_count:
        ids.append(x["id"])
    return ids

def return_channels(guild_id):
    textchannelnames = []
    textchannels = DiscordGuild.find_one({"id":guild_id}, {"textchannels"})["textchannels"]

    return textchannels

def getDocumentation():
    botguilds = BotGuilds.find_one({"id":str(822265614244511754)}, {"documentation"})["documentation"]
    return botguilds

def get_guild(guild_id):
    botguilds = BotGuilds.find_one({"id":str(822265614244511754)}, {"guilds"})["guilds"]
    return botguilds[str(guild_id)]


def get_guild_settings(guildid):
    def swearleader(guildid):
        memberz = DiscordGuild.find_one({"id":guildid}, {"members"})["members"]

        rankings = levelling.find().sort("swears",-1)
        returnlist = []
        count=0
        i=1
        for x in rankings:
            try:
                temp = memberz[str(x["id"])]

                tempswears = x["swears"]
                returnlist.append(f"{temp}'s' Swears: `{tempswears}`") 
                i+=1
                if i==11:
                    break
            except:
                pass
        return returnlist

    def rankleader(guildid):
        memberz = DiscordGuild.find_one({"id":guildid}, {"members"})["members"]
        rankings = levelling.find().sort("xp",-1)
        returnlist = []
        i=1
        for x in rankings:
            try:
                temp = memberz[str(x["id"])]

                tempswears = x["xp"]
                returnlist.append(f"{temp}'s Level: `{Globals.getLevelfromxp(tempswears)}`") 
                i+=1
                if i==11:
                    break
            except:
                pass
        return returnlist

    def richleader(guildid):
        memberz = DiscordGuild.find_one({"id":guildid}, {"members"})["members"]
        returnlist = []
        rankings = mulah.find().sort("net",-1)
        count=0
        i=1
        for x in rankings:
            try:
                temp = memberz[str(x["id"])]

                tempswears = x["net"]
                returnlist.append(f"{temp}'s net worth: `${tempswears}`") 
                i+=1
                if i==11:
                    break
            except:
                pass
        return returnlist


    prefix = DiscordGuild.find_one({"id":guildid}, {"prefix"})["prefix"]
    currentGuildSettings = DiscordGuild.find_one({"id":guildid}, {"settings"})["settings"]
    announcementChannels =DiscordGuild.find_one({"id":guildid}, {"announcement channels"})["announcement channels"]
    suggestionChannels =DiscordGuild.find_one({"id":guildid}, {"suggestion channels"})["suggestion channels"]
    automod = DiscordGuild.find_one({"id":guildid}, {"automod"})["automod"]
    badwords = DiscordGuild.find_one({"id":guildid}, {"badwords"})["badwords"]
    swearlb = swearleader(guildid)
    ranklb = rankleader(guildid)
    richlb = richleader(guildid)
    channelz = DiscordGuild.find_one({"id":guildid}, {"textchannels"})["textchannels"]


    settings = {
        "Profanity Filter": currentGuildSettings["Profanity Filter"]["enabled"],
        "lol on message" : currentGuildSettings["lol on message"]["enabled"],
        "announce": currentGuildSettings["announce"]["enabled"],
        "suggest":currentGuildSettings["suggest"]["enabled"],

        "prefix":prefix,
        "announcement channels":[x for x in channelz if int(GetFirstKey(x)) in announcementChannels],
        "suggestion channels":[x for x in channelz if int(GetFirstKey(x)) in suggestionChannels],
        "automod":automod,
        "badwords":badwords,

        "richlb":richlb,
        "ranklb":ranklb,
        "swearlb":swearlb
    }
    print(channelz)
    print(announcementChannels)
    print([x for x in channelz if int(GetFirstKey(x)) in announcementChannels])
    return settings

get_guild_settings(859145748545273886)

    

