"""
BobBot, a Discord bot made with Discord.py
This bot is the main branch of FinnBot, and is intended to be public
Birthday: 20/02/2021
"""

import discord
from discord.ext import commands, tasks
from datetime import datetime
import time
import random
import aiohttp
import urllib.parse
import validators
import os
from dotenv import load_dotenv
import asyncio
import traceback
import sys
import platform
import psutil

load_dotenv("bobtoken.env")
token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.none()
intents.members = True
intents.guilds = True
intents.messages = True
# above code configures intents to the minimum required for this bot.

activities = (
    discord.Game(name="with the settings."),
    discord.Activity(type=discord.ActivityType.listening, name="some 8-bit tunes!"),
    discord.Activity(type=discord.ActivityType.watching, name="100% legally downloaded movies.")
)

bot = commands.Bot(command_prefix='%',
                   help_command=None,
                   intents=intents,
                   case_insensitiive=True,
                   owner_id=487145006734245899,
                   activity=random.choice(activities))

bot.isPaused = False

bot.version = "1.1.2"

bot.startTime = None

bot.uptimeMilestone = 0

bot.logins = 0

bot.loggedItems = 0

bot.essentialGuilds = {
    "sub-essential": [738909955976986704],
    "essential": [812548566186197013, 855593419484168192]
}

async def log(statement: str, author=None, display: bool = True, webhook_dispatch: bool = False, count: bool = True, fmt: bool = True) -> str:
    if fmt:
        if author is None:
            if statement.endswith("  - "):
                msg = "{0}: {1} - {2}".format(bot.loggedItems, datetime.now().strftime("%d/%m/%Y, %H:%M:%S"), statement)
            else:
                msg = "{0}: {1} - {2}  - ".format(bot.loggedItems, datetime.now().strftime("%d/%m/%Y, %H:%M:%S"), statement)
        else:
            if statement.endswith("  - "):
                msg = "{0}: {1} - {2} - {3}".format(bot.loggedItems, datetime.now().strftime("%d/%m/%Y, %H:%M:%S"), author, statement)
            else:
                msg = "{0}: {1} - {2} - {3}  - ".format(bot.loggedItems, datetime.now().strftime("%d/%m/%Y, %H:%M:%S"), author, statement)
    else:
        msg = statement
    if display:
        print(msg)
    if webhook_dispatch:
        # noinspection PyBroadException
        try:
            async with aiohttp.ClientSession() as session:
                loggingWebhook = discord.Webhook.from_url("https://discord.com/api/webhooks/845469296045719602/F96pvLUdCV1fSuUHsUJaGpnQsekrFnrVnLJ51hyrNh-VeMpGwuEqlY3S2N29R8AHE8QX", adapter=discord.AsyncWebhookAdapter(session))
                await loggingWebhook.send("```\n{0}```".format(msg))
        except Exception:
            print("Failed to dispatch log entry No.#{0}. Traceback is as follows.".format(bot.loggedItems))
            await log("\033[0;31;40m{}".format(traceback.format_exc()), count=False, fmt=False)
    if count:
        bot.loggedItems += 1
    return msg

@bot.event
async def on_connect():
    await log("The bot has connected to Discord's servers successfully.")

@bot.event
async def on_ready():
    bot.logins += 1
    await log("The bot logged in successfully.", bot.user)
    bot.startTime = bot.startTime or time.time()
    if bot.logins == 1:
        uptime_checker.start()  # only calls on first login, in case of random disconnects
    channel = bot.get_channel(855594451987333130)  # announcements, updates server
    msg = await channel.send("I'm online! Type `%help` for a list of commands.")
    await msg.publish()
    print("Server count: {}.  - ".format(len(bot.guilds)))
    print("Status chosen: {}.  - ".format(bot.activity.type))
    h = 0
    for _ in bot.guilds:
        guild = bot.get_guild(bot.guilds[h].id)
        member = guild.get_member(bot.user.id)
        await member.edit(nick=None)
        h += 1

@bot.event
async def on_disconnect():
    await log("The bot seems to have disconnected from Discord's servers.")

@bot.event
async def on_guild_join(guild):
    await log(f"The bot has been added to a new guild. ID: {guild.id}, Name: '{guild.name}', Owner: {guild.owner}.")

@bot.event
async def on_guild_remove(guild):
    if guild.id in bot.essentialGuilds["essential"]:
        await log(f"CRITICAL: The bot was removed from an ESSENTIAL guild. ID: {guild.id}, Name: {guild.name}, Owner: {guild.owner}. The bot can no longer operate without this server, and hence will now stop.", webhook_dispatch=True)
        sys.exit(0)
    elif guild.id in bot.essentialGuilds["sub-essential"]:
        await log(f"WARNING: The bot was removed from a sub-essential guild. ID: {guild.id}, Name: {guild.name}, Owner: {guild.owner}. The bot can still operate, but some functionality may be missing.", webhook_dispatch=True)
    else:
        await log(f"The bot was removed from a non-essential guild. ID: {guild.id}, Name: '{guild.name}', Owner: {guild.owner}.")

@tasks.loop(hours=3)
async def uptime_checker():
    if bot.uptimeMilestone != 0:
        print("\nUptime Milestone: {0} hours.\n".format(bot.uptimeMilestone))
    bot.uptimeMilestone += 3

@bot.event
async def on_message_edit(before, after):
    if after.author.id != bot.user.id and before.content != after.content:
        await bot.process_commands(after)

