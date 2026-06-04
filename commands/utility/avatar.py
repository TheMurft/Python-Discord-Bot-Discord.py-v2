import discord
from discord.ext import commands

class Avatar(commands.Cog, name="Utility"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="avatar", aliases=["av"], help="Shows user's avatar.")
    async def avatar(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        avatar_url = member.display_avatar.url

        embed = discord.Embed(
            title=f"{member.name}'s Avatar",
            color=discord.Color.from_rgb(88, 101, 242)
        )
        embed.set_image(url=avatar_url)
        embed.set_timestamp()

        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(Avatar(bot))
