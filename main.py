# Overview
# - Sets up the bot with libraries & intents
# - Loads all files from the "cogs" folder
# - Starts the bot

# Libraries to import
import os
from dotenv import load_dotenv
from discord.ext import commands
import discord
from cogs.suggestions import Suggestions

# Bot definition & intents
description = "A bot for making, voting on & approving suggestions, coded by Raven Fyre for use in the TLOU Esports Discord server."
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", description=description, help_command=None, intents=intents)

# Initial start-up event when the bot first runs or restarts
@bot.event
async def on_ready():
    try:
        bot.add_view(Suggestions.SuggestionsPanelButton(bot))
    except:
        pass
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='TLOU Esports'))
    await bot.tree.sync()
    print("TE Suggestions is online! Commands synced.")

# Load cogs
async def load_cogs():
    await bot.load_extension("cogs.suggestions")
    await bot.load_extension("cogs.events")
    await bot.load_extension("cogs.admin_controls")
    await bot.load_extension("cogs.fis_pay_reminders")

# Run bot
async def main():
    async with bot:
        await load_cogs()
        load_dotenv()
        await bot.start(os.getenv("BOT_TOKEN"))

# This code runs only if main.py is executed directly.
if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