@bot.event
async def on_message(message):
    botPrefixes = ('!', '?', '$', '%', '/', '+', 'pls ')
    if message.author.id == bot.user.id:
        return
    if bot.isPaused:
        if message.content.strip().lower() == "{0.command_prefix}unpause".format(bot) and await bot.is_owner(message.author):
            await message.add_reaction("<:greentick:823091069025386497>")
            bot.isPaused = False
            await message.reply("__**Bot unpaused.**__")
            await log("Bot unpaused.", message.author)
            status = random.randint(1, 3)
            print("Status chosen: " + str(status) + ".  - ")
            if status == 1:
                await bot.change_presence(activity=discord.Game(name="with the settings."))
            elif status == 2:
                await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="some 8-bit tunes!"))
            elif status == 3:
                await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="100% legally downloaded movies."))
            return
        else:
            return
    if "420" in str(message.content) and "http" not in message.content and not message.content.startswith(botPrefixes):
        if "<" in str(message.content):
            return
        else:
            chance1A = random.randint(1, 2)
            if chance1A == 1:
                await message.add_reaction("<:BobBot:822957765667979314>")
                await log("The bot responded to the user saying '420' in their with a GIF of Snoop Dogg.", message.author)
                chance1B = random.randint(1, 3)
                if chance1B == 1:
                    await message.reply("https://tenor.com/view/snoop-dogg-dance-dancing-moves-gif-4747697", mention_author=False)
                elif chance1B == 2:
                    await message.reply("https://tenor.com/view/peace-out-snoop-dogg-snoop-dogg-gif-5626955", mention_author=False)
                elif chance1B == 3:
                    await message.reply("https://tenor.com/view/snoop-dogg-yep-now-thats-what-im-talking-about-nodding-gif-15203802", mention_author=False)
            elif chance1A == 2:
                return
    if "69" in str(message.content) and "http" not in message.content and not message.content.startswith(botPrefixes):
        if "<" in str(message.content):
            return
        else:
            chance2A = random.randint(1, 2)
            if chance2A == 1:
                await message.add_reaction("<:BobBot:822957765667979314>")
                chance2B = random.randint(1, 2)
                if chance2B == 1:
                    await log("The bot responded to the user saying '69' in their message by saying 'Nice.'.", message.author)
                    await message.reply("*Nice.*", mention_author=False)
                elif chance2B == 2:
                    await log("The bot responded to the user saying '69' in their message by sending a GIF of Micheal Rosen.", message.author)
                    await message.reply("https://tenor.com/view/noice-nice-click-gif-8843762", mention_author=False)
    if "morse" in message.content.lower():
        if message.author.id != 487145006734245899:
            morseSecret = random.randint(1, 3)
            if morseSecret == 1:
                await message.add_reaction("👏")
                await log("The user found the morse code secret.", message.author)
                await message.reply("`-.-- --- ..- / ..-. --- ..- -. -.. / .- / ... . -.-. .-. . - -.-.-- / .-- . .-.. .-.. / -.. ---` :clap:", mention_author=False)
                channel = bot.get_channel(820108534427418645)
                await channel.send(str(message.author) + " found the morse code secret!")
    if "le friends dm group" in message.content.lower() and message.guild.id == 738909955976986704:
        await message.add_reaction("👏")
        await message.reply("LE FRIENDS DM GROUP 2.0 is the best name this server ever had.", mention_author=False)
        await log("The user triggered the secret LE FRIENDS DM GROUP secret.", message.author)
    if "rick astley" in message.content.lower():
        if message.author.id == 487145006734245899:
            return
        else:
            rickSecret = random.randint(1, 2)
            if rickSecret == 1:
                await message.add_reaction("<:RickAstley1:823003312999497739>")
                await log("The user got Never Gonna Give You Up stuck in the bot's head by saying Rick Astley.", message.author)
                await message.reply("Well thanks a lot, now I've got Never Gonna Give You Up stuck in my head. :angry:", mention_author=False)
            else:
                return
    if "never gonna give you up" in message.content.lower():
        if message.author.id == 487145006734245899:
            return
        else:
            nggyuSecret = random.randint(1, 2)
            if nggyuSecret == 1:
                await message.add_reaction("<:RickAstley1:823003312999497739>")
                await log("The user said 'Never Gonna Give You Up' and the bot responded by continuing the song on.", message.author)
                await message.reply("*Never Gonna Let You Down...*", mention_author=False)
    if "rick" in message.content.lower() and "roll" in message.content.lower() and message.author.id != 487145006734245899 and not message.author.bot and "http" not in message.content and 'rickrolltest' not in message.content:
        rickrollSecret = random.randint(1, 3)
        if rickrollSecret == 1:
            await message.add_reaction("👏")
            rickrollEmbed = discord.Embed(title="https://www.youtube.com/watch?v=dQw4w9WgXcQ", color=0x43b581)
            rickrollEmbed.set_footer(text="Summoned at " + datetime.now().strftime("%H:%M:%S") + ".")
            await message.reply(embed=rickrollEmbed, mention_author=False)
            await log("The user said 'rickroll' in their message, so the bot sent a rickroll link.", message.author)
    if "dQw4w9WgXcQ" in message.content and message.author.id != 487145006734245899 and "http" not in message.content and not message.author.bot:
        await message.add_reaction("<:RickAstley1:823003312999497739>")
        await message.reply("Hmm... I wonder why that rings a bell... :wink:")
        await log("The user sent the Never Gonna Give You Up video ID in their message.  - ", message.author)
    if "https://tenor.com/view/cant-trust-anybody-bird-turn-the-picture-upside-down-rick-rolled-rick-astley-gif-17818758" in message.content and message.author.id != 487145006734245899:
        await message.delete()
        await message.channel.send("Haha, pathetic attempt " + message.author.mention + ".")
        await log("The bot deleted a Rickroll GIF.  - ", message.author)
    if "mee6" in message.content.lower() and str(message.author) != "MEE6#4876":
        mee6_random = random.randint(1, 3)
        if mee6_random == 1:
            await message.add_reaction("🤮")
            await message.reply(":face_vomiting:", mention_author=False)
            await log("The user triggered the bot sending a vomit emoji in response to them mentioning MEE6.", message.author)
        elif mee6_random == 2:
            await message.add_reaction("🤢")
            await message.reply(":nauseated_face:", mention_author=False)
            await log("The user triggered the bot sending a sickened emoji in response to them mentioning MEE6.", message.author)
        else:
            return
    if message.author == "MEE6#4876" and message.channel.id != 739301088494223382:
        mee6_random1 = random.randint(1, 3)
        if mee6_random1 == 1:
            await message.add_reaction("🤢")
            await message.reply("Ew.", mention_author=False)
            await log("The bot responded to MEE6 sending a message with a sick emoji.")
        elif mee6_random1 == 2:
            await message.add_reaction("🤮")
            await message.reply("Yuck.", mention_author=False)
            await log("The bot responded to MEE6 sending a message with a vomiting emoji.")
        else:
            return
    if "traffic" in message.content.lower() and "light" in message.content.lower():
        await log("The user triggered the secret 'Traffic Light' response.  - ", message.author)
        await message.add_reaction("🟢")
        await message.add_reaction("🟡")
        await message.add_reaction("🔴")
    if "bob" in message.content.lower() and "bobbot" not in message.content.lower() and "http" not in message.content.lower():
        bobSecret = random.randint(1, 2)
        if bobSecret == 1:
            await log("The user found the 'bob' secret.  - ", message.author)
            await message.add_reaction("👏")
            await message.reply("Would you happen to be talking about my good friend BobTheBuilder69420?", mention_author=False)
        else:
            return
    if "furry" in message.content.lower():
        if message.guild.id == 738909955976986704 or message.guild.id == 812548566186197013:
            furrySecret = random.randint(1, 4)
            if furrySecret == 1:
                await log("The user found the furry Aurelia secret.  - ", message.author)
                await message.add_reaction("🤢")
                await message.reply(file=discord.File('furry aurelia.png'), mention_author=False)
    if "rrr" in message.content.lower() and message.author.id != 487145006734245899 and "http" not in message.content.lower():
        await message.reply("Haha R key go brrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr.", mention_author=False)
        await log("The bot responded to the user typing with a broken R key.  - ", message.author)
    if message.content.lower() == message.content and message.author.id != 487145006734245899 and len(message.content) > 10 and not message.content.startswith(botPrefixes):
        lowercaseChance = random.randint(1, 30)
        if lowercaseChance == 1:
            await message.add_reaction("<:BobBot:822957765667979314>")
            await message.reply("I feel sorry for your shift key, it must never get used. <:BobBot:822957765667979314>", mention_author=False)
            await log("The bot responded to the user using no capitals in their message.  - ", message.author)
        else:
            return
    if message.content.upper() == message.content and message.author.id != 487145006734245899 and len(message.content) > 15 and not message.content.startswith(botPrefixes):
        uppercaseChance = random.randint(1, 20)
        if uppercaseChance == 1:
            await message.add_reaction("<:BobBot:822957765667979314>")
            await message.reply("I THINK YOU LEFT CAPS LOCK ON. " + "<:BobBot:822957765667979314>", mention_author=False)
            await log("The bot responded to the user using all caps in their message.  - ", message.author)
    await bot.process_commands(message)  # processes the message object and checks for command usage and carries out said usage

@bot.command(name='test', aliases=['t'])
async def test(ctx):
    await ctx.message.add_reaction("<:greentick:823091069025386497>")
    await ctx.message.reply("Hey, I'm working, bud! I believe the time is {0}.".format(datetime.now().strftime("%H:%M:%S")), mention_author=False)
    await log("The user used '%test'.  - ", ctx.author)

@bot.command(name='about', aliases=['a'])
async def about(ctx):
    await ctx.message.add_reaction("<:greentick:823091069025386497>")
    await ctx.message.reply("I'm BobBot, a Discord bot made by PatronusCharm#7453. I do random fun stuff, as well as a few somewhat useful commands. I'm in {0} servers.\n\tVersion: `v{1}`.".format(len(bot.guilds), bot.version), mention_author=False)
    await log("The user used '%about'.  - ", ctx.author)

