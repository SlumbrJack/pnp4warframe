
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
 
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all() )



session = Session()
invasionMessages = []

@bot.event
async def on_ready():
    channel = bot.get_channel(channel_id)
   
    await channel.purge(bulk = False)
    
#buy table
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            #await cursor.execute('DROP TABLE buyorders')
            await cursor.execute('CREATE TABLE IF NOT EXISTS buyorders (id INTEGER , item STRING, price INTEGER)')
        await db.commit()
#sell table
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('CREATE TABLE IF NOT EXISTS sellorders (id INTEGER , item STRING, price INTEGER)')
        await db.commit()
#channels table
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('CREATE TABLE IF NOT EXISTS channels (guildID INTEGER , channelID INTEGER, channelUse STRING)')
        await db.commit()
#news table
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('CREATE TABLE IF NOT EXISTS newsMessages (guildID INTEGER , channelID INTEGER, messageID INTEGER, newsID STRING)')
        await db.commit()
#alerts table
#events table
#invasions table
    news_Reset.start() 
    clearOldNews.start()
    checkPurchaseOrders.start()
    checkSellOrders.start()
    print("Hello! Study bot is ready!")

    await channel.send("Hello! Warframebot is ready!", silent = True)

#START OF SETUP CODE
#
@bot.event
async def on_guild_join(guild):
    print("joined server")
    channel =  guild.system_channel
    await channel.send("Hello, I am WarframeBot. Please type '!setup' to get started.")

@bot.command(brief='Sets up the server by adding new channels', description='This command will add new channels under a new category to the server.\nWARNING: DO NO RUN THIS COMMAND MULTIPLE TIMES. DO NOT DELETE THISE CHANNELS WITHOUT USING THE CORRECT COMMAND')
async def setup(ctx):
    guild = ctx.guild
    
    print("starting setup")
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(send_messages=False)
    }
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            category = await guild.create_category("WARFRAMEBOT")
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
        await db.commit()
        news_Reset.restart()
    await ctx.send("The server is now set up for WarframeBot. Please type !help to learn more. Type \"!help (command name)\" to learn more about a specific command")

@bot.command(brief='Removes all channels created by the bot', description='This command will remove the channels and categories created by this bot\nOnce complete the bot will leave the server')
async def removeBotFromServer(ctx):
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('SELECT channelID FROM channels WHERE guildID = ?', (ctx.guild.id,))
            data = await cursor.fetchall()
            if data:
                for channel in data:
                    await bot.get_channel(channel[0]).delete()
                await cursor.execute('DELETE FROM channels WHERE guildID = ?', (ctx.guild.id,))
            await cursor.execute('SELECT channelID FROM newsMessages where guildID = ?', (ctx.guild.id,))
            data = await cursor.fetchall()
            if data:
                for message in data:
                    await cursor.execute('DELETE FROM newsMessages where guildID = ?', (ctx.guild.id,))
            await ctx.guild.leave()
         
        await db.commit()

'''
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
                    
'''
@tasks.loop(hours=6)
async def news_Reset():
    response = requests.get("https://api.warframestat.us/pc/news")
    status = int(response.status_code)
    channel = 0
    if status == 200:

        async with aiosqlite.connect("main.db") as db:
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
                            for x in data:
                                DBID = x[0] 
                                if jsonNewsID == DBID:
                                    matchFound = True
                            if not matchFound:
                                print("match not found")
                                description = news["message"]
                                link = news["link"]
                                embed = discord.Embed(description=news["eta"],
                                                    url='https://discordpy.readthedocs.io/en/stable/api.html?highlight=send#discord.abc.Messageable.send')  # pretty sure these links are just placeholder
                                embed.set_image(url=news["imageLink"])
                                message = await guild.get_channel(channel).send(f"\n\n{description}\n{link}", embeds=[embed],silent=True)
                                await cursor.execute('INSERT INTO newsMessages (guildID, channelID, messageID, newsID) VALUES (?,?,?,?)', (guild.id, channel, message.id, jsonNewsID ))
                        print("data found")
                    #if there are no news messages in the guild, fill it
                    else:
                        print("no data")
                        for news in response.json():
                                newsID = news["id"]
                                description = news["message"]
                                link = news["link"]
                                embed = discord.Embed(description=news["eta"],
                                                    url='https://discordpy.readthedocs.io/en/stable/api.html?highlight=send#discord.abc.Messageable.send')  # pretty sure these links are just placeholder
                                embed.set_image(url=news["imageLink"])
                                message = await guild.get_channel(channel).send(f"\n\n{description}\n{link}", embeds=[embed],silent=True)
                                await cursor.execute('INSERT INTO newsMessages (guildID, channelID, messageID, newsID) VALUES (?,?,?,?)', (guild.id, channel, message.id, newsID ))



                           
            await db.commit()

