import os
import platform
import random
import dateutil.parser
import discord
import omdb
import psutil
from aiohttp import request
from discord.ext import commands
from discord.ext.buttons import Paginator as Pag
import datetime
import asyncio
import textwrap

def to_emoji(c):
    base = 0x1f1e6
    return chr(base + c)

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

class Info(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process(os.getpid())

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

#####################################################################################################################
#####################################################################################################################

    @commands.command(
        name="Channelinfo",
        aliases=['cInfo', 'ci'], 
        description=
        "Bot permissions: None\n"
        "User permissions: None"
    )
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def channel_stats(self, ctx):
        """Find the channel info!"""
        channel = ctx.channel
        embed = discord.Embed(
            title=f"Information about #{channel.name}",
            description=f"Category: {channel.category.name if channel.category else 'This channel is not in a category'}",
            colour=self.bot.colour
        )
        embed.add_field(name="Slowmode:", value=channel.slowmode_delay, inline=False)
        embed.add_field(name="Topic:", value=f"{channel.topic if channel.topic else 'No topic.'}", inline=False)

        embed.add_field(name="Permissions Synced?", value=channel.permissions_synced, inline=True)
        embed.add_field(name="NSFW?", value=channel.is_nsfw(), inline=True)
        embed.add_field(name="News?", value=channel.is_news(), inline=True)

        embed.add_field(name="Created:", value=channel.created_at.strftime("%I:%M %p %d %B %Y"), inline=True)
        embed.add_field(name="Position:", value=channel.position, inline=True)

        embed.set_footer(text=f'ID: {channel.id}')

        await ctx.send(embed=embed)

    # UserInfo Command

    @commands.command(
        name='Userinfo',
        aliases=['uInfo', 'ui'], 
        description=
        "Bot permissions: None\n"
        "User permissions: None"
    )
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def UserInfo(self, ctx, member: discord.Member=None):
        """Find a user's info!"""
        member = member or ctx.author

        if member.raw_status == "online":
            status = '🟢 Online'
        if member.raw_status == "idle":
            status = '🟠 Idle'
        if member.raw_status == "dnd":
            status = '🔴 Do not disturb'
        if member.raw_status == "offline":
            status = '⚪ Offline'

        activity = member.activity

        if activity is not None:
            embed = discord.Embed(
                colour=self.bot.colour, timestamp=ctx.message.created_at,
                description=f'{status}\nStatus: {activity.name}'
            )
        else:
            embed = discord.Embed(
                colour=self.bot.colour, timestamp=ctx.message.created_at,
                description=f'{status}\nStatus: Not doing anything'
            )

        embed.set_author(name=f'{member.name}#{member.discriminator}')
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f"ID: {member.id}")

        embed.add_field(name='Created: ', value=member.created_at.strftime("%I:%M %p %d %B %Y"))
        embed.add_field(name='Joined: ', value=member.joined_at.strftime("%I:%M %p %d %B %Y"))

        roles = sorted([role for role in member.roles[1:]], reverse=True)
        mroles = ' '.join([role.mention for role in roles])
        embed.add_field(name=f'Roles: [{len(roles) or None}]', value=mroles or None, inline=False)

        p = []
        for i in member.guild_permissions:
            if i[1] is False:
                pass
            else:
                i = i[0].replace("_", " ")
                p.append(i)

        p = str(sorted(p))[1:][:-1].title().replace("'", "")

        embed.add_field(name=f'Permissions: ', value=p or None, inline=False)

        await ctx.send(embed=embed)

    # Avatar Command

    @commands.command(
        name='Avatar', aliases=['Av'], 
        description=
        "Bot permissions: None\n"
        "User permissions: None"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _av(self, ctx, member: discord.Member=None):
        """Get a user's avatar"""
        member = member or ctx.author
        embed = discord.Embed(colour=self.bot.colour, timestamp=ctx.message.created_at)

        embed.set_author(name=f"{member}'s avatar")
        embed.set_image(url=member.avatar_url)
        embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

#####################################################################################################################
#####################################################################################################################

    # ServerInfo Command

    @commands.command(
        name='Serverinfo', 
        aliases=['sInfo', 'si'], 
        description=
        "Bot permissions: None\n"
        "User permissions: None"
    )
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ServerInfo(self, ctx):
        """Find the server's info!"""
        guild = ctx.guild
        trueMembcount = len([m for m in guild.members if not m.bot])
        trueBotcount = len([m for m in guild.members if m.bot])
        onlinemem = 0
        idlemem = 0
        dndmem = 0
        offmem = 0
        for x in ctx.guild.members:
            if x.raw_status == "online":
                onlinemem += 1
            if x.raw_status == "idle":
                idlemem += 1
            if x.raw_status == "dnd":
                dndmem += 1
            if x.raw_status == "offline":
                offmem += 1
        if str(ctx.guild.verification_level) == "none":
            verify = "No verification level."
        if str(ctx.guild.verification_level) == "low":
            verify = "Members must have a verified email."
        if str(ctx.guild.verification_level) == "medium":
            verify = "Members must have a verified email, and be registered on Discord for more than five minutes."
        if str(ctx.guild.verification_level) == "high":
            verify = "Members must have a verified email, be registered on Discord for more than five minutes, and be a member of the guild for more than ten minutes."
        if str(ctx.guild.verification_level) == "highest":
            verify = "Members must have a verified email, be registered on Discord for more than five minutes, be a member of the guild for more than ten minutes, and have a verified phone on their Discord Account."
        totalChannelCount = len(guild.text_channels) + len(guild.voice_channels)
        desc =f"""
        {verify}
        {guild.description or 'No guild description.'}
        Created {guild.created_at.strftime('%I:%M %p %d %B %Y')}
        """
        embed = discord.Embed(
            title=f'{guild.name} - {guild.id}',
            description=desc,
            timestamp=ctx.message.created_at,
            colour=self.bot.colour
        )
        embed.set_thumbnail(url=guild.icon_url)
        
        embed.add_field(name='Total Channel Count:', value=totalChannelCount, inline=True)
        embed.add_field(name='Text Channel Count:', value=len(guild.text_channels), inline=True)
        embed.add_field(name='Voice Channel Count:', value=len(guild.voice_channels), inline=True)

        embed.add_field(name='Total Count:', value=guild.member_count, inline=True)
        embed.add_field(name='User Count:', value=trueMembcount, inline=True)
        embed.add_field(name='Bot Count:', value=trueBotcount, inline=True)
        embed.add_field(name="Member Presences: ", value=f"**🟢 Online :**  {onlinemem}\n"
                                                       f"**🟠 Idle :**  {idlemem}\n"
                                                       f"**🔴 Dnd :**  {dndmem}\n"
                                                       f"**⚪ Offline :**  {offmem}\n", inline=False)

        roles = sorted([role for role in guild.roles[1:]], reverse=True)
        mroles = ' '.join([role.mention for role in roles])
        if len(mroles) < 1000:
            embed.add_field(name=f'Roles: [{len(roles) or None}]', value=mroles, inline=False)
        else:
            embed.add_field(name=f'Roles: [{len(roles) or None}]', value='Too many roles to display.', inline=False)

        embed.set_footer(text=f'Owner: {guild.owner}', icon_url=guild.owner.avatar_url)
        await ctx.send(embed=embed)


    # Membercount Command

    @commands.command(
        name='Membercount', aliases=['Members'],
        description=
        "Bot permissions: None\n"
        "User permissions: None"
    )
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def avatar(self, ctx):
        """Get the membercount with presences"""
        guild = ctx.guild
        trueMembcount = len([m for m in guild.members if not m.bot])
        trueBotcount = len([m for m in guild.members if m.bot])
        onlinemem = 0
        idlemem = 0
        dndmem = 0
        offmem = 0
        for x in guild.members:
            if x.raw_status == "online":
                onlinemem += 1
            if x.raw_status == "idle":
                idlemem += 1
            if x.raw_status == "dnd":
                dndmem += 1
            if x.raw_status == "offline":
                offmem += 1

        embed = discord.Embed(colour=discord.Color.blue(), timestamp=ctx.message.created_at)
        embed.set_author(name=f"Membercount for {guild.name}", icon_url=guild.icon_url)
        embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)

        embed.add_field(name='**Total Count: **', value=guild.member_count, inline=True)
        embed.add_field(name='**User Count: **', value=trueMembcount, inline=True)
        embed.add_field(name='**Bot Count: **', value=trueBotcount, inline=True)

        embed.add_field(name="**Member Presences: **", value=f"**🟢 Online :**  {onlinemem}\n"
                                                       f"**🟠 Idle :**  {idlemem}\n"
                                                       f"**🔴 Dnd :**  {dndmem}\n"
                                                       f"**⚪ Offline :**  {offmem}\n", inline=False)

        await ctx.send(embed=embed)



