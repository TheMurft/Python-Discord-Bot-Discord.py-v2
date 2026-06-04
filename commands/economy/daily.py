import discord
from discord.ext import commands
import datetime

DAILY_AMOUNT = 200
DAILY_CD_H   = 24

class Daily(commands.Cog, name="Economy"):
    def __init__(self, bot):
        self.bot = bot

    def _cd_remaining(self, last_iso):
        if not last_iso:
            return None
        cd = datetime.timedelta(hours=DAILY_CD_H)
        elapsed = datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.fromisoformat(last_iso)
        remaining = cd - elapsed
        return remaining if remaining.total_seconds() > 0 else None

    @commands.command(name="daily", help="Claim your daily reward of 200 coins (24h cooldown).")
    async def daily(self, ctx):
        data, user = self.bot.get_economy(str(ctx.guild.id), str(ctx.author.id))
        rem = self._cd_remaining(user.get("last_daily"))
        if rem:
            h, m = divmod(int(rem.total_seconds() // 60), 60)
            return await ctx.reply(f"⏳ You already claimed your daily! Come back in **{h}h {m}m**.")

        user["cash"] += DAILY_AMOUNT
        user["last_daily"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.bot.save_economy(data)

        embed = discord.Embed(
            title="💰 Daily Reward Claimed!",
            description=f"You received **{DAILY_AMOUNT:,} coins**!\nNew balance: **{user['cash']:,} coins** in hand.",
            color=discord.Color.green()
        )
        embed.set_footer(text="Come back in 24 hours!")
        embed.set_timestamp()
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(Daily(bot))
