from pymongo.mongo_client import MongoClient
from quart import Quart, render_template, request, session, redirect, url_for
from oath import Oauth
from quart_discord import DiscordOAuth2Session
from pymongo import MongoClient
import config
import re
def getMongo():
    return MongoClient("mongodb+srv://SCP:Geneavianina@scp16cluseter.foubt.mongodb.net/myFirstDatabase?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")

cluster = getMongo()
DiscordGuild = cluster["discord"]["guilds"]




#python pagekite.py 5000 scp16tsundere.pagekite.me


app = Quart(
    __name__, 
    template_folder=r"templates",
    static_folder=r"static",
    )

app.config["SECRET_KEY"] = "geneavianina"
app.config["DISCORD_CLIENT_ID"] = 822265614244511754   # Discord client ID.
app.config["DISCORD_CLIENT_SECRET"] = "vaqJa9ZQAWawL7FJlHYYBeuQw-JIBtO2"  # Discord client secret.
app.config["DISCORD_REDIRECT_URI"] = "http://127.0.0.1:5000/callback" 

discord = DiscordOAuth2Session(app)

@app.route("/")
async def home():
    guild_count = config.get_guild_count()
    return await render_template(
        "./intex.html", 
        discord_url=Oauth.discord_login_url, 
        authorized = await discord.authorized,
        servercount=guild_count)

@app.route("/intex.html")
async def home1():
    guild_count = config.get_guild_count()

    return await render_template(
        "./intex.html", 
        discord_url=Oauth.discord_login_url,
        authorized = await discord.authorized, 
        servercount=guild_count)

@app.route("/documentation.html")
async def doc():
    cmds = config.getDocumentation()

    return await render_template(
        "./Documentation.html", 
        dictOfCommands=cmds,
        authorized = await discord.authorized
    )

@app.route("/About.html")
async def about():
    return await render_template("./About.html", discord_url=Oauth.discord_login_url, authorized = await discord.authorized)

@app.route("/dashboard/<int:guild_id>")
async def dashboard(guild_id):
    if not await discord.authorized:
        print("not authorized")
        return redirect(url_for("login")) 
    guild = config.get_guild(guild_id)
    if guild is None:
        print("guildnotfoundlmao")
        return redirect(f'https://discord.com/oauth2/authorize?&client_id={app.config["DISCORD_CLIENT_ID"]}&scope=bot&permissions=8&guild_id={guild_id}&response_type=code&redirect_uri={app.config["DISCORD_REDIRECT_URI"]}')
    
    user = await discord.fetch_user()
    settings = config.get_guild_settings
    return await render_template(
        "/dashboard.html", 
        username = user.name, 
        guildname=guild, 
        guild_id=guild_id,
        settings=settings,
        authorized = await discord.authorized, 
        selected="mainsettings")





@app.route("/dashboard/<int:guild_id>/<string:settingPage>")
async def dashboardSettingPage(guild_id, settingPage):
    if not await discord.authorized:
        print("not authorized")
        return redirect(url_for("login")) 
    guild = config.get_guild(guild_id)
    if guild is None:
        print("guildnotfoundlmao")
        return redirect(f'https://discord.com/oauth2/authorize?&client_id={app.config["DISCORD_CLIENT_ID"]}&scope=bot&permissions=8&guild_id={guild_id}&response_type=code&redirect_uri={app.config["DISCORD_REDIRECT_URI"]}')
    
    textchannels = config.return_channels(guild_id)

    user = await discord.fetch_user()

    print("check")
    settings = config.get_guild_settings(guild_id)

    return await render_template(
        "/dashboard.html", 
        username = user.name, 
        guildname=guild, 
        guild_id=guild_id,
        authorized = await discord.authorized, 
        settings = settings,
        textchannels = textchannels,
        selected=settingPage)




