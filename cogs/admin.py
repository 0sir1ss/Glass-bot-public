import contextlib
import io
import os
import sys
import textwrap
from traceback import format_exception
import importlib
import inspect
import asyncpg
import discord
from discord import Embed
from discord.ext import commands
from discord.ext.buttons import Paginator as Pag
from utils.util import clean_code
from typing import Union
from utils.encrypt import AESCipher

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
  'BLURPLE': 0x7289DA
}
# Colours for embed

colour_list = [c for c in colours.values()]
# This does 2 things, it converts colours into a list and allows us to use the random module

class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Events

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.group(
        name='Dev', invoke_without_command=True,
        description=
        "Bot permissions: None\n"
        "User permissions: Owner",
        case_insensitive=True,
        usage='<subcommand>',
        hidden=True
        )
    @commands.is_owner()
    async def dev(self, ctx):
        """Dev Commands"""
        await ctx.invoke(self.bot.get_command("help"), entity="Dev")

    @dev.command(
        description=
        "Bot permissions: None\n"
        "User permissions: Owner",
        hidden=True
    )
    @commands.is_owner()
    async def loadall(self, ctx):
        """Load all of the cogs"""
        succ = []
        unsucc = []

        for file in os.listdir("cogs"):
            if file.endswith(".py"):
                name = file[:-3]
                if name == 'admin':
                    pass
                else:
                    try:
                        self.bot.load_extension(f"cogs.{name}")
                        succ.append(f"Loaded extension **{name}.py**\n")
                    except:
                        unsucc.append(f"Unable to load extension **{name}.py**\n")

        em = discord.Embed(
            title='Loadall',
            description=f"{' '.join([s for s in succ])}\n\n{' '.join([u for u in unsucc])}",
            colour=self.bot.colour
        )
        await ctx.send(embed=em)

    @dev.command(
        description=
        "Bot permissions: None\n"
        "User permissions: Owner",
        hidden=True
    )
    @commands.is_owner()
    async def unloadall(self, ctx):
        """Unload all of the cogs"""
        succ = []
        unsucc = []

        for file in os.listdir("cogs"):
            if file.endswith(".py"):
                name = file[:-3]
                if name == 'admin':
                    pass
                else:
                    try:
                        self.bot.unload_extension(f"cogs.{name}")
                        succ.append(f"Unloaded extension **{name}.py**\n")
                    except:
                        unsucc.append(f"Unable to load extension **{name}.py**\n")

        em = discord.Embed(
            title='Unloadall',
            description=f"{' '.join([s for s in succ])}\n\n{' '.join([u for u in unsucc])}",
            colour=self.bot.colour
        )
        await ctx.send(embed=em)


    @dev.command(
        description=
        "Bot permissions: None\n"
        "User permissions: Owner",
        hidden=True
    )
    @commands.is_owner()
    async def reloadall(self, ctx):
        """Reload all of the cogs"""
        succ = []
        unsucc = []

        for file in os.listdir("cogs"):
            if file.endswith(".py"):
                name = file[:-3]

                try:
                    self.bot.reload_extension(f"cogs.{name}")
                    succ.append(f"Reloaded extension **{name}.py**\n")
                except:
                    unsucc.append(f"Unable to load extension **{name}.py**\n")

        em = discord.Embed(
            title='Reloadall',
            description=f"{' '.join([s for s in succ])}\n\n{' '.join([u for u in unsucc])}",
            colour=self.bot.colour
        )
        await ctx.send(embed=em)

    @dev.command(
        name="eval", aliases=["exec"],
        description=
        "Bot permissions: None\n"
        "User permissions: Owner",
        hidden=True
    )
    @commands.is_owner()
    async def _eval(self, ctx, *, code: str):
        """Evaluate python code"""
        if code.endswith("-s"):
            silent = True
            code = code[:-3]
        else:
            silent = False
        code = clean_code(code)

        local_variables = {
            "discord": discord,
            "commands": commands,
            "bot": self.bot,
            "self": self,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message,
            "embed": Embed,
            "Embed": Embed
        }

        stdout = io.StringIO()

        try:
            with contextlib.redirect_stdout(stdout):
                exec(
                    f"async def func():\n{textwrap.indent(code, '    ')}", local_variables,
                )

                obj = await local_variables["func"]()
                result = f"{stdout.getvalue()}\n>>> {obj if obj != None else 'No return value'}\n"
        except Exception as e:
            result = "".join(format_exception(e, e, e.__traceback__)).replace("""
  File "/home/osiris/Glass/cogs/admin.py", line 207, in _eval
    obj = await local_variables["func"]()
""", "\n") # Will need to edit this to your own cmd line to remove it and have a clean eval output
        if silent:
            return
        else:
            pager = Pag(
                timeout=100,
                entries=[result[i: i + 2000] for i in range(0, len(result), 2000)],
                length=1,
                prefix="```py\n",
                suffix="```",
                colour=self.bot.colour
            )

            await pager.start(ctx)

    @dev.command(
        name="ignore",
        description=
        "Bot permissions: None\n"
        "User permissions: Owner",
        hidden=True
    )
    @commands.is_owner()
    async def ignore(self, ctx, user: Union[discord.Member, discord.User]):
        """Stop a user from using the bot"""
        if ctx.message.author.id == user.id:
            await ctx.send("Hey, you cannot blacklist yourself!")
            return

        self.bot.blacklisted_users.append(user.id)
        await ctx.send(f"Ignoring {user}")

    @dev.command(
        name="unignore",
        description=
        "Bot permissions: None\n"
        "User permissions: Owner",
        hidden=True
    )
    @commands.is_owner()
    async def unignore(self, ctx, user: Union[discord.Member, discord.User]):
        """Allow a user to use the bot again"""
        self.bot.blacklisted_users.remove(user.id)
        await ctx.send(f"Stopped ignoring {user}")

    @dev.command(
        name="leave",
        description=
        "Bot permissions: None\n"
        "User permissions: Owner",
        hidden=True
    )
    @commands.is_owner()
    async def leave(self, ctx, guild: int):
        """Make the bot leave a server"""
        guild = self.bot.get_guild(guild)
        await ctx.send(f"Leaving {guild.name}")
        await guild.leave()

    # Servers command for owner

    @dev.command(
        description=
        "Bot permissions: None\n"
        "User permissions: Owner",
        hidden=True
    )
    @commands.is_owner()
    async def servers(self, ctx):
        """Full list of servers with member count and bot count"""
        page = self.bot.guilds
        page = sorted(page, reverse=True, key=lambda x: x.me.joined_at)

        pages = []
        for x in page:
            joined = x.me.joined_at.strftime("%I:%M %p %d %B %Y")
            name = x.name
            _id = x.id
            owner = x.owner
            trueMembcount = len([m for m in x.members if not m.bot])
            trueBotcount = len([m for m in x.members if m.bot])
            full = f'{name} - {_id}\nOwned by {owner}\n{trueMembcount} members - {trueBotcount} bots\nJoined: {joined}\n'
            pages.append(full)


        await Pag(
            title=f'I am in {len(self.bot.guilds)} guilds',
            colour=self.bot.colour,
            entries=pages, length=5, prefix='```', suffix='```'
        ).start(ctx)

    @dev.command(
        name='restart', aliases=['reboot'],
        description=
        "Bot permissions: None\n"
        "User permissions: Owner",
        hidden=True
    )
    @commands.is_owner()
    async def restart(self, ctx):
        """Restart the bot"""
        await ctx.send("Restarting now!")
        sys.exit(1)

    @dev.command(
        name='reloadutils',
        description=
        "Bot permissions: None\n"
        "User permissions: Owner",
        hidden=True
    )
    @commands.is_owner()
    async def reloadutils(self, ctx, name: str):
        """ Reloads a utils module. """
        name_maker = f"utils/{name}.py"
        try:
            module_name = importlib.import_module(f"utils.{name}")
            importlib.reload(module_name)
        except ModuleNotFoundError:
            return await ctx.send(f"Couldn't find module named **{name_maker}**")
        except Exception as e:
            return await ctx.send(f"Module **{name_maker}** returned error:\n{e}")
        await ctx.send(f"Reloaded module **{name_maker}**")

    @dev.command(
        name='Update',
        description=
        "Bot permissions: None\n"
        "User permissions: Owner",
        hidden=True
    )
    @commands.is_owner()
    async def update(self, ctx):
        """Updates the bot using git"""
        res = os.popen("""git stash
                       git pull origin master""")
        result = res.read()
        res.close()

        embed = discord.Embed(
            description=f"```sh\n{result}\n```", colour=self.bot.colour
        )
        m = await ctx.send(embed=embed)
        await m.add_reaction("<:Tick:850334541918765076>")
        await m.add_reaction("<:Cross:850334541897269276>")
        await m.add_reaction("<:retry:850337515189960734>")

        reaction, member = await self.bot.wait_for(
            "reaction_add",
            timeout=60,
            check=lambda reaction, user: user == ctx.author and reaction.message.id == m.id
        )
        if str(reaction.emoji) not in ["<:Tick:850334541918765076>", "<:Cross:850334541897269276>", "<:retry:850337515189960734>"] or str(reaction.emoji) == "<:Cross:850334541897269276>":
            return await ctx.send("Not restarting!")
        elif str(reaction.emoji) == "<:Tick:850334541918765076>":
            await ctx.invoke(self.bot.get_command("dev restart"))
        elif str(reaction.emoji) == "<:retry:850337515189960734>":
            await ctx.invoke(self.bot.get_command("dev reloadall"))

    @dev.command(
        name='Shell', aliases=['SH'],
        description=
        "Bot permissions: None\n"
        "User permissions: Owner",
        hidden=True
    )
    @commands.is_owner()
    async def shell(self, ctx, *, argument: str):
        argument = clean_code(argument)

        res = os.popen(argument)
        result = res.read()
        res.close()

        pager = Pag(
            timeout=100,
            entries=[result[i: i + 2000] for i in range(0, len(result), 2000)],
            length=1,
            prefix=f"```sh\n$ {argument}\n\n",
            suffix=f"\n```",
            colour=self.bot.colour
        )

        await pager.start(ctx)

    @dev.command(
        name='Source', aliases=['src'],
        description=
        "Bot permissions: None\n"
        "User permissions: Owner",
        hidden=True
    )
    @commands.is_owner()
    async def source(self, ctx, *, command_name: str):
        command = self.bot.get_command(command_name)
        if not command:
            return await ctx.send(f"Command `{command_name}` not found.")
        try:
            source_lines, _ = inspect.getsourcelines(command.callback)
        except (TypeError, OSError):
            return await ctx.send(f"Unable to retrieve the source for `{command.name}`.")
        source_text = ''.join(source_lines)
        file = discord.File(filename=f"{command.name}.py", fp=io.BytesIO(source_text.encode('utf-8')))
        await ctx.send(file=file)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        aes = AESCipher()
        guild = aes.encrypt(guild.id)
        db = await asyncpg.connect(self.bot.db_conf, timeout=10)
        await db.execute("DELETE FROM blacklist WHERE gid = $1", guild)
        await db.execute("DELETE FROM config WHERE gid = $1", guild)
        await db.execute("DELETE FROM invites WHERE gid = $1", guild)
        await db.execute("DELETE FROM logging WHERE gid = $1", guild)
        await db.execute("DELETE FROM mutes WHERE gid = $1", guild)
        await db.execute("DELETE FROM spamfilter WHERE gid = $1", guild)
        await db.execute("DELETE FROM urls WHERE gid = $1", guild)
        await db.execute("DELETE FROM warning WHERE gid = $1", guild)
        await db.execute("DELETE FROM xp WHERE guild_id = $1", guild)
        await db.execute("DELETE FROM xpalerts WHERE gid = $1", guild)
        await db.close()

def setup(bot):
    bot.add_cog(Admin(bot))
