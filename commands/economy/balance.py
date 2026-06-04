import discord
from discord.ext import commands

class Balance(commands.Cog, name="Economy"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="balance", aliases=["bal", "money"],
                      help="Shows your (or another user's) cash and bank balance.")
    async def balance(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        _, user = self.bot.get_economy(str(ctx.guild.id), str(target.id))

        embed = discord.Embed(
            title=f"💰 {target.name}'s Balance",
            color=discord.Color.gold()
        )
        embed.add_field(name="👛 Cash",     value=f"**{user['cash']:,} coins**",                inline=True)
        embed.add_field(name="🏦 Bank",     value=f"**{user['bank']:,} coins**",                inline=True)
        embed.add_field(name="📊 Net Worth",value=f"**{user['cash'] + user['bank']:,} coins**", inline=True)
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.set_timestamp()
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(Balance(bot))
