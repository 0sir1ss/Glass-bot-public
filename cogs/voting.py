import dbl
import discord
from discord.ext import commands, tasks
import requests

class Voting(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.token = 'YOUR_TOKEN_HERE' # set this to your DBL token
        self.dblpy = dbl.DBLClient(self.bot, self.token, autopost=True) # Autopost will post your guild count every 30 minutes
        self.dbggtoken = 'YOUR_TOKEN_HERE'
        self.dbltoken = 'YOUR_TOKEN_HERE'
        self.votecount = self.votecounttask.start()

    def cog_unload(self):
        self.votecount.cancel()

    @tasks.loop(minutes=30)
    async def votecounttask(self):
        url = 'https://discord.bots.gg/api/v1/bots/786640235245076480/stats'
        headers={
            "Authorization": self.dbggtoken 
        }
        data={
            "guildCount": len(self.bot.guilds)
        }
        requests.post(url=url, headers=headers, data=data)
        url = 'https://discordbotlist.com/api/v1/bots/786640235245076480/stats'
        headers={
            "Authorization": self.dbltoken
        }
        data={
            "guilds": len(self.bot.guilds), 
            "users": len(set(self.bot.get_all_members()))
        }
        requests.post(url=url, headers=headers, data=data)

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    # Vote Command

    @commands.command(
        name='Vote', 
        description=
        "Bot permissions: None\n"
        "User permissions: None"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def Upvote(self, ctx):
        """Vote for me!"""
        embed = discord.Embed(
            title='Vote for me!', colour=self.bot.colour, 
            description="""
            **__[top.gg](https://top.gg/bot/786640235245076480/vote)__**
            **__[discordbotlist.com](https://discordbotlist.com/bots/glass/upvote)__**
            """
        )
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Voting(bot))