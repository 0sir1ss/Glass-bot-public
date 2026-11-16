import discord
from discord.ext import commands

def perms(self, ctx, user):
    """
    Examples:
        p = perms(self, ctx, user)
        if p:
            await ctx.send(embed=p)
        else:
            await user.kick
    Args:
        self: Self.bot
        ctx: Context
        user: User being banned/kicked etc

    Returns:
        Error embed or passes to let code continue
    """
    if user.id not in [i.id for i in ctx.guild.members]:
        return
    elif ctx.author.id == user.id:
        """
        This check is for if the author is the user.
        """
        embed = discord.Embed(
            description="You can't perform that action on yourself",
            colour=discord.Colour.red(),
        )
        embed.set_author(name='Error | Generic', icon_url='https://i.imgur.com/qYyJ5cC.png')
        return embed

    elif user.id == self.bot.user.id:
        """
        This check is for if the bot is the user.
        """
        embed = discord.Embed(
            description="You can't perform that action on the bot",
            colour=discord.Colour.red(),
        )
        embed.set_author(name='Error | Generic', icon_url='https://i.imgur.com/qYyJ5cC.png')
        return embed

    elif ctx.guild.me.top_role.position <= user.top_role.position:
        """
        This check is for if the bot's role is less than the user's role.
        """
        embed = discord.Embed(
            description="That user has a higher role than me",
            colour=discord.Colour.red(),
        )
        embed.set_author(name='Error | Permissions', icon_url='https://i.imgur.com/qYyJ5cC.png')
        return embed

    elif user.guild_permissions.administrator:
        """
        This check is for if the user is admin.
        """
        embed = discord.Embed(
            description="That user has administator",
            colour=discord.Colour.red(),
        )
        embed.set_author(name='Error | Permissions', icon_url='https://i.imgur.com/qYyJ5cC.png')
        return embed

    elif ctx.author.top_role.position <= user.top_role.position:
        """
        This check is for if the authors's role is less than the user's role.
        """
        embed = discord.Embed(
            description="That user's roles are higher or equal to your own",
            colour=discord.Colour.red(),
        )
        embed.set_author(name='Error | Permissions', icon_url='https://i.imgur.com/qYyJ5cC.png')
        return embed

    else:
        pass


def clean_code(content):
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:])[:-3]
    else:
        return content