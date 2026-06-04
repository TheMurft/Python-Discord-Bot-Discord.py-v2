import os
import json
import discord
from discord.ext import commands

class SetWelcomeMsg(commands.Cog, name="Config"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setwelcomemsg", help="Set a custom welcome message template. e.g. !setwelcomemsg Welcome {user} to {server}!")
    @commands.has_permissions(administrator=True)
    async def setwelcomemsg(self, ctx, *, template: str):
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

            data["guilds"][guild_id_str]["welcome_message"] = template

            with open(db_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            await ctx.reply(f"✅ Welcome message template updated to:\n```\n{template}\n```")
        except Exception as e:
            print("[SETWELCOMEMSG ERROR]", e)
            await ctx.reply("❌ Failed to update database configuration.")

    @setwelcomemsg.error
    async def setwelcomemsg_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply("You do not have permission to use this command. Administrator permission is required.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(f"Usage: `{self.bot.command_prefix}setwelcomemsg <message template>`\nPlaceholders: `{{user}}`, `{{server}}`, `{{count}}`.")
        else:
            await ctx.reply(f"❌ Error: {error}")

async def setup(bot):
    await bot.add_cog(SetWelcomeMsg(bot))
