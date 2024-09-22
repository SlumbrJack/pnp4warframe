
from datetime import datetime
from discord.ext import commands, tasks
import discord
from dataclasses import dataclass
import requests
import aiosqlite
import time

bot_token = "MTE4NDIzOTY4OTY3NTMyMTQwNQ.GZdsFr.-B-RIpUGWAVqIXb-oRaz_ArZJ-0vxMaTUrgD2Y"
channel_id = 1184248253722669096
bot_user_id = 1184239689675321405
newschannel_id = 1234501703961808906


max_session_time_minutes = 1
startInvasionRefresh = False
def check(message):
        return message.author.id == bot_user_id
@dataclass
class Session:
    is_active: bool = False
    start_time: int = 0
 
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all() )



session = Session()
invasionMessages = []

@bot.event
async def on_ready():
    #channel = bot.get_channel(channel_id)
   # await channel.purge(bulk = False)
    async with aiosqlite.connect("main2.db", timeout=30) as db:
        async with db.cursor() as cursor:
            await cursor.execute('SELECT guildID FROM channels',)
            data = await cursor.fetchall()
            await db.commit()
            if data:
#buy table
                async with aiosqlite.connect("main2.db") as db:
                    async with db.cursor() as cursor:
                        #await cursor.execute('DROP TABLE buyorders')
                        await cursor.execute('CREATE TABLE IF NOT EXISTS buyorders (id INTEGER , item STRING, price INTEGER)')
                    await db.commit()
            #sell table
                async with aiosqlite.connect("main2.db") as db:
                    async with db.cursor() as cursor:
                        await cursor.execute('CREATE TABLE IF NOT EXISTS sellorders (id INTEGER , item STRING, price INTEGER)')
                    await db.commit()
            #channels table
                async with aiosqlite.connect("main2.db") as db:
                    async with db.cursor() as cursor:
                        #await cursor.execute('DROP TABLE channels')
                        await cursor.execute('CREATE TABLE IF NOT EXISTS channels (guildID INTEGER , channelID INTEGER, channelUse STRING)')
                    await db.commit()
            #news table
                async with aiosqlite.connect("main2.db") as db:
                    async with db.cursor() as cursor:
                        #await cursor.execute('DROP TABLE newsMessages')
                        await cursor.execute('CREATE TABLE IF NOT EXISTS newsMessages (guildID INTEGER , channelID INTEGER, messageID INTEGER, newsID STRING)')
                    await db.commit()
            #alerts table
                async with aiosqlite.connect("main2.db") as db:
                    async with db.cursor() as cursor:
                        #await cursor.execute('DROP TABLE alertsMessages')
                        await cursor.execute('CREATE TABLE IF NOT EXISTS alertsMessages (guildID INTEGER , channelID INTEGER, messageID INTEGER, alertsID STRING)')
                    await db.commit()
            #events table
                async with aiosqlite.connect("main2.db") as db:
                    async with db.cursor() as cursor:
                        #await cursor.execute('DROP TABLE eventsMessages')
                        await cursor.execute('CREATE TABLE IF NOT EXISTS eventsMessages (guildID INTEGER , channelID INTEGER, messageID INTEGER, eventsID STRING)')
                    await db.commit()
            #invasions table
                async with aiosqlite.connect("main2.db") as db:
                    async with db.cursor() as cursor:
                        #await cursor.execute('DROP TABLE invasionsMessages')
                        await cursor.execute('CREATE TABLE IF NOT EXISTS invasionsMessages (guildID INTEGER , channelID INTEGER, messageID INTEGER, invasionsID STRING)')
                    await db.commit()
                news_Reset.start() 
                clearOldNews.start()
                alerts_Reset.start()
                clearOldAlerts.start()
                invasions_Reset.start()
                clearOldInvasions.start()
                events_Reset.start()
                clearOldEvents.start()
                checkPurchaseOrders.start()
                checkSellOrders.start()
            for guild in bot.guilds:
                if(data):
                    for x in data:
                        if guild.id not in x:
                            await guild.system_channel.send("Hello, I am WarframeBot. Click below to setup this bot!", view=SetupButtons())
                else:
                    await guild.system_channel.send("Hello, I am WarframeBot. Click below to setup this bot!", view=SetupButtons())
            
                

    #await channel.send("Hello! Warframebot is ready!", silent = True)

#START OF SETUP CODE
#
@bot.event
async def on_guild_join(guild):
    print("joined server")
    channel =  guild.system_channel
    await channel.send("Hello, I am WarframeBot. Click below to setup this bot!", view=SetupButtons())

