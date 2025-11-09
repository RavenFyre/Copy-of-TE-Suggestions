import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime
import aiosqlite


class Reminders(commands.Cog):
    FIXED_TIMEZONE_OFFSET = 8  # GMT+8

    def __init__(self, bot):
        self.bot = bot
        self.check_reminders.start()

    # ---------- DB INITIALIZATION ----------
    async def init_db(self):
        async with aiosqlite.connect("reminders.db") as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                    guild_id INTEGER,
                    channel_id INTEGER,
                    time TEXT,
                    message TEXT
                )
            """)
            await db.commit()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.init_db()
        print("[Reminder Cog] Database initialized")

    # ---------- REMINDER LOOP ----------
    @tasks.loop(seconds=30)
    async def check_reminders(self):
        now_utc = datetime.utcnow()
        now_gmt8 = now_utc.replace(hour=(now_utc.hour + self.FIXED_TIMEZONE_OFFSET) % 24)

        current_time = now_gmt8.strftime("%H:%M")

        async with aiosqlite.connect("reminders.db") as db:
            rows = await db.execute_fetchall(
                "SELECT channel_id, time, message FROM reminders"
            )

        for channel_id, reminder_time, message in rows:
            if reminder_time == current_time:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    await channel.send(message)

    @check_reminders.before_loop
    async def before_check(self):
        print("Reminder loop waiting for bot ready...")
        await self.bot.wait_until_ready()

    # ---------- SLASH COMMANDS ----------
    @app_commands.command(name="add_reminder", description="Add a reminder (time is GMT+8)")
    @app_commands.describe(
        time="Time in HH:MM (24h GMT+8)",
        message="What should the bot say?",
        mention="(Optional) Mention a user or role"
    )
    async def add_reminder(
        self,
        interaction: discord.Interaction,
        time: str,
        message: str,
        mention: discord.Role | discord.User | None = None,
    ):
        """Slash command: /add_reminder time:HH:MM message:'text' mention:@user_or_role"""
    
        # Validate time format
        try:
            datetime.strptime(time, "%H:%M")
        except ValueError:
            return await interaction.response.send_message(
                "❌ Time must be in **HH:MM (24h format, GMT+8)**",
                ephemeral=True
            )
    
        # Store message including mention (if supplied)
        final_message = f"{mention.mention}\n{message}" if mention else message
    
        async with aiosqlite.connect("reminders.db") as db:
            await db.execute(
                "INSERT INTO reminders (guild_id, channel_id, time, message) VALUES (?, ?, ?, ?)",
                (interaction.guild_id, interaction.channel_id, time, final_message)
            )
            await db.commit()
    
        await interaction.response.send_message(
            f"✅ Reminder added for **{time} GMT+8**\n"
            f"Message: `{message}`"
            + (f"\nWill mention: {mention.mention}" if mention else "")
        )

    
    @app_commands.command(name="list_reminders", description="List all reminders for this server")
    async def list_reminders(self, interaction: discord.Interaction):
        async with aiosqlite.connect("reminders.db") as db:
            rows = await db.execute_fetchall(
                "SELECT time, message FROM reminders WHERE guild_id = ?",
                (interaction.guild_id,)
            )

        if not rows:
            return await interaction.response.send_message("No reminders set.", ephemeral=True)

        formatted = "\n".join([f"• **{time}** GMT+8 → {msg}" for time, msg in rows])
        await interaction.response.send_message(f"📅 **Reminders:**\n{formatted}")

    @app_commands.command(name="delete_reminder", description="Delete a reminder by time (HH:MM)")
    async def delete_reminder(self, interaction: discord.Interaction, time: str):
        async with aiosqlite.connect("reminders.db") as db:
            await db.execute(
                "DELETE FROM reminders WHERE guild_id = ? AND time = ?",
                (interaction.guild_id, time)
            )
            await db.commit()

        await interaction.response.send_message(
            f"🗑️ Removed reminder set for **{time} GMT+8**"
        )


async def setup(bot):
    await bot.add_cog(Reminders(bot))
