import discord
from discord.ext import commands

class Withdraw(commands.Cog, name="Economy"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="withdraw", aliases=["with"],
                      help="Withdraw coins from your bank. e.g. !withdraw 100 or !withdraw all")
    async def withdraw(self, ctx, amount: str):
        data, user = self.bot.get_economy(str(ctx.guild.id), str(ctx.author.id))
        if amount.lower() == "all":
            amt = user["bank"]
        else:
            try: amt = int(amount)
            except ValueError:
                return await ctx.reply("❌ Please provide a valid number or `all`.")

        if amt <= 0:
            return await ctx.reply("❌ Amount must be greater than 0.")
        if amt > user["bank"]:
            return await ctx.reply(f"❌ You only have **{user['bank']:,} coins** in your bank.")

        user["bank"] -= amt
        user["cash"] += amt
        self.bot.save_economy(data)

        embed = discord.Embed(title="🏧 Withdrawal Successful!", color=discord.Color.red())
        embed.add_field(name="Withdrawn",   value=f"**{amt:,} coins**",       inline=True)
        embed.add_field(name="👛 Cash Now", value=f"**{user['cash']:,} coins**", inline=True)
        embed.add_field(name="🏦 Bank Now", value=f"**{user['bank']:,} coins**", inline=True)
        embed.set_timestamp()
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(Withdraw(bot))