@tasks.loop(hours = 24)
async def clearOldNews():
    channel = 0
    response = requests.get("https://api.warframestat.us/pc/news")
    status = int(response.status_code)
    if status == 200:

        async with aiosqlite.connect("main.db") as db:
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
                        guild.get_channel(channel).fetch_message(x[1])
                        await cursor.execute('DELETE FROM newsMessages WHERE newsID = ? AND messageID = ?', (DBID, x[1]))
                        print("DELETED NEWS")
            await db.commit()

     
                        
    
'''
    #newsChannel = bot.get_channel(1234501703961808906)
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
                               silent=True))'''

            
           
@bot.event
async def on_command_error(ctx,error):
    if isinstance(error, commands.CommandError):
        
        await ctx.send("There was an error using that command, use \"!help (the command you are trying to use)\" to learn more!")    

@bot.command(brief= 'Adds an item to a purchase wishlist', description = 'Adds an item you would like to purchase to a wish list.\nWhen a sell order is placed on WarframeMarket for less than or equal to your desired price, you will recieve a DM letting you know.\nExample usage: !addPurchase nezha_price_neuroptics 20')
async def addPurchase(ctx, item = commands.parameter(description="Must be represented in this format: mirage_prime_systems"), price = commands.parameter(description="The price (in platinum) you are looking to buy this item for")): 
    if not price.isdigit():
        await ctx.send("There was an error using that command, use \"!help (the command you are trying to use)\" to learn more!")
    else:
        async with aiosqlite.connect("main.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute('SELECT id FROM buyorders WHERE item = ? AND id = ?', (item.lower(), ctx.message.author.id))
                data = await cursor.fetchone()
                if data:
                    print("you have already wishlisted this item")
                else:
                    await cursor.execute('INSERT INTO buyorders (id, item, price) VALUES (?,?,?)', (ctx.message.author.id, item.lower(), price))
                    await ctx.send("You have added " + item + " to your purchase wishlist for " + price + " platinum")
            await db.commit()

@bot.command(brief= 'Removes an item from the purchase wishlist', description= 'Removes an item from your purchase wishlist.\nYou will no longer receive messages about this item. Example usage: !removePurchase nidus_prime_chassis') 
async def removePurchase(ctx, item = commands.parameter(description="Must be represented in this format: mirage_prime_systems")):
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('DELETE FROM buyorders WHERE item = ? AND id = ?',  (item.lower(), ctx.message.author.id))
            await ctx.send("You have removed " + item + " from your purchase wishlist")
        await db.commit()

@bot.command(brief= 'Adds an item to a sell wishlist', description = 'Adds an item you would like to sell to a wish list.\nWhen a buy order is placed on WarframeMarket for more than or equal to your desired price, you will recieve a DM letting you know.\nExample usage: !addSale nezha_price_neuroptics 10')
async def addSale(ctx, item = commands.parameter(description="Must be represented in this format: mirage_prime_systems"), price = commands.parameter(description="The price (in platinum) you are looking to buy this item for")):
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('SELECT id FROM sellorders WHERE item = ? AND id = ?', (item.lower(), ctx.message.author.id))
            data = await cursor.fetchone()
            if data:
                print("you have already wishlisted this item")
            else:
                await cursor.execute('INSERT INTO sellorders (id, item, price) VALUES (?,?,?)', (ctx.message.author.id, item.lower(), price))
                await ctx.send("You have added " + item + " to your sell wishlist for " + price + " platinum")
        await db.commit()

@bot.command(brief= 'Removes an item from the sell wishlist', description= 'Removes an item from your sale wishlist.\nYou will no longer receive messages about this item. Example usage: !removeSale nidus_prime_chassis')
async def removeSale(ctx, item):
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('DELETE FROM sellorders WHERE item = ? AND id = ?',  (item.lower(), ctx.message.author.id))
            await ctx.send("You have removed " + item + " from your sell wishlist")
        await db.commit()

@bot.command(brief="Shows a list of your wishlisted items", description="Shows a list of your purchase and sell wishlisted items.")
async def wishlist(ctx):
    message = ""
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('SELECT item FROM buyorders WHERE id = ?', (ctx.author.id,))
            data = await cursor.fetchall()
            if data:
                message += ("Purchase:\n")
                for x in data:
                    message  += (x[0] + "\n")
            await cursor.execute('SELECT item FROM sellorders WHERE id = ?', (ctx.author.id,))
            data = await cursor.fetchall()
            if data:
                message += ("Sell:\n")
                for x in data:
                    message += (x[0] + "\n")
            await ctx.send(message)

@tasks.loop(minutes = 7)
async def checkPurchaseOrders():
    if checkPurchaseOrders.current_loop ==0:
        return
    #for every row in buy orders
    #check api if buy order price is less than sale api price
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('SELECT * FROM buyorders')
            data = await cursor.fetchall()
            if data:
                for order in data:
                    userID = order[0]
                    item = order[1]
                    price = order[2]
                    loopInt = 0
                    print(userID, item, price)
                    response = requests.get(f"https://api.warframe.market/v1/items/{item}/orders")
                    status = int(response.status_code)
                    if status == 200:
                        APIorder = response.json()["payload"]["orders"]
                        for x in reversed(APIorder):
                            loopInt += 1
                            if x["visible"] == True and x["order_type"] == "sell" and x["platinum"] <= price:
                                channel = await bot.get_user(userID).create_dm()
                                await channel.send("The item you wishlisted: " + item + " is on sale for your asking price (or less!)")
                                print("looped " + str(loopInt) + " times")
                                break
            await db.commit()

@tasks.loop(minutes = 15)
async def checkSellOrders():
    if checkSellOrders.current_loop ==0:
        return
    #for every row in buy orders
    #check api if buy order price is less than sale api price
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('SELECT * FROM sellorders')
            data = await cursor.fetchall()
            if data:
                for order in data:
                    userID = order[0]
                    item = order[1]
                    price = order[2]
                    loopInt = 0
                    print(userID, item, price)
                    response = requests.get(f"https://api.warframe.market/v1/items/{item}/orders")
                    status = int(response.status_code)
                    if status == 200:
                        APIorder = response.json()["payload"]["orders"]
                        for x in reversed(APIorder):
                            loopInt += 1
                            if x["visible"] == True and x["order_type"] == "buy" and x["platinum"] >= price:
                                channel = await bot.get_user(userID).create_dm()
                                await channel.send("The item you wishlisted: " + item + " is being requested for your asking price (or more!)")
                                print("looped " + str(loopInt) + " times")
                                break
            await db.commit()
                    
'''
@bot.command
async def help(ctx, specific = "default"):
    if(specific == "default"):
        helpMessage = "Welcome to Warframe Bot!\nHere's some information on how this bot works:\nThrough the !setup command, I created several channels you can find information in.\n"
        helpMessage2 = "Most of these channels are automatically updating channels that will post live information about what is going on in warframe. Some information about these:\n"
        helpMessage3 = "News - Contains updated information about updates, hotfixes, Prime Times, and more!\n\nAlerts, Events, and Invasions - These channels contain information on the active missions in their respectice categories and includes the locations, rewards, and necessary details about each\n\n"
        helpMessage4 = "Cycles - This channel contains the current cycle for open world zones\n\nMarket - This channel is available to make wishlist requests to Warframe Market. Type !help market to learn more!"
        ctx.send(helpMessage + helpMessage2 + helpMessage3 + helpMessage4)
    elif specific == "market":
        marketHelp1 = "market yay"
        ctx.send(marketHelp1)
'''

@bot.event
async def on_reaction_add(genreaction, user):
    channel = genreaction.message.channel
    
    emoji = str(genreaction)
    await channel.send(f"Thanks for the reaction! {emoji}")

'''
@bot.command()
async def checkPrice(ctx, item):
    price = 5000
    response = requests.get(f"https://api.warframe.market/v1/items/{item}/orders")
    status = int(response.status_code)
    if status == 200:
        #size = len(response.json()["payload"]["orders"]) - 1
        response = response.json()["payload"]["orders"]
        for order in reversed(response):
            if order["order_type"] == "buy":
                print(order["platinum"])
                break

        #for order in response.json()["payload"]["orders"]:
        '''
'''
        for x in range(51):
           order = response.json()["payload"]["orders"][x]
           if order["platinum"] < price:
               price = order["platinum"]
        await ctx.send(f"Lowest Price: {price} platinum")
        '''

'''
@bot.command()
async def warframeInvasion2(ctx):
    message = await bot.get_guild(1235283017002516561).get_channel(1235310956851232950).fetch_message(1235318783120375889)
    await message.delete()

@tasks.loop(minutes=5)
async def warframeInvasion():
    print("hi")

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
'''          
@tasks.loop(minutes=max_session_time_minutes)
async def invasion_Reset():
    if invasion_Reset.current_loop == 0:
        return
    channel = bot.get_channel(channel_id)
    #await channel.send(f"**Take a break!** You've been studying for {max_session_time_minutes} minutes.")
    await warframeInvasion(channel)'''



'''
@bot.command()
async def photoSendTest(ctx):
    response = requests.get("https://api.warframestat.us/pc/invasions")
    status = int(response.status_code)
    if status == 200:
        mission = response.json()[0]
        if mission["completed"] != True:
             attackreward = mission["attackerReward"]["thumbnail"]
             await ctx.send(file=discord.File(attackreward))
'''

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
