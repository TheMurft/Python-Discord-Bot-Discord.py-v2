import discord
from discord.ext import commands
import asyncio

class Clear(commands.Cog, name="Moderation"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="clear", aliases=["purge"], help="Deletes a specified number of messages. e.g. !clear 10")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        if amount < 1 or amount > 99:
            await ctx.reply("Please provide a number between 1 and 99 of messages to clear.")
            return

        try:
            # Delete invocation + messages
            deleted = await ctx.channel.purge(limit=amount + 1)
            msg = await ctx.send(f"✅ Cleared **{len(deleted) - 1}** message(s).")
            await asyncio.sleep(5)
            await msg.delete()
        except Exception as e:
            await ctx.reply(f"❌ Failed to clear messages. Error: {e}")

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply("You do not have permission to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply("Please provide the number of messages to clear.")
        else:
            await ctx.reply(f"❌ Error: {error}")

async def setup(bot):
    await bot.add_cog(Clear(bot))
