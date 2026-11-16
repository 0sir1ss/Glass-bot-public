import os
import asyncpg
import discord
from discord.ext import commands
import time
import json
from utils.encrypt import AESCipher
# import logging
# logging.basicConfig(level=logging.INFO, format='%(levelname)s | %(name)s: %(message)s')

async def get_prefix(bot, message):
    # If dm's
    if not message.guild:
        return commands.when_mentioned_or(";")(bot, message)

    try:
        aes = AESCipher()
        db = await asyncpg.connect(bot.db_conf, timeout=10)
        result = await db.fetchrow("SELECT * FROM config WHERE gid = $1", aes.encrypt(message.guild.id))
        await db.close()
        if result:
            prefix = aes.decrypt(result[1])
            return commands.when_mentioned_or(prefix)(bot, message)
        else:
            return commands.when_mentioned_or(";")(bot, message)

    except:
        return commands.when_mentioned_or(";")(bot, message)

bot = commands.AutoShardedBot(
    command_prefix=get_prefix,
    owner_id=YOUROWNERID,
    case_insensitive=True,
    intents=discord.Intents.all(),
    help_command=None, # Remove discord.py basic help command to replace with our own.
    activity=discord.Activity(type=discord.ActivityType.watching, name='@Glass | ;help'),
    status=discord.Status.online
)
bot.config = json.loads(open('config/secrets.json').read())
bot.config_token = bot.config["token"]
bot.db_conf = bot.config["db_conf"]
bot.aa = bot.config["alexflipnote_api"]
bot.KSoft = bot.config["KSoft_api"]
bot.blacklisted_users = []
bot.xp_cooldown = []
bot.tp = {}
bot.colour = 0x7289da

# Check if bot online

@bot.event
async def on_ready():                                                               # Do this when the bot is logged in
    print(f'Logged in as {bot.user.name} - {bot.user.id}\n-----')                   # Print the name and ID of the bot logged in.
    print(f'{len(bot.guilds)} servers || {len(set(bot.get_all_members()))} members\n-----')
    c = bot.get_channel(855846345222651994)                                         # My own personal channel for logging
    await c.send(embed=discord.Embed(
        title=f"Logged in as {bot.user.name} - {bot.user.id}",
        description=f"{len(bot.guilds)} servers || {len(set(bot.get_all_members()))} members",
        colour=bot.colour
        )
    )


@bot.event
async def on_message(message):
    # Ignore messages sent by yourself
    if message.author.bot:
        return

    # Blacklisted users ignored for abusing the bot
    if message.author.id in bot.blacklisted_users:
        return

    await bot.process_commands(message)

# Ping Command
@bot.command(
    name='Ping',
    aliases=['p'], 
    description=
    "Bot permissions: None\n"
    "User permissions: None"
)
@commands.cooldown(1, 5, commands.BucketType.user)
async def ping_command(ctx):
    """ Pong! """
    before = time.monotonic()
    before_ws = int(round(bot.latency * 1000, 1))
    message = await ctx.send("Pinging...")
    ping = (time.monotonic() - before) * 1000
    embed = discord.Embed(
        title='🏓 Ping',
        description=f'<:speedtest:852956732199272450> **Websocket** : {before_ws}ms\n'
                    f'<a:loading:852956731885355080> **REST** : {int(ping)}ms',
        colour=bot.colour
    )
    await message.edit(content="", embed=embed)

@bot.command(
    hidden=True
)
@commands.is_owner()
async def load(ctx, name: str):
    try:
        bot.load_extension(f"cogs.{name}")
        await ctx.send(f"Loaded extension **{name}.py**")
    except Exception as e:
        em = discord.Embed(
            title='Error', 
            description=f'```py\n{e}\n```', 
            colour=discord.Colour.red()
            )
        await ctx.send(embed=em)

@bot.command(
    hidden=True
)
@commands.is_owner()
async def unload(ctx, name: str):
    try:
        bot.unload_extension(f"cogs.{name}")
        await ctx.send(f"Unloaded extension **{name}.py**")
    except Exception as e:
        em = discord.Embed(
            title='Error', 
            description=f'```py\n{e}\n```', 
            colour=discord.Colour.red()
            )
        await ctx.send(embed=em)

@bot.command(
    hidden=True
)
@commands.is_owner()
async def reload(ctx, name: str):
    try:
        bot.reload_extension(f"cogs.{name}")
        await ctx.send(f"Reloaded extension **{name}.py**")
    except Exception as e:
        em = discord.Embed(
            title='Error', 
            description=f'```py\n{e}\n```', 
            colour=discord.Colour.red()
            )
        await ctx.send(embed=em)

# Load the cogs in

for filename in os.listdir('./cogs'):
    if filename.endswith('.py') and not filename.startswith("_"):
        bot.load_extension(f'cogs.{filename[:-3]}')
        
print("\n-----\nIn order to end press ctrl + c\n-----")

# Run bot
bot.run(bot.config_token, bot=True, reconnect=True)
