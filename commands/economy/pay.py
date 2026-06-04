import discord
from discord.ext import commands

class Pay(commands.Cog, name="Economy"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pay", aliases=["give"],
                      help="Transfer coins to another user. e.g. !pay @user 100")
    async def pay(self, ctx, member: discord.Member, amount: int):
        if member.id == ctx.author.id:
            return await ctx.reply("❌ You can't pay yourself!")
        if member.bot:
            return await ctx.reply("❌ You can't pay bots!")
        if amount <= 0:
            return await ctx.reply("❌ Amount must be greater than 0.")

        data, sender = self.bot.get_economy(str(ctx.guild.id), str(ctx.author.id))
        econ = data["guilds"][str(ctx.guild.id)]["economy"]
        econ.setdefault(str(member.id), {})
        receiver = econ[str(member.id)]
        receiver.setdefault("cash", 0)
        receiver.setdefault("bank", 0)

        if amount > sender["cash"]:
            return await ctx.reply(f"❌ You only have **{sender['cash']:,} coins** in hand.")

        sender["cash"]   -= amount
        receiver["cash"] = receiver.get("cash", 0) + amount
        self.bot.save_economy(data)

        embed = discord.Embed(
            title="💸 Payment Sent!",
            description=f"**{ctx.author.name}** sent **{amount:,} coins** to **{member.name}**!",
            color=discord.Color.purple()
        )
        embed.add_field(name=f"{ctx.author.name}'s Cash", value=f"**{sender['cash']:,} coins**",   inline=True)
        embed.add_field(name=f"{member.name}'s Cash",     value=f"**{receiver['cash']:,} coins**", inline=True)
        embed.set_timestamp()
        await ctx.reply(embed=embed)

    @pay.error
    async def pay_error(self, ctx, error):
        if isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument)):
            await ctx.reply(f"Usage: `{self.bot.command_prefix}pay @user <amount>`")

async def setup(bot):
    await bot.add_cog(Pay(bot))
