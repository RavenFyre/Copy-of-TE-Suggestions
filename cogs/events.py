# Overview for events.py
# - Ensures users cannot select more than one reaction at a time when voting
# - Auto-deletes messages to ensure the suggestions channel is command-only
# - Keeps track of votes in JSON

# Libraries to import
import discord
from discord.ext import commands
from utils.suggestion_management import load_data, save_data

suggestions_channel = 1390343546791268507  # TE Server - #suggestions channel
tick_emoji = "<:Tick:1422628423620366469>" 
cross_emoji = "<:Cross:1422628421913149440>" 

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- reaction add ---
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.channel_id != suggestions_channel:
            return
        if payload.user_id == self.bot.user.id:
            return  # ignore bot itself

        # Build emoji string exactly like in JSON
        emoji_str = f"<:{payload.emoji.name}:{payload.emoji.id}>" if payload.emoji.id else str(payload.emoji)
        print(f"[ADD] User {payload.user_id} reacted with {emoji_str}")

        # Load suggestions
        data = load_data()
        suggestion = next((s for s in data["suggestions"] if s["message_id"] == payload.message_id), None)
        if not suggestion:
            print(f"[ADD] No suggestion found for message {payload.message_id}")
            return

        # Fetch the message to manage reactions
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = self.bot.get_user(payload.user_id)

        # Enforce single vote: if they reacted tick, remove their cross; if cross, remove their tick
        if emoji_str == tick_emoji and payload.user_id in suggestion["votes"].get(cross_emoji, []):
            await message.remove_reaction(cross_emoji, user)
            suggestion["votes"][cross_emoji].remove(payload.user_id)
            print(f"[ADD] Removed {payload.user_id} from {cross_emoji} (switched to tick)")
        elif emoji_str == cross_emoji and payload.user_id in suggestion["votes"].get(tick_emoji, []):
            await message.remove_reaction(tick_emoji, user)
            suggestion["votes"][tick_emoji].remove(payload.user_id)
            print(f"[ADD] Removed {payload.user_id} from {tick_emoji} (switched to cross)")

        # Add the new vote
        if emoji_str in suggestion["votes"]:
            if payload.user_id not in suggestion["votes"][emoji_str]:
                suggestion["votes"][emoji_str].append(payload.user_id)
                print(f"[ADD] Added {payload.user_id} to {emoji_str}")
        else:
            print(f"[ADD] Emoji {emoji_str} not tracked in suggestion votes")

        save_data(data)
        print(f"[ADD] Data saved: {suggestion['votes']}")

    # --- reaction remove ---
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.channel_id != suggestions_channel:
            return
        if payload.user_id == self.bot.user.id:
            return  # ignore bot itself

        # Build emoji string
        emoji_str = f"<:{payload.emoji.name}:{payload.emoji.id}>" if payload.emoji.id else str(payload.emoji)
        print(f"[REMOVE] User {payload.user_id} removed {emoji_str}")

        # Load suggestions
        data = load_data()
        suggestion = next((s for s in data["suggestions"] if s["message_id"] == payload.message_id), None)
        if not suggestion:
            print(f"[REMOVE] No suggestion found for message {payload.message_id}")
            return

        # Update votes
        if emoji_str in suggestion["votes"]:
            if payload.user_id in suggestion["votes"][emoji_str]:
                suggestion["votes"][emoji_str].remove(payload.user_id)
                print(f"[REMOVE] Removed {payload.user_id} from {emoji_str}")
            else:
                print(f"[REMOVE] {payload.user_id} was not in {emoji_str}")
        else:
            print(f"[REMOVE] Emoji {emoji_str} not tracked in suggestion votes")

        save_data(data)
        print(f"[REMOVE] Data saved: {suggestion['votes']}")

async def setup(bot):
    await bot.add_cog(Events(bot))