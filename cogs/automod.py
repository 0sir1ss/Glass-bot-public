import asyncio
import asyncpg
import discord
from discord.ext import commands
from utils.encrypt import AESCipher

class Automoderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.group(
        name='Automod', aliases=['Am'],
        usage='<subcommand>',
        description=
        "Bot permissions: None\n"
        "User permissions: Manage server",
        invoke_without_command=True, case_insensitive=True
    )
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.has_guild_permissions(manage_guild=True)
    @commands.guild_only()
    async def automod(self, ctx):
        """Automod commands"""
        aes = AESCipher()
        db = await asyncpg.connect(self.bot.db_conf, timeout=10)
        result = await db.fetchrow("SELECT * FROM config WHERE gid = $1", aes.encrypt(ctx.guild.id))
        if result:
            prefix = aes.decrypt(result[1])
        else:
            prefix = ';'
        result = await db.fetchrow("SELECT * FROM blacklist WHERE gid = $1", aes.encrypt(ctx.guild.id))
        if result:
            bl = f'<:Tick:850334541918765076> Word Blacklisting - {prefix}automod blacklist'
        else:
            bl = f'<:Cross:850334541897269276> Word Blacklisting - {prefix}automod blacklist'

        result = await db.fetchrow("SELECT * FROM spamfilter WHERE gid = $1", aes.encrypt(ctx.guild.id))
        if result:
            if aes.decrypt(result[1]) == "True":
                spam = f'<:Tick:850334541918765076> Spam filter - {prefix}automod antispam'
            else:
                spam = f'<:Cross:850334541897269276> Spam filter - {prefix}automod antispam'
        else:
            spam = f'<:Cross:850334541897269276> Spam filter - {prefix}automod antispam'
        result = await db.fetchrow("SELECT * FROM urls WHERE gid = $1", aes.encrypt(ctx.guild.id))
        if result:
            if aes.decrypt(result[1]) == "True":
                urls = f'<:Tick:850334541918765076> Url Filter - {prefix}automod urls'
            else:
                urls = f'<:Cross:850334541897269276> Url Filter - {prefix}automod urls'
        else:
            urls = f'<:Cross:850334541897269276> Url Filter - {prefix}automod urls'
        result = await db.fetchrow("SELECT * FROM invites WHERE gid = $1", aes.encrypt(ctx.guild.id))
        if result:
            if aes.decrypt(result[1]) == "True":
                invites = f'<:Tick:850334541918765076> Invite filter - {prefix}automod invites'
            else:
                invites = f'<:Cross:850334541897269276> Invite filter - {prefix}automod invites'
        else:
            invites = f'<:Cross:850334541897269276> Invite filter - {prefix}automod invites'

        e = discord.Embed(
            description=f"""
            {bl}
            {spam}
            {urls}
            {invites}
            """,
            colour=discord.Colour.red()
        )
        e.set_author(name='Automod Settings', icon_url='https://i.imgur.com/qekGkXS.png')
        await ctx.send(embed=e)

    @automod.command(
        name='Blacklist', usage='[word]',
        description=
        "Bot permissions: Manage messages\n"
        "User permissions: Manage server"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.guild_only()
    async def blacklist(self, ctx, word=None):
        """Add blacklisted words which will be deleted automatically in your guild."""
        db = await asyncpg.connect(self.bot.db_conf, timeout=10)
        aes = AESCipher()
        result = await db.fetchrow("SELECT * FROM config WHERE gid = $1", aes.encrypt(ctx.guild.id))
        if result:
            prefix = aes.decrypt(result[1])
        else:
            prefix = ';'
        if word is None:
            result = await db.fetchrow("SELECT * FROM blacklist WHERE gid = $1", aes.encrypt(ctx.guild.id))

            if result:
                words = []
                for word in result[1]:
                    words.append(aes.decrypt(word))
                content = ', '.join(i for i in words)
                e = discord.Embed(
                    description=content,
                    colour=discord.Colour.red()
                )
                e.set_author(name='Blacklisted Words', icon_url='https://i.imgur.com/qekGkXS.png')
                e.set_footer(text=f'To blacklist a word do {prefix}automod blacklist <word>')
                await ctx.send(embed=e)
            else:
                embed = discord.Embed(
                    description="You have no blacklisted words",
                    colour=discord.Colour.red(),
                )
                embed.set_author(name='Error | Database', icon_url='https://i.imgur.com/qYyJ5cC.png')
                embed.set_footer(text=f'To blacklist a word do {prefix}automod blacklist <word>')
                await ctx.send(embed=embed)
        else:
            eword = aes.encrypt(word.lower())
            result = await db.fetchrow("SELECT * FROM blacklist WHERE gid = $1", aes.encrypt(ctx.guild.id))
            if result:
                words = result[1]
                if eword in words:
                    embed = discord.Embed(
                        description="That word is already blacklisted",
                        colour=discord.Colour.red(),
                    )
                    embed.set_author(name='Error | Database', icon_url='https://i.imgur.com/qYyJ5cC.png')
                    return await ctx.send(embed=embed)
                else:
                    words.append(eword)
                    await db.execute("UPDATE blacklist SET words = $1 WHERE gid = $2", words, aes.encrypt(ctx.guild.id))
                    e = discord.Embed(
                        description=f'`{word}` is blacklisted',
                        colour=discord.Colour.red()
                    )
                    e.set_author(name='Blacklist', icon_url='https://i.imgur.com/qekGkXS.png')
                    await ctx.send(embed=e)
            else:
                words = [eword]
                await db.execute("INSERT INTO blacklist VALUES($1, $2)", aes.encrypt(ctx.guild.id), words)
                e = discord.Embed(
                    description=f'`{word}` is blacklisted',
                    colour=discord.Colour.red()
                )
                e.set_author(name='Blacklist', icon_url='https://i.imgur.com/qekGkXS.png')
                await ctx.send(embed=e)
        await db.close()

    @automod.command(
        name='Unblacklist', usage='[word]',
        description=
        "Bot permissions: Manage messages\n"
        "User permissions: Manage server"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.guild_only()
    async def unblacklist(self, ctx, word=None):
        """Delete blacklisted words from your guild."""
        db = await asyncpg.connect(self.bot.db_conf, timeout=10)
        aes = AESCipher()
        result = await db.fetchrow("SELECT * FROM config WHERE gid = $1", aes.encrypt(ctx.guild.id))
        if result:
            prefix = aes.decrypt(result[1])
        else:
            prefix = ';'
        if word is None:
            result = await db.fetchrow("SELECT * FROM blacklist WHERE gid = $1", aes.encrypt(ctx.guild.id))
            if result:
                e = discord.Embed(
                    description='Are you sure you want to clear your blacklisted word list?',
                    colour=discord.Colour.red()
                )
                e.set_footer(text=f'To unblacklist a specifc word do {prefix}automod unblacklist <word>')
                e.set_author(name='Blacklist Confirmation', icon_url='https://i.imgur.com/qekGkXS.png')
                m = await ctx.send(embed=e)
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
                    return await ctx.send("Confirmation Failure. Please try again.")

                if str(reaction.emoji) not in ["<:Tick:850334541918765076>", "<:Cross:850334541897269276>"] or str(reaction.emoji) == "<:Cross:850334541897269276>":
                    await ctx.send("Cancelling request.")
                else:
                    await db.execute("DELETE FROM blacklist WHERE gid = $1", aes.encrypt(ctx.guild.id))
                    embed = discord.Embed(
                        description="All blacklisted words have been cleared",
                        colour=discord.Colour.red(),
                    )
                    embed.set_author(name='Blacklist Confirmed', icon_url='https://i.imgur.com/qYyJ5cC.png')
                    await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    description="You have no blacklisted words",
                    colour=discord.Colour.red(),
                )
                embed.set_author(name='Error | Database', icon_url='https://i.imgur.com/qYyJ5cC.png')
                embed.set_footer(text=f'To blacklist a word do {prefix}automod blacklist <word>')
                await ctx.send(embed=embed)
        else:
            eword = aes.encrypt(word.lower())
            result = await db.fetchrow("SELECT * FROM blacklist WHERE gid = $1", aes.encrypt(ctx.guild.id))
            if result:
                words = result[1]
                if eword not in words:
                    embed = discord.Embed(
                        description="That word isn't blacklisted",
                        colour=discord.Colour.red(),
                    )
                    embed.set_author(name='Error | Database', icon_url='https://i.imgur.com/qYyJ5cC.png')
                    await ctx.send(embed=embed)
                else:
                    words.remove(eword)
                    await db.execute("UPDATE blacklist SET words = $1 WHERE gid = $2", words, aes.encrypt(ctx.guild.id))
                    e = discord.Embed(
                        description=f'`{word}` is unblacklisted',
                        colour=discord.Colour.red()
                    )
                    e.set_author(name='Blacklist', icon_url='https://i.imgur.com/qekGkXS.png')
                    await ctx.send(embed=e)
                    # Checking if no profanities left

                    result = await db.fetchrow("SELECT * FROM blacklist WHERE gid = $1", aes.encrypt(ctx.guild.id))
                    words = result[1]

                    if not words:
                        await db.execute("DELETE FROM blacklist WHERE gid = $1", aes.encrypt(ctx.guild.id))

            else:
                embed = discord.Embed(
                    description="You have no blacklisted words",
                    colour=discord.Colour.red(),
                )
                embed.set_author(name='Error | Database', icon_url='https://i.imgur.com/qYyJ5cC.png')
                embed.set_footer(text=f'To blacklist a word do {prefix}automod blacklist <word>')
                await ctx.send(embed=embed)

        await db.close()

    @automod.command(
        name="Urls",
        description=
        "Bot permissions: Manage messages\n"
        "User permissions: Manage server"
    )
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.commands.has_guild_permissions(manage_guild=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.guild_only()
    async def urlfilter(self, ctx):
        """Allows or disallows urls"""
        db = await asyncpg.connect(self.bot.db_conf, timeout=10)
        aes = AESCipher()

        result = await db.fetchrow("SELECT * FROM urls WHERE gid = $1", aes.encrypt(ctx.guild.id))
        if result:
            option = aes.decrypt(result[1])
            if option == "False":
                await db.execute("UPDATE urls SET option = $1 where gid = $2", aes.encrypt(True), aes.encrypt(ctx.guild.id))
                embed = discord.Embed(
                    description="<:Tick:850334541918765076> Url Filter Enabled",
                    colour=discord.Colour.red(),
                )
                embed.set_author(name='Url Filter', icon_url='https://i.imgur.com/cMduP1p.png')
                await ctx.send(embed=embed)
            else:
                await db.execute("UPDATE urls SET option = $1 where gid = $2", aes.encrypt(False), aes.encrypt(ctx.guild.id))
                embed = discord.Embed(
                    description="<:Cross:850334541897269276> Url Filter Disabled",
                    colour=discord.Colour.red(),
                )
                embed.set_author(name='Url Filter', icon_url='https://i.imgur.com/cMduP1p.png')
                await ctx.send(embed=embed)
        else:
            await db.execute("INSERT INTO urls VALUES($1, $2)", aes.encrypt(ctx.guild.id), aes.encrypt(True))
            embed = discord.Embed(
                description="<:Tick:850334541918765076> Url Filter Enabled",
                colour=discord.Colour.red(),
            )
            embed.set_author(name='Url Filter', icon_url='https://i.imgur.com/cMduP1p.png')
            await ctx.send(embed=embed)

        await db.close()

    @automod.command(
        name="Antispam", aliases=['Spam'],
        description=
        "Bot permissions: Manage messages\n"
        "User permissions: Manage server"
    )
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.commands.has_guild_permissions(manage_guild=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.guild_only()
    async def spamfilter(self, ctx):
        """Enables or disables the spam filter"""
        db = await asyncpg.connect(self.bot.db_conf, timeout=10)
        aes = AESCipher()

        result = await db.fetchrow("SELECT * FROM spamfilter WHERE gid = $1", aes.encrypt(ctx.guild.id))
        if result:
            option = aes.decrypt(result[1])
            if option == "False":
                await db.execute("UPDATE spamfilter SET option = $1 where gid = $2", aes.encrypt(True), aes.encrypt(ctx.guild.id))
                embed = discord.Embed(
                    description="<:Tick:850334541918765076> Antispam Enabled",
                    colour=discord.Colour.red(),
                )
                embed.set_author(name='Spam Filter', icon_url='https://i.imgur.com/62HXt19.png')
                await ctx.send(embed=embed)
            else:
                await db.execute("UPDATE spamfilter SET option = $1 where gid = $2", aes.encrypt(False), aes.encrypt(ctx.guild.id))
                embed = discord.Embed(
                    description="<:Cross:850334541897269276> Antispam Disabled",
                    colour=discord.Colour.red(),
                )
                embed.set_author(name='Spam Filter', icon_url='https://i.imgur.com/62HXt19.png')
                await ctx.send(embed=embed)
        else:
            await db.execute("INSERT INTO spamfilter VALUES($1, $2)", aes.encrypt(ctx.guild.id), aes.encrypt(True))
            embed = discord.Embed(
                description="<:Tick:850334541918765076> Antispam Enabled",
                colour=discord.Colour.red(),
            )
            embed.set_author(name='Spam Filter', icon_url='https://i.imgur.com/62HXt19.png')
            await ctx.send(embed=embed)
        await db.close()

    @automod.command(
        name="Invites",
        description=
        "Bot permissions: Manage messages\n"
        "User permissions: Manage server"
    )
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.commands.has_guild_permissions(manage_guild=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.guild_only()
    async def invfilter(self, ctx):
        """Allows or disallows external server invites"""
        db = await asyncpg.connect(self.bot.db_conf, timeout=10)
        aes = AESCipher()

        result = await db.fetchrow("SELECT * FROM invites WHERE gid = $1", aes.encrypt(ctx.guild.id))
        if result:
            option = aes.decrypt(result[1])
            if option == "False":
                await db.execute("UPDATE invites SET option = $1 where gid = $2", aes.encrypt(True), aes.encrypt(ctx.guild.id))
                embed = discord.Embed(
                    description="<:Tick:850334541918765076> Invite Filter Enabled",
                    colour=discord.Colour.red(),
                )
                embed.set_author(name='Invite Filter', icon_url='https://i.imgur.com/0T55PZj.png')
                await ctx.send(embed=embed)
            else:
                await db.execute("UPDATE invites SET option = $1 where gid = $2", aes.encrypt(False), aes.encrypt(ctx.guild.id))
                embed = discord.Embed(
                    description="<:Cross:850334541897269276> Invite Filter Disabled",
                    colour=discord.Colour.red(),
                )
                embed.set_author(name='Invite Filter', icon_url='https://i.imgur.com/0T55PZj.png')
                await ctx.send(embed=embed)
        else:
            await db.execute("INSERT INTO invites VALUES($1, $2)", aes.encrypt(ctx.guild.id), aes.encrypt(True))
            embed = discord.Embed(
                description="<:Tick:850334541918765076> Invite Filter Enabled",
                colour=discord.Colour.red(),
            )
            embed.set_author(name='Invite Filter', icon_url='https://i.imgur.com/0T55PZj.png')
            await ctx.send(embed=embed)

        await db.close()

def setup(bot):
    bot.add_cog(Automoderation(bot))
