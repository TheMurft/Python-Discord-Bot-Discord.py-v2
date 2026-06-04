import discord
from discord.ext import commands

class Ban(commands.Cog, name="Moderation"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ban", help="Bans a member from the server.")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        # Check hierarchy
        if ctx.author.top_role <= member.top_role and ctx.guild.owner_id != ctx.author.id:
            await ctx.reply("You cannot ban this member due to role hierarchy.")
            return

        if ctx.guild.me.top_role <= member.top_role:
            await ctx.reply("I cannot ban this member due to role hierarchy.")
            return

        await member.ban(reason=reason)
        self.bot.log_moderation("BAN", member, ctx.author, reason)
        await ctx.reply(f"✅ **{member}** has been banned.\n**Reason:** {reason}")

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply("You do not have permission to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply("Please specify a member to ban.")
        else:
            await ctx.reply(f"❌ Error: {error}")

async def setup(bot):
    await bot.add_cog(Ban(bot))
