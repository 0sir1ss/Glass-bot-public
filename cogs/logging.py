from datetime import datetime
import discord
from discord import Webhook, AsyncWebhookAdapter
from discord.ext import commands
import asyncpg
import aiohttp
from utils.encrypt import AESCipher

class Logging(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not isinstance(before.channel, discord.DMChannel):
            try:
                aes = AESCipher()
                db = await asyncpg.connect(self.bot.db_conf, timeout=10)
                result = await db.fetchrow("SELECT * FROM logging WHERE gid = $1", aes.encrypt(before.guild.id))
                await db.close()
                if result:
                    async with aiohttp.ClientSession() as session:
                        log_channel = Webhook.from_url(aes.decrypt(result[2]), adapter=AsyncWebhookAdapter(session))

                        if before.content != after.content:
                            embed = discord.Embed(
                                description=f"Message ID: {after.id}",
                                colour=self.bot.colour,
                                timestamp=datetime.utcnow()
                            )
                            embed.set_author(name='Message Edited', icon_url='https://i.imgur.com/cybswo5.png')
                            embed.add_field(name="Before", value=before.content, inline=False)
                            embed.add_field(name="After", value=after.content, inline=False)
                            embed.add_field(name="Channel", value=after.channel.mention, inline=False)
                            embed.set_footer(text=f"Edit by {after.author}", icon_url=after.author.avatar_url)

                            await log_channel.send(embed=embed, avatar_url='https://cdn.glassbot.club/glass.png')
                else:
                    pass
            except:
                pass

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not isinstance(message.channel, discord.DMChannel):
            try:
                aes = AESCipher()
                db = await asyncpg.connect(self.bot.db_conf, timeout=10)
                result = await db.fetchrow("SELECT * FROM logging WHERE gid = $1", aes.encrypt(message.guild.id))
                await db.close()
                if result:
                    async with aiohttp.ClientSession() as session:
                        log_channel = Webhook.from_url(aes.decrypt(result[2]), adapter=AsyncWebhookAdapter(session))

                        if message.content:
                            embed = discord.Embed(
                                description=f"Message ID: {message.id}",
                                colour=self.bot.colour,
                                timestamp=datetime.utcnow()
                            )
                            embed.set_author(name='Message Deleted', icon_url='https://i.imgur.com/wkkFc15.png')
                            embed.add_field(name="Content", value=message.content, inline=False)
                            embed.add_field(name="Channel", value=message.channel.mention, inline=False)
                            embed.set_footer(text=f"Sent by {message.author}",
                                             icon_url=message.author.avatar_url)
                            await log_channel.send(embed=embed, avatar_url='https://cdn.glassbot.club/glass.png')
                        if message.embeds:
                            await log_channel.send("**Deleted message contained embeds**")
                            for e in message.embeds:
                                await log_channel.send(embed=e, avatar_url='https://cdn.glassbot.club/glass.png')
                else:
                    pass
            except:
                pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            aes = AESCipher()
            db = await asyncpg.connect(self.bot.db_conf, timeout=10)
            result = await db.fetchrow("SELECT * FROM logging WHERE gid = $1", aes.encrypt(member.guild.id))
            await db.close()
            if result:
                async with aiohttp.ClientSession() as session:
                    log_channel = Webhook.from_url(aes.decrypt(result[2]), adapter=AsyncWebhookAdapter(session))
                    if member.raw_status == "online":
                        status = '🟢 Online'
                    if member.raw_status == "idle":
                        status = '🟠 Idle'
                    if member.raw_status == "dnd":
                        status = '🔴 Do not disturb'
                    if member.raw_status == "offline":
                        status = '⚪ Offline'
                    embed = discord.Embed(
                        description=f'Member ID: {member.id}\nStatus: {status}\nCreated at: {member.created_at.strftime("%I:%M %p %d %B %Y")}',
                        colour=self.bot.colour,
                        timestamp=datetime.utcnow()
                    )
                    embed.set_author(name='Member Joined', icon_url='https://i.imgur.com/FKkolYK.png')
                    embed.set_footer(text=member, icon_url=member.avatar_url)
                    embed.set_thumbnail(url=member.avatar_url)
                    await log_channel.send(embed=embed, avatar_url='https://cdn.glassbot.club/glass.png')
            else:
                pass
        except:
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        try:
            aes = AESCipher()
            db = await asyncpg.connect(self.bot.db_conf, timeout=10)
            result = await db.fetchrow("SELECT * FROM logging WHERE gid = $1", aes.encrypt(member.guild.id))
            await db.close()
            if result:
                async with aiohttp.ClientSession() as session:
                    log_channel = Webhook.from_url(aes.decrypt(result[2]), adapter=AsyncWebhookAdapter(session))
                    if member.raw_status == "online":
                        status = '🟢 Online'
                    if member.raw_status == "idle":
                        status = '🟠 Idle'
                    if member.raw_status == "dnd":
                        status = '🔴 Do not disturb'
                    if member.raw_status == "offline":
                        status = '⚪ Offline'
                    embed = discord.Embed(
                        description=f'Member ID: {member.id}\n'
                                    f'Status: {status}\n'
                                    f'Created at: {member.created_at.strftime("%I:%M %p %d %B %Y")}\n'
                                    f'Joined at: {member.joined_at.strftime("%I:%M %p %d %B %Y")}',
                        colour=self.bot.colour,
                        timestamp=datetime.utcnow()
                    )
                    embed.set_author(name='Member Left', icon_url='https://i.imgur.com/12LCped.png')
                    embed.set_footer(text=member, icon_url=member.avatar_url)
                    embed.set_thumbnail(url=member.avatar_url)
                    await log_channel.send(embed=embed, avatar_url='https://cdn.glassbot.club/glass.png')
            else:
                pass
        except:
            pass



#####################################################################################################################
#####################################################################################################################


def setup(bot):
    bot.add_cog(Logging(bot))