@bot.command(name='help', aliases=['h'])
async def help_me_please(ctx, *args):
    await ctx.message.add_reaction("<:greentick:823091069025386497>")
    helpEmbed = discord.Embed(title="**Commands**", description="""Use `%help [command]` to find out more about a command from this list.

- `%test`

- `%about`

- `%sing`

- `%yt`

- `%setstatus`

- `%daddyphil`

- `%kill`

- `%8ball`

- `%embedtest`

- `%reacttest`

- `%scan`

- `%serverinfo`

- `%userinfo`

- `%ping`

- `%uptime`

- `%techinfo`

**Extras:**
- There's a chance I'll respond to some certain words, numbers or phrases with a GIF or a (possibly) funny message!

- I may have a few secret commands and keywords... Why don't you go looking for them? :wink:""", color=0x43b581)
    helpEmbed.set_footer(text="Summoned by {0} at {1}.".format(ctx.author, datetime.now().strftime("%H:%M:%S")))
    helpEmbed.set_thumbnail(url=bot.user.avatar_url)
    if len(args) != 1:
        await ctx.message.reply(embed=helpEmbed, mention_author=False)
        await log("The user used '%help'.  - ", ctx.author)
    elif args[0].lower() == "help" or args[0].lower() == "h":
        helpHelp = discord.Embed(title="**Command:** `help`", description="Lists all my commands and their purpose, or provides help with a given command.", color=0x43b581)
        helpHelp.add_field(name="Example 1:", value="`%help`")
        helpHelp.add_field(name="Example 2:", value="`%help kill`")
        helpHelp.add_field(name="Aliases:", value="`h`")
        helpHelp.set_footer(text="Summoned by {0} at {1}.".format(ctx.author, datetime.now().strftime("%H:%M:%S")))
        helpHelp.set_thumbnail(url=bot.user.avatar_url)
        await ctx.message.reply(embed=helpHelp, mention_author=False)
        await log("The user used '%help help'.  - ", ctx.author)
    elif args[0].lower() == "test" or args[0].lower() == "t":
        testHelp = discord.Embed(title="**Command:** `test`", description="Makes me send a little message so you can see if I'm online and working, and this also contains what I think the current time is.", color=0x43b581)
        testHelp.add_field(name="Example:", value="`%test`")
        testHelp.add_field(name="Aliases:", value="`t`")
        testHelp.set_footer(text="Summoned by {0} at {1}.".format(ctx.author, datetime.now().strftime("%H:%M:%S")))
        testHelp.set_thumbnail(url=bot.user.avatar_url)
        await ctx.message.reply(embed=testHelp, mention_author=False)
        await log("The user used '%help test'.  - ", ctx.author)
    elif args[0].lower() == "about" or args[0].lower() == "a":
        aboutHelp = discord.Embed(title="**Command:** `about`", description="Tells you about me!", color=0x43b581)
        aboutHelp.add_field(name="Example:", value="`%about`")
        aboutHelp.add_field(name="Aliases:", value="`a`")
        aboutHelp.set_footer(text="Summoned by {0} at {1}.".format(ctx.author, datetime.now().strftime("%H:%M:%S")))
        aboutHelp.set_thumbnail(url=bot.user.avatar_url)
        await ctx.message.reply(embed=aboutHelp, mention_author=False)
        await log("The user used '%help about'.  - ", ctx.author)
    elif args[0].lower() == "sing":
        singHelp = discord.Embed(title="**Command:** `sing`", description="Makes me sing a song... Can you guess which one?", color=0x43b581)
        singHelp.add_field(name="Example:", value="`%sing`")
        singHelp.set_footer(text="Summoned by {0} at {1}.".format(ctx.author, datetime.now().strftime("%H:%M:%S")))
        singHelp.set_thumbnail(url=bot.user.avatar_url)
        await ctx.message.reply(embed=singHelp, mention_author=False)
        await log("The user used '%help sing'.  - ", ctx.author)
    elif args[0].lower() == "yt" or args[0].lower() == "youtube":
        ytHelp = discord.Embed(title="**Command:** `yt`", description="Searches YouTube for your specified search tag and returns the top 5 results.", color=0x43b581)
        ytHelp.add_field(name="Example:", value="`%yt Never Gonna Give You Up`")
        ytHelp.add_field(name="Aliases:", value="`youtube`")
        ytHelp.set_footer(text="Summoned by {0} at {1}.".format(ctx.author, datetime.now().strftime("%H:%M:%S")))
        ytHelp.set_thumbnail(url=bot.user.avatar_url)
        await ctx.message.reply(embed=ytHelp, mention_author=False)
        await log("The user used '%help yt'.  - ", ctx.author)
    elif args[0].lower() == "setstatus" or args[0].lower() == "ss":
        setstatusHelp = discord.Embed(title="**Command:** `setstatus`", description="Sets the bot's status to one of three predefined statuses.", color=0x43b581)
        setstatusHelp.add_field(name="Statuses:", value="`playing`: 'Playing with the settings.' `listening`: 'Listening to some 8-bit tunes!' `watching`: 'Watching 100% legally downloaded movies.'")
        setstatusHelp.add_field(name="Example:", value="`%setstatus playing`")
        setstatusHelp.add_field(name="Aliases:", value="`ss`")
        setstatusHelp.set_footer(text="Summoned by {0} at {1}.".format(str(ctx.author), datetime.now().strftime("%H:%M:%S")))
        setstatusHelp.set_thumbnail(url=bot.user.avatar_url)
        await ctx.reply(embed=setstatusHelp, mention_author=False)
        await log("The user used '%help setstatus'.  - ", ctx.author)
    elif args[0].lower() == "daddyphil":
        philHelp = discord.Embed(title="**Command:** `daddyphil`", description="I haven't really got much to say here, it's just... Dr. Phil...", color=0x43b581)
        philHelp.add_field(name="Example:", value="`%daddyphil`")
        philHelp.set_footer(text="Summoned by {0} at {1}.".format(str(ctx.author), datetime.now().strftime("%H:%M:%S")))
        philHelp.set_thumbnail(url=bot.user.avatar_url)
        await ctx.reply(embed=philHelp, mention_author=False)
        await log("The user used '%help daddyphil.  - ", ctx.author)
    elif args[0].lower() == "kill" or args[0].lower() == "k":
        killHelp = discord.Embed(title="**Command:** `kill`", description="Puts whoever you want in a Minecraft death message, example: 'BobTheBuilder fell out of the world.'", color=0x43b581)
        killHelp.add_field(name="Example 1:", value="`%kill MEE6`")
        killHelp.add_field(name="Example 2:", value="`%kill Donald Duck`")
        killHelp.add_field(name="Aliases:", value="`k`")
        killHelp.set_footer(text="Summoned by {0} at {1}.".format(str(ctx.author), datetime.now().strftime("%H:%M:%S")))
        killHelp.set_thumbnail(url=bot.user.avatar_url)
        await ctx.reply(embed=killHelp, mention_author=False)
        await log("The user used '%help kill'.  - ", ctx.author)
    elif args[0].lower() == "8ball" or args[0].lower() == "8b":
        ballHelp = discord.Embed(title="**Command:** `8ball`", description="Predicts your query! ||~~Nor this bot or it's owner, PatronusCharm, are responsible for any actions and/or decisions made based on the output of this command.~~||", color=0x43b581)
        ballHelp.add_field(name="Example:", value="`%8ball Is BobBot the best Discord bot ever?`")
        ballHelp.add_field(name="Aliases:", value="`8b`")
        ballHelp.set_footer(text="Summoned by {0} at {1}.".format(str(ctx.author), datetime.now().strftime("%H:%M:%S")))
        ballHelp.set_thumbnail(url=bot.user.avatar_url)
        await ctx.reply(embed=ballHelp, mention_author=False)
        await log("The user used '%help 8ball.  - ", ctx.author)
    elif args[0].lower() == "embedtest" or args[0].lower() == "et":
        embedHelp = discord.Embed(title="**Command:** `embedtest`", description="Sends a test embed, so you know that Patronus managed to get me to send 'em properly.", color=0x43b581)
        embedHelp.add_field(name="Example:", value="`%embedtest`")
        embedHelp.add_field(name="Aliases:", value="`et`")
        embedHelp.set_footer(text="Summoned by {0} at {1}.".format(str(ctx.author), datetime.now().strftime("%H:%M:%S")))
        embedHelp.set_thumbnail(url=bot.user.avatar_url)
        await ctx.reply(embed=embedHelp, mention_author=False)
        await log("The user used '%help embedtest'.  - ", ctx.author)
    elif args[0].lower() == "reacttest" or args[0].lower() == "rt" or args[0].lower() == "react":
        reactHelp = discord.Embed(title="**Command:** `reacttest`", description="Makes me react to your message with all my possible emojis, also just so you know that Patronus managed to ~~wrap his monkey brain around how to do it~~ cleverly figure out how to add the functionality.", color=0x43b581)
        reactHelp.add_field(name="Example:", value="`%reacttest`")
        reactHelp.add_field(name="Aliases:", value="`rt`, `react`")
        reactHelp.set_footer(text="Summoned by {0} at {1}.".format(str(ctx.author), datetime.now().strftime("%H:%M:%S")))
        reactHelp.set_thumbnail(url=bot.user.avatar_url)
        await ctx.reply(embed=reactHelp, mention_author=False)
        await log("The user used '%help reacttest'.  - ", ctx.author)
    elif args[0].lower() == "scan" or args[0].lower() == "s":
        scanHelp = discord.Embed(title="**Command:** `scan`", description="Scans the provided URL to a QR code image and returns the content of the QR code. This sends a request to an external API, and hence was a bit tedious for Patronus to add it to me.", color=0x43b581)
        scanHelp.add_field(name="Example:", value="`%scan https://cdn.discordapp.com/attachments/812548566722/833858704377511976/image0.png`")
        scanHelp.add_field(name="Aliases:", value="`s`")
        scanHelp.set_footer(text="Summoned by {0} at {1}.".format(str(ctx.author), datetime.now().strftime("%H:%M:%S")))
        scanHelp.set_thumbnail(url=bot.user.avatar_url)
        await ctx.reply(embed=scanHelp, mention_author=False)
        await log("The user used '%help scan'.  - ", ctx.author)
    elif args[0].lower() == "serverinfo" or args[0].lower() == "si" or args[0].lower() == "server" or args[0].lower() == "guild":
        serverinfoHelp = discord.Embed(title="**Command:** `serverinfo`", description="Provides info about the current server or a server you specify. Not much else to it...", color=0x43b581)
        serverinfoHelp.add_field(name="Example 1", value="`%serverinfo`")
        serverinfoHelp.add_field(name="Example 2:", value="`%serverinfo 855593419484168192`")
        serverinfoHelp.add_field(name="Aliases:", value="`si`, `server`, `guild`")
        serverinfoHelp.set_footer(text="Summoned by {0} at {1}.".format(ctx.author, datetime.now().strftime("%H:%M:%S")))
        serverinfoHelp.set_thumbnail(url=bot.user.avatar_url)
        await ctx.reply(embed=serverinfoHelp, mention_author=False)
        await log("The user used '%help serverinfo'.", ctx.author)
    elif args[0].lower() == "userinfo" or args[0].lower() == "ui" or args[0].lower() == "user":
        userinfoHelp = discord.Embed(title="**Command:** `userinfo`", description="Provides info about whatever user you specify. Yet again, not much else to it...", color=0x43b581)
        userinfoHelp.add_field(name="Example 1:", value="`%userinfo 819448604011659267`")
        userinfoHelp.add_field(name="Example 2:", value="`%userinfo Fun Police`")
        userinfoHelp.add_field(name="Example 3:", value="`%userinfo Carl-bot#1536`")
        userinfoHelp.add_field(name="Aliases:", value="`ui`, `user`")
        userinfoHelp.set_footer(text="Summoned by {0} at {1}.".format(ctx.author, datetime.now().strftime("%H:%M:%S")))
        userinfoHelp.set_thumbnail(url=bot.user.avatar_url)
        await ctx.reply(embed=userinfoHelp, mention_author=False)
        await log("The user used '%help userinfo'.", ctx.author)
    elif args[0].lower() == "ping" or args[0].lower() == "p":
        pingHelp = discord.Embed(title="**Command:** `ping`", description="Tells you how long my latency is. Pretty simple.", color=0x43b581)
        pingHelp.add_field(name="Example:", value="`%ping`")
        pingHelp.add_field(name="Aliases:", value="`p`")
        pingHelp.set_footer(text="Summoned by {0} at {1}.".format(ctx.author, datetime.now().strftime("%H:%M:%S")))
        pingHelp.set_thumbnail(url=bot.user.avatar_url)
        await ctx.reply(embed=pingHelp, mention_author=False)
        await log("The user used '%help ping'.", ctx.author)
    elif args[0].lower() == "uptime" or args[0].lower() == "ut":
        uptimeHelp = discord.Embed(title="**Command:** `uptime`", description="Returns how long I've been online for. Don't be surprised if this breaks, Patronus bodged this command together as he couldn't bother doing all the math and checks required for time conversions.", color=0x43b581)
        uptimeHelp.add_field(name="Example:", value="`%uptime`")
        uptimeHelp.add_field(name="Aliases:", value="`ut`")
        uptimeHelp.set_footer(text="Summoned by {0} at {1}.".format(ctx.author, datetime.now().strftime("%H:%M:%S")))
        uptimeHelp.set_thumbnail(url=bot.user.avatar_url)
        await ctx.reply(embed=uptimeHelp, mention_author=False)
        await log("The user used '%help uptime'.", ctx.author)
    elif args[0].lower() == "techinfo" or args[0].lower() == "ti":
        techinfoHelp = discord.Embed(title="**Command:** `techinfo`", description="Returns a bunch of info that the average user of this bot doesn't need to know, let alone understand it.", color=0x43b581)
        techinfoHelp.add_field(name="Example:", value="`%techinfo`")
        techinfoHelp.add_field(name="Aliases:", value="`ti`")
        techinfoHelp.set_footer(text="Summoned by {0} at {1}.".format(ctx.author, datetime.now().strftime("%H:%M:%S")))
        techinfoHelp.set_thumbnail(url=bot.user.avatar_url)
        await ctx.reply(embed=techinfoHelp, mention_author=False)
        await log("The user used '%help techinfo'.", ctx.author)
    else:
        await ctx.reply(embed=helpEmbed, mention_author=False)
        await log("The user used '%help'.  - ", ctx.author)

