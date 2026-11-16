import asyncio
import random
import re
import secrets
import discord
from aiohttp import request
from discord.ext import commands
import json

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
  'DARK_ORANGE': 0xA84300,
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

colour_list = [c for c in colours.values()]

class Fun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.sites = json.loads(open("config/sites.json", "r").read())

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    # 8ball

    @commands.command(
        name='8ball', usage='<question>', 
        description=
        "Bot permissions: None\n"
        "User permissions: None"
        )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _8ball(self, ctx, *, question=None):
        """Ask the magic 8ball a question"""
        if question is not None:
            responses = [
                'It is certain.',
                'It is decidedly so.',
                'Without a doubt.', 
                'Yes - definitely.', 
                'You may rely on it.', 
                'As I see it, yes.', 
                'Most likely.', 
                'Outlook good.', 
                'Yes.', 
                'Signs point to yes.', 
                'Reply hazy, try again.', 
                'Ask again later.', 
                'Better not tell you now.', 
                'Cannot predict now.', 
                'Concentrate and ask again.', 
                "Don't count on it.", 
                'My reply is no.', 
                'My sources say no.', 
                'Outlook not so good.', 
                'Very doubtful.'
            ]
            await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')
        else:
            await ctx.invoke(self.bot.get_command("help"), entity="8ball")

    # Coinflip

    @commands.command(
        name='Coinflip',
        aliases=['cf'], 
        description=
        "Bot permissions: None\n"
        "User permissions: None"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cf(self, ctx):
        """Flip a coin"""
        coinsides = ['Heads', 'Tails']
        await ctx.send(f"**{ctx.author.name}** flipped a coin and got **{random.choice(coinsides)}**!")

    # Rolling the dice

    @commands.command(
        name='Dice', 
        description=
        "Bot permissions: None\n"
        "User permissions: None"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def dice(self, ctx):
        """Roll a dice"""
        Dice_response = ['1', '2', '3', '4', '5', '6',]
        await ctx.send(f'You rolled {random.choice(Dice_response)}')

    # Reversing text

    @commands.command(
        name='Reverse', usage='<text>',
        description=
        "Bot permissions: None\n"
        "User permissions: None"
        )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _reverse(self, ctx, *, text: commands.clean_content(fix_channel_mentions=True, use_nicknames=True)=None):
        """!spoohw ,ffuts sesreveR"""
        if text is not None:
            t_rev = text[::-1].replace("@", "@\u200B").replace("&", "&\u200B")
            await ctx.send(f"🔁 {t_rev}")
        else:
            await ctx.invoke(self.bot.get_command("help"), entity="Reverse")

    # How hot

    @commands.command(
        name='Howhot', aliases=['Hot'], 
        description=
        "Bot permissions: None\n"
        "User permissions: None"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def hotcalc(self, ctx, *, user: discord.Member = None):
        """How hot is a discord user"""
        user = user or ctx.author

        hot = random.randint(1, 100)

        emoji = "💔"
        if hot > 25:
            emoji = "❤"
        if hot > 50:
            emoji = "💖"
        if hot > 75:
            emoji = "💞"

        await ctx.send(f"**{user.name}** is **{hot}%** hot {emoji}")

    # Slots

    @commands.command(
        name='Slots', 
        description=
        "Bot permissions: None\n"
        "User permissions: None"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def slot(self, ctx):
        """Roll the slot machine"""
        emojis = "🍎🍊🍐🍋🍉🍇🍓🍒"
        a1 = random.choice(emojis)
        b1 = random.choice(emojis)
        c1 = random.choice(emojis)
        a2 = random.choice(emojis)
        b2 = random.choice(emojis)
        c2 = random.choice(emojis)
        a3 = random.choice(emojis)
        b3 = random.choice(emojis)
        c3 = random.choice(emojis)


        embed1 = discord.Embed(title='Slots Machine', 
        description = f"**[ {random.choice(emojis)} {random.choice(emojis)} {random.choice(emojis)} ]\n[ {random.choice(emojis)} {random.choice(emojis)} {random.choice(emojis)} ]\n[ {random.choice(emojis)} {random.choice(emojis)} {random.choice(emojis)} ]\n**", 
        colour=self.bot.colour)

        embed2 = discord.Embed(title='Slots Machine', 
        description = f"**[ {random.choice(emojis)} {random.choice(emojis)} {random.choice(emojis)} ]\n[ {random.choice(emojis)} {random.choice(emojis)} {random.choice(emojis)} ]\n[ {random.choice(emojis)} {random.choice(emojis)} {random.choice(emojis)} ]\n**", 
        colour=self.bot.colour)

        embed3 = discord.Embed(title='Slots Machine', 
        description = f"**[ {random.choice(emojis)} {random.choice(emojis)} {random.choice(emojis)} ]\n[ {random.choice(emojis)} {random.choice(emojis)} {random.choice(emojis)} ]\n[ {random.choice(emojis)} {random.choice(emojis)} {random.choice(emojis)} ]\n**", 
        colour=self.bot.colour)

        embed = discord.Embed(title='Slots Machine', 
        description = f"**[ {a1} {b1} {c1} ]\n[ {a2} {b2} {c2} ]\n[ {a3} {b3} {c3} ]\n**", 
        colour=self.bot.colour)

        msg = await ctx.send(embed=embed1)
        await asyncio.sleep(0.5)
        await msg.edit(embed=embed2)
        await asyncio.sleep(0.5)
        await msg.edit(embed=embed3)
        await asyncio.sleep(0.5)
        await msg.edit(embed=embed)

        if a2 == b2 == c2:
            await ctx.send("All matching, you win 🎉")
        elif (a2 == b2) or (a2 == c2) or (b2 == c2):
            await ctx.send(f"2 in a row, you win 🎉")
        else:
            await ctx.send(f"No match, you lose 😭")


    @commands.command(
        name='Password', usage='[length]', 
        description=
        "Bot permissions: None\n"
        "User permissions: None"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def password(self, ctx, nbytes: int = 18):
        """Generates a random password string for you"""
        if nbytes not in range(3, 1401):
            return await ctx.send("I only accept numbers between 3-1400")
        if hasattr(ctx, 'guild') and ctx.guild is not None:
            await ctx.send(f"<a:loading:852956731885355080> Generating password in your DM's")
        try:
            embed = discord.Embed(
                title="Password", url='https://howsecureismypassword.net/', colour=self.bot.colour,
                description=f"```\n{secrets.token_urlsafe(nbytes)}\n```"
            )
            await ctx.author.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("DM's disabled, unable to securely send your password.")

    @commands.command(
        name='Colour', aliases=['color'],
        usage='<hexcode>',  
        description=
        "Bot permissions: None\n"
        "User permissions: None"
        )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def colour(self, ctx, colour: str=None):
        """View the colour HEX details"""
        if not colour:
            await ctx.send("Please enter in a hex code, e.g. #ab12fc")
        else:
            if colour[:1] == "#":
                colour = colour[1:]

            if not re.search(r'^(?:[0-9a-fA-F]{3}){1,2}$', colour):
                return await ctx.send("You're only allowed to enter HEX (0-9 & A-F)")

            url = f'https://api.alexflipnote.dev/colour/{colour}'
            headers = {
                "Authorization": self.bot.aa
            }
            async with request("GET", url, headers=headers) as response:
                if response.status == 200:
                    r = await response.json()

                    embed = discord.Embed(colour=r["int"], title=r["name"])
                    embed.set_thumbnail(url=r["image"])

                    embed.add_field(name="HEX", value=r['hex'], inline=True)
                    embed.add_field(name="RGB", value=r['rgb'], inline=True)
                    embed.add_field(name="Int", value=r['int'], inline=True)

                    await ctx.send(embed=embed)

                else:
                    embed = discord.Embed(
                        description=f"API returned a {response.status} response",
                        colour=discord.Colour.red(),
                    )
                    embed.set_author(name='Error | External', icon_url='https://i.imgur.com/qYyJ5cC.png')
                    await ctx.send(embed=embed)

    # Reddit Command

    @commands.command(
      name='Reddit', usage='<subreddit>', 
      description=
      "Bot permissions: None\n"
      "User permissions: None"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def reddit_api(self, ctx, search=None):
        """Pull something from a subreddit"""

        if search is not None:
            async with ctx.channel.typing():
                url = f"https://api.ksoft.si/images/rand-reddit/{search}"
                headers={
                    "Authorization": self.bot.KSoft
                }

                async with request("GET", url, headers=headers) as response:
                    if response.status == 200:
                        r = await response.json()

                        title = r['title']
                        img = r['image_url']
                        src = r['source']
                        nsfw = r['nsfw']

                    elif response.status == 404:
                        embed = discord.Embed(
                            description="Can't find any images for that subreddit!",
                            colour=discord.Colour.red(),
                        )
                        embed.set_author(name='Error | External', icon_url='https://i.imgur.com/qYyJ5cC.png')

                    else:
                        embed = discord.Embed(
                            description=f"API returned a {response.status} response",
                            colour=discord.Colour.red(),
                        )
                        embed.set_author(name='Error | External', icon_url='https://i.imgur.com/qYyJ5cC.png')
                        await ctx.send(embed=embed)

                embed = discord.Embed(
                    title=title,
                    url=src,
                    colour=self.bot.colour)
                embed.set_image(url=img)
                embed.set_footer(text='Powered by KSoft.Si', icon_url='https://cdn.ksoft.si/images/Logo128.png')

                if not nsfw:
                    await ctx.send(embed=embed)
                elif nsfw and not ctx.channel.is_nsfw():
                    embed = discord.Embed(
                        description="This channel is not NSFW. Please try again in an NSFW channel",
                        colour=discord.Colour.red(),
                    )
                    embed.set_author(name='Error | Permissions', icon_url='https://i.imgur.com/qYyJ5cC.png')
                    await ctx.send(embed=embed)
                elif nsfw and ctx.channel.is_nsfw():
                    await ctx.send(embed=embed)
            return
        else:
            await ctx.invoke(self.bot.get_command("help"), entity="Reddit")

    # Meme command

    @commands.command(
      name="Meme",
      aliases=['Memes'], 
      description=
      "Bot permissions: None\n"
      "User permissions: None"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def meme_api(self, ctx):
        """Get a dank meme"""
        async with ctx.channel.typing():
            url = "https://api.ksoft.si/images/random-meme"
            headers = {
                "Authorization": self.bot.KSoft
            }

            async with request("GET", url, headers=headers) as response:
                if response.status == 200:
                    r = await response.json()

                    title = r['title']
                    img = r['image_url']
                    src = r['source']

                else:
                    embed = discord.Embed(
                        description=f"API returned a {response.status} response",
                        colour=discord.Colour.red(),
                    )
                    embed.set_author(name='Error | External', icon_url='https://i.imgur.com/qYyJ5cC.png')
                    await ctx.send(embed=embed)
            embed = discord.Embed(
                title=title,
                url=src,
                colour=self.bot.colour)
            embed.set_image(url=img)
            embed.set_footer(text='Powered by KSoft.Si', icon_url='https://cdn.ksoft.si/images/Logo128.png')
            await ctx.send(embed=embed)
        return

    # Wikihow API command

    @commands.command(
      name="Wikihow", usage='<search>', 
      description=
      "Bot permissions: None\n"
      "User permissions: None"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def wikihow_api(self, ctx, *, search=None):
        """Greatest tips from wikihow"""
        if search is not None:
            url = "https://hargrimm-wikihow-v1.p.rapidapi.com/images"

            headers = {
            'x-rapidapi-key': "YOUR_TOKEN_HERE",
            'x-rapidapi-host': "hargrimm-wikihow-v1.p.rapidapi.com"
            }

            async with request("GET", url, headers=headers) as response:
                if response.status == 200:
                    w = await response.json()

                    url = w['1']

            embed = discord.Embed(
              title=f'Wikihow: {search}',
              colour=self.bot.colour
            )
            embed.set_image(url=url)
            await ctx.send(embed=embed)
        else:
            await ctx.invoke(self.bot.get_command("help"), entity="Wikihow")

    # Urban API command

    @commands.command(
        name="Urban", usage='<search>',
        description=
        "Bot permissions: None\n"
        "User permissions: None"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def Urban_api(self, ctx, *, search=None):
        """Get a term from urban dictionary"""
        if search is not None:
            search.replace(' ', '+')
            url = f"https://mashape-community-urban-dictionary.p.rapidapi.com/define?term={search}"

            headers = {
            'x-rapidapi-key': "YOUR_TOKEN_HERE",
            'x-rapidapi-host': "mashape-community-urban-dictionary.p.rapidapi.com"
            }

            async with request("GET", url, headers=headers) as response:
                if response.status == 200:
                    u = await response.json()


                    define = u['list'][0]['definition'].replace('[', '').replace(']', '')
                    link = u['list'][0]['permalink']
                    word = u['list'][0]['word']
                    example = u['list'][0]['example'].replace('[', '').replace(']', '')
                    full = f"**Meaning**\n{define}\n\n**Example**\n```\n{example}\n```"

            embed = discord.Embed(
                title=f'Search for {word}',
                description=full,
                url=link,
                colour=self.bot.colour
            )
            await ctx.send(embed=embed)

        else:
            await ctx.invoke(self.bot.get_command("help"), entity="Urban")

    @commands.command(
        name='WouldYouRather', aliases=['wyr'],
        description=
        "Bot permissions: None\n"
        "User permissions: None"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def wyr(self, ctx):
        """Would you rather do this or that?"""

        url = 'https://www.conversationstarters.com/wyrqlist.php'

        async with request("GET", url, headers={}) as response:
            if response.status == 200:
                a = await response.text()

                b = a.split('<div', 4)

                qa = b[1].replace('id=qa>', '').replace('</div>', '')
                qb = b[4].replace('id=qb>', '').replace('</div>', '')

                embed = discord.Embed(
                    title='Would you rather?',
                    description=f"1️⃣ | {qa}\n2️⃣ | {qb}",
                    color=self.bot.colour
                )
                await ctx.send(embed=embed)


    @commands.command(
        name='Joke',
        description=
        "Bot permissions: None\n"
        "User permissions: None"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def joke(self, ctx):
        """Here's a fun joke for you"""

        url = 'http://www.official-joke-api.appspot.com/random_joke'

        async with request("GET", url, headers={}) as response:
            if response.status == 200:
                j = await response.json()

                setup = j['setup']
                punchline = j['punchline']

                embed = discord.Embed(
                    title=setup,
                    description=f"||{punchline}||",
                    color=self.bot.colour
                )
                await ctx.send(embed=embed)

    @commands.command(
        name='Screenshot', aliases=['ss'],
        description=
        "Bot permissions: None\n"
        "User permissions: None"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def screenshot(self, ctx, *, url=None):
        """Take a screenshot of a website"""
        if url is None:
            return await ctx.send("Please provide a valid url e.g. <https://glassbot.club/>")
        url = url.strip("<>")
        if not url.startswith("https://"):
            return await ctx.send("Please provide a valid url e.g. <https://glassbot.club/>")
        else:
            urls = url.replace("https://", "").split("/")
            for site in self.bot.sites:
                if site in urls[0] and not ctx.channel.is_nsfw():
                    embed = discord.Embed(
                        description="This channel is not NSFW. Please try again in an NSFW channel",
                        colour=discord.Colour.red(),
                    )
                    embed.set_author(name='Error | Permissions', icon_url='https://i.imgur.com/qYyJ5cC.png')
                    return await ctx.send(embed=embed)
            ssurl = f"https://image.thum.io/get/{url}"
            embed = discord.Embed(title=url, colour=self.bot.colour)
            embed.set_image(url=ssurl)
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Fun(bot))

