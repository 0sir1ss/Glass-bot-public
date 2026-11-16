import base64
import binascii
import codecs
import discord
from io import BytesIO
from discord.ext import commands


class Encryption(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.group(
		name='Encode', aliases=['Encrypt'],
		usage='<subcommand>',
		description=
		"Bot permissions: None\n"
		"User permissions: None",
		invoke_without_command=True, case_insensitive=True
	)
	@commands.cooldown(1, 10, commands.BucketType.guild)
	async def encode(self, ctx):
		""" All encode methods """
		await ctx.invoke(self.bot.get_command("help"), entity="Encode")

	@commands.group(
		name='Decode', aliases=['Decrypt'],
		usage='<subcommand>',
		description=
		"Bot permissions: None\n"
		"User permissions: None",
		invoke_without_command=True, case_insensitive=True
	)
	@commands.cooldown(1, 10, commands.BucketType.guild)
	async def decode(self, ctx):
		""" All decode methods """
		await ctx.invoke(self.bot.get_command("help"), entity="Decode")

	async def encryptout(self, ctx, convert: str, input):
		""" The main, modular function to control encrypt/decrypt commands """
		if len(input) > 1900:
			try:
				data = BytesIO(input.encode('utf-8'))
			except AttributeError:
				data = BytesIO(input)

			try:
				embed = discord.Embed(
					description="The text returned is too large to send as a message.",
					colour=discord.Colour.red(),
				)
				embed.set_author(name='Error | Generic', icon_url='https://i.imgur.com/qYyJ5cC.png')
				return await ctx.send(
					embed=embed,
					file=discord.File(data, filename=f"{convert}.txt")
				)
			except discord.HTTPException:
				embed = discord.Embed(
					description="The file returned is too large to send as a file.",
					colour=discord.Colour.red(),
				)
				embed.set_author(name='Error | Generic', icon_url='https://i.imgur.com/qYyJ5cC.png')
				return await ctx.send(embed=embed)
		else:
			try:
				return await ctx.send(f"**{convert}**```\n{input.decode('UTF-8')}```")
			except AttributeError:
				return await ctx.send(f"**{convert}**```\n{input}```")

	@encode.command(
		name="Base32", aliases=["b32"],
		description=
		"Bot permissions: None\n"
		"User permissions: None"
	)
	async def encode_base32(self, ctx, *, input: commands.clean_content = None):
		""" Encode in base32 """
		if input is None:
			embed = discord.Embed(
				description="I require text to encode",
				colour=discord.Colour.red(),
			)
			embed.set_author(name='Error | Arguments', icon_url='https://i.imgur.com/qYyJ5cC.png')
			return await ctx.send(embed=embed)
		await self.encryptout(
			ctx, "Base32", base64.b32encode(input.encode('UTF-8'))
		)

	@decode.command(
		name="Base32", aliases=["b32"],
		description=
		"Bot permissions: None\n"
		"User permissions: None"
	)
	async def decode_base32(self, ctx, *, input: commands.clean_content = None):
		""" Decode in base32 """
		if input is None:
			embed = discord.Embed(
				description="I require text to decode",
				colour=discord.Colour.red(),
			)
			embed.set_author(name='Error | Arguments', icon_url='https://i.imgur.com/qYyJ5cC.png')
			return await ctx.send(embed=embed)
		try:
			await self.encryptout(ctx, "Base32", base64.b32decode(input.encode('UTF-8')))
		except Exception:
			await ctx.send("Invalid base32.")

	@encode.command(
		name="Base64", aliases=["b64"],
		description=
		"Bot permissions: None\n"
		"User permissions: None"
	)
	async def encode_base64(self, ctx, *, input: commands.clean_content = None):
		""" Encode in base64 """
		if input is None:
			embed = discord.Embed(
				description="I require text to encode",
				colour=discord.Colour.red(),
			)
			embed.set_author(name='Error | Arguments', icon_url='https://i.imgur.com/qYyJ5cC.png')
			return await ctx.send(embed=embed)
		await self.encryptout(
			ctx, "Base64", base64.urlsafe_b64encode(input.encode('UTF-8'))
		)

	@decode.command(
		name="Base64", aliases=["b64"],
		description=
		"Bot permissions: None\n"
		"User permissions: None"
	)
	async def decode_base64(self, ctx, *, input: commands.clean_content = None):
		""" Decode in base64 """
		if input is None:
			embed = discord.Embed(
				description="I require text to decode",
				colour=discord.Colour.red(),
			)
			embed.set_author(name='Error | Arguments', icon_url='https://i.imgur.com/qYyJ5cC.png')
			return await ctx.send(embed=embed)
		try:
			await self.encryptout(ctx, "Base64", base64.urlsafe_b64decode(input.encode('UTF-8')))
		except Exception:
			await ctx.send("Invalid base64.")

	@encode.command(
		name="Rot13", aliases=["r13"],
		description=
		"Bot permissions: None\n"
		"User permissions: None"
	)
	async def encode_rot13(self, ctx, *, input: commands.clean_content = None):
		""" Encode in rot13 """
		if input is None:
			embed = discord.Embed(
				description="I require text to encode",
				colour=discord.Colour.red(),
			)
			embed.set_author(name='Error | Arguments', icon_url='https://i.imgur.com/qYyJ5cC.png')
			return await ctx.send(embed=embed)
		await self.encryptout(
			ctx, "Rot13", codecs.decode(input, 'rot_13')
		)

	@decode.command(
		name="Rot13", aliases=["r13"],
		description=
		"Bot permissions: None\n"
		"User permissions: None"
	)
	async def decode_rot13(self, ctx, *, input: commands.clean_content = None):
		""" Decode in rot13 """
		if input is None:
			embed = discord.Embed(
				description="I require text to decode",
				colour=discord.Colour.red(),
			)
			embed.set_author(name='Error | Arguments', icon_url='https://i.imgur.com/qYyJ5cC.png')
			return await ctx.send(embed=embed)
		try:
			await self.encryptout(ctx, "Rot13", codecs.decode(input, 'rot_13'))
		except Exception:
			await ctx.send("Invalid rot13.")

	@encode.command(
		name="Hex",
		description=
		"Bot permissions: None\n"
		"User permissions: None"
	)
	async def encode_hex(self, ctx, *, input: commands.clean_content = None):
		""" Encode in hex """
		if input is None:
			embed = discord.Embed(
				description="I require text to encode",
				colour=discord.Colour.red(),
			)
			embed.set_author(name='Error | Arguments', icon_url='https://i.imgur.com/qYyJ5cC.png')
			return await ctx.send(embed=embed)
		await self.encryptout(
			ctx, "Hex", binascii.hexlify(input.encode('UTF-8'))
		)

	@decode.command(
		name="Hex",
		description=
		"Bot permissions: None\n"
		"User permissions: None"
	)
	async def decode_hex(self, ctx, *, input: commands.clean_content = None):
		""" Decode in hex """
		if input is None:
			embed = discord.Embed(
				description="I require text to decode",
				colour=discord.Colour.red(),
			)
			embed.set_author(name='Error | Arguments', icon_url='https://i.imgur.com/qYyJ5cC.png')
			return await ctx.send(embed=embed)
		try:
			await self.encryptout(ctx, "Hex", binascii.unhexlify(input.encode('UTF-8')))
		except Exception:
			await ctx.send("Invalid hex.")

	@encode.command(
		name="Base85", aliases=["b85"],
		description=
		"Bot permissions: None\n"
		"User permissions: None"
	)
	async def encode_base85(self, ctx, *, input: commands.clean_content = None):
		""" Encode in base85 """
		if input is None:
			embed = discord.Embed(
				description="I require text to encode",
				colour=discord.Colour.red(),
			)
			embed.set_author(name='Error | Arguments', icon_url='https://i.imgur.com/qYyJ5cC.png')
			return await ctx.send(embed=embed)
		await self.encryptout(
			ctx, "Base85", base64.b85encode(input.encode('UTF-8'))
		)

	@decode.command(
		name="Base85", aliases=["b85"],
		description=
		"Bot permissions: None\n"
		"User permissions: None"
	)
	async def decode_base85(self, ctx, *, input: commands.clean_content = None):
		""" Decode in base85 """
		if input is None:
			embed = discord.Embed(
				description="I require text to decode",
				colour=discord.Colour.red(),
			)
			embed.set_author(name='Error | Arguments', icon_url='https://i.imgur.com/qYyJ5cC.png')
			return await ctx.send(embed=embed)
		try:
			await self.encryptout(ctx, "Base85", base64.b85decode(input.encode('UTF-8')))
		except Exception:
			await ctx.send("Invalid base85.")

	@encode.command(
		name="Ascii85", aliases=["a85"],
		description=
		"Bot permissions: None\n"
		"User permissions: None"
	)
	async def encode_ascii85(self, ctx, *, input: commands.clean_content = None):
		""" Encode in ASCII85 """
		if input is None:
			embed = discord.Embed(
				description="I require text to encode",
				colour=discord.Colour.red(),
			)
			embed.set_author(name='Error | Arguments', icon_url='https://i.imgur.com/qYyJ5cC.png')
			return await ctx.send(embed=embed)
		await self.encryptout(
			ctx, "ASCII85", base64.a85encode(input.encode('UTF-8'))
		)

	@decode.command(
		name="Ascii85", aliases=["a85"],
		description=
		"Bot permissions: None\n"
		"User permissions: None"
	)
	async def decode_ascii85(self, ctx, *, input: commands.clean_content = None):
		""" Decode in ASCII85 """
		if input is None:
			embed = discord.Embed(
				description="I require text to decode",
				colour=discord.Colour.red(),
			)
			embed.set_author(name='Error | Arguments', icon_url='https://i.imgur.com/qYyJ5cC.png')
			return await ctx.send(embed=embed)
		try:
			await self.encryptout(ctx, "ASCII85", base64.a85decode(input.encode('UTF-8')))
		except Exception:
			await ctx.send("Invalid ASCII85.")


def setup(bot):
	bot.add_cog(Encryption(bot))
