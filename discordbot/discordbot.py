
import datetime
from discord.ext import commands, tasks
import discord
from dataclasses import dataclass
import requests
import aiosqlite


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
 
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
session = Session()
invasionMessages = []

@bot.event
async def on_ready():
    channel = bot.get_channel(channel_id)
   
    await channel.purge(bulk = False)
    #news_Reset.start() 

    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('CREATE TABLE IF NOT EXISTS buyorders (id INTEGER , item STRING, price INTEGER)')
        await db.commit()
#channels table
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('CREATE TABLE IF NOT EXISTS channels (guildID INTEGER , channelID INTEGER, channelUse STRING)')
        await db.commit()

    print("Hello! Study bot is ready!")

    await channel.send("Hello! Warframebot is ready!", silent = True)

#START OF SETUP CODE
#
@bot.event
async def on_guild_join(guild):
    print("joined server")
    channel =  guild.system_channel
    await channel.send("Hello, I am in this server now")

@bot.command()
async def setup(ctx, auto):
    guild = ctx.guild
    category = await guild.create_category("WARFRAMEBOT")
    print("starting setup")
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(send_messages=False)
    }
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
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
        await db.commit()



@bot.command()
async def testchannels(ctx):
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            for guild in bot.guilds:
                await cursor.execute('SELECT channelID FROM channels WHERE channelUse = ? AND guildID = ?', ("invasions", guild.id))
                data = await cursor.fetchall()
                if data:
                    for x in data:
                        print(x[0])
                        await guild.get_channel(x[0]).send("Invasions")
                
                await cursor.execute('SELECT channelID FROM channels WHERE channelUse = ? AND guildID = ?', ("alerts", guild.id))
                data = await cursor.fetchall()
                if data:
                    for x in data:
                        print(x[0])
                        await guild.get_channel(x[0]).send("Alerts")

                await cursor.execute('SELECT channelID FROM channels WHERE channelUse = ? AND guildID = ?', ("events", guild.id))
                data = await cursor.fetchall()
                if data:
                    for x in data:
                        print(x[0])
                        await guild.get_channel(x[0]).send("events")

        await db.commit()
                    


            
           
    

@bot.command()
async def addpurchase(ctx, item, price):
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('SELECT id FROM buyorders WHERE item = ?', (item.lower(),))
            data = await cursor.fetchone()
            if data:
                await cursor.execute('INSERT INTO buyorders (id, item, price) VALUES (?,?,?)', (ctx.message.author.id, item.lower(), price))
            else:
                await cursor.execute('INSERT INTO buyorders (id, item, price) VALUES (?,?,?)', (ctx.message.author.id, item.lower(), price))
        await db.commit()


@bot.event
async def on_reaction_add(genreaction, user):
    channel = genreaction.message.channel
    
    emoji = str(genreaction)
    await channel.send(f"Thanks for the reaction! {emoji}")

@bot.command()
async def checkPrice(ctx, item):
    price = 5000
    response = requests.get(f"https://api.warframe.market/v1/items/{item}/orders")
    status = int(response.status_code)
    if status == 200:
        #for order in response.json()["payload"]["orders"]:
        for x in range(51):
           order = response.json()["payload"]["orders"][x]
           if order["platinum"] < price:
               price = order["platinum"]
        await ctx.send(f"Lowest Price: {price} platinum")


@bot.command()
async def warframeInvasion(ctx):
    response = requests.get("https://api.warframestat.us/pc/invasions")
    status = int(response.status_code)
    print(status)
    if status == 200:
        #totalmessage = ""
        #if len(invasionMessages) > 0:
            #for message in invasionMessages:
                #await message.delete()  
        #for mission in response.json(): #THIS IS TEMPORARILY CHANGED TO NOT LAG DISCORD
            mission = response.json()[2]
            
            if mission["completed"] != True:
                if "reward" in mission["attacker"]:
                    attackreward = mission["attacker"]["reward"]["asString"]
                    embed1 = discord.Embed(description=f"Attacker Reward: {attackreward}",
                                           url='https://discordpy.readthedocs.io/en/stable/api.html?highlight=send#discord.abc.Messageable.send') #pretty sure these links are just placeholder
                    embed1.set_image(url=mission["attacker"]["reward"]["thumbnail"])

                if "reward" in mission["defender"]:
                    defendreward = mission["defender"]["reward"]["asString"]
                    embed2 = discord.Embed(description=f"Defender Reward: {defendreward}",
                                           url='https://old.discordjs.dev/#/docs/discord.js/14.14.1/class/EmbedBuilder')
                    embed2.set_image(url=mission["defender"]["reward"]["thumbnail"])

                location = mission["node"]
                description = mission["desc"]




                #await ctx.send(f"Mission: {description}: {location}\nAttacker Reward: {attackreward}\nDefebder Reward: {defendreward}\n\n")
                #totalmessage += f"Mission: {description}: {location}\nAttacker Reward: {attackreward}\nDefender Reward: {defendreward}\n\n"
                if attackreward != "":
                    print("runningmission")
                    invasionMessages.append( await ctx.send( f"\n\nMission: {description}\nLocation: {location}", embeds = [embed1, embed2], silent=True))

                else:
                    print("runningmission2")
                    invasionMessages.append(await ctx.send( f"\n\nMission: {description}\nLocation: {location}", embed = embed2, silent=True))

                attackreward = ""
                defendreward = ""
                embed1.clear_fields()
                embed2.clear_fields()
        
           
        
            
                    
        #invasion_Reset.start()    
        #await ctx.send(totalmessage)