@app.route('/dashboard/<int:guild_id>/<string:settingPage>/handledata', methods=['POST'])
async def handledata(guild_id, settingPage):
    projectpath = await request.form
    form = {}
    for key in projectpath.keys():
        values = projectpath.getlist(key)
        if len(values) == 1:
            form[key] = values[0]
        else:
            form[key] = values
    print("------------------------------")
    print(form)
    print("------------------------------\n\n\n")
    modop = DiscordGuild.find_one({"id":guild_id}, {"automod"})["automod"]
    mainsettings = DiscordGuild.find_one({"id":guild_id}, {"settings"})["settings"]
    announcementChannels =DiscordGuild.find_one({"id":guild_id}, {"announcement channels"})["announcement channels"]
    suggestionChannels =DiscordGuild.find_one({"id":guild_id}, {"suggestion channels"})["suggestion channels"]
    automod = DiscordGuild.find_one({"id":guild_id}, {"automod"})["automod"]
    badwords = DiscordGuild.find_one({"id":guild_id}, {"badwords"})["badwords"]

    if settingPage == "automod":
        for x in projectpath:
            if projectpath.get(x) == "enabled" and x not in modop:
                modop.append(x)
            elif projectpath.get(x) == "disabled" and x in modop:
                modop.remove(x)
        DiscordGuild.update_one({"id":guild_id}, {"$set":{"automod":modop}})

    if settingPage == "mainsettings":
        for x in projectpath:
            if projectpath.get(x) == "enabled":
                mainsettings[x]["enabled"] = True
            else:
                mainsettings[x]["enabled"] = False
        DiscordGuild.update_one({"id":guild_id}, {"$set":{"settings":mainsettings}})

    if settingPage == "config":
        DiscordGuild.update_one({"id":guild_id}, {"$set":{"prefix":projectpath.get("prefix")}})
        regex = "\'\d{18}\'\:\s.+\}$"
        testreg = ".*"
        geId = "\d{18}"
        formKeys = form.keys()

        if "announcement channels" in formKeys:
            announcementChannels.clear()
            if type(form["announcement channels"]) == list:
                for channelDict in form["announcement channels"]:
                    valueString = re.findall(regex, channelDict)[0]
                    channelId = int(re.findall(geId, valueString)[0])
                    announcementChannels.append(channelId)
            else:
                valueString = re.findall(regex, form["announcement channels"])[0]
                channelId = int(re.findall(geId, valueString)[0])
                announcementChannels.append(channelId)
            announcementChannels = config.removeDupes(announcementChannels)
            DiscordGuild.update_one({"id":guild_id}, {"$set":{"announcement channels":announcementChannels}})


        if "suggestion channels" in formKeys:
            suggestionChannels.clear()
            if type(form["suggestion channels"]) == list:
                for channelDict in form["suggestion channels"]:
                    valueString = re.findall(regex, channelDict)[0]
                    channelId = int(re.findall(geId, valueString)[0])
                    suggestionChannels.append(channelId)
            else:
                valueString = re.findall(regex, form["suggestion channels"])[0]
                channelId = int(re.findall(geId, valueString)[0])
                suggestionChannels.append(channelId)
            suggestionChannels = config.removeDupes(suggestionChannels)
            DiscordGuild.update_one({"id":guild_id}, {"$set":{"suggestion channels":suggestionChannels}})


        if "badwords" in formKeys:
            newBadWords = form["badwords"]
            print(newBadWords)

            if type(newBadWords) == list:
                newBadWords = [x for x in newBadWords if x!=""]
                DiscordGuild.update_one({"id":guild_id}, {"$set":{"badwords":newBadWords}})
            else:
                DiscordGuild.update_one({"id":guild_id}, {"$set":{"badwords":[newBadWords]}})

    
    return redirect(f"/dashboard/{guild_id}/{settingPage}")





@app.route("/selectServerPage.html")
async def selectServer():
    if not await discord.authorized:
        return redirect(url_for("login")) 

    guild_count = config.get_guild_count()
    guild_ids = config.get_guild_ids()

    user_guilds = await discord.fetch_guilds()
    

    guilds = []

    for guild in user_guilds:
        if guild.permissions.administrator:			
            guild.class_color = "green-border" if guild.id in guild_ids else "red-border"
            guilds.append(guild)

    guilds.sort(key = lambda x: x.class_color == "red-border")
    name = (await discord.fetch_user()).name
    return await render_template("/selectServerPage.html", guild_count = guild_count, guilds = guilds, username=name, authorized = await discord.authorized)


@app.route("/login")
async def login():
    return await discord.create_session()


@app.route("/callback")
async def callback():
    try:
        await discord.callback()
    except Exception:
        pass

    return redirect(url_for("selectServer"))


if __name__ == '__main__':
    app.run(debug=True)