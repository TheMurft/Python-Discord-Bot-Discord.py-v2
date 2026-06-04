import discord
from discord.ext import commands

class Unmute(commands.Cog, name="Moderation"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="unmute", help="Unmutes (removes timeout) a member in the server.")
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if not member.is_timed_out():
            await ctx.reply("This member is not muted/timed out.")
            return

        try:
            await member.timeout(None, reason=reason)
            self.bot.log_moderation("UNMUTE", member, ctx.author, reason)
            await ctx.reply(f"✅ **{member}** has been unmuted.")
        except Exception as e:
            await ctx.reply(f"❌ Failed to unmute user. Error: {e}")

    @unmute.error
    async def unmute_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply("You do not have permission to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply("Please specify a member to unmute.")
        else:
            await ctx.reply(f"❌ Error: {error}")

async def setup(bot):
    await bot.add_cog(Unmute(bot))
