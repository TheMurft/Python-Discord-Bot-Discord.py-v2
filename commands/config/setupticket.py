import os
import json
import discord
from discord.ext import commands
import asyncio

class TicketPanelView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.primary, custom_id="create_ticket", emoji="📩")
    async def create_ticket_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        user = interaction.user
        
        # Read database config
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
            "database.json"
        )
        data = {}
        if os.path.exists(db_path):
            try:
                with open(db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                pass
                
        guild_config = data.get("guilds", {}).get(str(guild.id), {})
        ticket_config = guild_config.get("ticket_config")
        if not ticket_config:
            await interaction.followup.send("Ticket system is not set up on this server.", ephemeral=True)
            return

        # Check if a channel with name ticket-{username} already exists
        existing_channel = discord.utils.get(guild.text_channels, name=f"ticket-{user.name.lower()}")
        if existing_channel:
            await interaction.followup.send(f"You already have an open ticket: {existing_channel.mention}", ephemeral=True)
            return

        # Get category
        category_id = ticket_config.get("category_id")
        category = guild.get_channel(int(category_id)) if category_id else None

        # Setup permissions
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, read_message_history=True, manage_channels=True)
        }

        try:
            # Create channel
            channel = await guild.create_text_channel(
                name=f"ticket-{user.name}",
                category=category,
                overwrites=overwrites
            )

            # Send inner embed
            inner_title = ticket_config.get("inner_title", "Ticket Support")
            inner_desc = ticket_config.get("inner_desc", "Please state your question and staff will assist you shortly.")
            
            embed = discord.Embed(
                title=inner_title,
                description=inner_desc,
                color=discord.Color.from_rgb(88, 101, 242)
            )
            embed.set_timestamp()

            # Create Close button view
            close_view = CloseTicketView()
            await channel.send(content=f"{user.mention}, welcome to your ticket channel.", embed=embed, view=close_view)
            await interaction.followup.send(f"Ticket channel created successfully: {channel.mention}", ephemeral=True)
        except Exception as e:
            print("[TICKET CREATE ERROR]", e)
            await interaction.followup.send("Failed to create ticket channel. Make sure my roles/permissions are correct.", ephemeral=True)

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket", emoji="🔒")
    async def close_ticket_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Closing ticket in 5 seconds...")
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete()
        except Exception as e:
            print("[TICKET CLOSE ERROR]", e)

class SetupTicket(commands.Cog, name="Config"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setupticket", help="Interactive setup wizard for the ticket system.")
    @commands.has_permissions(administrator=True)
    async def setupticket(self, ctx):
        def check(m):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        config = {}
        
        await ctx.reply("Welcome to the **Ticket System Setup Wizard**! Let's configure it step-by-step.\n\n**Step 1:** Mention the channel where the ticket panel should be sent (or provide the Channel ID):")
        
        try:
            # Step 1: Channel
            msg = await self.bot.wait_for('message', check=check, timeout=300.0)
            channel_content = msg.content.strip()
            # Extract channel ID
            channel_id = channel_content.replace("<#", "").replace(">", "")
            target_channel = ctx.guild.get_channel(int(channel_id))
            if not target_channel or not isinstance(target_channel, discord.TextChannel):
                await ctx.send("❌ Invalid text channel. Setup cancelled. Please run the command again.")
                return
            config["panel_channel_id"] = str(target_channel.id)

            # Step 2: Category
            await ctx.send("**Step 2:** Provide the Category ID where ticket channels will be created (type `none` for no category):")
            msg = await self.bot.wait_for('message', check=check, timeout=300.0)
            category_content = msg.content.strip()
            if category_content.lower() == "none":
                config["category_id"] = None
            else:
                category = ctx.guild.get_channel(int(category_content))
                if not category or not isinstance(category, discord.CategoryChannel):
                    await ctx.send("❌ Invalid Category ID. Setup cancelled. Please run the command again.")
                    return
                config["category_id"] = str(category.id)

            # Step 3: Outer Title
            await ctx.send("**Step 3:** Enter the **Title** for the outer ticket panel (e.g., `📩 Support Tickets`):")
            msg = await self.bot.wait_for('message', check=check, timeout=300.0)
            config["outer_title"] = msg.content.strip()

            # Step 4: Outer Description
            await ctx.send("**Step 4:** Enter the **Description** for the outer ticket panel:")
            msg = await self.bot.wait_for('message', check=check, timeout=300.0)
            config["outer_desc"] = msg.content.strip()

            # Step 5: Button text
            await ctx.send("**Step 5:** Enter the text to display on the **Button** (e.g., `Create Ticket`):")
            msg = await self.bot.wait_for('message', check=check, timeout=300.0)
            config["button_text"] = msg.content.strip()

            # Step 6: Inner Title
            await ctx.send("**Step 6:** Enter the **Title** for the inner ticket message (displayed inside the ticket channel):")
            msg = await self.bot.wait_for('message', check=check, timeout=300.0)
            config["inner_title"] = msg.content.strip()

            # Step 7: Inner Description
            await ctx.send("**Step 7:** Enter the **Description** for the inner ticket message:")
            msg = await self.bot.wait_for('message', check=check, timeout=300.0)
            config["inner_desc"] = msg.content.strip()

        except asyncio.TimeoutError:
            await ctx.send("❌ Setup wizard timed out. Please try again.")
            return
        except Exception as e:
            await ctx.send(f"❌ An error occurred during setup: {e}")
            return

        # Save to database.json
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

            data["guilds"][guild_id_str]["ticket_config"] = config

            with open(db_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Create embed
            outer_embed = discord.Embed(
                title=config["outer_title"],
                description=config["outer_desc"],
                color=discord.Color.from_rgb(88, 101, 242)
            )
            outer_embed.set_timestamp()

            # Create persistent button view
            view = TicketPanelView(self.bot)
            for item in view.children:
                if isinstance(item, discord.ui.Button) and item.custom_id == "create_ticket":
                    item.label = config["button_text"]

            await target_channel.send(embed=outer_embed, view=view)
            await ctx.send(f"✅ **Ticket system setup completed!**\nThe ticket panel has been sent to {target_channel.mention}.")

        except Exception as e:
            print("[TICKET SETUP ERROR]", e)
            await ctx.send("❌ An error occurred while saving the configuration.")

    @setupticket.error
    async def setupticket_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply("You do not have permission to use this command. Administrator permission is required.")
        else:
            await ctx.reply(f"❌ Error: {error}")

async def setup(bot):
    await bot.add_cog(SetupTicket(bot))
