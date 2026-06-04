import discord
from discord.ext import commands
import datetime
import random

ROB_CD_MIN = 10

class Rob(commands.Cog, name="Economy"):
    def __init__(self, bot):
        self.bot = bot

    def _cd_remaining(self, last_iso):
        if not last_iso:
            return None
        cd = datetime.timedelta(minutes=ROB_CD_MIN)
        elapsed = datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.fromisoformat(last_iso)
        remaining = cd - elapsed
        return remaining if remaining.total_seconds() > 0 else None

    @commands.command(name="rob", help="Attempt to rob a user's cash (50% success, 10min cooldown). !rob @user")
    async def rob(self, ctx, member: discord.Member):
        if member.id == ctx.author.id:
            return await ctx.reply("❌ You can't rob yourself!")
        if member.bot:
            return await ctx.reply("❌ You can't rob bots!")

        data, robber = self.bot.get_economy(str(ctx.guild.id), str(ctx.author.id))
        econ = data["guilds"][str(ctx.guild.id)]["economy"]
        econ.setdefault(str(member.id), {})
        victim = econ[str(member.id)]
        victim.setdefault("cash", 0)
        victim.setdefault("bank", 0)

        # Cooldown
        rem = self._cd_remaining(robber.get("last_rob"))
        if rem:
            m, s = divmod(int(rem.total_seconds()), 60)
            return await ctx.reply(f"⏳ You need to lay low! Try again in **{m}m {s}s**.")

        if victim["cash"] <= 0:
            return await ctx.reply(f"❌ **{member.name}** has no cash to steal!")

        robber["last_rob"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

        if random.random() < 0.5:
            pct    = random.uniform(0.10, 0.40)
            stolen = max(1, int(victim["cash"] * pct))
            victim["cash"]  -= stolen
            robber["cash"]  = robber.get("cash", 0) + stolen
            self.bot.save_economy(data)
            embed = discord.Embed(
                title="🦹 Robbery Successful!",
                description=f"You stole **{stolen:,} coins** from **{member.name}**!",
                color=discord.Color.green()
            )
        else:
            robber_cash = robber.get("cash", 0)
            fine        = max(1, int(robber_cash * random.uniform(0.10, 0.25)))
            actual_fine = min(fine, robber_cash)
            robber["cash"]  = robber_cash - actual_fine
            victim["cash"]  = victim.get("cash", 0) + actual_fine
            self.bot.save_economy(data)
            embed = discord.Embed(
                title="🚔 Caught in the Act!",
                description=f"You were caught and paid a fine of **{actual_fine:,} coins** to **{member.name}**!",
                color=discord.Color.red()
            )

        embed.set_timestamp()
        await ctx.reply(embed=embed)

    @rob.error
    async def rob_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply("❌ Please mention a user to rob.")

async def setup(bot):
    await bot.add_cog(Rob(bot))
