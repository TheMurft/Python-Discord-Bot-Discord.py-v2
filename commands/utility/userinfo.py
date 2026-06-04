import discord
from discord.ext import commands

class UserInfo(commands.Cog, name="Utility"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="userinfo", aliases=["user", "ui"], help="Shows user information.")
    async def userinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        
        roles = ", ".join([role.mention for role in member.roles if role.name != "@everyone"]) or "None"
        created_timestamp = int(member.created_at.timestamp())
        joined_timestamp = int(member.joined_at.timestamp()) if member.joined_at else 0

        embed = discord.Embed(
            title=f"{member.name}'s Details",
            color=discord.Color.from_rgb(88, 101, 242)
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Username", value=str(member), inline=True)
        embed.add_field(name="User ID", value=str(member.id), inline=True)
        embed.add_field(name="Joined Server", value=f"<t:{joined_timestamp}:F> (<t:{joined_timestamp}:R>)", inline=False)
        embed.add_field(name="Account Created", value=f"<t:{created_timestamp}:F> (<t:{created_timestamp}:R>)", inline=False)
        embed.add_field(name="Roles", value=roles, inline=False)
        embed.set_timestamp()

        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(UserInfo(bot))
