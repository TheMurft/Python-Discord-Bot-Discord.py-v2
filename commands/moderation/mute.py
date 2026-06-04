import discord
from discord.ext import commands
import datetime
import re

class Mute(commands.Cog, name="Moderation"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mute", help="Mutes (timeouts) a member in the server. e.g. !mute @user 10m [reason]")
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, time_str: str = "10m", *, reason: str = "No reason provided"):
        if ctx.author.top_role <= member.top_role and ctx.guild.owner_id != ctx.author.id:
            await ctx.reply("You cannot mute this member due to role hierarchy.")
            return

        if ctx.guild.me.top_role <= member.top_role:
            await ctx.reply("I cannot mute this member due to role hierarchy.")
            return

        # Parse duration
        duration = datetime.timedelta(minutes=10)
        label = "10 minute(s)"
        match = re.match(r"^(\d+)([mhd])$", time_str)
        if match:
            amount = int(match.group(1))
            unit = match.group(2)
            if unit == "m":
                duration = datetime.timedelta(minutes=amount)
                label = f"{amount} minute(s)"
            elif unit == "h":
                duration = datetime.timedelta(hours=amount)
                label = f"{amount} hour(s)"
            elif unit == "d":
                duration = datetime.timedelta(days=amount)
                label = f"{amount} day(s)"
        else:
            # If the second argument is not a time string, treat it as the start of the reason
            reason = f"{time_str} {reason}".strip()

        try:
            await member.timeout(duration, reason=reason)
            self.bot.log_moderation("MUTE", member, ctx.author, reason)
            await ctx.reply(f"✅ **{member}** has been muted for **{label}**.\n**Reason:** {reason}")
        except Exception as e:
            await ctx.reply(f"❌ Failed to mute user. Error: {e}")

    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply("You do not have permission to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply("Please specify a member to mute.")
        else:
            await ctx.reply(f"❌ Error: {error}")

async def setup(bot):
    await bot.add_cog(Mute(bot))
