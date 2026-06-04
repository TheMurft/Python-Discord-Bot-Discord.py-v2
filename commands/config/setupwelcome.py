import os
import json
import discord
from discord.ext import commands

class SetupWelcome(commands.Cog, name="Config"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setupwelcome", help="Configure welcome and goodbye channels. e.g. !setupwelcome #welcome #goodbye")
    @commands.has_permissions(administrator=True)
    async def setupwelcome(self, ctx, welcome_channel: discord.TextChannel, goodbye_channel: discord.TextChannel):
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
            "database.json"
        )
        
        try:
            data = {}
            if os.path.exists(db_path):
                with open(db_path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = {}
            
            if "guilds" not in data:
                data["guilds"] = {}
            guild_id_str = str(ctx.guild.id)
            if guild_id_str not in data["guilds"]:
                data["guilds"][guild_id_str] = {}

            data["guilds"][guild_id_str]["welcome_channel"] = str(welcome_channel.id)
            data["guilds"][guild_id_str]["goodbye_channel"] = str(goodbye_channel.id)

            with open(db_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            await ctx.reply(
                f"✅ Welcome and Goodbye channels configured successfully!\n"
                f"**Welcome:** {welcome_channel.mention}\n"
                f"**Goodbye:** {goodbye_channel.mention}"
            )
        except Exception as e:
            print("[SETUPWELCOME ERROR]", e)
            await ctx.reply("❌ Failed to update database configuration.")

    @setupwelcome.error
    async def setupwelcome_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply("You do not have permission to use this command. Administrator permission is required.")
        elif isinstance(error, commands.BadArgument) or isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(f"Usage: `{self.bot.command_prefix}setupwelcome <#welcome-channel> <#goodbye-channel>`")
        else:
            await ctx.reply(f"❌ Error: {error}")

async def setup(bot):
    await bot.add_cog(SetupWelcome(bot))
