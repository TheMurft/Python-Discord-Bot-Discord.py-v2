import discord
from discord.ext import commands

class Kick(commands.Cog, name="Moderation"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="kick", help="Kicks a member from the server.")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        # Check hierarchy
        if ctx.author.top_role <= member.top_role and ctx.guild.owner_id != ctx.author.id:
            await ctx.reply("You cannot kick this member due to role hierarchy.")
            return

        if ctx.guild.me.top_role <= member.top_role:
            await ctx.reply("I cannot kick this member due to role hierarchy.")
            return

        await member.kick(reason=reason)
        self.bot.log_moderation("KICK", member, ctx.author, reason)
        await ctx.reply(f"✅ **{member}** has been kicked.\n**Reason:** {reason}")

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply("You do not have permission to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply("Please specify a member to kick.")
        else:
            await ctx.reply(f"❌ Error: {error}")

async def setup(bot):
    await bot.add_cog(Kick(bot))
