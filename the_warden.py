import os, time, random

import discord
from discord.ext import commands
from dotenv import load_dotenv

# pip install pynacl
# install ffmpeg on path

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

JAIL_VOICE_ID = os.getenv('JAIL_VOICE_ID')
JAIL_TEXT_ID = os.getenv('JAIL_TEXT_ID')

hangout_channel = None
jail_channel = None

# client = discord.Client()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_voice_state_update(member, before, after):
    if before != None and before.channel != None and before.channel.id == JAIL_VOICE_ID:
        hangout_channel = await bot.fetch_channel(JAIL_TEXT_ID)
        inmate_role = discord.utils.get(member.guild.roles, name="Inmate")
        await member.remove_roles(inmate_role, reason="You busted out of horny jail.", atomic=True)


async def change_avatar(avatar_file):
    try:
        in_file = open(avatar_file, "rb") # opening for [r]eading as [b]inary
        data = in_file.read() # if you only wanted to read 512 bytes, do .read(512)
        in_file.close()
        print("Avatar change in progress")
        await bot.user.edit(avatar=data)
        print("Avatar change complete")
        return True
    except:
        print("Avatar change failed")
        return False

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break
    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

    hangout_channel = await bot.fetch_channel(JAIL_TEXT_ID)
    jail_channel = await bot.fetch_channel(JAIL_VOICE_ID)


async def bonk(context, voiceclient, bonker, bonkee):
    voiceclient.play(discord.FFmpegPCMAudio('bonk.mp3'))
    await sendToJail(context, bonkee)
    while not voiceclient.is_playing():
        pass

async def bonk_all(context, voiceclient, bonker):
    listOfBonkees = bonker.voice.channel.members
    listOfBonkees = list(filter(lambda b: b.display_name != bonker.display_name and b.display_name!=context.guild.me.display_name, listOfBonkees))
    random.shuffle(listOfBonkees)
    print("Bonkees are: ")
    for b in listOfBonkees:
        print(b.display_name)
    time.sleep(2)
    if not await change_avatar("saiyan.png"):
        return False
    voiceclient.play(discord.FFmpegPCMAudio('superbonk.mp3'))
    currentTiming = 0
    bonkTimings = [2, 0.5, 0.5]
    while len(listOfBonkees) > 0:
        currentBonkee = listOfBonkees.pop(0)
        if len(bonkTimings) > 0:
            currentTiming = bonkTimings.pop(0)
            time.sleep(currentTiming)
            print("Jailing " + currentBonkee.display_name)
            await sendToJail(context, currentBonkee)
        else:
            await bonk(context, bonker, currentBonkee)

    await change_avatar("police.png")
    time.sleep(2)
    await bonk(context, voiceclient, bonker, bonker)
    return True


async def sendToJail(context, bonkee):
    inmate_role = discord.utils.get(context.guild.roles, name="Inmate")
    await bonkee.add_roles(inmate_role, reason="You have been sent to horny jail.", atomic=True)
    jail_channel = await bot.fetch_channel(JAIL_VOICE_ID)
    jail_text_channel = await bot.fetch_channel(JAIL_TEXT_ID)
    await bonkee.move_to(jail_channel)
    await jail_text_channel.send(bonkee.display_name + ", you were arrested by " + bonkee.display_name + " for your thirsty crimes.")

# @bot.event
# async def on_message(message):
#     if message.content.startswith('!member'):
#         for guild in bot.guilds:
#             for member in guild.members:
#                 print(member)

@bot.command()
async def jail(context, *args):
    target_name = ' '.join(args)
    hangout_channel = await bot.fetch_channel(JAIL_TEXT_ID)
    jail_channel = await bot.fetch_channel(JAIL_VOICE_ID)
    bonker = context.message.author
    await context.message.delete()

    vc = None
    if target_name.lower() == "all":
        await bonker.send("I'm too tired for that, Sir.")
        vc = await bonker.voice.channel.connect()
        # ret = await bonk_all(context, vc, bonker)
        # if not ret:
        #     await bonker.send("I'm too tired for that, Sir.")
    elif target_name != '':
        bonkee = context.message.guild.get_member_named(target_name)
        if bonkee != None:
            if bonkee.voice != None and bonkee.voice.channel != None:
                vc = await bonkee.voice.channel.connect()
                await bonk(context, vc, bonker, bonkee)
            else:
                vc = bonker.voice.channel.connect()
                await bonker.send("Sorry Sir, the suspect '" + bonkee.display_name + "' is not currently in a voice channel.")
        else:
            await bonker.send("Sorry Sir, I cannot find anyone with the name '" + target_name + "'.")

    if vc != None:
        time.sleep(3)
        await vc.disconnect()

bot.run(TOKEN)