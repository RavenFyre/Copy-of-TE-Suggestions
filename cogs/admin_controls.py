# Overview for admin_controls.py
# - Cog for admin commands
# - Contains slash commands to approve/reject suggestions and view votes for a certain suggestion

# Libraries to import
import discord
from discord.ext import commands
from discord import app_commands
from discord.utils import get
import datetime
from utils.suggestion_management import load_data, save_data, get_panel_id, set_panel_id
from cogs.suggestions import Suggestions

# Universal variables
suggestions_channel = 1390343546791268507  # TE Server - #suggestions channel
reviewed_suggestions_channel = 1390343546791268507 # TE Server - #suggestions channel - If this channel is different from suggestions_channel, please review the code in the /approve and /deny slash commands.
bot_id = 981854054760185927 # The ID of the bot on Discord
tick_emoji = "<:Tick:1422628423620366469>" # emoji from TE Discord
cross_emoji = "<:Cross:1422628421913149440>" # emoji from TE Discord

# Admin controls cog
class AdminControls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Slash command for admins to approve suggestions
    @app_commands.command(name="approve", description="Approve and finalise a suggestion")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(suggestion_id="The ID of the suggestion to approve", reason="Optional staff response")
    async def approve(self, interaction: discord.Interaction, suggestion_id: int, reason: str = None):
        data = load_data()
        # If suggestion_id comes from user input (string)
        int_suggestion_id = int(suggestion_id)
        # Load all suggestions from JSON
        data = load_data()

        # Initialize suggestion variable
        suggestion = None

        # Loop through each suggestion in the list
        for s in data["suggestions"]:
            # s is a single suggestion dictionary
            if s["id"] == int_suggestion_id:
                suggestion = s  # Found the suggestion
                break  # Stop looping once found

        # Check if we found it
        if suggestion is None:
            await interaction.response.send_message(
                f"{interaction.user.mention}, this is not a valid Suggestion ID.",
                ephemeral=True
            )
        else:
            # suggestion now contains the dictionary of the matching suggestion
            # You can continue with approval logic here
            print("Found suggestion:", suggestion)

        # Suggestion ID not found
        if not suggestion:
            await interaction.response.send_message(f"{interaction.user.mention}, this is not a valid Suggestion ID.", ephemeral=True)
            return

        # Update suggestion status and staff response if given
        suggestion["status"] = "approved"
        if reason:
            suggestion["staff_response"] = reason
        save_data(data)

        # Get suggestion
        channel = self.bot.get_channel(suggestions_channel)
        suggestion_message = await channel.fetch_message(suggestion['message_id'])

        # Get author of the suggestion
        author = await self.bot.fetch_user(suggestion['author_id'])

        # Discord Embed that posts when suggestion is accepted
        embed_description = (
            f"The suggestion below is now closed for voting and has been **approved** by staff!\n\n"
            f"**Suggestion:** {suggestion['content']}\n\n"
            f"**Suggested by:** {author.mention}\n\n"
            f"**Voting results:**\n{tick_emoji}: {len(suggestion['votes'][tick_emoji])}\n"
            f"{cross_emoji}: {len(suggestion['votes'][cross_emoji])}\n\n"
            f"**Approved by:** {interaction.user.mention}"
        )
        if reason:
            embed_description += f"\n\n**Staff Response:**\n{reason}"

        embed = discord.Embed(description=embed_description, timestamp=datetime.datetime.utcnow(), color=0x00FF00)
        embed.set_footer(text=f"{self.bot.user.display_name} • Suggestion ID: {suggestion_id}")

        # Get current suggestion panel
        panel_id = get_panel_id()
        if panel_id:
            try:
                suggestion_panel = await channel.fetch_message(panel_id)
                await suggestion_panel.delete()  # Remove old panel before posting new
            except:
                pass

        # Post embed to reviewed suggestions channel
        reviewed_channel = self.bot.get_channel(reviewed_suggestions_channel)
        await reviewed_channel.send(embed=embed)

        # Makes a new suggestion panel
        panel_embed = discord.Embed(
            description=f"**Make a Suggestion**\n\nIf you have something you would like to suggest relating to TLOU Esports, feel free to press the button below and type in your suggestion on the pop-up screen that follows.",
            color=0x00FF00
            )
        new_panel = await channel.send(f"```yaml\n\nWelcome to Suggestions!\n\n```\n• Before making a suggestion, be sure to check the messages __above__ this one to see suggestions that other members have posted.\n\n• Use the {tick_emoji}/{cross_emoji} reaction buttons to cast your votes! This will help us in the decision-making process when we come to review the community's suggestions.\n\n• It's also a good idea to check {reviewed_channel.mention} to view suggestions that have already been approved/rejected by staff.\n\n*Please avoid duplicating any suggestion that has been previously made within a short space of time & try to stick to one suggestion per use, as this will streamline the voting & reviewal processes. Any message that has not been made using the bot is automatically removed from this channel. Usual server rules apply.*", embed=panel_embed, view=Suggestions.SuggestionsPanelButton(self.bot))
        set_panel_id(new_panel.id)

        await suggestion_message.delete() # removes the original suggestion
        await interaction.response.send_message(f"{interaction.user.mention}, suggestion {suggestion_id} approved!", ephemeral=True)

    # ---

    # Slash command for admins to reject suggestions
    @app_commands.command(name="reject", description="Reject and finalise a suggestion")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(suggestion_id="The ID of the suggestion to reject", reason="Optional staff response")
    async def reject(self, interaction: discord.Interaction, suggestion_id: int, reason: str = None):
        data = load_data()
        # If suggestion_id comes from user input (string)
        int_suggestion_id = int(suggestion_id)
        # Load all suggestions from JSON
        data = load_data()

        # Initialize suggestion variable
        suggestion = None

        # Loop through each suggestion in the list
        for s in data["suggestions"]:
            # s is a single suggestion dictionary
            if s["id"] == int_suggestion_id:
                suggestion = s  # Found the suggestion
                break  # Stop looping once found

        # Check if we found it
        if suggestion is None:
            await interaction.response.send_message(
                f"{interaction.user.mention}, this is not a valid Suggestion ID.",
                ephemeral=True
            )
        else:
            # suggestion now contains the dictionary of the matching suggestion
            # You can continue with approval logic here
            print("Found suggestion:", suggestion)

        # Suggestion ID not found
        if not suggestion:
            await interaction.response.send_message(f"{interaction.user.mention}, this is not a valid Suggestion ID.", ephemeral=True)
            return

        # Update suggestion status and staff response if given
        suggestion["status"] = "rejected"
        if reason:
            suggestion["staff_response"] = reason
        save_data(data)

        # Get original suggestion message
        channel = self.bot.get_channel(suggestions_channel)
        suggestion_message = await channel.fetch_message(suggestion['message_id'])

        # Get author of the suggestion
        author = await self.bot.fetch_user(suggestion['author_id'])

        # Discord Embed that posts when suggestion is denied
        embed_description = (
            f"The suggestion below is now closed for voting and has been **rejected** by staff.\n\n"
            f"**Suggestion:** {suggestion['content']}\n\n"
            f"**Suggested by:** {author.mention}\n\n"
            f"**Voting results:**\n{tick_emoji}: {len(suggestion['votes'][tick_emoji])}\n"
            f"{cross_emoji}: {len(suggestion['votes'][cross_emoji])}\n\n"
            f"**Rejected by:** {interaction.user.mention}"
        )
        if reason:
            embed_description += f"\n\n**Staff Response:**\n{reason}"

        embed = discord.Embed(description=embed_description, timestamp=datetime.datetime.utcnow(), color=0xFF0000)
        embed.set_footer(text=f"{self.bot.user.display_name} • Suggestion ID: {suggestion_id}")

        # Get current suggestion panel
        panel_id = get_panel_id()
        if panel_id:
            try:
                suggestion_panel = await channel.fetch_message(panel_id)
                await suggestion_panel.delete()  # Remove old panel before posting new
            except:
                pass

        # Post embed to reviewed suggestions channel
        reviewed_channel = self.bot.get_channel(reviewed_suggestions_channel)
        await reviewed_channel.send(embed=embed)

        # Makes a new suggestion panel
        panel_embed = discord.Embed(
            description=f"**Make a Suggestion**\n\nIf you have something you would like to suggest relating to TLOU Esports, feel free to press the button below and type in your suggestion on the pop-up screen that follows.",
            color=0x00FF00
            )
        new_panel = await channel.send(f"```yaml\n\nWelcome to Suggestions!\n\n```\n• Before making a suggestion, be sure to check the messages __above__ this one to see suggestions that other members have posted.\n\n• Use the {tick_emoji}/{cross_emoji} reaction buttons to cast your votes! This will help us in the decision-making process when we come to review the community's suggestions.\n\n• It's also a good idea to check {reviewed_channel.mention} to view suggestions that have already been approved/rejected by staff.\n\n*Please avoid duplicating any suggestion that has been previously made within a short space of time & try to stick to one suggestion per use, as this will streamline the voting & reviewal processes. Any message that has not been made using the bot is automatically removed from this channel. Usual server rules apply.*", embed=panel_embed, view=Suggestions.SuggestionsPanelButton(self.bot))
        set_panel_id(new_panel.id)

        await suggestion_message.delete() # removes the original suggestion
        await interaction.response.send_message(f"{interaction.user.mention}, suggestion {suggestion_id} rejected!", ephemeral=True)

