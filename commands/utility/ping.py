import discord
from discord.ext import commands
import time

class Ping(commands.Cog, name="Utility"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping", help="Shows bot and API latency.")
    async def ping(self, ctx):
        start_time = time.time()
        message = await ctx.reply("Pinging...")
        end_time = time.time()
        latency = round((end_time - start_time) * 1000)
        api_latency = round(self.bot.latency * 1000)
        await message.edit(content=f"Pong! 🏓\nBot Latency: `{latency}ms`\nAPI Latency: `{api_latency}ms`")

async def setup(bot):
    await bot.add_cog(Ping(bot))