@bot.command()
async def sing(ctx):
    await log("The user was Rickroll'd by using '%sing'.  - ", ctx.author)
    rickroll = open("NotPatronusDiscordBotRickroll.txt", "r")
    await ctx.message.add_reaction("<:RickAstley1:823003312999497739>")
    await ctx.message.reply(rickroll.read(), mention_author=False)
    rickroll.close()
    await ctx.message.channel.send("https://tenor.com/view/dance-moves-dancing-singer-groovy-gif-17029825", mention_author=False)

@bot.command(name='yt', aliases=['youtube'])
async def yt(ctx, *args):
    if len(args) < 1:
        pass
    await ctx.message.add_reaction("<:greentick:823091069025386497>")
    await log("The user used '%yt'.  - ", ctx.author)
    await ctx.message.reply("Ha! You actually thought Patronus would know how to interact with the YouTube API? Well you're very, very wrong.", mention_author=False)

@bot.command(name='setstatus', aliases=['ss'])
async def setstatus(ctx, *args):
    if len(args) != 1:
        await ctx.message.reply("You gave me an invalid or non-existent status to change to! Make sure you actually wrote a valid status from the list in `%help`.", mention_author=False)
        await log("The user tried to set the bot's status to an invalid or non-existent value, and was declined.  - ", ctx.author)
        return
    elif args[0].lower() == "playing":
        await bot.change_presence(activity=discord.Game(name="with the settings."))
        await ctx.message.add_reaction("<:greentick:823091069025386497>")
        await ctx.message.reply("Status set.", mention_author=False)
        await log("The user set the bot's status to 'playing'.", ctx.author)
    elif args[0].lower() == "listening":
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="some 8-bit tunes!"))
        await ctx.message.add_reaction("<:greentick:823091069025386497>")
        await ctx.message.reply("Status set.", mention_author=False)
        await log("The user set the bot's status to 'listening'.", ctx.author)
    elif args[0].lower() == "watching":
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="100% legally downloaded movies."))
        await ctx.message.add_reaction("<:greentick:823091069025386497>")
        await ctx.message.reply("Status set.", mention_author=False)
        await log("The user set the bot's status to 'watching'.", ctx.author)
    else:
        await ctx.message.reply("You gave me an invalid or non-existent status to change to! Make sure you actually wrote a valid status from the list in `%help`.", mention_author=False)
        await ctx.message.add_reaction("❔")
        await log("The user tried to set the bot's status to an invalid or non-existent value, and was declined.  - ", ctx.author)

@bot.command(name='statusupdate', aliases=['su'])
async def statusupdate(ctx, *, msg):
    msg = msg.replace("{~newline~}", "\n").replace("{~ping-everyone~}", "@everyone").replace("{~ping-here~}", "@here").replace("{~ping-self~}", bot.user.mention).replace("{~ping-owner~}", bot.get_user(bot.owner_id).mention).replace("{~indent~}", "    ")
    if ctx.message.author.id != 487145006734245899:
        await ctx.message.add_reaction("<:redcross:824952391882768414>")
        await ctx.message.reply("Only PatronusCharm can use that!", mention_author=False)
        await log("The user tried to make a status update, and was refused due to insufficient perms.  - ", ctx.author)
    else:
        await ctx.message.add_reaction("<:greentick:823091069025386497>")
        await ctx.message.reply("Status update made successfully.", mention_author=False)
        await log("The user made a status update: '{0}'.  - ".format(msg), ctx.author)
        channel = bot.get_channel(855594451987333130)  # announcements, updates server
        msgSent = await channel.send(msg)
        await msgSent.publish()
