import discord
from discord.ext import commands
import asyncpg
from utils.encrypt import AESCipher

class Errors(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Events

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")


    ####################################################################################################################
    # Handle Errors
    ####################################################################################################################


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        aes = AESCipher()
        guild = aes.encrypt(ctx.guild.id)
        db = await asyncpg.connect(self.bot.db_conf, timeout=10)
        result = await db.fetchrow("SELECT * FROM config WHERE gid = $1", guild)
        if result:
            prefix = aes.decrypt(result[1])
        else:
            prefix = ';'
        await db.close()
        try:
            # Handles Errors So Bot Doesnt Crash
            if isinstance(error, commands.MissingRequiredArgument):
                # generic error handler for commands entered wrong
                try:
                    embed = discord.Embed(
                        description=f"Please refer to {prefix}help <command> and try again.",
                        colour=discord.Colour.red(),
                    )
                    embed.set_author(name='Error | Arguments', icon_url='https://i.imgur.com/qYyJ5cC.png')
                    return await ctx.send(embed=embed)
                except:
                    return await ctx.send(f"Required Arguments are missing.\n"
                                          f"Please refer to {prefix}help <command> and try again.\n"
                                          f"As this error is not in an embed, please enable the `embed links` permission, "
                                          f"or else I cannot continue.")

            if isinstance(error, commands.MissingPermissions):
                # generic error handler for commands from guilds without permissions
                perms = str(error.missing_perms)[1:][:-1].title().replace("_", " ").replace("'", "")
                try:
                    embed = discord.Embed(
                        description=f"You are missing the following permissions: \n"
                                    f"`{perms}`",
                        colour=discord.Colour.red(),
                    )
                    embed.set_author(name='Error | Permissions', icon_url='https://i.imgur.com/qYyJ5cC.png')
                    return await ctx.send(embed=embed)
                except:
                    return await ctx.send(f"You are missing the following permissions:\n"
                                          f"`{perms}`\n"
                                          f"As this error is not in an embed, please enable the `embed links` permission, "
                                          f"or else I cannot continue.")

            if isinstance(error, commands.MessageNotFound):
                # generic error handler for commands from guilds without permissions
                return error
            if isinstance(error, commands.BotMissingPermissions):
                # generic error handler for commands from guilds without permissions
                perms = str(error.missing_perms)[1:][:-1].title().replace("_", " ").replace("'", "")
                try:
                    embed = discord.Embed(
                        description=f"I am missing the following permissions: \n"
                                    f"`{perms}`",
                        colour=discord.Colour.red(),
                    )
                    embed.set_author(name='Error | Permissions', icon_url='https://i.imgur.com/qYyJ5cC.png')
                    return await ctx.send(embed=embed)
                except:
                    return await ctx.send(f"I am missing the following permissions:\n"
                                          f"`{perms}`\n"
                                          f"As this error is not in an embed, please enable the `embed links` permission, "
                                          f"or else I cannot continue.")
            if isinstance(error, commands.CommandOnCooldown):
                # Command is on cooldown
                try:
                    embed = discord.Embed(
                        description=f"You can use this command in {round(error.retry_after, 2)}s",
                        colour=discord.Colour.red(),
                    )
                    embed.set_author(name='Error | Cooldown', icon_url='https://i.imgur.com/qYyJ5cC.png')
                    return await ctx.send(embed=embed)
                except:
                    return await ctx.send(f"This command is on cooldown.\n"
                                          f"You can use this command in {round(error.retry_after, 2)}s\n"
                                          f"As this error is not in an embed, please enable the `embed links` permission, "
                                          f"or else I cannot continue.")
            if isinstance(error, commands.CheckAnyFailure):
                for error in error.errors:
                    perms = str(error.missing_perms)[1:][:-1].title().replace("_", " ").replace("'", "")
                    try:
                        embed = discord.Embed(
                            description=f"You are missing the following permissions: \n"
                                        f"`{perms}`",
                            colour=discord.Colour.red(),
                        )
                        embed.set_author(name='Error | Permissions', icon_url='https://i.imgur.com/qYyJ5cC.png')
                        return await ctx.send(embed=embed)
                    except:
                        return await ctx.send(f"You are missing the following permissions:\n"
                                            f"`{perms}`\n"
                                            f"As this error is not in an embed, please enable the `embed links` permission, "
                                            f"or else I cannot continue.")

        except:
            pass

def setup(bot):
    bot.add_cog(Errors(bot))
