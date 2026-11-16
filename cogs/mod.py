import asyncio
import datetime
import re
from typing import Optional, Union
import asyncpg
import discord
import uuid
from discord import Member, NotFound, Object
from discord.ext import commands, tasks
from discord.ext.commands import BadArgument, Converter, Greedy
from discord.utils import find
from utils.util import perms
from discord.ext.buttons import Paginator as Pag
from utils.encrypt import AESCipher

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for key, value in matches:
            try:
                time += time_dict[value] * float(key)
            except KeyError:
                raise commands.BadArgument(
                    f"{value} is an invalid time key! h|m|s|d are valid arguments"
                )
            except ValueError:
                raise commands.BadArgument(f"{key} is not a number!")
        if time == 0:
            return argument
        else:
            return round(time)


# These colour constants are taken from discord.js library
colours = {
    'WHITE': 0xFFFFFF,
    'AQUA': 0x1ABC9C,
    'GREEN': 0x2ECC71,
    'BLUE': 0x3498DB,
    'PURPLE': 0x9B59B6,
    'LUMINOUS_VIVID_PINK': 0xE91E63,
    'GOLD': 0xF1C40F,
    'ORANGE': 0xE67E22,
    'RED': 0xE74C3C,
    'NAVY': 0x34495E,
    'DARK_AQUA': 0x11806A,
    'DARK_GREEN': 0x1F8B4C,
    'DARK_BLUE': 0x206694,
    'DARK_PURPLE': 0x71368A,
    'DARK_VIVID_PINK': 0xAD1457,
    'DARK_GOLD': 0xC27C0E,
    'DARK_RED': 0x992D22,
    'DARK_GREY': 0x979C9F,
    'DARKER_GREY': 0x7F8C8D,
    'LIGHT_GREY': 0xBCC0C0,
    'DARK_NAVY': 0x2C3E50,
    'BLURPLE': 0x7289DA,
}

# Colours for embed
colour_list = [c for c in colours.values()]
# This does 2 things, it converts colours into a list and allows us to use the random module

class BannedUser(Converter):
    async def convert(self, ctx, arg):
        if ctx.guild.me.guild_permissions.ban_members and arg.isdigit():
            try:
                return (await ctx.guild.fetch_ban(Object(id=int(arg)))).user
            except NotFound:
                return None

        banned = [e.user for e in await ctx.guild.bans()]
        if banned:
            if (user := find(lambda u: str(u) == arg, banned)) is not None:
                return user
            else:
                return None