#####################################################################################################################
#####################################################################################################################

    # Bot Stats Command

    @commands.command(
        name='Stats',
        aliases=['BotInfo'], 
        description=
        "Bot permissions: None\n"
        "User permissions: None"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def Stats(self, ctx):
        """Display bot stats"""
        serverCount = len(self.bot.guilds)
        memberCount = len(set(self.bot.get_all_members()))
        commandCount = len([c for c in self.bot.walk_commands() if not c.hidden])

        pythonVersion = platform.python_version()
        dpyVersion = discord.__version__
        ramUsage = self.process.memory_full_info().rss / 1024**2
        start_time = self.process.create_time()
        current_time = datetime.datetime.now().timestamp()
        difference = int(round(current_time - start_time))
        uptime = str(datetime.timedelta(seconds=difference))
        
        embed = discord.Embed(title='Stats', colour=self.bot.colour)
        embed.add_field(
            name="Bot Info", 
            value=f"""
```
Servers: {serverCount}
Members: {memberCount}
Commands: {commandCount}
Uptime: {uptime}
```
            """
        )
        embed.add_field(
            name="Library", 
            value=f"""
```
Python: {pythonVersion}
Discord.py: {dpyVersion}
```
            """
        )
        embed.add_field(
            name="System", 
            value=f"""
```
RAM: {ramUsage:.2f}MB
CPU: {psutil.cpu_percent()}%
Cores: {psutil.cpu_count()}
```
            """
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
        await ctx.send(embed=embed)

    # Invite Command

    @commands.command(
        name='Invite', 
        description=
        "Bot permissions: None\n"
        "User permissions: None"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _invite(self, ctx):
        """Invite me to your server"""
        await ctx.send("https://invite.glassbot.club/")


    # Website Command

    @commands.command(
        name='Website', 
        description=
        "Bot permissions: None\n"
        "User permissions: None"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def website(self, ctx):
        """Sends the bot website"""
        await ctx.send("https://glassbot.club/")

#####################################################################################################################
#####################################################################################################################

    # On guild join
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        try:
            embed = discord.Embed(
                title='Glass',
                colour=self.bot.colour,
                description=
                f"""
                **__Setup__**
                My default prefix is `;` but can be configured using the `prefix` command.
                To find your prefix do <@786640235245076480> or <@786640235245076480> <command>.
                Glass has automod features which can be setup via the `automod` command.
                To setup logging use the command `logging`
                **__Role hierachy__**
                Place the `Glass` role above the members.
                If you haven't already, create a role named `Muted` and place this above members but below the `Glass` role.
                If you don't, Glass will create a role named `Muted` and place it beneath it's highest role.
                """
            )
            embed.set_thumbnail(url='https://cdn.glassbot.club/glasscirc.png')
            embed.set_footer(text='glassbot.club')
            channel = [c for c in guild.text_channels if ('general' in c.name) or ('chat' in c.name) or ('commands' in c.name)]
            if channel:
                channel = channel[0]
            else:
                channel = guild.text_channels[0]
            await channel.send(embed=embed)
        except:
            pass

    # Weather Command

    @commands.command(
      name='Weather', usage='<area>', 
      description=
      "Bot permissions: None\n"
      "User permissions: None"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def weather(self, ctx, *, search=None):
        """Find out the weather in your area"""
        if search is not None:
            search.replace(' ', '+')
            url = f'http://api.weatherapi.com/v1/current.json?key=YOUR_TOKEN_HERE&q={search}&aqi=no'
            async with request("GET", url, headers={}) as response:
                if response.status == 200:
                    j = await response.json()

                    name = j['location']['name']
                    country = j['location']['country']
                    localtime = j['location']['localtime']
                    lat = j['location']['lat']
                    lon = j['location']['lon']
                    icon = j['current']['condition']['icon']
                    desc = j['current']['condition']['text']
                    temp_c = j['current']['temp_c']
                    temp_f = j['current']['temp_f']
                    humidity = j['current']['humidity']
                    ftemp_c = j['current']['feelslike_c']
                    ftemp_f = j['current']['feelslike_f']
                    cloud = j['current']['cloud']
                    pressure = j['current']['pressure_in']
                    precipitation = j['current']['precip_mm']

            embed = discord.Embed(
                title=name, description=country,
                colour=self.bot.colour)
            embed.set_footer(text=f'Local time: {localtime}')
            embed.set_thumbnail(url=f'https:{icon}')
            embed.set_author(name=f'Coords: {lat} lat, {lon} lon')
            embed.add_field(name='Description', value=f'{desc}', inline=False)
            embed.add_field(name='Temperature', value=f'{temp_c}°C\n{temp_f}°F', inline=True)
            embed.add_field(name='Feels Like', value=f'{ftemp_c}°C\n{ftemp_f}°F', inline=True)
            embed.add_field(name='Humidity', value=f'{humidity}% Humidity', inline=True)
            embed.add_field(name='Clouds', value=f'{cloud}% Cloudy', inline=True)
            embed.add_field(name='Pressure', value=f'{pressure} per inch', inline=True)
            embed.add_field(name='Precipitation', value=f'{precipitation}mm', inline=True)
            await ctx.send(embed=embed)
        else:
            await ctx.invoke(self.bot.get_command("help"), entity="Weather")

    # Animal fact command

    @commands.command(
      name="Fact", 
      description=
      "Bot permissions: None\n"
      "User permissions: None"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def animal_fact(self, ctx, animal: str=None):
        """Find a fact on a dog, cat, panda, fox, bird, koala, kangaroo, racoon and whale"""
        ranimal = ['dog', 'cat', 'panda', 'fox', 'bird', 'koala', 'kangaroo', 'racoon', 'whale']
        animal = animal or random.choice(ranimal)
        if (animal := animal.lower()) in ("dog", "cat", "panda", "fox", "bird", "koala", "kangaroo", "racoon", "whale"):
            fact_url = f"https://some-random-api.ml/facts/{animal}"
            image_url = f"https://some-random-api.ml/img/{'birb' if animal == 'bird' else animal}"

            async with request("GET", image_url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()
                    image_link = data["link"]

                else:
                    image_link = None

            async with request("GET", fact_url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()

                    embed = discord.Embed(
                        title=f"{animal.title()} fact",
                        description=data["fact"],
                        colour=self.bot.colour
                    )
                    embed.set_footer(text=f'Command sent by {ctx.author}', icon_url=ctx.author.avatar_url)
                    if image_link is not None:
                        embed.set_image(url=image_link)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(
                        description=f"API returned a {response.status} response",
                        colour=discord.Colour.red(),
                    )
                    embed.set_author(name='Error | External', icon_url='https://i.imgur.com/qYyJ5cC.png')
                    await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                description="Animal not recognised",
                colour=discord.Colour.red(),
            )
            embed.set_author(name='Error | Arguments', icon_url='https://i.imgur.com/qYyJ5cC.png')
            embed.add_field(name='Animals allowed:', value='Dog, Cat, Fox\nBird, Panda, Koala\nWhale, Racoon, Kangaroo', inline=False)
            await ctx.send(embed=embed)

    # Lyric command

    @commands.command(
      name="Lyrics", usage='<song>', 
      description=
      "Bot permissions: Manage messages, Add reactions\n"
      "User permissions: None"
    )
    @commands.bot_has_guild_permissions(manage_messages=True, add_reactions=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def lyric(self, ctx, *, song=None):
        """Get song lyrics"""
        if song is not None:
            async with ctx.channel.typing():
                song = song.replace(' ', '+')
                url = f"https://some-random-api.ml/lyrics?title={song}"

                async with request("GET", url, headers={}) as response:
                    if response.status == 200:
                        data = await response.json()
                        pages = []

                        lyrics = data['lyrics']
                        title = data['title']
                        author = data['author']
                        art = data['thumbnail']['genius']

                        for l in textwrap.wrap(lyrics, 4096, replace_whitespace=False):
                            ly = f"{l}\n\n"
                            pages.append(ly)

                        await Pag(title=f'{title} by {author}',
                        colour=self.bot.colour,
                        entries=pages, length=1, thumbnail=art).start(ctx)
                    elif response.status == 404:
                        embed = discord.Embed(
                            description=f" Received a 404 error: Are you sure that song exists?",
                            colour=discord.Colour.red(),
                        )
                        embed.set_author(name='Error | External', icon_url='https://i.imgur.com/qYyJ5cC.png')
                        await ctx.send(embed=embed)
                    else:
                        embed = discord.Embed(
                            description=f"API returned a {response.status} response",
                            colour=discord.Colour.red(),
                        )
                        embed.set_author(name='Error | External', icon_url='https://i.imgur.com/qYyJ5cC.png')
                        await ctx.send(embed=embed)
            return
        else:
            await ctx.invoke(self.bot.get_command("help"), entity="Lyrics")


    # Movie API

    @commands.command(
      name='Movie', usage='<movie>', 
      description=
      "Bot permissions: None\n"
      "User permissions: None"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def movie_search(self, ctx, *, search=None):
        """Search for a movie"""
        if (search != None):
            search.replace(' ', '+')
            key = 'YOUR_TOKEN_HERE'
            client = omdb.OMDBClient(apikey=key)
            v = client.get(title=f'{search}')
            h = v['imdb_id']
            embed = discord.Embed(
                title=v['title'],
                colour=self.bot.colour,
                url=f'https://www.imdb.com/title/{h}/'
            )
            embed.add_field(name='Rated', value=v['rated'], inline=True)
            embed.add_field(name='Released', value=v['released'], inline=True)
            embed.add_field(name='Runtime', value=v['runtime'], inline=True)

            embed.add_field(name='Genre', value=v['genre'], inline=True)
            embed.add_field(name='Language', value=v['language'], inline=True)
            embed.add_field(name='Country', value=v['country'], inline=True)

            embed.add_field(name='IMDB Rating', value=v['imdb_rating'], inline=True)
            embed.add_field(name='IMDB Votes', value=v['imdb_votes'], inline=True)
            embed.add_field(name='IMDB ID', value=v['imdb_id'], inline=True)

            embed.add_field(name='Director', value=v['director'], inline=False)
            embed.add_field(name='Actors', value=v['actors'], inline=False)
            embed.add_field(name='Plot', value=v['plot'], inline=False)
            embed.add_field(name='Awards', value=v['awards'], inline=False)

            embed.set_image(url=v['poster'])

            await ctx.send(embed=embed)
        else:
            await ctx.invoke(self.bot.get_command("help"), entity="Movie")

    # Quote API command

    @commands.command(
      name="Quote", 
      description=
      "Bot permissions: None\n"
      "User permissions: None"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def Quote_api(self, ctx):
        """Get the daily quote"""
        url = f"https://quotes-inspirational-quotes-motivational-quotes.p.rapidapi.com/quote?token=ipworld.info"

        headers = {
        'x-rapidapi-key': "YOUR_TOKEN_HERE",
        'x-rapidapi-host': "quotes-inspirational-quotes-motivational-quotes.p.rapidapi.com"
        }

        async with request("GET", url, headers=headers) as response:
          if response.status == 200:
            q = await response.json()

            author = q['author']
            quote = q['text']

        embed = discord.Embed(
            title=author,
            description=quote,
            colour=self.bot.colour
        )
        embed.set_footer(text='Quote of the Day')
        await ctx.send(embed=embed)

    @commands.command(
      name="Spotify",
      description=
      "Bot permissions: None\n"
      "User permissions: None"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def spotify(self, ctx, member: discord.Member=None):
        """Get the song that a user is listening to"""
        member = member or ctx.author
        spotify = next((activity for activity in member.activities if isinstance(activity, discord.Spotify)), None)

        if spotify is None:
            embed = discord.Embed(
                description="That user is not listening to Spotify",
                colour=discord.Colour.red(),
            )
            embed.set_author(name='Error | Generic', icon_url='https://i.imgur.com/qYyJ5cC.png')
            return await ctx.send(embed=embed)

        embed = discord.Embed(
            title=f"{spotify.title} By {', '.join([s for s in spotify.artists])}",
            description=f"<:spotify:840877967495528468>Listen here\n"
                        f"https://open.spotify.com/track/{spotify.track_id}\n"
                        f"Listened to by {member.name}#{member.discriminator}",
            colour=spotify.colour
        )
        embed.set_footer(text=f"0:00 - {dateutil.parser.parse(str(spotify.duration)).strftime('%M:%S')}")
        embed.set_thumbnail(url=spotify.album_cover_url)
        await ctx.send(embed=embed)

    @commands.command(
      name="Convert", usage="<From> <Value> [To]",
      description=
      "Bot permissions: None\n"
      "User permissions: None"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def convert(self, ctx, cur1=None, value=None, cur2=None):
        """Convert from one currency to another"""
        if cur1 is None and value is None:
            return await ctx.send("Please provide a currency and value! e.g. GBP 60")
        else:
            async with ctx.channel.typing():
                cur1 = cur1.upper()
                if cur2 is None:
                    cur2 = 'USD'
                else:
                    cur2 = cur2.upper()
                url = f"https://api.ksoft.si/kumo/currency?from={cur1}&to={cur2}&value={value}"
                headers={
                    "Authorization": self.bot.KSoft
                }

                async with request("GET", url, headers=headers) as response:
                    if response.status == 200:
                        r = await response.json()

                        nvalue = r["pretty"]
                        embed = discord.Embed(
                            title=f'{cur1} -> {cur2} : {value}',
                            description=nvalue,
                            colour=self.bot.colour
                        )
                        embed.set_footer(text='Powered by KSoft.Si',
                                         icon_url='https://cdn.ksoft.si/images/Logo128.png')
                    elif response.status == 404:
                        r = await response.json()
                        embed = discord.Embed(
                            description=f"C{str(r['message'])[1:]}",
                            colour=discord.Colour.red(),
                        )
                        embed.set_author(name='Error | External', icon_url='https://i.imgur.com/qYyJ5cC.png')
                        embed.set_footer(text='Refer to https://en.wikipedia.org/wiki/ISO_4217#Active_codes')
                        return await ctx.send(embed=embed)
                    else:
                        embed = discord.Embed(
                            description=f"API returned a {response.status} response",
                            colour=discord.Colour.red(),
                        )
                        embed.set_author(name='Error | External', icon_url='https://i.imgur.com/qYyJ5cC.png')
                        await ctx.send(embed=embed)
                await ctx.send(embed=embed)
            return

    @commands.command(
      name="Poll", usage="*<answers>",
      description=
      "Bot permissions: Add reactions\n"
      "User permissions: Manage Messages"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.bot_has_guild_permissions(add_reactions=True)
    @commands.has_guild_permissions(manage_messages=True)
    @commands.guild_only()
    async def poll(self, ctx):
        """Create a poll with up to 20 questions"""
        # a list of messages to delete when we're all done
        messages = [ctx.message]
        answers = []
        i = int(0)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and len(m.content) <= 100

        messages.append(await ctx.send("Please provide a question to make a poll from!"))
        try:
            question = await self.bot.wait_for('message', check=check, timeout=60.0)
            messages.append(question)
            await question.add_reaction("<:Tick:850334541918765076>")
            question = question.clean_content
        except asyncio.TimeoutError:
            return await ctx.send("No reply within 60 seconds. Too slow!")

        while i < 20:
            messages.append(await ctx.send('Please provide a poll option or type `publish` to publish the poll!'))

            try:
                entry = await self.bot.wait_for('message', check=check, timeout=60.0)
            except asyncio.TimeoutError:
                break

            messages.append(entry)

            if entry.clean_content.startswith('publish'):
                if len(answers) >= 2:
                    break
                elif len(answers) < 2:
                    messages.append(await ctx.send(f"You require atleast 2 options. You have {len(answers)} options!"))
            else:
                await entry.add_reaction("<:Tick:850334541918765076>")
                answers.append((to_emoji(i), entry.clean_content))
                i += 1

        try:
            await ctx.channel.delete_messages(messages)
        except:
            pass # oh well

        answer = '\n'.join(f'{keycap} {content}' for keycap, content in answers)
        embed = discord.Embed(
            title=question,
            description=answer,
            colour=self.bot.colour
        )
        poll = await ctx.send(embed=embed)
        for emoji, _ in answers:
            await poll.add_reaction(emoji)

def setup(bot):
    bot.add_cog(Info(bot))