@bot.command()
async def warframeEvent(ctx):
    response = requests.get("https://api.warframestat.us/pc/events/")
    status = int(response.status_code)
    print(status)
    if status == 200:
        mission = response.json()[0]
        description = mission["description"]
        reward = mission["rewards"][0]["asString"]
        await ctx.send( f"\n\nMission: {description}\nRewards {reward}", silent=True)
        
           
        
            
                    
        #invasion_Reset.start()    
        #await ctx.send(totalmessage)
                    
@bot.command()
async def warframeSnapshot(ctx):
    response = requests.get("https://api.warframestat.us/pc/invasions")
    status = int(response.status_code)
   # if status == 200:

'''                  
@tasks.loop(minutes=max_session_time_minutes)
async def invasion_Reset():
    if invasion_Reset.current_loop == 0:
        return
    channel = bot.get_channel(channel_id)
    #await channel.send(f"**Take a break!** You've been studying for {max_session_time_minutes} minutes.")
    await warframeInvasion(channel)'''
@tasks.loop(minutes=5)
async def news_Reset():
    newsChannel = bot.get_channel(1234501703961808906)
    await newsChannel.purge(bulk=False)
    response = requests.get("https://api.warframestat.us/pc/news")
    status = int(response.status_code)
    if status == 200:
        #for news in response.json():
            news = response.json()[0]
            description = news["message"]
            link = news["link"]
            embed = discord.Embed(description=news["eta"],
                                   url='https://discordpy.readthedocs.io/en/stable/api.html?highlight=send#discord.abc.Messageable.send')  # pretty sure these links are just placeholder
            embed.set_image(url=news["imageLink"])
            invasionMessages.append(
                await newsChannel.send(f"\n\n{description}\n{link}", embeds=[embed],
                               silent=True))




@bot.command()
async def photoSendTest(ctx):
    response = requests.get("https://api.warframestat.us/pc/invasions")
    status = int(response.status_code)
    if status == 200:
        mission = response.json()[0]
        if mission["completed"] != True:
             attackreward = mission["attackerReward"]["thumbnail"]
             await ctx.send(file=discord.File(attackreward))


"""
@bot.event
async def on_message(message):
    if (message.author.id != bot_user_id):
        mention = message.author.mention
        message_user_id = message.author.id
        channel = message.channel
        user = str(message.author)
        await channel.send(f"Shut up {mention}")

    

@tasks.loop(minutes=max_session_time_minutes, count=2)
async def break_reminder():
    if break_reminder.current_loop == 0:
        return
    channel = bot.get_channel(channel_id)
    await channel.send(f"**Take a break!** You've been studying for {max_session_time_minutes} minutes.")

@bot.command()
async def apex(ctx, legend_name):
    if legend_name.lower() == "revenant":
        await ctx.send(file=discord.File('C:/Users/thega/Documents/FSU/discordbot/discordbot/files/rev_img.webp'))
        await ctx.send(file=discord.File('C:/Users/thega/Documents/FSU/discordbot/discordbot/files/rev_voicelines.mp3'))
@bot.command()
async def hello(ctx):
    await ctx.send("Hello!")
@bot.command()
async def add(ctx, x, y):
    result = int(x) + int(y)
    await ctx.send(f"{x} + {y} = {result}")

@bot.command()
async def addall(ctx, *arr):
    result = 0
    for i in arr:
        result += int(i)
    await ctx.send(f"Result: {result}")


@bot.command()
async def start(ctx):
    if session.is_active:
        await ctx.send("A session is already active!")
        return
    
    session.is_active = True
    session.start_time = ctx.message.created_at.timestamp()
    human_readable_time = ctx.message.created_at.strftime("%H:%M:%S")
    break_reminder.start()
    await ctx.send(f"New session started at {human_readable_time}")
@bot.command()
async def end(ctx):
    if session.is_active == False:
        await ctx.send("There is no session active, start one with !Start")
        return
    
    session.is_active = False
    end_time = ctx.message.created_at.timestamp()
    duration = end_time - session.start_time
    human_readable_duration = str(datetime.timedelta(seconds=duration))
    break_reminder.stop()
    await ctx.send(f"Session ended after {human_readable_duration}")
"""






bot.run(bot_token)
