import discord
from discord.ext import commands
import asyncpg
import asyncio
import re
import datetime
from utils.encrypt import AESCipher

def msg_contains_word(msg, word):
    return re.search(fr'\b({word})\b', msg) is not None

class Bwords(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.Cog.listener()
    async def on_message(self, message):
        msg = message.content.lower()
        if (not message.author.bot and not isinstance(message.channel, discord.DMChannel)
                and not message.author.guild_permissions.manage_messages
                and not message.author.guild_permissions.administrator):
            db = await asyncpg.connect(self.bot.db_conf, timeout=10)
            try:
                aes = AESCipher()
                blacklist = await db.fetchrow("SELECT * FROM blacklist WHERE gid = $1", aes.encrypt(message.guild.id))
                if blacklist:
                    words = blacklist[1]
                    for word in words:
                        word = aes.decrypt(word)
                        if msg_contains_word(msg, word):
                            await message.delete()
                            mid = message.author.id
                            gid = message.guild.id
                            fid = message.author.id + message.guild.id
                            try:
                                self.bot.tp[fid] += 1
                            except KeyError:
                                self.bot.tp[fid] = 1

                            if self.bot.tp[fid] == 5:
                                mutedRole = discord.utils.get(message.guild.roles, name='Muted')

                                if not mutedRole:
                                    mutedRole = await message.guild.create_role(name='Muted')

                                muted = datetime.datetime.utcnow().timestamp()
                                time = 1800
                                result = await db.fetchrow(
                                    "SELECT * FROM mutes WHERE mid = $1 and gid = $2 and fid = $3", aes.encrypt(mid), aes.encrypt(gid), aes.encrypt(fid))
                                if result:
                                    await db.execute(
                                        "DELETE FROM mutes WHERE mid = $1 and gid = $2 and fid = $3", aes.encrypt(mid), aes.encrypt(gid), aes.encrypt(fid)
                                    )
                                await db.execute(
                                    "INSERT INTO mutes VALUES($1, $2, $3, $4, $5)", aes.encrypt(mid), aes.encrypt(gid), aes.encrypt(fid), aes.encrypt(muted), aes.encrypt(time)
                                )
                                await message.author.add_roles(mutedRole)
                                embed = discord.Embed(
                                    description=f"Blacklisted word detected!\n"
                                                f"{message.author.mention} has been muted for 30m",
                                    colour=discord.Colour.red(),
                                )
                                embed.set_author(name=f'Automod [{self.bot.tp[fid]}]', icon_url='https://i.imgur.com/qekGkXS.png')
                                await message.channel.send(embed=embed)
                            elif self.bot.tp[fid] > 5:
                                self.bot.tp[fid] -= 1
                            else:
                                embed = discord.Embed(
                                    description=f"Blacklisted word detected!\n"
                                                f"{message.author.mention}",
                                    colour=discord.Colour.red(),
                                )
                                embed.set_author(name=f'Automod [{self.bot.tp[fid]}]', icon_url='https://i.imgur.com/qekGkXS.png')
                                await message.channel.send(embed=embed)
                            await asyncio.sleep(60)
                            if self.bot.tp[fid] != 0:
                                self.bot.tp[fid] -= 1
                            else:
                                pass
            except:
                pass
            await db.close()

def setup(bot):
    bot.add_cog(Bwords(bot))
