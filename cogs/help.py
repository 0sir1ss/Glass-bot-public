# Requires pip install buttons

import discord
from discord.ext import commands
from discord.ext.buttons import Paginator as Pag
import asyncpg
from utils.encrypt import AESCipher

# These colour constants are taken from discord.js library
colours = {
  'DEFAULT': 0x000000,
  'WHITE': 0xFFFFFF,
  'AQUA': 0x1ABC9C,
  'GREEN': 0x2ECC71,
  'BLUE': 0x3498DB,
  'PURPLE': 0x9B59B6,
  'LUMINOUS_VIVID_PINK': 0xE91E63,
  'GOLD': 0xF1C40F,
  'ORANGE': 0xE67E22,
  'RED': 0xE74C3C,
  'GREY': 0x95A5A6,
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
  'GREYPLE': 0x99AAB5,
  'DARK_BUT_NOT_BLACK': 0x2C2F33,
  'NOT_QUITE_BLACK': 0x23272A
}

# Colours for embed
colour_list = [c for c in colours.values()]
# This does 2 things, it converts colours into a list and allows us to use the random module

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cmds_per_page = 1

    def get_command_signature(self, command: commands.Command):
        cmd_invoke = command.name

        full_invoke = command.qualified_name.replace(command.name, "")

        signature = f"{full_invoke}{cmd_invoke} {command.signature}"
        return signature

    async def setup_help_pag(self, ctx, entity, title):
        db = await asyncpg.connect(self.bot.db_conf, timeout=10)
        aes = AESCipher()
        result = await db.fetchrow("SELECT * FROM config WHERE gid = $1", aes.encrypt(ctx.guild.id))
        await db.close()
        if result:
            prefix = aes.decrypt(result[1])
        else:
            prefix = ';'

        pages = []

        if hasattr(entity, "all_commands"):
            filtered_commands = (
                list(set(entity.all_commands.values()))
            )
        else:
            filtered_commands = []
        filtered_commands.insert(0, entity)

        for i in range(0, len(filtered_commands), self.cmds_per_page):
            next_commands = filtered_commands[i : i + self.cmds_per_page]
            commands_entry = ""

            for cmd in next_commands:
                desc = cmd.short_doc
                perms = cmd.description
                aliases = cmd.aliases
                signature = self.get_command_signature(cmd)

                commands_entry += (
                    f"• **__{cmd.name}__**\n"
                    f"{desc}\n\n"

                    "**Aliases**\n"
                    "```ini\n"
                    f"{aliases}\n"
                    "```\n"

                    "**Usage - [optional] | <required>**\n"
                    "```less\n"
                    f"{prefix}{signature}\n"
                    "```\n"
                    
                    "**Permissions**\n"
                    "```\n"
                    f"{perms}"
                    "\n```\n"

                    if isinstance(entity, commands.Command)                 # What u see when ;help ban
                    
                    else f"• **__{cmd.name}__**\n{desc}\n\n"                # What u see on the main help
                )
            pages.append(commands_entry)

        await Pag(title=title, colour=self.bot.colour, entries=pages, length=1).start(ctx)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command(
        name="Help", aliases=["h", "commands", "cmds"], 
        usage='[command]', 
        description=
        "Bot permissions: [Add reactions, Manage messages]\n"
        "User permissions: None"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def help_command(self, ctx, *, entity=None):
        """The help command!"""
        if isinstance(ctx.channel, discord.DMChannel):
            embed = discord.Embed(
                title=f'Server: Unavailable',
                description=f'Prefix: `;`',
                colour=self.bot.colour
            )
            embed.add_field(
                name='Useful links', value=
                '[Commands](https://docs.glassbot.club/)\n'
                '[Invite](https://discord.com/oauth2/authorize?client_id=786640235245076480&permissions=810548350&scope=bot)\n'
                '[Vote](https://top.gg/bot/786640235245076480/vote)\n'
                '[Support Server](https://discord.gg/9R87syXpZN)\n'
                '[Website](https://glassbot.club/)', inline=False
            )
            embed.set_thumbnail(url='https://cdn.glassbot.club/glasscirc.png')
            embed.set_footer(text='Made by 0sir1s#0669')
            await ctx.send(embed=embed)
        else:
            if entity is None:
                db = await asyncpg.connect(self.bot.db_conf, timeout=10)
                aes = AESCipher()
                result = await db.fetchrow("SELECT * FROM config WHERE gid = $1", aes.encrypt(ctx.guild.id))
                await db.close()
                if result:
                    prefix = aes.decrypt(result[1])
                else:
                    prefix = ';'
                embed = discord.Embed(
                    title=f'Server: {ctx.guild.name}',
                    description=f'Prefix: `{prefix}`',
                    colour=self.bot.colour
                )
                embed.add_field(
                    name='Useful links', value=
                    '[Commands](https://docs.glassbot.club/)\n'
                    '[Invite](https://discord.com/oauth2/authorize?client_id=786640235245076480&permissions=810548350&scope=bot)\n'
                    '[Vote](https://top.gg/bot/786640235245076480/vote)\n'
                    '[Support Server](https://discord.gg/9R87syXpZN)\n'
                    '[Website](https://glassbot.club/)', inline=False
                )
                embed.set_thumbnail(url='https://cdn.glassbot.club/glasscirc.png')
                embed.set_footer(text='Made by 0sir1s#0669')
                await ctx.send(embed=embed)

            else:
                command = self.bot.get_command(entity)
                if command:
                    if command.qualified_name.startswith('Dev') and ctx.author.id != 457893040728571919:
                        await ctx.send("Command not found.")
                    else:
                        await self.setup_help_pag(ctx, command, command.name)

                else:
                    await ctx.send("Command not found.")

    @commands.Cog.listener()
    async def on_message(self, message):
        # Whenever the bot is tagged, respond with help cmd basically

        if message.content.startswith(f"<@!{self.bot.user.id}>") and len(message.content) == len(
                f"<@!{self.bot.user.id}>"
        ):
            if isinstance(message.channel, discord.DMChannel):
                embed = discord.Embed(
                    title=f'Server: Unavailable',
                    description=f'Prefix: `;`',
                    colour=self.bot.colour
                )
                embed.add_field(
                    name='Useful links', value=
                    '[Commands](https://docs.glassbot.club/)\n'
                    '[Invite](https://discord.com/oauth2/authorize?client_id=786640235245076480&permissions=810548350&scope=bot)\n'
                    '[Vote](https://top.gg/bot/786640235245076480/vote)\n'
                    '[Support Server](https://discord.gg/9R87syXpZN)\n'
                    '[Website](https://glassbot.club/)', inline=False
                )
                embed.set_thumbnail(url='https://cdn.glassbot.club/glasscirc.png')
                embed.set_footer(text='Made by 0sir1s#0669')
                await message.channel.send(embed=embed)
            else:
                try:
                    db = await asyncpg.connect(self.bot.db_conf, timeout=10)
                    aes = AESCipher()
                    result = await db.fetchrow("SELECT * FROM config WHERE gid = $1",aes.encrypt(message.guild.id))
                    await db.close()
                    if result:
                        prefix = aes.decrypt(result[1])
                    else:
                        prefix = ';'
                    embed = discord.Embed(
                        title=f'Server: {message.guild.name}',
                        description=f'Prefix: `{prefix}`',
                        colour=self.bot.colour
                    )
                    embed.add_field(
                        name='Useful links', value=
                        '[Commands](https://docs.glassbot.club/)\n'
                        '[Invite](https://discord.com/oauth2/authorize?client_id=786640235245076480&permissions=810548350&scope=bot)\n'
                        '[Vote](https://top.gg/bot/786640235245076480/vote)\n'
                        '[Support Server](https://discord.gg/9R87syXpZN)\n'
                        '[Website](https://glassbot.club/)', inline=False
                    )
                    embed.set_thumbnail(url='https://cdn.glassbot.club/glasscirc.png')
                    embed.set_footer(text='Made by 0sir1s#0669')
                    await message.channel.send(embed=embed)
                except:
                    prefix = ';'
                    embed = discord.Embed(
                        title=f'Server: {message.guild.name}',
                        description=f'Prefix: `{prefix}`',
                        colour=self.bot.colour
                    )
                    embed.add_field(
                        name='Useful links', value=
                        '[Commands](https://docs.glassbot.club/)\n'
                        '[Invite](https://discord.com/oauth2/authorize?client_id=786640235245076480&permissions=810548350&scope=bot)\n'
                        '[Vote](https://top.gg/bot/786640235245076480/vote)\n'
                        '[Support Server](https://discord.gg/9R87syXpZN)\n'
                        '[Website](https://glassbot.club/)', inline=False
                    )
                    embed.set_thumbnail(url='https://cdn.glassbot.club/glasscirc.png')
                    embed.set_footer(text='Made by 0sir1s#0669')
                    await message.channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Help(bot))