@statusupdate.error
async def statusupdate_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.message.add_reaction("❔")
        await log("The user tried to make a status update about nothing.  - ", ctx.author)
        await ctx.message.reply("You haven't told me anything to announce...", mention_author=False)
    else:
        await ctx.message.add_reaction("❗")
        await log("An unhandled error occurred when attempting to make a status update. Traceback is as follows. Message ID: '{0}'.".format(ctx.message.id), ctx.author)
        await log("\033[0;31;40m{}".format(traceback.format_exc()), webhook_dispatch=True, count=False, fmt=False)
        await ctx.reply("An unexpected error occurred when attempting to process the command: `{0}`".format(error), mention_author=False)

@bot.command(name='scan', aliases=['s'])
@commands.cooldown(1, 10.0, commands.BucketType.user)
async def scan(ctx, *args):
    checks = False
    if len(args) != 1:
        if len(args) == 0:
            if len(ctx.message.attachments) != 0:
                checks = True
        if not checks:
            await ctx.message.add_reaction("<:redcross:824952391882768414>")
            await log("The user gave the bot too many or too few arguments ({0}) with '%scan'.  - ".format(len(args)), ctx.author)
            await ctx.message.reply("That's not a valid link...", mention_author=False)
            return
    if not checks:
        if not validators.url(args[0]):
            await ctx.message.add_reaction("<:redcross:824952391882768414>")
            await log("The user gave an malformed/improper URL to scan.  - ", ctx.author)
            await ctx.message.reply("That's not a proper URL.", mention_author=False)
            return
    await ctx.message.add_reaction("<:loading:826991804313632809>")
    await log("The user requested a QR code scan.  - ", ctx.author)
    if checks:
        QR_code = urllib.parse.quote_plus(ctx.message.attachments[0].url)
    else:
        QR_code = urllib.parse.quote_plus(args[0])
    await ctx.channel.trigger_typing()
    scanStart = time.time()
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.qrserver.com/v1/read-qr-code/?fileurl=" + QR_code) as result:
            QR_code_scan = await result.json()
    scanEnd = time.time()
    QR_result = QR_code_scan[0]["symbol"][0]["data"]
    QR_error = QR_code_scan[0]["symbol"][0]["error"]
    if QR_result is None:
        await ctx.message.add_reaction("<:redcross:824952391882768414>")
        await log("An invalid URL was passed to the QR API by the user. Time taken: {0} seconds. Error code: '{1}'.  - ".format(round(scanEnd-scanStart, 2), QR_error), ctx.author)
        if QR_error == "download error (could not establish connection)":
            await ctx.reply("I couldn't access that url. It either doesn't exist or I don't have permission to access it.", mention_author=False)
        elif QR_error == "filetype not supported":
            await ctx.reply("That's not a supported file type. Files can only be .png, .jpg, or still .gif images.", mention_author=False)
        elif QR_error == "could not find/read QR Code":
            await ctx.reply("I couldn't find a QR code in that image.", mention_author=False)
        elif QR_error == "download error (file is too big)":
            await ctx.reply("That file is too big for me to read. I can only read files smaller than 1049 kilobytes.", mention_author=False)
        else:
            await ctx.message.add_reaction("❗")
            await ctx.reply("Unexpected error raised by the API: `{0}`.".format(QR_error), mention_author=False)
            await log("The user triggered an unexpected error from the API with `%scan`. Error: `{0}`. URL: {1}".format(QR_error, args[0]), ctx.author)
            channel = bot.get_channel(820108534427418645)  # test server, bot-status-and-errors
            await channel.send("{0} triggered an unexpected error from the API with `%scan`. Error: `{1}`. URL: {2}".format(str(ctx.author), QR_error, args[0]))
            await ctx.message.remove_reaction("<:redcross:824952391882768414>", bot.user)
        await ctx.message.remove_reaction("<:loading:826991804313632809>", bot.user)
    else:
        await ctx.message.add_reaction("<:greentick:823091069025386497>")
        await log("The user's QR code request was finished successfully. Time taken: {0} seconds. Content: '{1}'.  - ".format(round(scanEnd-scanStart, 2), QR_result), ctx.author)
        await ctx.message.reply("QR code content: '{0}'.".format(QR_result), mention_author=False)
        if checks and len(ctx.message.attachments) > 1:
            await ctx.send("I only scanned one attachment, yet there were a total of {0} attachments in that message. I only scan the first attachment of a message for networking and performance reasons.".format(len(ctx.message.attachments)))
        await ctx.message.remove_reaction("<:loading:826991804313632809>", bot.user)
@scan.error
async def scan_error(ctx, error):
    if isinstance(error, discord.ext.commands.CommandOnCooldown):
        await ctx.message.add_reaction("<:redcross:824952391882768414>")
        if round(error.retry_after, 2) > 1.0:
            scan_error_sec = "seconds"
        else:
            scan_error_sec = "second"
        await ctx.message.reply("Woah, hold your horses bud, you have to wait another {0} {1} to use that command.".format(round(error.retry_after, 2), scan_error_sec), mention_author=False)
        await log("The user tried to use '%scan' whilst it was on a cooldown.  - ", ctx.author)
        await ctx.message.remove_reaction("<:loading:826991804313632809>", bot.user)
    else:
        await ctx.message.add_reaction("❗")
        await ctx.reply("Something went horribly wrong: `{0}`.".format(error), mention_author=False)
        await log("An unexpected error occurred in '%scan'. Traceback is as follows. Message ID: {0}.".format(ctx.message.id), ctx.author)
        await log("\033[0;31;40m{}".format(traceback.format_exc()), webhook_dispatch=True, count=False, fmt=False)
        await ctx.message.remove_reaction("<:loading:826991804313632809>", bot.user)

@bot.command()
async def daddyphil(ctx):
    await ctx.message.add_reaction("<:greentick:823091069025386497>")
    await log("The user used '%daddyphil'.  - ", ctx.author)
    await ctx.message.reply("May I present the almighty Daddy Phil!", mention_author=False)
    await ctx.message.channel.send("https://tenor.com/view/dr-phil-gasp-wow-what-am-gif-5020190")
    await asyncio.sleep(1)
    await ctx.message.channel.send("*God, what a legend.*")

@bot.command(name='kill', aliases=['k'])
async def kill(ctx, *, arg):
    await ctx.message.add_reaction("<:greentick:823091069025386497>")
    chance3A = random.randint(1, 32)
    await log("{0} was killed by the user. Response picked: {1}.  - ".format(arg, chance3A), ctx.author)
    if chance3A == 1:
        await ctx.message.reply(arg + " was slain by Arrow.", mention_author=False)
    if chance3A == 2:
        await ctx.message.reply(arg + " was shot by " + str(ctx.message.author) + ".", mention_author=False)
    if chance3A == 3:
        await ctx.message.reply(arg + " was prickled to death.", mention_author=False)
    if chance3A == 4:
        await ctx.message.reply(arg + " drowned.", mention_author=False)
    if chance3A == 5:
        await ctx.message.reply(arg + " experienced kinetic energy.", mention_author=False)
    if chance3A == 6:
        await ctx.message.reply(arg + " blew up.", mention_author=False)
    if chance3A == 7:
        await ctx.message.reply(arg + " was blown up by " + str(ctx.message.author) + ".", mention_author=False)
    if chance3A == 8:
        await ctx.message.reply(arg + " hit the ground too hard.", mention_author=False)
    if chance3A == 9:
        await ctx.message.reply(arg + " fell from a high place.", mention_author=False)
    if chance3A == 10:
        await ctx.message.reply(arg + " was squashed by a falling anvil.", mention_author=False)
    if chance3A == 11:
        await ctx.message.reply(arg + " was squashed by a falling block.", mention_author=False)
    if chance3A == 12:
        await ctx.message.reply(arg + " went up in flames.", mention_author=False)
    if chance3A == 13:
        await ctx.message.reply(arg + " burned to death.", mention_author=False)
    if chance3A == 14:
        await ctx.message.reply(arg + " went off with a bang.", mention_author=False)
    if chance3A == 15:
        await ctx.message.reply(arg + " tried to swim in lava.", mention_author=False)
    if chance3A == 16:
        await ctx.message.reply(arg + " was struck by lightning.", mention_author=False)
    if chance3A == 17:
        await ctx.message.reply(arg + " discovered floor was lava.", mention_author=False)
    if chance3A == 18:
        await ctx.message.reply(arg + " was killed by magic.", mention_author=False)
    if chance3A == 19:
        await ctx.message.reply(arg + " was killed by " + str(ctx.message.author) + " using magic.", mention_author=False)
    if chance3A == 20:
        await ctx.message.reply(arg + " was slain by " + str(ctx.message.author) + ".", mention_author=False)
    if chance3A == 21:
        await ctx.message.reply(arg + " was slain by Small Fireball.", mention_author=False)
    if chance3A == 22:
        await ctx.message.reply(arg + " starved to death.", mention_author=False)
    if chance3A == 23:
        await ctx.message.reply(arg + " suffocated in a wall.", mention_author=False)
    if chance3A == 24:
        await ctx.message.reply(arg + " was killed trying to hurt " + str(ctx.message.author) + ".", mention_author=False)
    if chance3A == 25:
        await ctx.message.reply(arg + " was impaled to death by " + str(ctx.message.author) + ".", mention_author=False)
    if chance3A == 26:
        await ctx.message.reply(arg + " fell out of the world.", mention_author=False)
    if chance3A == 27:
        await ctx.message.reply(arg + " withered away.", mention_author=False)
    if chance3A == 28:
        await ctx.message.reply(arg + " died.", mention_author=False)
    if chance3A == 29:
        await ctx.message.reply(arg + " was fireballed by " + str(ctx.message.author) + ".", mention_author=False)
    if chance3A == 30:
        await ctx.message.reply(arg + " was sniped by Shulker.", mention_author=False)
    if chance3A == 31:
        await ctx.message.reply(arg + " was spitballed by Llama.", mention_author=False)
    if chance3A == 32:
        await ctx.message.reply(arg + " was so shocked from getting Rickroll'd by " + str(ctx.message.author) + " that they died.", mention_author=False)
        channel = bot.get_channel(820108534427418645)
        await channel.send(str(ctx.message.author) + " got the rare death message using `%kill`!")
