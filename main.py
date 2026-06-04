import os
import json
import datetime
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

token  = os.getenv("DISCORD_TOKEN")
prefix = os.getenv("PREFIX", "!")

if not token or token == "TU_DISCORD_TOKEN_AQUI":
    print("ERROR: Please configure a valid Discord Bot Token in the .env file.")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True
intents.members         = True

class CustomBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=prefix, intents=intents, help_command=None)
        self.prefix_str = prefix

    # ── Moderation logger ──────────────────────────────────────────────────────
    def log_moderation(self, action, target, moderator, reason):
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.json")
        data = {}
        if os.path.exists(db_path):
            try:
                with open(db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}
        data.setdefault("moderation_logs", []).append({
            "timestamp":  datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "action":     action,
            "target":     {"id": target.id, "tag": str(target)},
            "moderator":  {"id": moderator.id, "tag": str(moderator)},
            "reason":     reason or "No reason provided"
        })
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ── Economy helpers ────────────────────────────────────────────────────────
    def get_economy(self, guild_id: str, user_id: str):
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.json")
        data = {}
        if os.path.exists(db_path):
            try:
                with open(db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}
        data.setdefault("guilds", {}).setdefault(guild_id, {}).setdefault("economy", {})
        data["guilds"][guild_id]["economy"].setdefault(user_id, {})
        user = data["guilds"][guild_id]["economy"][user_id]
        user.setdefault("cash", 0)
        user.setdefault("bank", 0)
        user.setdefault("last_daily", None)
        user.setdefault("last_work", None)
        user.setdefault("last_rob", None)
        return data, user

    def save_economy(self, data):
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.json")
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ── Setup hook: register views + load cogs ─────────────────────────────────
    async def setup_hook(self):
        # Register persistent ticket views
        try:
            from commands.config.setupticket import TicketPanelView, CloseTicketView
            self.add_view(TicketPanelView(self))
            self.add_view(CloseTicketView())
            print("[LOG] Registered persistent ticket views.")
        except Exception as e:
            print(f"[ERROR] Failed to register ticket views: {e}")

        # Recursively walk subfolders inside commands/
        commands_dir = os.path.join(os.path.dirname(__file__), "commands")
        for subfolder in os.listdir(commands_dir):
            subfolder_path = os.path.join(commands_dir, subfolder)
            if not os.path.isdir(subfolder_path):
                continue
            for filename in os.listdir(subfolder_path):
                if filename.endswith(".py") and filename != "__init__.py":
                    cog_name = f"commands.{subfolder}.{filename[:-3]}"
                    try:
                        await self.load_extension(cog_name)
                        print(f"[LOG] [{subfolder.title()}] Loaded cog: {filename[:-3]}")
                    except Exception as e:
                        print(f"[ERROR] Failed to load {cog_name}: {e}")

    async def on_ready(self):
        print(f"[LOG] Bot online as {self.user} (ID: {self.user.id})")
        print(f"[LOG] Prefix: \"{self.prefix_str}\" | Commands loaded: {len(self.commands)}")

    # ── Welcome ────────────────────────────────────────────────────────────────
    async def on_member_join(self, member):
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.json")
        if not os.path.exists(db_path): return
        try:
            with open(db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            cfg = data.get("guilds", {}).get(str(member.guild.id), {})
            ch_id = cfg.get("welcome_channel")
            if ch_id:
                channel = member.guild.get_channel(int(ch_id))
                if channel:
                    raw_template = cfg.get("welcome_message", "Welcome to **{server}**, {user}!\nWe now have **{count}** members.")
                    description = raw_template.replace("{user}", member.mention).replace("{server}", member.guild.name).replace("{count}", str(member.guild.member_count))
                    
                    embed = discord.Embed(
                        title="Welcome!",
                        description=description,
                        color=discord.Color.from_rgb(88, 101, 242)
                    )
                    embed.set_thumbnail(url=member.display_avatar.url)
                    embed.set_timestamp()
                    await channel.send(embed=embed)
        except Exception as e:
            print("[WELCOME ERROR]", e)

    # ── Goodbye ────────────────────────────────────────────────────────────────
    async def on_member_remove(self, member):
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.json")
        if not os.path.exists(db_path): return
        try:
            with open(db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            cfg = data.get("guilds", {}).get(str(member.guild.id), {})
            ch_id = cfg.get("goodbye_channel")
            if ch_id:
                channel = member.guild.get_channel(int(ch_id))
                if channel:
                    raw_template = cfg.get("goodbye_message", "**{user}** has left **{server}**.\nWe now have **{count}** members.")
                    description = raw_template.replace("{user}", str(member)).replace("{server}", member.guild.name).replace("{count}", str(member.guild.member_count))
                    
                    embed = discord.Embed(
                        title="Goodbye!",
                        description=description,
                        color=discord.Color.from_rgb(237, 66, 69)
                    )
                    embed.set_thumbnail(url=member.display_avatar.url)
                    embed.set_timestamp()
                    await channel.send(embed=embed)
        except Exception as e:
            print("[GOODBYE ERROR]", e)

bot = CustomBot()

if __name__ == "__main__":
    bot.run(token)
