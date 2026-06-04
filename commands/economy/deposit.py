import discord
from discord.ext import commands

class Deposit(commands.Cog, name="Economy"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="deposit", aliases=["dep"],
                      help="Deposit coins into your bank. e.g. !deposit 100 or !deposit all")
    async def deposit(self, ctx, amount: str):
        data, user = self.bot.get_economy(str(ctx.guild.id), str(ctx.author.id))
        if amount.lower() == "all":
            amt = user["cash"]
        else:
            try: amt = int(amount)
            except ValueError:
                return await ctx.reply("❌ Please provide a valid number or `all`.")

        if amt <= 0:
            return await ctx.reply("❌ Amount must be greater than 0.")
        if amt > user["cash"]:
            return await ctx.reply(f"❌ You only have **{user['cash']:,} coins** in hand.")

        user["cash"] -= amt
        user["bank"] += amt
        self.bot.save_economy(data)

        embed = discord.Embed(title="🏦 Deposit Successful!", color=discord.Color.green())
        embed.add_field(name="Deposited",   value=f"**{amt:,} coins**",       inline=True)
        embed.add_field(name="👛 Cash Now", value=f"**{user['cash']:,} coins**", inline=True)
        embed.add_field(name="🏦 Bank Now", value=f"**{user['bank']:,} coins**", inline=True)
        embed.set_timestamp()
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(Deposit(bot))