@kill.error
async def kill_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.message.add_reaction("❔")
        await log("The user tried to kill no one.  - ")
        await ctx.message.reply("You didn't give me anyone to kill...", mention_author=False)
    else:
        await ctx.message.add_reaction("❗️")
        await log("An unexpected error occurred in '%kill': Traceback is as follows.", ctx.author)
        await log("\033[0;31;40m{}".format(traceback.format_exc()), webhook_dispatch=True, count=False, fmt=False)
        await ctx.message.reply("Something went horribly wrong. Error: \n```py\n{0}```".format(error))

@bot.command(name="8ball", aliases=['8b'])
async def _8ball(ctx):
    await ctx.message.add_reaction("<:greentick:823091069025386497>")
    ballDecision = random.randint(1, 20)
    await log("The user used '8ball'. Decision picked: {0}.  - ".format(ballDecision))
    if ballDecision == 1:
        await ctx.message.reply("It is certain.", mention_author=False)
    elif ballDecision == 2:
        await ctx.message.reply("It is decidedly so.", mention_author=False)
    elif ballDecision == 3:
        await ctx.message.reply("Without a doubt.", mention_author=False)
    elif ballDecision == 4:
        await ctx.message.reply("Yes - definitely.", mention_author=False)
    elif ballDecision == 5:
        await ctx.message.reply("You may rely on it.", mention_author=False)
    elif ballDecision == 6:
        await ctx.message.reply("As I see it, yes.", mention_author=False)
    elif ballDecision == 7:
        await ctx.message.reply("Most likely.", mention_author=False)
    elif ballDecision == 8:
        await ctx.message.reply("Outlook good.", mention_author=False)
    elif ballDecision == 9:
        await ctx.message.reply("Yes.", mention_author=False)
    elif ballDecision == 10:
        await ctx.message.reply("Signs point to yes.", mention_author=False)
    elif ballDecision == 11:
        await ctx.message.reply("Reply hazy, try again.", mention_author=False)
    elif ballDecision == 12:
        await ctx.message.reply("Ask again later.", mention_author=False)
    elif ballDecision == 13:
        await ctx.message.reply("Better not tell you now.", mention_author=False)
    elif ballDecision == 14:
        await ctx.message.reply("Cannot predict now.", mention_author=False)
    elif ballDecision == 15:
        await ctx.message.reply("Concentrate and ask again.", mention_author=False)
    elif ballDecision == 16:
        await ctx.message.reply("Don't count on it.", mention_author=False)
    elif ballDecision == 17:
        await ctx.message.reply("My reply is no.", mention_author=False)
    elif ballDecision == 18:
        await ctx.message.reply("My sources say no.", mention_author=False)
    elif ballDecision == 19:
        await ctx.message.reply("Outlook not so good.", mention_author=False)
    elif ballDecision == 20:
        await ctx.message.reply("Very doubtful.", mention_author=False)

@bot.command()
@commands.cooldown(1, 120.0, commands.BucketType.guild)
async def bobthebuilder(ctx):
    await ctx.message.delete()
    await log("The user found the secret command '%bobthebuilder'.  - ", ctx.author)
    await ctx.message.channel.send(ctx.message.author.mention + " You found a secret... Nice.", delete_after=10)
    channel = bot.get_channel(820108534427418645)
    await channel.send(str(ctx.message.author) + " found the secret '%BobTheBuilder' command!")
@bobthebuilder.error
async def bobthebuilder_error(ctx, error):
    if isinstance(error, discord.ext.commands.CommandOnCooldown):
        await log("The user tried to use the secret '%bobthebuilder' command on cooldown, and was silently ignored.", ctx.author)
        return

@bot.command()
async def die(ctx):
    await ctx.message.add_reaction("👏")
    await log("The user found the secret command '%die'.  - ", ctx.author)
    await ctx.message.reply("no u", mention_author=False)

@bot.command(name='embedtest', aliases=['et', 'embed'])
async def embedtest(ctx):
    await ctx.message.add_reaction("<:greentick:823091069025386497>")
    testEmbed = discord.Embed(title="**This** *is* __a__ `test` ~~embed.~~", description="This embed test was summoned by **" + str(ctx.message.author) + "** at *" + datetime.now().strftime("%H:%M:%S") + "*.", color=0x43b581)
    testEmbed.add_field(name="Summoner is Lord?", value=str(ctx.message.author.id == 487145006734245899), inline=False)
    testEmbed.add_field(name="Summoner ID", value=str(ctx.message.author.id), inline=False)
    testEmbed.set_image(url="https://cdn.discordapp.com/attachments/812548566722805772/823070181487280128/image0.png")
    await ctx.message.reply(embed=testEmbed, mention_author=False)
    await log("The user summoned a test embed.  - ", ctx.author)

@bot.command(name='reacttest', aliases=['rt', 'react'])
async def reacttest(ctx):
    await log("The user summoned a reaction test.  - ", ctx.author)
    await ctx.message.add_reaction("🟢")  # green_circle
    await ctx.message.add_reaction("🟡")  # yellow_circle
    await ctx.message.add_reaction("🔴")  # red_circle
    await ctx.message.add_reaction("<:greentick:823091069025386497>")  # custom - greentick (test server)
    await ctx.message.add_reaction("<:redcross:824952391882768414>")  # custom - redcross (test server)
    await ctx.message.add_reaction("❔")  # grey_question
    await ctx.message.add_reaction("❓")  # question (red)
    await ctx.message.add_reaction("❕")  # grey_exclamation
    await ctx.message.add_reaction("❗")  # exclamation (red)
    await ctx.message.add_reaction("<:BobBot:822957765667979314>")  # custom - BobBot (test server)
    await ctx.message.add_reaction("👏")  # clap
    await ctx.message.add_reaction("<:RickAstley1:823003312999497739>")  # custom - RickAstley1 (test server)
    await ctx.message.add_reaction("🤢")  # nauseated_face
    await ctx.message.add_reaction("🤮")  # face_vomiting
    await ctx.message.add_reaction("<:angryping:824953625453264918>")  # custom - angryping (test server)
    await ctx.message.add_reaction("<:uac:836940180584661031>")  # custom - uac (test server)
    await log("The bot finished the reaction test summoned by the user.  - ", ctx.author)
    await ctx.message.reply("That should be all of them, bud!", mention_author=False)

@bot.command()
async def rickrolltest(ctx):
    if ctx.message.author.id == 487145006734245899:
        await ctx.message.add_reaction("<:greentick:823091069025386497>")
        await ctx.message.reply("https://youtu.be/dQw4w9WgXcQ", mention_author=False)
        await log("The user used '%rickrolltest' successfully.  - ")
    else:
        await ctx.message.add_reaction("<:uac:836940180584661031>")
        await ctx.message.reply("You can't use that.", mention_author=False)
        await log("The user tried to use '%rickrolltest', and was declined.  - ", ctx.author)