class SetupButtons(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
    @discord.ui.button(label="Set Up",style=discord.ButtonStyle.blurple)
    async def gray_button(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.edit_message(content="", delete_after=1)
        await setup(interaction.channel_id, interaction.guild_id)

class LeaveButtonConfirm(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
    @discord.ui.button(label="Keep", style=discord.ButtonStyle.green)
    async def green_button(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.edit_message(content="", delete_after=0)
        await testStay()
    @discord.ui.button(label="Reset Channels", style=discord.ButtonStyle.blurple)
    async def blurple_button(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.edit_message(content="", delete_after=0)
        await resetChannels(interaction.guild_id)
        await setup(interaction.channel_id, interaction.guild_id)
    @discord.ui.button(label="Remove", style=discord.ButtonStyle.red)
    async def red_button(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.edit_message(content="", delete_after=0)
        await resetChannels(interaction.guild_id)
        await interaction.guild.leave()
    

@bot.command()
async def testRemove(ctx):
    await ctx.send("Remove WarframeBot?", view=LeaveButtonConfirm())
async def testLeave():
    print("I left!")
async def testStay():
    print("I stayed!")
@bot.command()    
async def testInvasionButtons(ctx):
    response = requests.get("https://api.warframestat.us/pc/invasions")
    status = int(response.status_code)
    newsDict = {}
    if status == 200:
        for mission in response.json():
            jsonInvasionID = mission["id"]
            title = mission["desc"]
            node = mission["node"]
            attackreward = ""
            defendreward = ""
            defendimage = ""
            if "reward" in mission["attacker"]:
                attackreward = mission["attacker"]["reward"]["asString"]
                attackimage = mission["attacker"]["reward"]["thumbnail"]
            if "reward" in mission["defender"]:
                defendreward = mission["defender"]["reward"]["asString"]
                defendimage = mission["defender"]["reward"]["thumbnail"]
            embedVar = discord.Embed(title=title, description=node, color=0xffa40d)
            if(attackreward != ""): embedVar.add_field(name="Attack Reward", value=attackreward, inline=True)
            if(defendreward != ""): embedVar.add_field(name="Defend Reward", value=defendreward, inline=True)
            embedVar.set_image(url=defendimage) 
            await ctx.send(embeds=[embedVar])
            


#@bot.command(brief='Sets up the server by adding new channels', description='This command will add new channels under a new category to the server.\nWARNING: DO NO RUN THIS COMMAND MULTIPLE TIMES. DO NOT DELETE THISE CHANNELS WITHOUT USING THE CORRECT COMMAND')
async def setup(channelid, guildid):
    guild = bot.get_guild(guildid)
    mainchannel = guild.get_channel(channelid)
    print("starting setup")
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(send_messages=False)
    }
    async with aiosqlite.connect("main2.db") as db:
        async with db.cursor() as cursor:
            
            category = await guild.create_category("WARFRAMEBOT")
            #await cursor.execute('DROP TABLE channels')
            await cursor.execute('INSERT INTO channels (guildID, channelID, channelUse) VALUES (?,?,?)', (guild.id, category.id, "header"))
            channel = await guild.create_text_channel("warframe-news", overwrites = overwrites, category = category)
            await cursor.execute('INSERT INTO channels (guildID, channelID, channelUse) VALUES (?,?,?)', (guild.id, channel.id, "news"))
            channel = await guild.create_text_channel("warframe-alerts", overwrites = overwrites, category = category)
            await cursor.execute('INSERT INTO channels (guildID, channelID, channelUse) VALUES (?,?,?)', (guild.id, channel.id, "alerts"))
            channel = await guild.create_text_channel("warframe-events", overwrites = overwrites, category = category)
            await cursor.execute('INSERT INTO channels (guildID, channelID, channelUse) VALUES (?,?,?)', (guild.id, channel.id, "events"))
            channel = await guild.create_text_channel("warframe-invasions", overwrites = overwrites, category = category)
            await cursor.execute('INSERT INTO channels (guildID, channelID, channelUse) VALUES (?,?,?)', (guild.id, channel.id, "invasions"))
            channel = await guild.create_text_channel("warframe-cycles", overwrites = overwrites, category = category)
            await cursor.execute('INSERT INTO channels (guildID, channelID, channelUse) VALUES (?,?,?)', (guild.id, channel.id, "cycles"))
            channel = await guild.create_text_channel("warframe-market", category = category)
            await cursor.execute('INSERT INTO channels (guildID, channelID, channelUse) VALUES (?,?,?)', (guild.id, channel.id, "market"))
            await cursor.execute('DELETE FROM newsMessages where guildID = ?', (guildid,))
            await cursor.execute('DELETE FROM alertsMessages where guildID = ?', (guildid,))
            await cursor.execute('DELETE FROM invasionsMessages where guildID = ?', (guildid,))
            await cursor.execute('DELETE FROM eventsMessages where guildID = ?', (guildid,))
        await db.commit()
        if(news_Reset.is_running()):
            news_Reset.restart()
            alerts_Reset.restart()
            invasions_Reset.restart()
            events_Reset.restart()
            checkPurchaseOrders.restart()
            checkSellOrders.restart()
        else:
            news_Reset.start()
            alerts_Reset.start()
            invasions_Reset.start()
            events_Reset.start()
            checkPurchaseOrders.start()
            checkSellOrders.start()
    if mainchannel:
        await mainchannel.send("The server is now set up for WarframeBot. Please type !help to learn more. Type \"!help (command name)\" to learn more about a specific command")

@bot.command(brief='Removes all channels created by the bot', description='This command will remove the channels and categories created by this bot\nOnce complete the bot will leave the server')
async def removeBotFromServer(ctx):
    await ctx.send("What would you like to do?", view=LeaveButtonConfirm())


async def resetChannels(guildID):
    async with aiosqlite.connect("main2.db", timeout=30) as db:
        async with db.cursor() as cursor:
            await cursor.execute('SELECT channelID FROM channels WHERE guildID = ?', (guildID,))
            data = await cursor.fetchall()
            if data:
                for channel in data:
                    await bot.get_channel(channel[0]).delete()
                await cursor.execute('DELETE FROM channels WHERE guildID = ?', (guildID,))
                
            await cursor.execute('SELECT channelID FROM newsMessages where guildID = ?', (guildID,))
            data = await cursor.fetchall()
            if data:
                await cursor.execute('DELETE FROM newsMessages where guildID = ?', (guildID,))

            await cursor.execute('SELECT channelID FROM alertsMessages where guildID = ?', (guildID,))
            data = await cursor.fetchall()
            if data:
                await cursor.execute('DELETE FROM alertsMessages where guildID = ?', (guildID,))

            await cursor.execute('SELECT channelID FROM eventsMessages where guildID = ?', (guildID,))
            data = await cursor.fetchall()
            if data:
                await cursor.execute('DELETE FROM eventsMessages where guildID = ?', (guildID,))
            
            await cursor.execute('SELECT channelID FROM invasionsMessages where guildID = ?', (guildID,))
            data = await cursor.fetchall()
            if data:
                await cursor.execute('DELETE FROM invasionsMessages where guildID = ?', (guildID,))
        await db.commit()
    await db.close()

@tasks.loop(minutes=30)
async def news_Reset():
    response = requests.get("https://api.warframestat.us/pc/news")
    status = int(response.status_code)
    channel = 0
    if status == 200:

        async with aiosqlite.connect("main2.db", timeout=30) as db:
            async with db.cursor() as cursor: 
                for guild in bot.guilds:
                    await cursor.execute('SELECT channelID from channels where guildID = ? AND channelUse = ?', (guild.id, "news"))
                    data = await cursor.fetchone()
                    if data:
                        for x in data:
                            channel = data[0]         
                    await cursor.execute('SELECT newsID FROM newsMessages WHERE guildID = ?', (guild.id,))
                    data = await cursor.fetchall()
                    if data: #if there are news messages, go through all possible ones to find matches, if no match, post it
                        for news in response.json():
                            jsonNewsID = news["id"]
                            matchFound = False
                            stringbase = news["date"]
                            datestring = stringbase.split("T")[0]
                            timestring = stringbase[:-5].split("T")[1]
                            datetimestring = f"{datestring}-{timestring}"
                            timeobj = datetime.strptime(datetimestring, '%Y-%m-%d-%H:%M:%S')#T%H:%M%S
                            epochtime = time.mktime(timeobj.timetuple())
                            #await ctx.send(f"<t:{int(epochtime)}:R>")
                            for x in data:
                                DBID = x[0] 
                                if jsonNewsID == DBID:
                                    matchFound = True
                            if not matchFound:
                                stringbase = news["date"]
                                description = news["message"]
                                link = news["link"]
                                embedVar = discord.Embed(title=description, description=f"<t:{int(epochtime)}:R>", color=0x00ff00)
                                embedVar.add_field(name="", value=f"[Link]({link})", inline=False)
                                embedVar.set_image(url=news["imageLink"]) 
                                message = await guild.get_channel(channel).send(embeds=[embedVar],silent=True)
                                await cursor.execute('INSERT INTO newsMessages (guildID, channelID, messageID, newsID) VALUES (?,?,?,?)', (guild.id, channel, message.id, jsonNewsID ))
                    #if there are no news messages in the guild, fill it
                    else:
                        for news in response.json():
                                newsID = news["id"]
                                description = news["message"]
                                link = news["link"]
                                stringbase = news["date"]
                                datestring = stringbase.split("T")[0]
                                timestring = stringbase[:-5].split("T")[1]
                                datetimestring = f"{datestring}-{timestring}"
                                timeobj = datetime.strptime(datetimestring, '%Y-%m-%d-%H:%M:%S')#T%H:%M%S
                                epochtime = time.mktime(timeobj.timetuple())
                                embedVar = discord.Embed(title=description, description=f"<t:{int(epochtime)}:R>", color=0x00ff00)
                                embedVar.add_field(name="", value=f"[Link]({link})", inline=False)
                                embedVar.set_image(url=news["imageLink"]) 
                                message = await guild.get_channel(channel).send(embeds=[embedVar],silent=True)
                                await cursor.execute('INSERT INTO newsMessages (guildID, channelID, messageID, newsID) VALUES (?,?,?,?)', (guild.id, channel, message.id, newsID ))           
            await db.commit()
            await db.close()
            print("News Finished")



@tasks.loop(minutes=30)
async def alerts_Reset():
    response = requests.get("https://api.warframestat.us/pc/alerts")
    status = int(response.status_code)
    channel = 0
    if status == 200:
        async with aiosqlite.connect("main2.db", timeout=30) as db:
            async with db.cursor() as cursor: 
                for guild in bot.guilds:
                    await cursor.execute('SELECT channelID from channels where guildID = ? AND channelUse = ?', (guild.id, "alerts"))
                    data = await cursor.fetchone()
                    if data:
                        for x in data:
                            channel = data[0]
                    await cursor.execute('SELECT alertsID FROM alertsMessages WHERE guildID = ?', (guild.id,))
                    data = await cursor.fetchall()
                    if data: #if there are alerts, go through all possible ones to find matches, if no match, post it
                        for alerts in response.json():
                            jsonAlertsID = alerts["id"]
                            matchFound = False
                            for x in data:
                                DBID = x[0] 
                                if jsonAlertsID == DBID:
                                    matchFound = True
                            if not matchFound:
                                stringbase = alerts["expiry"]
                                datestring = stringbase.split("T")[0]
                                timestring = stringbase[:-5].split("T")[1]
                                datetimestring = f"{datestring}-{timestring}"
                                timeobj = datetime.strptime(datetimestring, '%Y-%m-%d-%H:%M:%S')#T%H:%M%S
                                epochtime = time.mktime(timeobj.timetuple())
                
                                description = alerts["mission"]["levelOverride"]
                                location = alerts["mission"]["nodeKey"]
                                rewards = alerts["mission"]["reward"]["asString"]
                                end = f"<t:{int(epochtime)}:R>"
                                embedVar = discord.Embed(title=description, description=f"<t:{int(epochtime)}:R>", color=0x6699ff)
                                embedVar.add_field(name="Location", value=location, inline=False)
                                embedVar.add_field(name="Rewards", value=rewards, inline=True)
                                embedVar.add_field(name="Ends", value=end)
                                message = await guild.get_channel(channel).send(embeds=[embedVar],silent=True)
                                await cursor.execute('INSERT INTO alertsMessages (guildID, channelID, messageID, alertsID) VALUES (?,?,?,?)', (guild.id, channel, message.id, jsonAlertsID ))
                    #if there are no news messages in the guild, fill it
                    else:
                        for alerts in response.json():
                                jsonAlertsID = alerts["id"]
                                stringbase = alerts["expiry"]
                                datestring = stringbase.split("T")[0]
                                timestring = stringbase[:-5].split("T")[1]
                                datetimestring = f"{datestring}-{timestring}"
                                timeobj = datetime.strptime(datetimestring, '%Y-%m-%d-%H:%M:%S')#T%H:%M%S
                                epochtime = time.mktime(timeobj.timetuple())
                
                                description = alerts["mission"]["levelOverride"]
                                location = alerts["mission"]["nodeKey"]
                                rewards = alerts["mission"]["reward"]["asString"]
                                end = f"<t:{int(epochtime)}:R>"
                                embedVar = discord.Embed(title=description, description=f"", color=0x6699ff)
                                embedVar.add_field(name="Location", value=location, inline=False)
                                embedVar.add_field(name="Rewards", value=rewards, inline=True)
                                embedVar.add_field(name="Ends", value=end)
                                message = await guild.get_channel(channel).send(embeds=[embedVar],silent=True)
                                await cursor.execute('INSERT INTO alertsMessages (guildID, channelID, messageID, alertsID) VALUES (?,?,?,?)', (guild.id, channel, message.id, jsonAlertsID ))



                           
            await db.commit()
            await db.close()
            print("Alerts Finished")

@tasks.loop(minutes=30)
async def invasions_Reset():
    response = requests.get("https://api.warframestat.us/pc/invasions")
    status = int(response.status_code)
    if status == 200:
        async with aiosqlite.connect("main2.db", timeout=30) as db:
            async with db.cursor() as cursor: 
                for guild in bot.guilds:
                    await cursor.execute('SELECT channelID from channels where guildID = ? AND channelUse = ?', (guild.id, "invasions"))
                    data = await cursor.fetchone()
                    if data:
                        for x in data:
                            channel = data[0]
                    await cursor.execute('SELECT invasionsID FROM invasionsMessages WHERE guildID = ?', (guild.id,))
                    data = await cursor.fetchall()
                    if data: #if there are invasions, go through all possible ones to find matches, if no match, post it
                        matchFound = False
                        for mission in response.json():
                            jsoninvasionsID = mission["id"]
                            matchFound = False
                            for x in data:
                                DBID = x[0] 
                                if jsoninvasionsID == DBID:
                                    matchFound = True
                            if not matchFound:
                                if mission["completed"] != True:
                                    title = mission["desc"]
                                    node = mission["node"]
                                    attackreward = ""
                                    defendreward = ""
                                    defendimage = ""
                                    if "reward" in mission["attacker"]:
                                        attackreward = mission["attacker"]["reward"]["asString"]
                                    if "reward" in mission["defender"]:
                                        defendreward = mission["defender"]["reward"]["asString"]
                                        defendimage = mission["defender"]["reward"]["thumbnail"]
                                    embedVar = discord.Embed(title=title, description=node, color=0xffa40d)
                                    if(attackreward != ""): embedVar.add_field(name="Attack Reward", value=attackreward, inline=True)
                                    if(defendreward != ""): embedVar.add_field(name="Defend Reward", value=defendreward, inline=True)
                                    embedVar.set_image(url=defendimage) 
                                    message = await guild.get_channel(channel).send(embeds=[embedVar])
                                    await cursor.execute('INSERT INTO invasionsMessages (guildID, channelID, messageID, invasionsID) VALUES (?,?,?,?)', (guild.id, channel, message.id, jsoninvasionsID ))
                    else:
                        for mission in response.json(): 
                            jsoninvasionsID = mission["id"]
                            if mission["completed"] != True:
                                title = mission["desc"]
                                node = mission["node"]
                                attackreward = ""
                                defendreward = ""
                                defendimage = ""
                                if "reward" in mission["attacker"]:
                                    attackreward = mission["attacker"]["reward"]["asString"]
                                if "reward" in mission["defender"]:
                                    defendreward = mission["defender"]["reward"]["asString"]
                                    defendimage = mission["defender"]["reward"]["thumbnail"]
                                embedVar = discord.Embed(title=title, description=node, color=0xffa40d)
                                if(attackreward != ""): embedVar.add_field(name="Attack Reward", value=attackreward, inline=True)
                                if(defendreward != ""): embedVar.add_field(name="Defend Reward", value=defendreward, inline=True)
                                embedVar.set_image(url=defendimage) 
                                message = await guild.get_channel(channel).send(embeds=[embedVar])
                                await cursor.execute('INSERT INTO invasionsMessages (guildID, channelID, messageID, invasionsID) VALUES (?,?,?,?)', (guild.id, channel, message.id, jsoninvasionsID ))
                    await db.commit() 
            await db.close()
        print("Invasions finished")
        

@tasks.loop(minutes=30)
async def events_Reset():
    response = requests.get("https://api.warframestat.us/pc/events")
    status = int(response.status_code)
    channel = 0
    if status == 200:
        async with aiosqlite.connect("main2.db", timeout=30) as db:
            async with db.cursor() as cursor: 
                for guild in bot.guilds:
                    await cursor.execute('SELECT channelID from channels where guildID = ? AND channelUse = ?', (guild.id, "events"))
                    data = await cursor.fetchone()
                    if data:
                        for x in data:
                            channel = data[0]
                    await cursor.execute('SELECT eventsID FROM eventsMessages WHERE guildID = ?', (guild.id,))
                    data = await cursor.fetchall()
                    if data: #if there are events, go through all possible ones to find matches, if no match, post it
                        for events in response.json():
                            jsoneventsID = events["id"]
                            matchFound = False
                            for x in data:
                                DBID = x[0] 
                                if jsoneventsID == DBID:
                                    matchFound = True
                            if not matchFound:
                                stringbase = events["expiry"]
                                datestring = stringbase.split("T")[0]
                                timestring = stringbase[:-5].split("T")[1]
                                datetimestring = f"{datestring}-{timestring}"
                                timeobj = datetime.strptime(datetimestring, '%Y-%m-%d-%H:%M:%S')#T%H:%M%S
                                epochtime = time.mktime(timeobj.timetuple())

                                description = events["tooltip"]
                                node = ""
                                if("node" in events):
                                    node = events["node"]
                                elif("victimNode" in events):
                                    node = events["victimNode"]
                                rewards = ""
                                if(len(events["rewards"]) != 0):
                                    rewards = events["rewards"][0]["asString"]
                                img = ""
                                if events["rewards"][0]["thumbnail"] != "": img = events["rewards"][0]["thumbnail"]
                                end = f"<t:{int(epochtime)}:R>"
                                embedVar = discord.Embed(title=description, description=f"", color=0xffff99)
                                embedVar.add_field(name="Location", value=node, inline=False)
                                embedVar.add_field(name="Rewards", value=rewards, inline=True)
                                embedVar.add_field(name="Ends", value=end)
                                if img != "": embedVar.set_image(url=img)
                                message = await guild.get_channel(channel).send(embeds=[embedVar],silent=True)
                                await cursor.execute('INSERT INTO eventsMessages (guildID, channelID, messageID, eventsID) VALUES (?,?,?,?)', (guild.id, channel, message.id, jsoneventsID ))
                    #if there are no news messages in the guild, fill it
                    else:
                        for events in response.json():
                                jsoneventsID = events["id"]
                                stringbase = events["expiry"]
                                datestring = stringbase.split("T")[0]
                                timestring = stringbase[:-5].split("T")[1]
                                datetimestring = f"{datestring}-{timestring}"
                                timeobj = datetime.strptime(datetimestring, '%Y-%m-%d-%H:%M:%S')#T%H:%M%S
                                epochtime = time.mktime(timeobj.timetuple())
                                description = events["tooltip"]
                                node = ""
                                if("node" in events):
                                    node = events["node"]
                                elif("victimNode" in events):
                                    node = events["victimNode"]
                                rewards = ""
                                img = ""
                                if(len(events["rewards"]) != 0):
                                    rewards = events["rewards"][0]["asString"]
                                    if events["rewards"][0]["thumbnail"] != "": img = events["rewards"][0]["thumbnail"]
                                
                                
                                end = f"<t:{int(epochtime)}:R>"
                                embedVar = discord.Embed(title=description, description=f"", color=0xffff99)
                                embedVar.add_field(name="Location", value=node, inline=False)
                                if rewards != "": embedVar.add_field(name="Rewards", value=rewards, inline=True)
                                embedVar.add_field(name="Ends", value=end)
                                if img != "": embedVar.set_image(url=img)
                                message = await guild.get_channel(channel).send(embeds=[embedVar],silent=True)
                                await cursor.execute('INSERT INTO eventsMessages (guildID, channelID, messageID, eventsID) VALUES (?,?,?,?)', (guild.id, channel, message.id, jsoneventsID ))



                           
            await db.commit()
        await db.close()
        print("events Finished")


@tasks.loop(minutes=30)
async def clearOldNews():
    channel = 0
    response = requests.get("https://api.warframestat.us/pc/news")
    status = int(response.status_code)
    if status == 200:

        async with aiosqlite.connect("main2.db") as db:
            async with db.cursor() as cursor: 
                for guild in bot.guilds:
                    await cursor.execute('SELECT channelID from channels where guildID = ? AND channelUse = ?', (guild.id, "news"))
                    data = await cursor.fetchone()
                    if data:
                        for x in data:
                            channel = data[0]
                await cursor.execute('SELECT newsID, messageID FROM newsMessages WHERE guildID = ?', (guild.id,))
                data = await cursor.fetchall()
                for x in data:
                    matchFound = False
                    DBID = x[0]

                    for news in response.json():
                        if news["id"] == DBID:
                            matchFound = True
                    if not matchFound:
                        message = await guild.get_channel(channel).fetch_message(x[1])
                        await message.delete()
                        await cursor.execute('DELETE FROM newsMessages WHERE newsID = ? AND messageID = ?', (DBID, x[1]))
                        print("DELETED NEWS")
            await db.commit()
        await db.close()

@tasks.loop(minutes=30)
async def clearOldAlerts():
    channel = 0
    response = requests.get("https://api.warframestat.us/pc/alerts")
    status = int(response.status_code)
    if status == 200:
        async with aiosqlite.connect("main2.db") as db:
            async with db.cursor() as cursor: 
                for guild in bot.guilds:
                    await cursor.execute('SELECT channelID from channels where guildID = ? AND channelUse = ?', (guild.id, "alerts"))
                    data = await cursor.fetchone()
                    if data:
                        for x in data:
                            channel = data[0]
                await cursor.execute('SELECT alertsID, messageID FROM alertsMessages WHERE guildID = ?', (guild.id,))
                data = await cursor.fetchall()
                for x in data:
                    matchFound = False
                    DBID = x[0]

                    for alerts in response.json():
                        if alerts["id"] == DBID:
                            matchFound = True
                    if not matchFound:
                        message = await guild.get_channel(channel).fetch_message(x[1])
                        await message.delete()
                        await cursor.execute('DELETE FROM alertsMessages WHERE alertsID = ? AND messageID = ?', (DBID, x[1]))
                        print("DELETED ALERTS")
            await db.commit()
        await db.close()

@tasks.loop(minutes=30)
async def clearOldInvasions():
    channel = 0
    response = requests.get("https://api.warframestat.us/pc/invasions")
    status = int(response.status_code)
    if status == 200:

        async with aiosqlite.connect("main2.db") as db:
            async with db.cursor() as cursor: 
                for guild in bot.guilds:
                    await cursor.execute('SELECT channelID from channels where guildID = ? AND channelUse = ?', (guild.id, "invasions"))
                    data = await cursor.fetchone()
                    if data:
                        for x in data:
                            channel = data[0]
                await cursor.execute('SELECT invasionsID, messageID FROM invasionsMessages WHERE guildID = ?', (guild.id,))
                data = await cursor.fetchall()
                for x in data:
                    matchFound = False
                    DBID = x[0]

                    for invasions in response.json():
                        if invasions["id"] == DBID and invasions["completed"] == False:
                            matchFound = True
                    if not matchFound:
                        message = await guild.get_channel(channel).fetch_message(x[1])
                        await message.delete()
                        await cursor.execute('DELETE FROM invasionsMessages WHERE invasionsID = ? AND messageID = ?', (DBID, x[1]))
                        print("DELETED invasions")
            await db.commit()
        await db.close()

@tasks.loop(minutes=30)
async def clearOldEvents():
    channel = 0
    response = requests.get("https://api.warframestat.us/pc/events")
    status = int(response.status_code)
    if status == 200:

        async with aiosqlite.connect("main2.db") as db:
            async with db.cursor() as cursor: 
                for guild in bot.guilds:
                    await cursor.execute('SELECT channelID from channels where guildID = ? AND channelUse = ?', (guild.id, "events"))
                    data = await cursor.fetchone()
                    if data:
                        for x in data:
                            channel = data[0]
                await cursor.execute('SELECT eventsID, messageID FROM eventsMessages WHERE guildID = ?', (guild.id,))
                data = await cursor.fetchall()
                for x in data:
                    matchFound = False
                    DBID = x[0]

                    for events in response.json():
                        if events["id"] == DBID:
                            matchFound = True
                    if not matchFound:
                        message = await guild.get_channel(channel).fetch_message(x[1])
                        await message.delete()
                        await cursor.execute('DELETE FROM eventsMessages WHERE eventsID = ? AND messageID = ?', (DBID, x[1]))
                        print("DELETED events")
            await db.commit()
        await db.close()

     
                        

@bot.command(brief='Lists cycles for open zones', description= 'Lists the current cycles for Cetus, Orb Vallis, and Cambion Drift')
async def cycles(ctx):
    requests.patch(url="https://discord.com/api/v9/users/@warframebot", headers= {"authorization": bot_token}, json = {"bio": "TestBot Bio"} )
    response = requests.get("https://api.warframestat.us/pc/cetusCycle")
    status = int(response.status_code)
    if status == 200:
        stringbase = response.json()["shortString"]
        cycleStatus = response.json()["state"]
        await ctx.send("It is currently: " + cycleStatus + " in Cetus\n" + stringbase)


    response = requests.get("https://api.warframestat.us/pc/vallisCycle")
    status = int(response.status_code)
    if status == 200:
        stringbase = response.json()["shortString"]
        cycleStatus = response.json()["state"]
        await ctx.send("It is currently: " + cycleStatus + " in Orb Vallis\n" + stringbase)

    response = requests.get("https://api.warframestat.us/pc/cambionCycle")
    status = int(response.status_code)
    if status == 200:
        stringbase = response.json()["timeLeft"]
        cycleStatus = response.json()["state"]
        await ctx.send("It is currently: " + cycleStatus + " in Cambion Drift\n" + stringbase)

@bot.command(brief='Information on the Void Trader', description='')
async def baro(ctx):
    response = requests.get("https://api.warframestat.us/pc/voidTrader")
    status = int(response.status_code)
    if status == 200:
        bActive = response.json()["active"]
        location = response.json()["location"]
        arrives = response.json()["startString"]
        leaves = response.json()["endString"]
        if(bActive):
            stringbase = response.json()["expiry"]
            datestring = stringbase.split("T")[0]
            timestring = stringbase[:-5].split("T")[1]
            datetimestring = f"{datestring}-{timestring}"
            timeobj = datetime.strptime(datetimestring, '%Y-%m-%d-%H:%M:%S')#T%H:%M%S
            epochtime = time.mktime(timeobj.timetuple())
            await ctx.send("Baro is currently at " + location +" and will leave " + f"<t:{int(epochtime)}:R>")
        else:
            stringbase = response.json()["activation"]
            datestring = stringbase.split("T")[0]
            timestring = stringbase[:-5].split("T")[1]
            datetimestring = f"{datestring}-{timestring}"
            timeobj = datetime.strptime(datetimestring, '%Y-%m-%d-%H:%M:%S')#T%H:%M%S
            epochtime = time.mktime(timeobj.timetuple())
            await ctx.send("Baro will arrive at " + location + f" <t:{int(epochtime)}:R>")


'''
@bot.event
async def on_command_error(ctx,error):
    if isinstance(error, commands.CommandError):
        
        await ctx.send("There was an error using that command, use \"!help (the command you are trying to use)\" to learn more!")    
'''
@bot.command(brief= 'Adds an item to a purchase wishlist', description = 'Adds an item you would like to purchase to a wish list.\nWhen a sell order is placed on WarframeMarket for less than or equal to your desired price, you will recieve a DM letting you know.\nExample usage: !addPurchase nezha_prime_neuroptics_blueprint 20')
async def addPurchase(ctx, item = commands.parameter(description="Must be represented in this format: mirage_prime_systems"), price = commands.parameter(description="The price (in platinum) you are looking to buy this item for")): 
    response = requests.get(f"https://api.warframe.market/v1/items/{item}/orders")
    status = int(response.status_code)
    if not price.isdigit():
        await ctx.send("There was an error using that command, use \"!help (the command you are trying to use)\" to learn more!")
    elif status != 200:
        await ctx.send("There was an error using that command, you may have type the item name incorrectly. Use \"!help (the command you are trying to use)\" to learn more!")
    else:
        async with aiosqlite.connect("main2.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute('SELECT id FROM buyorders WHERE item = ? AND id = ?', (item.lower(), ctx.message.author.id))
                data = await cursor.fetchone()
                if data:
                    await ctx.send("You have already wishlisted this item")
                else:
                    await cursor.execute('INSERT INTO buyorders (id, item, price) VALUES (?,?,?)', (ctx.message.author.id, item.lower(), price))
                    await ctx.send("You have added " + item + " to your purchase wishlist for " + price + " platinum")
            await db.commit()
        await db.close()

@bot.command(brief= 'Removes an item from the purchase wishlist', description= 'Removes an item from your purchase wishlist.\nYou will no longer receive messages about this item. Example usage: !removePurchase nidus_prime_chassis_blueprint') 
async def removePurchase(ctx, item = commands.parameter(description="Must be represented in this format: mirage_prime_systems")):
    async with aiosqlite.connect("main2.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('DELETE FROM buyorders WHERE item = ? AND id = ?',  (item.lower(), ctx.message.author.id))
            await ctx.send("You have removed " + item + " from your purchase wishlist")
        await db.commit()
    await db.close()

@bot.command(brief= 'Adds an item to a sell wishlist', description = 'Adds an item you would like to sell to a wish list.\nWhen a buy order is placed on WarframeMarket for more than or equal to your desired price, you will recieve a DM letting you know.\nExample usage: !addSale nezha_prime_neuroptics_blueprint 10')
async def addSale(ctx, item = commands.parameter(description="Must be represented in this format: mirage_prime_systems"), price = commands.parameter(description="The price (in platinum) you are looking to buy this item for")):
    response = requests.get(f"https://api.warframe.market/v1/items/{item}/orders")
    status = int(response.status_code)
    if not price.isdigit():
        await ctx.send("There was an error using that command, use \"!help (the command you are trying to use)\" to learn more!")
    elif status != 200:
        await ctx.send("There was an error using that command, you may have type the item name incorrectly. Use \"!help (the command you are trying to use)\" to learn more!")
    else:
        async with aiosqlite.connect("main2.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute('SELECT id FROM sellorders WHERE item = ? AND id = ?', (item.lower(), ctx.message.author.id))
                data = await cursor.fetchone()
                if data:
                    await ctx.send("You have already wishlisted this item")
                else:
                    await cursor.execute('INSERT INTO sellorders (id, item, price) VALUES (?,?,?)', (ctx.message.author.id, item.lower(), price))
                    await ctx.send("You have added " + item + " to your sell wishlist for " + price + " platinum")
            await db.commit()
        await db.close()

@bot.command(brief= 'Removes an item from the sell wishlist', description= 'Removes an item from your sale wishlist.\nYou will no longer receive messages about this item. Example usage: !removeSale nidus_prime_chassis_blueprint')
async def removeSale(ctx, item):
    async with aiosqlite.connect("main2.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('DELETE FROM sellorders WHERE item = ? AND id = ?',  (item.lower(), ctx.message.author.id))
            await ctx.send("You have removed " + item + " from your sell wishlist")
        await db.commit()
    await db.close()

@bot.command(brief="Shows a list of your wishlisted items", description="Shows a list of your purchase and sell wishlisted items.")
async def wishlist(ctx):
    message = ""
    embedVar = discord.Embed(title="Wishlist", description=f"", color=0x660066)
    async with aiosqlite.connect("main2.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('SELECT item, price FROM buyorders WHERE id = ?', (ctx.author.id,))
            data = await cursor.fetchall()
        
            if data:
                items = ""
                prices = ""
                for x in data:
                    items  += (x[0] + "\n")
                    prices += (str(x[1]) + "\n")
            embedVar.add_field(name="Purchases", value=items, inline=True)
            embedVar.add_field(name="Prices", value=prices, inline=True)
            await cursor.execute('SELECT item, price FROM sellorders WHERE id = ?', (ctx.author.id,))
            data = await cursor.fetchall()
            if data:
                items = ""
                prices = ""
                for x in data:
                    items  += (x[0] + "\n")
                    prices += (str(x[1]) + "\n")
            embedVar.add_field(name="",value="", inline=False)
            embedVar.add_field(name="Sales", value=items, inline=True)
            embedVar.add_field(name="Prices", value=prices, inline=True)
            await ctx.send(embed=embedVar)
    await db.close()

class RemoveFromPurchaseWishlistButton(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
    @discord.ui.button(label="Remove From Wishlist?",style=discord.ButtonStyle.red)
    async def red_button(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.edit_message(content="", delete_after=0)
        await removePurchaseButton(interaction.message.content.split(" ")[-4], interaction.user.id)
        await interaction.channel.send("This item has been removed")

async def removePurchaseButton(item, authorID):
    async with aiosqlite.connect("main2.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('DELETE FROM buyorders WHERE item = ? AND id = ?',  (item.lower(), authorID))
            #await ctx.send("You have removed " + item + " from your sell wishlist")
        await db.commit()
    await db.close()

class RemoveFromSaleWishlistButton(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
    @discord.ui.button(label="Remove From Wishlist??",style=discord.ButtonStyle.red)
    async def red_button(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.edit_message(content="", delete_after=0)
        await removeSaleButton(interaction.message.content.split(" ")[-4], interaction.user.id)
        await interaction.channel.send("This item has been removed")

async def removeSaleButton(item, authorID):
    async with aiosqlite.connect("main2.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('DELETE FROM sellorders WHERE item = ? AND id = ?',  (item.lower(), authorID))
            #await ctx.send("You have removed " + item + " from your sell wishlist")
        await db.commit()
    await db.close()

@tasks.loop(minutes = 1)
async def checkPurchaseOrders():
    if checkPurchaseOrders.current_loop ==0:
        return
    #for every row in buy orders
    #check api if buy order price is less than sale api price
    async with aiosqlite.connect("main2.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('SELECT * FROM buyorders')
            data = await cursor.fetchall()
            if data:
                for order in data:
                    userID = order[0]
                    item = order[1]
                    price = order[2]
                    loopInt = 0
                    response = requests.get(f"https://api.warframe.market/v1/items/{item}/orders")
                    status = int(response.status_code)
                    if status == 200:
                        APIorder = response.json()["payload"]["orders"]
                        for x in reversed(APIorder):
                            loopInt += 1
                            if x["visible"] == True and x["order_type"] == "sell" and x["platinum"] <= price:
                                channel = await bot.get_user(userID).create_dm()
                                await channel.send("The item you wishlisted: " + item + " is on sale for your asking price (or less!)")
                                await channel.send(f"Would you like to remove {item} from your wishlist?",view=RemoveFromPurchaseWishlistButton())
                                print("looped " + str(loopInt) + " times")
                                break
            await db.commit()
    await db.close()

@tasks.loop(minutes = 1)
async def checkSellOrders():
    if checkSellOrders.current_loop ==0:
        return
    #for every row in buy orders
    #check api if buy order price is less than sale api price
    async with aiosqlite.connect("main2.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('SELECT * FROM sellorders')
            data = await cursor.fetchall()
            if data:
                for order in data:
                    userID = order[0]
                    item = order[1]
                    price = order[2]
                    loopInt = 0
                    response = requests.get(f"https://api.warframe.market/v1/items/{item}/orders")
                    status = int(response.status_code)
                    if status == 200:
                        APIorder = response.json()["payload"]["orders"]
                        for x in reversed(APIorder):
                            loopInt += 1
                            if x["visible"] == True and x["order_type"] == "buy" and x["platinum"] >= price:
                                channel = await bot.get_user(userID).create_dm()
                                await channel.send("The item you wishlisted: " + item + " is being requested for your asking price (or more!)")
                                await channel.send(f"Would you like to remove {item} from your wishlist?",view=RemoveFromSaleWishlistButton())
                                print("looped " + str(loopInt) + " times")
                                break
            await db.commit()
    await db.close()



bot.run(bot_token)
