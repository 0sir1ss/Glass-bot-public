import discord
from discord.ext import commands
from utils import argparser

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

class Parrot(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

#####################################################################################################################
#####################################################################################################################

# Embed Command

    @commands.command(
        name='Embed', 
        description=
        "Bot permissions: None\n"
        "User permissions: Manage messages", 
        usage='--title [title] --desc [desc] --footer [footer]'
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.commands.has_guild_permissions(manage_messages=True)
    async def embed_command(self, ctx, *, text: str=None):
        """Creates a custom embed"""
        
        parser = argparser.Arguments()
        parser.add_argument('-t', '--title', nargs='*', default=" ")
        parser.add_argument('-d', '--desc', nargs='*', default=" ")
        parser.add_argument('-f', '--footer', nargs='*', default=" ")

        args, valid_check = parser.parse_args(text)
        if not valid_check:
            return await ctx.send(args)

        title = ' '.join([a for a in args.title])
        desc = ' '.join([a for a in args.desc])
        footer = ' '.join([a for a in args.footer])

        if title == ' ' and desc == ' ' and footer == ' ':
            title = 'Args'
            desc = "Title: -t or --title\n" \
                   "Description: -d or --desc\n" \
                   "Footer: -f or --footer\n" \

        e = discord.Embed(
            title=title, 
            description=desc, 
            colour=self.bot.colour
        )
        e.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        e.set_footer(text=footer)
        await ctx.send(embed=e)

# Say Command

    @commands.command(
        name='Say', 
        description=
        "Bot permissions: None\n"
        "User permissions: Manage messages"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.commands.has_guild_permissions(manage_messages=True)
    async def say_command(self, ctx, *, text: commands.clean_content(fix_channel_mentions=True)=None):
        """Sends a message as the bot"""
        if not text:
            return await ctx.invoke(self.bot.get_command("help"), entity="Say")
        else:
            text = f"{ctx.author} Says:\n\n{text}"
            return await ctx.send(text.replace("@", "@\u200B"))

def setup(bot):
    bot.add_cog(Parrot(bot))