@bot.command(name='nickreset', aliases=['nr'])
async def nickreset(ctx):
    if ctx.message.author.id == 487145006734245899:
        await ctx.message.add_reaction("<:greentick:823091069025386497>")
        o = 0
        for _ in bot.guilds:
            guild = bot.get_guild(bot.guilds[o].id)
            member = guild.get_member(bot.user.id)
            await member.edit(nick=None)
            o += 1
        await log("The user reset the bot's nickname on all servers.  - ", ctx.author)
        await ctx.message.reply("Done. :thumbsup:", mention_author=False)
    else:
        await ctx.message.add_reaction("<:uac:836940180584661031>")
        await ctx.message.reply("You cannot use that command.", mention_author=False)
        await log("The user tried to use '%nickreset', and was declined.  - ", ctx.author)

@bot.command()
async def debug(ctx, *args):
    if args[0].lower() == "message":
        if ctx.author.id != 487145006734245899:
            await ctx.message.add_reaction("<:uac:836940180584661031>")
            await ctx.reply("I'm afraid you can't use that command.", mention_author=False)
            await log("The user tried to use '%debug message' and was declined.", ctx.author)
        elif len(args) != 4:
            await ctx.message.add_reaction("<:greentick:823091069025386497>")
            message_info = "Raw `ctx` object: \n'`{0}`'\n\nRaw `message` object: \n'`{0.message}`'\n\n`message` content: \n'{0.message.content}'\n\n`message` attachments: \n'`{0.message.attachments}`'\n\n`message` reactions: \n'`{0.message.reactions}`'".format(ctx)
            message_info = message_info.replace("%27%3E", "")
            await ctx.reply(message_info, mention_author=False)
        else:
            if args[1].lower() == 'ctx':
                guild = ctx.guild
            else:
                try:
                    guild = bot.get_guild(int(args[1]))
                except ValueError:
                    await ctx.message.add_reaction("<:redcross:824952391882768414>")
                    await ctx.reply("That's not a valid guild ID.", mention_author=False)
                    return
                if guild is None:
                    await ctx.message.add_reaction("<:redcross:824952391882768414>")
                    await ctx.reply("Either that guild doesn't exist or I can't access it.", mention_author=False)
                    return
            if args[2].lower() == 'ctx':
                channel = ctx.channel
            else:
                if ctx.guild is None:
                    await ctx.message.add_reaction("<:redcross:824952391882768414>")
                    await ctx.reply("`ctx` has no attribute `guild` in DM channels.", mention_author=False)
                    return
                try:
                    channel = guild.get_channel(int(args[2]))
                except ValueError:
                    await ctx.message.add_reaction("<:redcross:824952391882768414>")
                    await ctx.reply("That's not a valid channel ID.", mention_author=False)
                    return
                if channel is None:
                    await ctx.message.add_reaction("<:redcross:824952391882768414>")
                    await ctx.reply("Either that channel doesn't exist or I can't access it.", mention_author=False)
                    return
            try:
                message = await channel.fetch_message(int(args[3]))
            except discord.errors.NotFound:
                await ctx.message.add_reaction("<:redcross:824952391882768414>")
                await ctx.reply("Either that message doesn't exist or I can't access it.", mention_author=False)
                return
            except Exception as oh_no:
                await ctx.message.add_reaction("❗")
                await ctx.reply("An unexpected error occurred when fetching the message: `{0}`.".format(oh_no), mention_author=False)
                await log("An unhandled error occurred when fetching a message in '%debug message'. Traceback is as follows.", ctx.author)
                await log("\033[0;31;40m{}".format(traceback.format_exc()), webhook_dispatch=True, count=False, fmt=False)
                return
            await ctx.message.add_reaction("<:greentick:823091069025386497>")
            message_info = "Raw `message` object: \n'`{0}`'\n\n`message` content: \n'{0.content}'\n\n`message` attachments: \n'`{0.attachments}`'\n\n`message` reactions: \n'`{0.reactions}`'".format(message)
            message_info = message_info.replace("%27%3E", "")
            await ctx.reply(message_info, mention_author=False)
            await log("The user used '%debug message' successfully.  - ", ctx.author)
@debug.error
async def debug_error(ctx, error):
    await ctx.reply("An unknown error occurred: `{0}`".format(str(error)), mention_author=False)
    await log("An unhandled error occurred when the user tried to use '%debug'. Traceback is as follows. Message ID: {0}.".format(ctx.message.id), ctx.author)
    await log("\033[0;31;40m{}".format(traceback.format_exc()), webhook_dispatch=True, count=False, fmt=False)

@bot.command()
async def echo(ctx, guild, channel, *, message):
    message = message.replace("{~newline~}", "\n").replace("{~ping-everyone~}", "@everyone").replace("{~ping-here~}", "@here").replace("{~ping-self~}", bot.user.mention).replace("{~ping-owner~}", bot.get_user(bot.owner_id).mention).replace("{~indent~}", "\t")
    if ctx.author.id != 487145006734245899:
        await ctx.message.add_reaction("<:uac:836940180584661031>")
        await ctx.reply("Mhm, yeah right I'm gonna let you make me send whatever message you want to wherever you want.", mention_author=False)
        await log("The user tried to use '%echo', and was declined.  - ", ctx.author)
        return
    else:
        if guild.lower() == 'ctx':
            if str(ctx.channel.type) == "private":
                await ctx.message.add_reaction("<:redcross:824952391882768414>")
                await ctx.reply("`ctx` has no attribute `guild` in DM channels.", mention_author=False)
                await log("The user tried to pass ctx for guild to '%echo' in a DM channel and was refused.  - ", ctx.author)
                return
            else:
                echoGuild = ctx.guild
        else:
            try:
                echoGuild = bot.get_guild(int(guild))
            except ValueError:
                await ctx.message.add_reaction("<:redcross:824952391882768414>")
                await ctx.reply("That's not a guild ID...", mention_author=False)
                await log("The user passed an invalid guild ID to '%echo'.  - ", ctx.author)
                return
            if echoGuild is None:
                await ctx.message.add_reaction("<:redcross:824952391882768414>")
                await ctx.reply("I couldn't find a guild with that ID: Either I can't access it, or it doesn't exist.", mention_author=False)
                await log("The user passed an unfindable guild ID to '%echo'.  - ", ctx.author)
                return
        if channel.lower() == 'ctx':
            echoChannel = ctx.channel
        else:
            try:
                echoChannel = echoGuild.get_channel(int(channel))
            except ValueError:
                await ctx.message.add_reaction("<:redcross:824952391882768414>")
                await ctx.reply("That's not a channel ID...", mention_author=False)
                await log("The user passed an invalid channel ID to '%echo'.  - ", ctx.author)
                return
            if echoChannel is None:
                await ctx.message.add_reaction("<:redcross:824952391882768414>")
                await ctx.reply("I couldn't find a channel with that ID: Either I can't access it, or it doesn't exist at the selected guild.", mention_author=False)
                await log("The user passed an unfindable channel ID to '%echo'.  - ", ctx.author)
                return
        try:
            await echoChannel.send(message)
        except Exception as whelp:
            await ctx.message.add_reaction("<:redcross:824952391882768414>")
            await ctx.reply("Something went wrong with sending the message: \n```py\n{0}```".format(whelp), mention_author=False)
            await log("An unexpected error occurred when trying to send a message in '%echo'. Traceback is as follows.".format(whelp), ctx.author)
            await log("\033[0;31;40m{}".format(traceback.format_exc()), webhook_dispatch=True, count=False, fmt=False)
            return
        await ctx.reply("The message seems to have sent properly. :thumbsup:", mention_author=False)
        await log("The bot successfully echoed a message as requested by the user. Message: '{0}'.", ctx.author)
@echo.error
async def echo_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.message.add_reaction("<:redcross:824952391882768414>")
        await ctx.reply("You didn't provide a required argument.", mention_author=False)
        await log("The user tried to use '%echo' without enough parameters, and was declined.", ctx.author)
    else:
        await ctx.message.add_reaction("❗")
        await ctx.reply("Something went wrong: \n```py\n{0}```".format(error), mention_author=False)
        await log(f"An unknown error occurred when the user used the '%echo' command. Traceback is as follows.", ctx.author)
        await log("\033[0;31;40m{}".format(traceback.format_exc()), webhook_dispatch=True, count=False, fmt=False)

@bot.command()
@commands.is_owner()
async def pause(ctx):
    await ctx.message.add_reaction("<:greentick:823091069025386497>")
    await bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game(name="bot paused, commands will be ignored."))
    await ctx.reply("__**Bot paused. All commands will be ignored.**__")
    bot.isPaused = True
    await log("Bot paused: all commands will be ignored until unpaused or restarted.", ctx.author)
