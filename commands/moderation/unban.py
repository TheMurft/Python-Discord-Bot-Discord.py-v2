import discord
from discord.ext import commands

class Unban(commands.Cog, name="Moderation"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="unban", help="Unbans a user from the server using their ID.")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int, *, reason: str = "No reason provided"):
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user, reason=reason)
            self.bot.log_moderation("UNBAN", user, ctx.author, reason)
            await ctx.reply(f"✅ User **{user}** (ID: {user_id}) has been unbanned.")
        except discord.NotFound:
            await ctx.reply("❌ User was not found or is not banned.")
        except Exception as e:
            await ctx.reply(f"❌ Failed to unban user. Error: {e}")

    @unban.error
    async def unban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply("You do not have permission to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply("Please specify a user ID to unban.")
        else:
            await ctx.reply(f"❌ Error: {error}")

async def setup(bot):
    await bot.add_cog(Unban(bot))
