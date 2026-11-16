import math
import asyncio
import random
import discord
from discord.ext import commands
import asyncpg
from discord.ext.buttons import Paginator as Pag
from utils.encrypt import AESCipher

async def adds_user_to_db(self, user_id, guild_id):
    """Adds User To DB Under User Table"""
    aes = AESCipher()
    user = user_id
    guild = guild_id
    params = (user + guild, user, guild, 0, 0)
    db = await asyncpg.connect(self.bot.db_conf, timeout=10)
    await db.execute(f"""INSERT INTO xp VALUES ($1, $2, $3, $4, $5) """, aes.encrypt(params[0]), aes.encrypt(params[1]), aes.encrypt(params[2]), aes.encrypt(params[3]), aes.encrypt(params[4]))
    await db.close()


async def get_user_from_db(self, user_id, guild_id):
    """Gets User From DB"""
    aes = AESCipher()
    user = user_id
    guild = guild_id
    id = user + guild
    db = await asyncpg.connect(self.bot.db_conf, timeout=10)
    result = await db.fetchrow(f"""SELECT * FROM xp WHERE user_guild = $1""", aes.encrypt(id))  # checks database to see if user is in database
    await db.close()
    return result


async def update_user_set_level_where_user_id(self, x, user_id, guild_id):
    """Sets a Users LEVEL in DB"""
    aes = AESCipher()
    user = user_id
    guild = guild_id
    id = user + guild
    db = await asyncpg.connect(self.bot.db_conf, timeout=10)
    result = await db.fetchrow(f"""Update xp set level = $1 where user_guild = $2""", aes.encrypt(x), aes.encrypt(id))
    await db.close()
    return result


async def update_user_set_xp_where_user_id(self, xp2, user_id, guild_id):
    """Sets a Users XP in DB"""
    aes = AESCipher()
    user = user_id
    guild = guild_id
    id1 = user + guild
    db = await asyncpg.connect(self.bot.db_conf, timeout=10)
    result = await db.fetchrow(f"""Update xp set xp = $1 where user_guild = $2""", aes.encrypt(xp2), aes.encrypt(id1))
    await db.close()
    return result


def calc_xp(x):
    return 100 * (x ** 2)

def calc_level(x):
    return math.sqrt(x) / 10

def calc_lvlxp(x):
    return math.pow((x * 10), 2)

def generatexp():
    return random.randint(10, 20)