@pause.error
async def pause_error(ctx, error):
    if isinstance(error, discord.ext.commands.NotOwner):
        await ctx.message.add_reaction("<:uac:836940180584661031>")
        await ctx.reply("You cannot use that.", mention_author=False)
        await log("The user tried to pause the bot and was declined.", ctx.author)
    else:
        await ctx.message.add_reaction("<:redcross:824952391882768414>")
        await ctx.reply("An unexpected error occurred: `{0}`.".format(error), mention_author=False)
        await log("An unhandled error occurred in '%pause'. Traceback is as follows.", ctx.author)
        await log("\033[0;31;40m{}".format(traceback.format_exc()), webhook_dispatch=True, count=False, fmt=False)

@bot.command(name='serverinfo', aliases=['si', 'server', 'guild'])
async def serverinfo(ctx, *, guild: discord.Guild = None):
    if ctx.guild is None and guild is None:
        await ctx.message.add_reaction("<:redcross:824952391882768414>")
        await ctx.reply("No server was provided.", mention_author=False)
        await log("The user tried to use '%serverinfo' in DMs without any arguments.", ctx.author)
        return
    elif guild is None:
        guild = ctx.guild
    await ctx.message.add_reaction("<:greentick:823091069025386497>")
    await log("The user used '%serverinfo'.", ctx.author)
    serverCreateDate = guild.created_at
    serverBots = 0
    for member in guild.members:
        if member.bot:
            serverBots += 1
    serverEmbed = discord.Embed(title="Server Info: {0}".format(guild.name), color=0x43b581)
    serverEmbed.set_thumbnail(url=guild.icon_url)
    serverEmbed.add_field(name="Owner:", value=guild.owner.mention)
    serverEmbed.add_field(name="Roles:", value="{0} roles.".format(len(guild.roles)))
    serverEmbed.add_field(name="Members:", value="{0} ({1} bots)".format(len(guild.members), serverBots))
    serverEmbed.add_field(name="Date Created:", value=serverCreateDate.strftime("%d/%m/%Y, %H:%M:%S UTC"))
    serverEmbed.add_field(name="Boosts:", value=str(guild.premium_subscription_count))
    await ctx.reply(embed=serverEmbed, mention_author=False)
@serverinfo.error
async def serverinfo_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.GuildNotFound):
        await ctx.message.add_reaction("<:redcross:824952391882768414>")
        await ctx.reply("I couldn't find that server.", mention_author=False)
        await log("The user passed an invalid or non-existent server to '%serverinfo'.", ctx.author)
    else:
        await ctx.message.add_reaction("❗")
        await ctx.reply("Something went horribly wrong: `{0}`".format(error), mention_author=False)
        await log("The user raised an unexpected error in '%serverinfo'. Traceback is as follows.", ctx.author, webhook_dispatch=True)
        await log("\033[0;31;40m{}".format(traceback.format_exc()), webhook_dispatch=True, count=False, fmt=False)

@bot.command(name='userinfo', aliases=['ui', 'user'])
async def userinfo(ctx, *, user: discord.User = None):
    await ctx.message.add_reaction("<:greentick:823091069025386497>")
    user = user or ctx.author
    isMember = False
    userEmbedColor = 0x43b581
    try:
        if user in ctx.guild.members:
            isMember = True
            member = ctx.guild.get_member(user.id)
            userEmbedColor = member.color
    except AttributeError:
        pass
    await log("The user used '%userinfo'.", ctx.author)
    userEmbed = discord.Embed(title="User Info: {0}".format(user), color=userEmbedColor)
    userEmbed.set_thumbnail(url=user.avatar_url)
    userEmbed.add_field(name="Is Bot:", value=str(user.bot))
    userEmbed.add_field(name='Date Created:', value=user.created_at.strftime("%d/%m/%Y, %H:%M:%S UTC"))
    if ctx.guild is not None:
        userEmbed.add_field(name='Is Member:', value=str(isMember))
    if isMember:
        member = ctx.guild.get_member(user.id)
        memberBoosting = False
        if member in ctx.guild.premium_subscribers:
            memberBoosting = True
        userEmbed.add_field(name='Is Boosting:', value=str(memberBoosting))
        if memberBoosting:
            userEmbed.add_field(name='Boosting Since:', value=member.premium_since.strftime("%d/%m/%Y, %H:%M:%S UTC"))
        userEmbed.add_field(name='Nickname:', value=str(member.nick))
        userEmbed.add_field(name="Date Joined:", value=member.joined_at.strftime("%d/%m/%Y, %H:%M:%S UTC"))
    await ctx.reply(embed=userEmbed, mention_author=False)
@userinfo.error
async def userinfo_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.UserNotFound):
        await ctx.message.add_reaction("<:redcross:824952391882768414>")
        await ctx.reply("I couldn't find that user.", mention_author=False)
        await log("The user passed an invalid or non-existent user to '%userinfo'.", ctx.author)
    else:
        await ctx.message.add_reaction("❗")
        await ctx.reply("Something went horribly wrong: `{0}`".format(error), mention_author=False)
        await log("The user raised an unexpected error in '%userinfo'. Traceback is as follows.", ctx.author, webhook_dispatch=True)
        await log("\033[0;31;40m{}".format(traceback.format_exc()), webhook_dispatch=True, count=False, fmt=False)

@bot.command(name='ping', aliases=['p'])
async def ping(ctx):
    await ctx.message.add_reaction("<:greentick:823091069025386497>")
    ping_indicator = ":sparkles:"
    if bot.latency*1000 >= 400:
        ping_indicator = ":green_circle:"
    if bot.latency*1000 >= 700:
        ping_indicator = ":yellow_circle:"
    if bot.latency*1000 >= 1100:
        ping_indicator = ":orange_circle:"
    if bot.latency*1000 >= 1600:
        ping_indicator = ":red_circle:"
    await log("The user checked the bot's ping. Ping: {0}ms.".format(round(bot.latency * 1000, 1)), ctx.author)
    await ctx.reply("`{0}ms` {1}".format(round(bot.latency * 1000, 1), ping_indicator), mention_author=False)

@bot.command(name='uptime', aliases=['ut'])
async def uptime_call(ctx):
    timeNow = time.time()
    seconds = timeNow - bot.startTime
    seconds = time.gmtime(seconds)
    days = int(time.strftime("%d", seconds)) - 1
    months = int(time.strftime("%m", seconds)) - 1
    formattedTime = time.strftime("%H hours, %M minutes and %S seconds.", seconds)
    formattedTime = "{0} months, {1} days, {2}".format(months, days, formattedTime)
    await log("The user checked the bot's uptime.", ctx.author)
    await ctx.reply("Uptime: {0}".format(formattedTime), mention_author=False)
@uptime_call.error
async def uptime_call_error(ctx, error):
    await ctx.message.add_reaction("❗️")
    await ctx.reply("Well, something went wrong. Don't be surprised, the uptime command is such a bodge. \nPatronus couldn't bother doing the maths for all the date conversion, so he used a cheat's workaround. \nError: {0}".format(error), mention_author=False)
    await log("Surprise, surprise, an error occurred in '%uptime_call'. Traceback is as follows.", ctx.author)
    await log("\033[0;31;40m{}".format(traceback.format_exc()), webhook_dispatch=True, count=False, fmt=False)

@bot.command(name='techinfo', aliases=['ti'])
async def techinfo(ctx):
    psutil.cpu_percent(None)
    techinfoEmbed = discord.Embed(title="Tech Info", color=0x43b581)
    techinfoEmbed.add_field(name="Ping", value=f"{bot.latency*1000}ms ({bot.latency})")
    techinfoEmbed.add_field(name="Start Time", value=f"<t:{round(bot.startTime)}:F>, <t:{round(bot.startTime)}:R> ({round(bot.startTime)})")
    techinfoEmbed.add_field(name="Host System", value=f"`{platform.platform()}`")
    techinfoEmbed.add_field(name="Logins", value=f"{bot.logins}")
    techinfoEmbed.add_field(name="Memory", value=f"{psutil.virtual_memory()[1]/1000000}MB/{psutil.virtual_memory()[0]/1000000}MB (used/total)")
    techinfoEmbed.add_field(name="CPU Usage", value=f"{psutil.cpu_percent(None)}%")
    await log("The user used '%techinfo'.", ctx.author)
    await ctx.reply(embed=techinfoEmbed, mention_author=False)

bot.run(token)
