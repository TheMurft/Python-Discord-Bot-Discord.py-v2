import discord
from discord.ext import commands

class ServerInfo(commands.Cog, name="Utility"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="serverinfo", aliases=["server", "si"], help="Shows server information.")
    async def serverinfo(self, ctx):
        guild = ctx.guild
        if not guild:
            await ctx.reply("This command can only be used in a server.")
            return

        # Fetch owner
        try:
            owner = guild.owner or await guild.fetch_member(guild.owner_id)
            owner_str = f"{owner.name} ({owner.id})"
        except Exception:
            owner_str = f"ID: {guild.owner_id}"

        created_timestamp = int(guild.created_at.timestamp())

        embed = discord.Embed(
            title=f"{guild.name} Server Details",
            color=discord.Color.from_rgb(88, 101, 242)
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="Server Name", value=guild.name, inline=True)
        embed.add_field(name="Server ID", value=guild.id, inline=True)
        embed.add_field(name="Owner", value=owner_str, inline=True)
        embed.add_field(name="Total Members", value=str(guild.member_count), inline=True)
        embed.add_field(name="Created At", value=f"<t:{created_timestamp}:F> (<t:{created_timestamp}:R>)", inline=False)
        embed.add_field(name="Roles Count", value=str(len(guild.roles)), inline=True)
        embed.add_field(name="Channels Count", value=str(len(guild.channels)), inline=True)
        embed.set_timestamp()

        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerInfo(bot))