# ---

    # Slash command for admins to view the votes of a given suggestion
    @app_commands.command(name="votes", description="View the votes & see usernames of who voted for a suggestion")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(suggestion_id="The ID of the suggestion to view votes for")
    async def votes(self, interaction: discord.Interaction, suggestion_id: int):
        data = load_data()
        suggestion = next((s for s in data["suggestions"] if s["id"] == suggestion_id), None)

        # Suggestion ID not found
        if not suggestion:
            await interaction.response.send_message(f"{interaction.user.mention}, this is not a valid Suggestion ID.", ephemeral=True)
            return

        # Display votes
        tick_users = "\n".join([f"<@{uid}>" for uid in suggestion["votes"][tick_emoji]]) or "No votes"
        cross_users = "\n".join([f"<@{uid}>" for uid in suggestion["votes"][cross_emoji]]) or "No votes"

        # Get author of the suggestion
        author = await self.bot.fetch_user(suggestion['author_id'])

        embed = discord.Embed(
            description=f"{interaction.user.mention}, here are the voting results for the following suggestion:\n\n"
                        f"**Suggestion:** {suggestion['content']}\n\n"
                        f"**Suggested by:** {author.mention}\n\n"
                        f"**{tick_emoji}: {len(suggestion['votes'][tick_emoji])}**\n{tick_users}\n\n"
                        f"**{cross_emoji}: {len(suggestion['votes'][cross_emoji])}**\n{cross_users}",
            timestamp=datetime.datetime.utcnow(),
            color=0x8F00FF
        )
        embed.set_footer(text=f"{self.bot.user.display_name} • Suggestion ID: {suggestion_id}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Setup cog and add it to the bot
async def setup(bot):
    await bot.add_cog(AdminControls(bot))