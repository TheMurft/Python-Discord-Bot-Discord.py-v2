import discord
from discord.ext import commands

CATEGORY_ICONS = {
    "Utility":    "🔧",
    "Moderation": "🛡️",
    "Config":     "⚙️",
    "Economy":    "💰",
}

class Help(commands.Cog, name="Utility"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", help="Shows all commands grouped by category.")
    async def help(self, ctx):
        prefix = self.bot.command_prefix

        # Build category → [commands] map from loaded cogs
        categories = {}
        for cog_name, cog in self.bot.cogs.items():
            cog_commands = [c for c in cog.get_commands() if not c.hidden]
            if not cog_commands:
                continue
            categories[cog_name] = cog_commands

        embed = discord.Embed(
            title="📖 Command Help",
            description=f"Prefix: `{prefix}` — Use `{prefix}help` to see this menu.",
            color=discord.Color.from_rgb(88, 101, 242)
        )
        embed.set_footer(text="Created by themurft • discord.gg/6C5t995jC6")
        embed.set_timestamp()

        for category_name in sorted(categories.keys()):
            icon = CATEGORY_ICONS.get(category_name, "📁")
            cmd_list = "\n".join(
                f"`{prefix}{cmd.name}` — {cmd.help or 'No description.'}"
                for cmd in categories[category_name]
            )
            embed.add_field(name=f"{icon} {category_name}", value=cmd_list, inline=False)

        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