class Mod(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.mute_task = self.check_current_mutes.start()

    def cog_unload(self):
        self.mute_task.cancel()

    @tasks.loop(minutes=1)
    async def check_current_mutes(self):
        try:
            aes = AESCipher()
            currentTime = datetime.datetime.utcnow().timestamp()
            db = await asyncpg.connect(self.bot.db_conf, timeout=10)
            mutes = await db.fetch("SELECT * FROM mutes")
            await db.close()
            for m in mutes:
                try:
                    if int(aes.decrypt(m[4])) == 0:
                        continue

                    unmuteTime = int(aes.decrypt(m[3])) + int(aes.decrypt(m[4]))

                    if currentTime >= unmuteTime:
                        guild = self.bot.get_guild(int(aes.decrypt(m[1])))
                        member = guild.get_member(int(aes.decrypt(m[0])))

                        mutedRole = discord.utils.get(guild.roles, name="Muted")
                        if mutedRole in member.roles:
                            await member.remove_roles(mutedRole)
                            try:
                                embed = discord.Embed(colour=discord.Colour.green())
                                embed.add_field(name="Guild: ", value=f"{guild.name}", inline=True)
                                embed.add_field(name="Reason: ", value="Mute timer has expired.", inline=False)
                                embed.set_author(name='Unmute Log', icon_url='https://i.imgur.com/6fOJyWE.png')
                                await member.send(embed=embed)
                            except:
                                pass
                        else:
                            pass

                        mid = member.id
                        gid = guild.id
                        fid = mid + gid
                        await db.execute(
                            "DELETE FROM mutes WHERE mid = $1 and gid = $2 and fid = $3", aes.encrypt(mid), aes.encrypt(gid), aes.encrypt(fid)
                        )
                except:
                    pass
        except:
            pass

    @check_current_mutes.before_loop
    async def before_check_current_mutes(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        db = await asyncpg.connect(self.bot.db_conf, timeout=10)
        aes = AESCipher()
        try:
            result = await db.fetchrow(
                "SELECT * FROM mutes WHERE gid = $1 and mid = $2", aes.encrypt(member.guild.id), aes.encrypt(member.id)
            )
            if result:
                guild = self.bot.get_guild(member.guild.id)
                mutedRole = discord.utils.get(guild.roles, name="Muted")

                if mutedRole not in member.roles:
                    await member.add_roles(mutedRole)
        except:
            pass
        await db.close()


    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    ####################################################################################################################
    ####################################################################################################################

    # Kick Command

    @commands.command(
        name='Kick',
        usage='<user> [reason]',
        description=
        "Bot permissions: Kick members\n"
        "User permissions: Kick members"
    )
    @commands.bot_has_guild_permissions(kick_members=True)
    @commands.has_guild_permissions(kick_members=True)
    async def kick(self, ctx, target: discord.Member=None, *, reason=None):
        """Kicks a user"""
        if not target:
            await ctx.invoke(self.bot.get_command("help"), entity="Kick")
        else:
            if reason is None:
                reason = 'No reason was provided'
            author = ctx.message.author

            p = perms(self, ctx, target)
            if p:
                await ctx.send(embed=p)
            else:
                embed = discord.Embed(colour=discord.Colour.red())
                embed.set_author(name='Kick Log', icon_url='https://i.imgur.com/s9Bt9HB.png')
                embed.add_field(name="Kicked by: ", value=author.mention, inline=True)
                embed.add_field(name="User: ", value=target.mention, inline=True)
                embed.add_field(name="Reason: ", value=reason, inline=False)
                embed.set_thumbnail(url=target.avatar_url)
                await ctx.send(embed=embed)
                try:
                    embed = discord.Embed(colour=discord.Colour.red())
                    embed.set_author(name='Kick Log', icon_url='https://i.imgur.com/s9Bt9HB.png')
                    embed.add_field(name="Kicked by: ", value=f"{author.mention}", inline=False)
                    embed.add_field(name="Guild: ", value=f"{ctx.guild.name}", inline=False)
                    embed.add_field(name="Reason: ", value=f"{reason}\n", inline=False)
                    embed.set_thumbnail(url=target.avatar_url)
                    await target.send(embed=embed)
                except discord.HTTPException:
                    await ctx.send("That user has DM's disabled, continuing Kick.")

                await target.kick(reason=reason)

    # Ban Command

    @commands.command(
        name='Ban',
        usage='<user> [reason]',
        description=
        "Bot permissions: Ban members\n"
        "User permissions: Ban members"
    )
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.has_guild_permissions(ban_members=True)
    async def ban(self, ctx, target: Union[discord.Member, discord.User]=None, *, reason=None):
        """Bans a user"""
        if not target:
            await ctx.invoke(self.bot.get_command("help"), entity="Ban")
        else:
            if reason is None:
                reason = 'No reason was provided'

            author = ctx.message.author

            p = perms(self, ctx, target)
            if p:
                await ctx.send(embed=p)
            else:
                embed = discord.Embed(colour=discord.Colour.red())
                embed.set_author(name='Ban Log', icon_url='https://i.imgur.com/3NJPDCq.png')
                embed.add_field(name="Banned by: ", value=author.mention, inline=True)
                embed.add_field(name="User: ", value=target.mention, inline=True)
                embed.add_field(name="Reason: ", value=reason, inline=False)
                embed.set_thumbnail(url=target.avatar_url)
                await ctx.send(embed=embed)
                try:
                    embed = discord.Embed(colour=discord.Colour.red())
                    embed.set_author(name='Ban Log', icon_url='https://i.imgur.com/3NJPDCq.png')
                    embed.add_field(name="Banned by: ", value=f"{author.mention}", inline=False)
                    embed.add_field(name="Guild: ", value=f"{ctx.guild.name}", inline=False)
                    embed.add_field(name="Reason: ", value=f"{reason}\n", inline=False)
                    embed.set_thumbnail(url=target.avatar_url)
                    await target.send(embed=embed)
                except discord.HTTPException:
                    await ctx.send("That user has DM's disabled, continuing Ban.")
                await ctx.guild.ban(target, reason=reason)

    # MultiKick Command

    @commands.command(
        name='Multikick', aliases=['Mkick', 'Masskick'],
        usage='<user(s) [Max 5]>',
        description=
        "Bot permissions: Kick members\n"
        "User permissions: Kick members"
    )
    @commands.bot_has_guild_permissions(kick_members=True)
    @commands.check_anyhas_guild_permissions(kick_members=True)
    async def Masskick(self, ctx, targets: Greedy[discord.Member]):
        """Kick upto 5 users"""
        if not len(targets):
            await ctx.invoke(self.bot.get_command("help"), entity="Masskick")
        else:
            author = ctx.message.author
            allowed = []

            if len(targets) > 5:
                embed = discord.Embed(
                    description="I can only kick 5 members at a time.\nContinuing to kick users.",
                    colour=discord.Colour.red(),
                )
                embed.set_author(name='Error | Arguments', icon_url='https://i.imgur.com/qYyJ5cC.png')
                await ctx.send(embed=embed)

            for target in targets:
                p = perms(self, ctx, target)
                if p:
                    await ctx.send(embed=p)
                else:
                    allowed.append(target)
            if allowed != 0:
                kicked = []
                for i in range(5):
                    target = allowed[i]
                    try:
                        embed = discord.Embed(colour=discord.Colour.red())
                        embed.set_author(name='Kick Log', icon_url='https://i.imgur.com/s9Bt9HB.png')
                        embed.add_field(name="Kicked by: ", value=f"{author.mention}", inline=False)
                        embed.add_field(name="Guild: ", value=f"{ctx.guild.name}", inline=False)
                        embed.set_thumbnail(url=target.avatar_url)
                        await target.send(embed=embed)
                    except discord.HTTPException:
                        await ctx.send("That user has DM's disabled, continuing Multikick.")
                    await target.kick()
                    kicked.append(f'{target.name}#{target.discriminator}')

                embed = discord.Embed(colour=discord.Colour.red())
                embed.set_author(name='Kick Log', icon_url='https://i.imgur.com/s9Bt9HB.png')
                embed.add_field(name="Kicked by: ", value=author.mention, inline=True)
                embed.add_field(name="Users: ", value='\n'.join(i for i in kicked), inline=False)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    description="No members available to kick.",
                    colour=discord.Colour.red(),
                )
                embed.set_author(name='Error | Arguments', icon_url='https://i.imgur.com/qYyJ5cC.png')
                await ctx.send(embed=embed)

    # Multiban Command

    @commands.command(
        name='Multiban', aliases=['Mban', 'Massban'],
        usage='<user(s) [Max 5]>',
        description=
        "Bot permissions: Ban members\n"
        "User permissions: Ban members"
    )
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.has_guild_permissions(ban_members=True)
    async def massban(self, ctx, targets: Greedy[Union[discord.Member, discord.User]]):
        """Ban upto 5 users"""
        if not len(targets):
            await ctx.invoke(self.bot.get_command("help"), entity="Massban")
        else:
            author = ctx.message.author
            allowed = []

            if len(targets) > 5:
                embed = discord.Embed(
                    description="I can only ban 5 members at a time.\nContinuing to ban users.",
                    colour=discord.Colour.red(),
                )
                embed.set_author(name='Error | Arguments', icon_url='https://i.imgur.com/qYyJ5cC.png')
                await ctx.send(embed=embed)

            for target in targets:
                p = perms(self, ctx, target)
                if p:
                    await ctx.send(embed=p)
                else:
                    allowed.append(target)
            if allowed != 0:
                banned = []
                for i in range(5):
                    target = allowed[i]
                    try:
                        embed = discord.Embed(colour=discord.Colour.red())
                        embed.set_author(name='Ban Log', icon_url='https://i.imgur.com/s9Bt9HB.png')
                        embed.add_field(name="Banned by: ", value=f"{author.mention}", inline=False)
                        embed.add_field(name="Guild: ", value=f"{ctx.guild.name}", inline=False)
                        embed.set_thumbnail(url=target.avatar_url)
                        await target.send(embed=embed)
                    except discord.HTTPException:
                        await ctx.send("That user has DM's disabled, continuing Multiban.")
                    await target.ban()
                    banned.append(f'{target.name}#{target.discriminator}')

                embed = discord.Embed(colour=discord.Colour.red())
                embed.set_author(name='Ban Log', icon_url='https://i.imgur.com/s9Bt9HB.png')
                embed.add_field(name="Banned by: ", value=author.mention, inline=True)
                embed.add_field(name="Users: ", value='\n'.join(i for i in banned), inline=False)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    description="No members available to ban.",
                    colour=discord.Colour.red(),
                )
                embed.set_author(name='Error | Arguments', icon_url='https://i.imgur.com/qYyJ5cC.png')
                await ctx.send(embed=embed)


    # Unban Command

    @commands.command(
        name='Unban',
        usage='<abc#1234 | userid>',
        description=
        "Bot permissions: Ban members\n"
        "User permissions: Ban members"
    )
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.has_guild_permissions(ban_members=True)
    async def unban(self, ctx, user: BannedUser=None):
        """Unbans a user"""
        if not user:
            embed = discord.Embed(
                description=f"User was not found or is already unbanned.",
                colour=discord.Colour.red(),
            )
            embed.set_author(name='Error | Arguments', icon_url='https://i.imgur.com/qYyJ5cC.png')
            return await ctx.send(embed=embed)
        else:
            author = ctx.message.author
            await ctx.guild.unban(user, reason='Unban')

            embed = discord.Embed(colour=discord.Colour.green())
            embed.set_author(name='Unban Log', icon_url='https://i.imgur.com/RCeWZ5E.png')
            embed.set_thumbnail(url=user.avatar_url)
            embed.add_field(name="Unbanned by: ", value=f"{author.mention}", inline=False)
            embed.add_field(name="User: ", value=f"{user} - <@{user.id}>", inline=False)
            await ctx.send(embed=embed)

    ####################################################################################################################
    ####################################################################################################################

    # Warn Command

    @commands.command(
        name="Warn", usage='<user> [reason]',
        description=
        "Bot permissions: None\n"
        "User permissions: Manage messages"
    )
    @commands.has_guild_permissions(manage_messages=True)
    async def warn(self, ctx, user: discord.Member = None, *, reason=None):
        """Warns a user"""
        db = await asyncpg.connect(self.bot.db_conf, timeout=10)
        aes = AESCipher()
        if user is None:
            await ctx.invoke(self.bot.get_command("help"), entity="Warn")
        else:
            if reason is None:
                reason = 'No reason was provided'

            p = perms(self, ctx, user)
            if p:
                await ctx.send(embed=p)
            else:

                mid = user.id
                gid = ctx.guild.id
                aid = ctx.author.id
                time = datetime.datetime.utcnow().timestamp()

                count = len(
                    await db.fetch(
                    f"SELECT * FROM warning WHERE mid = $1 and gid = $2", aes.encrypt(mid), aes.encrypt(gid)
                )
                ) + 1

                uid = str(uuid.uuid1())

                await db.execute(
                    f"INSERT INTO warning VALUES($1, $2, $3, $4, $5, $6)", aes.encrypt(mid), aes.encrypt(gid), aes.encrypt(uid), aes.encrypt(reason), aes.encrypt(time), aes.encrypt(aid)
                )

                try:
                    wembed = discord.Embed(colour=discord.Colour.red())
                    wembed.set_author(name="Warn Log", icon_url='https://i.imgur.com/GeycKVe.png')
                    wembed.add_field(name="Guild: ", value=f"{ctx.guild.name}", inline=False)
                    wembed.add_field(name="Warned by: ", value=ctx.author.mention, inline=True)
                    wembed.add_field(name="Warnings: ", value=str(count), inline=True)
                    wembed.add_field(name="Warn ID:", value=uid, inline=False)
                    wembed.add_field(name="Reason: ", value=reason, inline=False)
                    wembed.set_thumbnail(url=user.avatar_url)
                    await user.send(embed=wembed)
                except discord.HTTPException:
                    await ctx.send("That user has DM's disabled, continuing Warn.")

                embed = discord.Embed(colour=discord.Colour.red())
                embed.set_author(name="Warn Log", icon_url='https://i.imgur.com/GeycKVe.png')
                embed.add_field(name="Warned by: ", value=ctx.author.mention, inline=True)
                embed.add_field(name="User: ", value=user.mention, inline=True)
                embed.add_field(name="Warnings: ", value=str(count), inline=True)
                embed.add_field(name="Warn ID:", value=uid, inline=False)
                embed.add_field(name="Reason: ", value=reason, inline=False)
                embed.set_thumbnail(url=user.avatar_url)
                await ctx.send(embed=embed)
        await db.close()

    # ClearWarn Command

    @commands.command(
        name="RemoveWarn", usage='<warnid>',
        aliases=["RWarn", "ClearWarn"],
        description=
        "Bot permissions: None\n"
        "User permissions: Manage messages"
    )
    @commands.has_guild_permissions(manage_messages=True)
    async def rwarn(self, ctx, *, uuid: str=None):
        """Removes a warning from a user"""
        db = await asyncpg.connect(self.bot.db_conf, timeout=10)
        aes = AESCipher()
        if uuid is None:
            await ctx.invoke(self.bot.get_command("help"), entity="RemoveWarn")
        else:
            gid = ctx.guild.id
            uid = str(uuid)

            try:
                result = await db.fetchrow(
                    f"SELECT * FROM warning WHERE uuid = $1 and gid = $2", aes.encrypt(uid), aes.encrypt(gid)
                )
                user = ctx.guild.get_member(int(aes.decrypt(result[0])))

                p = perms(self, ctx, user)
                if p:
                    await ctx.send(embed=p)
                else:

                    await db.execute(
                        f"DELETE FROM warning WHERE uuid = $1 AND gid = $2", aes.encrypt(uid), aes.encrypt(gid)
                    )
                    count = len(await db.fetch(
                        f"SELECT * FROM warning WHERE mid = $1 and gid = $2", aes.encrypt(user.id), aes.encrypt(gid)
                    ))

                    try:
                        wembed = discord.Embed(colour=discord.Colour.green())
                        wembed.set_author(name="Remove Warn Log", icon_url='https://i.imgur.com/RCeWZ5E.png')
                        wembed.add_field(name="Guild: ", value=f"{ctx.guild.name}", inline=False)
                        wembed.add_field(name="Removed by: ", value=ctx.author.mention, inline=True)
                        wembed.add_field(name="Warnings: ", value=str(count), inline=True)
                        wembed.add_field(name="Warn ID:", value=uid, inline=False)
                        wembed.add_field(name="Reason: ", value=aes.decrypt(result[3]), inline=False)
                        wembed.set_thumbnail(url=user.avatar_url)
                        await user.send(embed=wembed)
                    except discord.HTTPException:
                        await ctx.send("That user has DM's disabled, continuing to Remove Warn.")

                    embed = discord.Embed(colour=discord.Colour.green())
                    embed.set_author(name="Remove Warn Log", icon_url='https://i.imgur.com/RCeWZ5E.png')
                    embed.add_field(name="Removed by: ", value=f"{ctx.author.mention}", inline=True)
                    embed.add_field(name="User: ", value=f"{user.mention}", inline=True)
                    embed.add_field(name="Warnings: ", value=str(count), inline=True)
                    embed.add_field(name="Warn ID:", value=uid, inline=False)
                    embed.add_field(name='Reason', value=aes.decrypt(result[3]), inline=False)
                    embed.set_thumbnail(url=user.avatar_url)
                    await ctx.send(embed=embed)
            except:
                embed = discord.Embed(
                    description=f"That warn ID doesn't exist in this guild",
                    colour=discord.Colour.red(),
                )
                embed.set_author(name='Error | Generic', icon_url='https://i.imgur.com/qYyJ5cC.png')
                return await ctx.send(embed=embed)
        await db.close()

    # Warnings Command

    @commands.command(
        name="Warns", usage='<user>', aliases=['Warnings'],
        description=
        "Bot permissions: Manage messages, Add reactions\n"
        "User permissions: Manage messages"
    )
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(manage_messages=True, add_reactions=True)
    async def warnings(self, ctx, user: discord.Member = None):
        """Checks a user's warnings"""
        db = await asyncpg.connect(self.bot.db_conf, timeout=10)
        aes = AESCipher()
        if user is None:
            await ctx.invoke(self.bot.get_command("help"), entity="Warns")
        else:
            mid = user.id
            gid = ctx.guild.id

            result = await db.fetch(
                f"SELECT * FROM warning WHERE mid = $1 AND gid = $2", aes.encrypt(mid), aes.encrypt(gid)
            )

            if result:
                warns = sorted(result, key=lambda x: int(aes.decrypt(x[4]).split('.')[0]))
                pages = []
                warnnum = 0

                for warn in warns:
                    warnnum += 1
                    desc = f"""
                    Warn ID:        `{aes.decrypt(warn[2])}`
                    Warned By:      <@{aes.decrypt(warn[5])}>
                    Warned At:      {datetime.datetime.fromtimestamp(int(aes.decrypt(warn[4]).split('.')[0])).strftime("%I:%M %p %d %B %Y")}
                    Warn Number:    {warnnum}
                    Warn Reason:    {aes.decrypt(warn[3])}
                    """
                    pages.append(desc)

                await Pag(
                    title=f"Warn Log: {user.name}#{user.discriminator} - {len(result)}",
                    colour=self.bot.colour,
                    entries=pages,
                    thumbnail=user.avatar_url,
                    length=1
                ).start(ctx)

            else:
                embed = discord.Embed(
                    description=f"That user does not have any warnings",
                    colour=discord.Colour.red(),
                )
                embed.set_author(name='Error | Generic', icon_url='https://i.imgur.com/qYyJ5cC.png')
                return await ctx.send(embed=embed)
        await db.close()


    ####################################################################################################################
    ####################################################################################################################

    # Clear Command

    @commands.command(
        name="Clear",
        aliases=['Purge'],
        usage='[user(s)] <2-100 default is 10>',
        description=
        "Bot permissions: Manage messages\n"
        "User permissions: Manage messages"
    )
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.has_guild_permissions(manage_messages=True)
    async def clear_messages(self, ctx, targets: Greedy[Member], amount: Optional[int] = 10):
        """Clears a specified amount of messages"""

        def _check(message):
            return not len(targets) or message.author in targets

        channel = ctx.channel

        if 1 < amount <= 100:
            await ctx.message.delete()
            await channel.purge(limit=amount, after=datetime.datetime.utcnow() - datetime.timedelta(days=14),
                                check=_check)

            if len(targets):
                embed = discord.Embed(
                    colour=self.bot.colour,
                    description=f"Cleared {amount} messages from {', '.join(f'{i.name}#{i.discriminator}' for i in targets)}"
                )
                embed.set_author(name='Clear Log', icon_url='https://i.imgur.com/wkkFc15.png')
            else:
                embed = discord.Embed(
                    description=f'Cleared {amount} messages', colour=self.bot.colour
                )
                embed.set_author(name='Clear Log', icon_url='https://i.imgur.com/wkkFc15.png')
            await ctx.send(embed=embed, delete_after=5)

        else:
            embed = discord.Embed(
                description=f"The amount provided must be between 2 - 100",
                colour=discord.Colour.red(),
            )
            embed.set_author(name='Error | Arguments', icon_url='https://i.imgur.com/qYyJ5cC.png')
            return await ctx.send(embed=embed)

    # Nuke command

    @commands.command(
        name="Nuke",
        description=
        "Bot permissions: Manage channels\n"
        "User permissions: Manage channels"
    )
    @commands.bot_has_guild_permissions(manage_channels=True)
    @commands.has_guild_permissions(manage_channels=True)
    async def _nuke(self, ctx, channel: discord.TextChannel = None):
        """Nukes the channel specified while keeping all the permissions the same"""
        nuke_channel = channel or ctx.channel
        url = "https://media.giphy.com/media/oe33xf3B50fsc/giphy.gif"

        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name="CHANNEL HAS BEEN NUKED")
        embed.set_image(url=url)
        embed.set_footer(text=f'This message will be deleted in 10 seconds')
        pos = nuke_channel.position
        await nuke_channel.delete()
        new_channel = await nuke_channel.clone(reason="Has been Nuked!")
        await new_channel.send(embed=embed, delete_after=10)
        await new_channel.edit(position=pos)


    #####################################################################################################################
    #####################################################################################################################

    # Mute Command

    @commands.command(
        name="Mute",
        usage='<user> [time] [reason]',
        description=
        "Bot permissions: Manage roles, Manage channels\n"
        "User permissions: Manage messages, Mute members"
    )
    @commands.bot_has_guild_permissions(manage_roles=True, manage_channels=True)
    @commands.has_guild_permissions(manage_messages=True, mute_members=True)
    async def mute(self, ctx, member: discord.Member = None, time: TimeConverter = None, *, reason=None):
        """Mutes a user"""
        db = await asyncpg.connect(self.bot.db_conf, timeout=10)
        aes = AESCipher()
        if member is None:
            await ctx.invoke(self.bot.get_command("help"), entity="Mute")

        if not isinstance(time, int):
            if reason is None:
                reason = time or 'No reason was provided.'
            else:
                reason = f"{time} {reason}"
            time = None

        p = perms(self, ctx, member)
        if p:
            await ctx.send(embed=p)
        else:
            guild = ctx.guild
            mutedRole = discord.utils.get(guild.roles, name='Muted')
            author = ctx.message.author

            if not mutedRole:
                mutedRole = await guild.create_role(name='Muted')
                pos = ctx.guild.me.top_role.position - 1
                await mutedRole.edit(position=pos)

            if mutedRole in member.roles:
                embed = discord.Embed(
                    description=f"That user is already muted",
                    colour=discord.Colour.red(),
                )
                embed.set_author(name='Error | Generic', icon_url='https://i.imgur.com/qYyJ5cC.png')
                return await ctx.send(embed=embed)

            else:
                muted = datetime.datetime.utcnow().timestamp()
                if time is None:
                    embed = discord.Embed(colour=discord.Colour.red())
                    embed.set_author(name='Mute Log', icon_url='https://i.imgur.com/837Qy8u.png')
                    embed.add_field(name="Muted by: ", value=f"{author.mention}", inline=True)
                    embed.add_field(name="User: ", value=f"{member.mention}", inline=True)
                    embed.add_field(name="Reason: ", value=f"{reason}\n", inline=False)
                    await ctx.send(embed=embed)

                    try:
                        membed = discord.Embed(colour=discord.Colour.red())
                        embed.set_author(name='Mute Log', icon_url='https://i.imgur.com/837Qy8u.png')
                        membed.add_field(name="Guild: ", value=f"{ctx.guild.name}", inline=True)
                        membed.add_field(name="Muted by: ", value=f"{author.mention}", inline=True)
                        membed.add_field(name="Reason: ", value=f"{reason}\n", inline=False)
                        await member.send(embed=membed)
                    except discord.HTTPException:
                        await ctx.send("That user has DM's disabled, continuing Mute.")
                else:
                    mutetime = str(datetime.timedelta(seconds=time))

                    embed = discord.Embed(colour=discord.Colour.red())
                    embed.set_author(name='Mute Log', icon_url='https://i.imgur.com/837Qy8u.png')
                    embed.add_field(name="Muted by: ", value=f"{author.mention}", inline=True)
                    embed.add_field(name="User: ", value=f"{member.mention}", inline=True)
                    embed.add_field(name="Time: ", value=mutetime, inline=True)
                    embed.add_field(name="Reason: ", value=f"{reason}\n", inline=False)
                    await ctx.send(embed=embed)

                    try:
                        membed = discord.Embed(colour=discord.Colour.red())
                        membed.set_author(name='Mute Log', icon_url='https://i.imgur.com/837Qy8u.png')
                        membed.add_field(name="Guild: ", value=f"{ctx.guild.name}", inline=True)
                        membed.add_field(name="Muted by: ", value=f"{author.mention}", inline=True)
                        membed.add_field(name="Time: ", value=mutetime, inline=True)
                        membed.add_field(name="Reason: ", value=f"{reason}\n", inline=False)
                        await member.send(embed=membed)
                    except discord.HTTPException:
                        await ctx.send("That user has DM's disabled, continuing Mute.")

                mid = member.id
                gid = ctx.guild.id
                fid = mid + gid
                time = time or 0
                result = await db.fetchrow("SELECT * FROM mutes WHERE mid = $1 and gid = $2 and fid = $3", aes.encrypt(mid), aes.encrypt(gid), aes.encrypt(fid))
                if result:
                    await db.execute(
                        "DELETE FROM mutes WHERE mid = $1 and gid = $2 and fid = $3", aes.encrypt(mid), aes.encrypt(gid), aes.encrypt(fid)
                    )
                await db.execute(
                    "INSERT INTO mutes VALUES($1, $2, $3, $4, $5)", aes.encrypt(mid), aes.encrypt(gid), aes.encrypt(fid), aes.encrypt(muted), aes.encrypt(time)
                )

                await member.add_roles(mutedRole)

                for channel in guild.channels:
                    await channel.set_permissions(mutedRole, speak=False, send_messages=False,
                                                  read_message_history=True)

                if time and time < 600:
                    await asyncio.sleep(time)

                    if mutedRole in member.roles:
                        await member.remove_roles(mutedRole)
                        embed = discord.Embed(colour=discord.Colour.green())
                        embed.set_author(name='Unmute Log', icon_url='https://i.imgur.com/6fOJyWE.png')
                        embed.add_field(name="Muted by: ", value=f"{author.mention}", inline=True)
                        embed.add_field(name="User: ", value=f"{member.mention}", inline=True)
                        embed.add_field(name="Reason: ", value=f"Mute timer has expired.", inline=False)
                        await ctx.send(embed=embed)
                        try:
                            embed = discord.Embed(colour=discord.Colour.green())
                            embed.add_field(name="Guild: ", value=f"{guild.name}", inline=True)
                            embed.add_field(name="Muted by: ", value=f"{author.mention}", inline=True)
                            embed.add_field(name="Reason: ", value="Mute timer has expired.", inline=False)
                            embed.set_author(name='Unmute Log', icon_url='https://i.imgur.com/6fOJyWE.png')
                            await member.send(embed=embed)
                        except discord.HTTPException:
                            pass

                    await db.execute(
                        "DELETE FROM mutes WHERE mid = $1 and gid = $2 and fid = $3", aes.encrypt(mid), aes.encrypt(gid), aes.encrypt(fid)
                    )
        await db.close()

    # Unmute Command

    @commands.command(
        name="Unmute", usage='<user> [reason]',
        description=
        "Bot permissions: Manage roles\n"
        "User permissions: Manage messages, Mute members"
    )
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.has_guild_permissions(manage_messages=True, mute_members=True)
    async def unmute(self, ctx, member: discord.Member = None, *, reason=None):
        """Unmutes a user"""
        db = await asyncpg.connect(self.bot.db_conf, timeout=10)
        aes = AESCipher()
        if member is None:
            return await ctx.invoke(self.bot.get_command("help"), entity="Unmute")
        if reason is None:
            reason = 'No reason was provided.'

        if ctx.author.id == member.id:
            embed = discord.Embed(
                description=f"You can't perform that action on yourself",
                colour=discord.Colour.red(),
            )
            embed.set_author(name='Error | Generic', icon_url='https://i.imgur.com/qYyJ5cC.png')
            return await ctx.send(embed=embed)

        elif member.id == self.bot.user.id:
            embed = discord.Embed(
                description=f"You can't perform that action on the bot",
                colour=discord.Colour.red(),
            )
            embed.set_author(name='Error | Generic', icon_url='https://i.imgur.com/qYyJ5cC.png')
            return await ctx.send(embed=embed)

        else:
            guild = ctx.guild
            mutedRole = discord.utils.get(guild.roles, name='Muted')
            author = ctx.message.author

            mid = member.id
            gid = guild.id
            fid = mid + gid
            await db.execute(
                "DELETE FROM mutes WHERE mid = $1 and gid = $2 and fid = $3", aes.encrypt(mid), aes.encrypt(gid), aes.encrypt(fid)
            )
            self.bot.tp[fid] = 0

            if mutedRole not in member.roles:
                embed = discord.Embed(
                    description=f"That user isn't muted",
                    colour=discord.Colour.red(),
                )
                embed.set_author(name='Error | Generic', icon_url='https://i.imgur.com/qYyJ5cC.png')
                return await ctx.send(embed=embed)

            await member.remove_roles(mutedRole)

            embed = discord.Embed(colour=discord.Colour.green())
            embed.set_author(name='Unmute Log', icon_url='https://i.imgur.com/6fOJyWE.png')
            embed.add_field(name="Unmuted by: ", value=f"{author.mention}", inline=True)
            embed.add_field(name="User: ", value=f"{member.mention}", inline=True)
            embed.add_field(name="Reason: ", value=reason, inline=False)
            await ctx.send(embed=embed)
            try:
                embed = discord.Embed(colour=discord.Colour.green())
                embed.add_field(name="Guild: ", value=f"{guild.name}", inline=True)
                embed.add_field(name="Unmuted by: ", value=f"{author.mention}", inline=True)
                embed.add_field(name="Reason: ", value=reason, inline=False)
                embed.set_author(name='Unmute Log', icon_url='https://i.imgur.com/6fOJyWE.png')
                await member.send(embed=embed)
            except discord.HTTPException:
                await ctx.send("That user has DM's disabled, continuing Unmute.")
        await db.close()

    ####################################################################################################################
    ####################################################################################################################

    # Lock Command

    @commands.command(
        name="Lock",
        description=
        "Bot permissions: Manage channels, Manage roles\n"
        "User permissions: Manage channels"
    )
    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_channels=True, manage_roles=True)
    @commands.has_guild_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel = None):
        """Put a channel into lockdown"""
        channel = channel or ctx.channel

        if ctx.guild.default_role not in channel.overwrites:
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False)
            }
            await channel.edit(overwrites=overwrites)
            embed = discord.Embed(colour=discord.Colour.red())
            embed.set_author(name='Lock Log', icon_url='https://i.imgur.com/Jjmh5Ke.png')
            embed.add_field(name='Channel', value=channel.mention, inline=False)
            embed.add_field(name='Locked by', value=ctx.author.mention, inline=False)
            await ctx.send(embed=embed)
        elif channel.overwrites[ctx.guild.default_role].send_messages is True or channel.overwrites[
            ctx.guild.default_role].send_messages is None:
            overwrites = channel.overwrites[ctx.guild.default_role]
            overwrites.send_messages = False
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrites)
            embed = discord.Embed(colour=discord.Colour.red())
            embed.set_author(name='Lock Log', icon_url='https://i.imgur.com/Jjmh5Ke.png')
            embed.add_field(name='Channel', value=channel.mention, inline=False)
            embed.add_field(name='Locked by', value=ctx.author.mention, inline=False)
            await ctx.send(embed=embed)
        else:
            overwrites = channel.overwrites[ctx.guild.default_role]
            overwrites.send_messages = True
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrites)
            embed = discord.Embed(colour=discord.Colour.green())
            embed.set_author(name='Unlock Log', icon_url='https://i.imgur.com/iECBNK9.png')
            embed.add_field(name='Channel', value=channel.mention, inline=False)
            embed.add_field(name='Unlocked by', value=ctx.author.mention, inline=False)
            await ctx.send(embed=embed)

    # Unlock Command

    @commands.command(
        name="Unlock",
        description=
        "Bot permissions: Manage channels, Manage roles\n"
        "User permissions: Manage channels"
    )
    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_channels=True, manage_roles=True)
    @commands.has_guild_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        """Removes a channel from lockdown"""
        channel = channel or ctx.channel

        if ctx.guild.default_role not in channel.overwrites:
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(send_messages=True)
            }
            await channel.edit(overwrites=overwrites)
            embed = discord.Embed(colour=discord.Colour.green())
            embed.set_author(name='Unlock Log', icon_url='https://i.imgur.com/iECBNK9.png')
            embed.add_field(name='Channel', value=channel.mention, inline=False)
            embed.add_field(name='Unlocked by', value=ctx.author.mention, inline=False)
            await ctx.send(embed=embed)
        else:
            overwrites = channel.overwrites[ctx.guild.default_role]
            overwrites.send_messages = True
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrites)
            embed = discord.Embed(colour=discord.Colour.green())
            embed.set_author(name='Unlock Log', icon_url='https://i.imgur.com/iECBNK9.png')
            embed.add_field(name='Channel', value=channel.mention, inline=False)
            embed.add_field(name='Unlocked by', value=ctx.author.mention, inline=False)
            await ctx.send(embed=embed)

    ####################################################################################################################
    ####################################################################################################################

    @commands.command(
        name="Snipe",
        description=
        "Bot permissions: None\n"
        "User permissions: None"
    )
    async def _snipe(self, ctx):
        """RIP snipe - Used to pickup the last deleted message"""
        embed = discord.Embed(title='Snipe Command Deprecation',
        description="""Sorry, to comply with Discord's message intents all snipe commands will be removed. However, Logging will still continue to exist.
        Read more here:
        https://support-dev.discord.com/hc/en-us/articles/4404772028055-Message-Content-Access-Deprecation-for-Verified-Bots
        """,
        colour=discord.Colour.red())
        await ctx.send(embed=embed)
    @commands.command(
        name="EditSnipe", aliases=['Esnipe'],
        description=
        "Bot permissions: None\n"
        "User permissions: None"
    )
    async def _esnipe(self, ctx):
        """RIP esnipe - Used to pickup the last edited message"""
        embed = discord.Embed(title='Snipe Command Deprecation',
        description="""Sorry, to comply with Discord's message intents all snipe commands will be removed. However, Logging will still continue to exist.
        Read more here:
        https://support-dev.discord.com/hc/en-us/articles/4404772028055-Message-Content-Access-Deprecation-for-Verified-Bots
        """,
        colour=discord.Colour.red())
        await ctx.send(embed=embed)
def setup(bot):
    bot.add_cog(Mod(bot))
