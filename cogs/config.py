import discord
from discord.ext import commands
import asyncpg
from utils.encrypt import AESCipher

class Configuration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command(
        name='Prefix', 
        description=
        "Bot permissions: None\n"
        "User permissions: Manage server"
    )
    @commands.has_guild_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.guild_only()
    async def prefix(self, ctx, *, prefix=';'):
        """Sets this guild's prefix"""
        prefix = prefix.split()[0]
        aes = AESCipher()
        if 0 < len(prefix) < 6:
            db = await asyncpg.connect(self.bot.db_conf, timeout=10)
            result = await db.fetchrow("SELECT * FROM config WHERE gid = $1", aes.encrypt(ctx.guild.id))
            if result:
                await db.execute("UPDATE config SET prefix = $1 where gid = $2", aes.encrypt(prefix), aes.encrypt(ctx.guild.id))
            else:
                await db.execute("INSERT INTO config VALUES($1, $2)", aes.encrypt(ctx.guild.id), aes.encrypt(prefix))
            await ctx.send(f"The guild prefix has been set to `{prefix}`. This can be used again after 10 seconds.")
            await db.close()
        else:
            return await ctx.send("The prefix provided must be between 1-5 characters long.")

    @commands.command(
        name="XPAlerts",
        description=
        "Bot permissions: None\n"
        "User permissions: Manage server"
    )
    @commands.has_guild_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.guild_only()
    async def xpalerts(self, ctx):
        """Enables or disables xp alerts"""
        db = await asyncpg.connect(self.bot.db_conf, timeout=10)
        aes = AESCipher()
        result = await db.fetchrow("SELECT * FROM xpalerts WHERE gid = $1", aes.encrypt(ctx.guild.id))
        if result:
            option = aes.decrypt(result[1])
            if option == "True":
                await db.execute("UPDATE xpalerts SET option = $1 where gid = $2", aes.encrypt(False), aes.encrypt(ctx.guild.id))
                await ctx.send("Disabling xp alerts")
            else:
                await db.execute("UPDATE xpalerts SET option = $1 where gid = $2", aes.encrypt(True), aes.encrypt(ctx.guild.id))
                await ctx.send("Enabling xp alerts")
        else:
            await db.execute("INSERT INTO xpalerts VALUES($1, $2)", aes.encrypt(ctx.guild.id), aes.encrypt(False))
            await ctx.send("Disabling xp alerts")
        await db.close()


    @commands.command(
        name='SetupLogs', aliases=['Logging'], 
        description=
        "Bot permissions: Manage channels\n"
        "User permissions: Manage server"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_channels=True)
    @commands.has_guild_permissions(manage_guild=True)
    async def setuplogs(self, ctx, channel: discord.TextChannel=None):
        """Setup logging for Glass"""
        db = await asyncpg.connect(self.bot.db_conf, timeout=10)
        aes = AESCipher()
        if channel is None:
            result = await db.fetchrow("SELECT * FROM logging WHERE gid = $1", aes.encrypt(ctx.guild.id))
            if result:
                embed = discord.Embed(
                    description=f"This guild already has a logging channel: <#{aes.decrypt(result[1])}>",
                    colour=discord.Colour.red(),
                )
                embed.set_author(name='Error | Database', icon_url='https://i.imgur.com/qYyJ5cC.png')
                await ctx.send(embed=embed)
            else:
                await ctx.send('Channel was not mentioned! Creating one now.')
                overwrites = {
                    ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                }
                channel = await ctx.guild.create_text_channel(
                    name='glass-logs',
                    overwrites=overwrites
                )
                try:
                    webhook = await channel.create_webhook(name='Glass Logs')
                    await db.execute("INSERT INTO logging VALUES($1, $2, $3)", aes.encrypt(ctx.guild.id), aes.encrypt(channel.id), aes.encrypt(webhook.url))
                    await ctx.send(f"{channel.mention} will now receive logs!")
                except Exception as e:
                    await ctx.send(e)
        else:
            result = await db.fetchrow("SELECT * FROM logging WHERE gid = $1", aes.encrypt(ctx.guild.id))
            if result:
                webhook = await channel.create_webhook(name='Glass Logs')
                await db.execute("UPDATE logging SET webhook = $1, cid = $2 WHERE gid = $3", aes.encrypt(webhook.url), aes.encrypt(channel.id), aes.encrypt(ctx.guild.id))
            else:
                webhook = await channel.create_webhook(name='Glass Logs')
                await db.execute("INSERT INTO logging VALUES($1, $2, $3)", aes.encrypt(ctx.guild.id), aes.encrypt(channel.id), aes.encrypt(webhook.url))
            await ctx.send(f"{channel.mention} will now receive logs!")
        await db.close()

    @commands.command(
        name='StopLogging', aliases=['DelLogs', 'StopLogs'], 
        description=
        "Bot permissions: Manage channels\n"
        "User permissions: Manage server"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_channels=True)
    @commands.has_guild_permissions(manage_guild=True)
    async def stoplogs(self, ctx):
        """Stop logs being posted to your log channel"""
        db = await asyncpg.connect(self.bot.db_conf, timeout=10)
        aes = AESCipher()
        result = await db.fetchrow("SELECT * FROM logging WHERE gid = $1", aes.encrypt(ctx.guild.id))
        if result:
            await db.execute("DELETE FROM logging WHERE gid = $1", aes.encrypt(ctx.guild.id))
            await ctx.send(f"<#{aes.decrypt(result[1])}> will no longer receive logs!")
        else:
            embed = discord.Embed(
                description="This guild does not have logging set up",
                colour=discord.Colour.red(),
            )
            embed.set_author(name='Error | Database', icon_url='https://i.imgur.com/qYyJ5cC.png')
            await ctx.send(embed=embed)
        await db.close()

def setup(bot):
    bot.add_cog(Configuration(bot))

