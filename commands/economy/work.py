import discord
from discord.ext import commands
import datetime
import random

WORK_CD_H = 1
JOBS = [
    ("Software Developer", 80, 150),
    ("Chef",               50, 100),
    ("Streamer",           40, 120),
    ("Delivery Driver",    30,  90),
    ("Freelancer",         60, 140),
    ("Miner",              50, 130),
]

class Work(commands.Cog, name="Economy"):
    def __init__(self, bot):
        self.bot = bot

    def _cd_remaining(self, last_iso):
        if not last_iso:
            return None
        cd = datetime.timedelta(hours=WORK_CD_H)
        elapsed = datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.fromisoformat(last_iso)
        remaining = cd - elapsed
        return remaining if remaining.total_seconds() > 0 else None

    @commands.command(name="work", help="Work to earn coins (1h cooldown).")
    async def work(self, ctx):
        data, user = self.bot.get_economy(str(ctx.guild.id), str(ctx.author.id))
        rem = self._cd_remaining(user.get("last_work"))
        if rem:
            m, s = divmod(int(rem.total_seconds()), 60)
            return await ctx.reply(f"⏳ You're still tired! Come back in **{m}m {s}s**.")

        title, low, high = random.choice(JOBS)
        earned = random.randint(low, high)
        user["cash"] += earned
        user["last_work"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.bot.save_economy(data)

        embed = discord.Embed(
            title="💼 Work Shift Complete!",
            description=f"You worked as a **{title}** and earned **{earned:,} coins**!\nNew balance: **{user['cash']:,} coins** in hand.",
            color=discord.Color.blue()
        )
        embed.set_footer(text="You can work again in 1 hour.")
        embed.set_timestamp()
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(Work(bot))
