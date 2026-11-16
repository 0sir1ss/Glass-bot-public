import asyncio
import random
import discord
from discord.ext import commands

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

class Suggest(commands.Cog):

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
        name='Suggest', 
        usage='<suggestion>', 
        description=
        "Bot permissions: Add reactions\n"
        "User permissions: None"
    )
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def _suggest(self, ctx, *, suggestion=None):
        """Suggest a feature for Glass every 5 minutes"""
        if suggestion is None:
            await ctx.send('Please add a suggestion, e.g. make the bot better')
            ctx.command.reset_cooldown(ctx)
        else:
            embed = discord.Embed(
                description=suggestion, 
                colour=self.bot.colour
                )
            
            m = await ctx.send("Is this suggestion valid?", embed=embed)
            await m.add_reaction("<:Tick:850334541918765076>")
            await m.add_reaction("<:Cross:850334541897269276>")

            try:
                reaction, member = await self.bot.wait_for(
                    "reaction_add",
                    timeout=60,
                    check=lambda reaction, user: user == ctx.author
                    and reaction.message.id == m.id
                )
            except asyncio.TimeoutError:
                await ctx.send("Confirmation Failure. Please try again.")
                ctx.command.reset_cooldown(ctx)
                return

            if str(reaction.emoji) not in ["<:Tick:850334541918765076>", "<:Cross:850334541897269276>"] or str(reaction.emoji) == "<:Cross:850334541897269276>":
                await ctx.send("Cancelling suggestion! You have not been given a 5 minute cooldown.")
                ctx.command.reset_cooldown(ctx)
                return
            else:
                embed.set_author(name=f'{ctx.author} - {ctx.author.id}', icon_url=ctx.author.avatar_url)
                embed.set_footer(text=ctx.guild or 'DMs')
                channel = self.bot.get_channel(814204622029848616)
                await ctx.send("Suggestion has been sent! You have been given a 5 minute cooldown.")
                await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Suggest(bot))