class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.Cog.listener()
    async def on_message(self, message):

        if not message.author.bot and not isinstance(message.channel, discord.DMChannel):  # Checks

            # cooldown check first
            mid = message.author.id
            gid = message.guild.id
            _id = mid + gid
            if _id in self.bot.xp_cooldown:
                return            # on cooldown

            else:
                aes = AESCipher()
                try:
                    xp1 = generatexp()
                    result = await get_user_from_db(self, message.author.id, message.guild.id)
                    if result is None:
                        await adds_user_to_db(self, message.author.id, message.guild.id)
                        await asyncio.sleep(2)
                    result = await get_user_from_db(self, message.author.id, message.guild.id)  # Refreshes the database check as it was giving me errors if it found no user and had to add them.
                    if int(aes.decrypt(result[2])) is None:  # If they were in database but had xp value of None, makes it 0 for lvl calculator to work properly
                        old_xp = 0
                    else:
                        old_xp = int(aes.decrypt(result[3]))
                    if old_xp < 10000000000: # Not at level cap
                        old_lvl = int(calc_level(old_xp))
                        newxp = old_xp + xp1
                        new_lvl = int(calc_level(newxp))
                        flag = False

                        if old_lvl < new_lvl:
                            flag = True
                        await update_user_set_xp_where_user_id(self, newxp, message.author.id, message.guild.id)

                        if flag:
                            await update_user_set_level_where_user_id(self, new_lvl, message.author.id, message.guild.id)
                            msg = f"Congrats! {message.author} has levelled up to **rank {int(new_lvl)}**" \
                                  f"\n||Disable these alerts with the `xpalerts` command||"
                            try:
                                db = await asyncpg.connect(self.bot.db_conf, timeout=10)
                                result = await db.fetchrow("SELECT * FROM xpalerts WHERE gid = $1", aes.encrypt(message.guild.id))
                                await db.close()
                                if result:
                                    allowed = aes.decrypt(result[1])
                                    if allowed == "True":
                                        await message.channel.send(msg, delete_after=10)
                                    else:
                                        pass
                                else:
                                    await message.channel.send(msg, delete_after=10)
                            except:
                                # Just a final thing if not accessible idk
                                await message.channel.send(msg, delete_after=10)
                        self.bot.xp_cooldown.append(_id)
                        await asyncio.sleep(60)
                        self.bot.xp_cooldown.remove(_id)
                except:
                    pass

    @commands.command(
        name="Set_Level", aliases=['Set_Rank'],
        usage='<level> [user]',
        description=
        "Bot permissions: None\n"
        "User permissions: Manage Server"
    )
    @commands.has_guild_permissions(manage_guild=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    async def changerank(self, ctx, level: int=None, user: discord.Member = None):
        """Changes a users rank and xp"""
        if not level:
            return await ctx.send("Please set a level.")
        if level > 10000:
            return await ctx.send("Sorry, but that level is too high. The max is 10000.")
        user = user or ctx.author

        result = await get_user_from_db(self, user.id, ctx.guild.id)  # checks database to see if user is in database
        aes = AESCipher()
        curlvl = int(aes.decrypt(result[4]))
        clvl_xp = int(aes.decrypt(result[3]))
        nlvl_xp = int(calc_lvlxp(level))
        await update_user_set_xp_where_user_id(self, nlvl_xp, user.id, ctx.guild.id)
        await update_user_set_level_where_user_id(self, level, user.id, ctx.guild.id)

        embed = discord.Embed(
            title=f"Rank and XP change for {user}!",
            description=f"Old Level: {curlvl} - {clvl_xp}\nNew Level: {level} - {nlvl_xp}",
            colour=self.bot.colour
        )
        embed.set_thumbnail(url=user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(
        name="Rank", aliases=['Level', 'XP'], 
        description=
        "Bot permissions: None\n"
        "User permissions: None"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    async def checkrank(self, ctx,  user: discord.Member = None):
        """Displays Users Level and XP"""
        if user is None:
            user = ctx.message.author

        result = await get_user_from_db(self, user.id, ctx.guild.id)  # checks database to see if user is in database
        aes = AESCipher()
        nxtlvl = int(aes.decrypt(result[4])) + 1
        nxtlvl_xp = int(calc_lvlxp(nxtlvl))
        curlvl = int(aes.decrypt(result[4]))
        curlvl_xp = int(calc_lvlxp(curlvl))
        curxp = int(aes.decrypt(result[3]))
        lvlxp = curxp - curlvl_xp
        lvlxp2 = nxtlvl_xp - curlvl_xp
        xpneeded = nxtlvl_xp - int(aes.decrypt(result[3]))

        lvl_per = int(round((lvlxp / lvlxp2) * 100))
        #                    curxp / xp to nxt lvl * 100
        
        bar1 = int(lvl_per / 10)
        bar_blue = bar1 * ':blue_square:'
        bar2 = int(10 - bar1)
        bar_white = bar2 * ':white_large_square:'
        bar = bar_blue + bar_white

        embed = discord.Embed(title=f"Displaying stats for {user}!", colour=self.bot.colour)
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name='**Level**', value=curlvl, inline=True)
        embed.add_field(name='**Total XP**', value=curxp, inline=True)
        embed.add_field(name='**XP Needed**', value=xpneeded, inline=True)
        embed.add_field(name='**Level Percentage**', value=f'{lvl_per}%', inline=False)
        embed.add_field(name='**Progress Bar**', value=f"{curlvl_xp} **|** {bar} **|** {nxtlvl_xp}", inline=False)
        await ctx.send(embed=embed)


    @commands.command(
        name="Leaderboard", aliases=["LB"], 
        description=
        "Bot permissions: None\n"
        "User permissions: None"
    )
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def leaderboard(self, ctx):
        """Displays users with the highest level in the guild"""
        db = await asyncpg.connect(self.bot.db_conf, timeout=10)
        aes = AESCipher()
        result = await db.fetch("SELECT * FROM xp WHERE guild_id = $1", aes.encrypt(ctx.guild.id))  # checks database to see if user is in database
        await db.close()
        lb = sorted(result, reverse=True, key=lambda x: int(aes.decrypt(x[3])))
        pages = []
        n = 1

        for x in lb:
            pages.append(f"**#{n} <@{aes.decrypt(x[1])}> : Level `{aes.decrypt(x[4])}` - `{aes.decrypt(x[3])}`xp**")
            n += 1

        await Pag(title=f"📋 Leaderboard for {ctx.guild.name}",
                  colour=self.bot.colour,
                  entries=pages, length=10, thumbnail=ctx.guild.icon_url).start(ctx)


def setup(bot):
    bot.add_cog(Levels(bot))
