# Overview for suggestions.py
# - Cog for handling suggestions that Discord users can make
# - Allows admins to create panels with a button that sends the user a modal to make a suggestion

# Libraries to import
import discord
from discord.ext import commands
from discord import app_commands
import datetime
from utils.suggestion_management import load_data, save_data, get_next_id, get_panel_id, set_panel_id

# Universal variables
suggestions_channel = 1390343546791268507  # TE Server - #suggestions channel
reviewed_suggestions_channel = 1390343546791268507 # TE Server - #suggestions channel - If this channel is different from suggestions_channel, please review the code in the /approve and /deny slash commands.
bot_id = 981854054760185927 # The ID of the bot on Discord
tick_emoji = "<:Tick:1422628423620366469>" # emoji from TE Discord
tick_emoji_id = 1422628423620366469
cross_emoji = "<:Cross:1422628421913149440>" # emoji from TE Discord
cross_emoji_id = 1422628421913149440

# Suggestions cog
class Suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Load persistent data (JSON)
        self.data = load_data()

    # Discord Modal for users to submit suggestions
    class SuggestModal(discord.ui.Modal):
        def __init__(self, bot):
            super().__init__(title="Making a Suggestion")
            self.bot = bot
            # Text field for suggestion
            self.suggestion_input = discord.ui.TextInput(
                label="Suggestion",
                style=discord.TextStyle.paragraph,
                placeholder="Type a suggestion for the Discord server here!",
                required=True,
                min_length=10,
                max_length=500
            )
            self.add_item(self.suggestion_input)

        async def on_submit(self, interaction: discord.Interaction):
            try:
                await interaction.response.defer()
                # Get suggestion channel
                channel = self.bot.get_channel(suggestions_channel)
                if channel is None:
                    await interaction.followup.send("❌ Could not find the suggestions channel.", ephemeral=True)
                    return

                # Get & delete current suggestion panel
                panel_id = get_panel_id()
                if panel_id:
                    try:
                        suggestion_panel = await channel.fetch_message(panel_id)
                        await suggestion_panel.delete()  # Remove old panel before posting new
                    except:
                        pass

                # Generates unique suggestion ID
                suggestion_id = get_next_id()

                # Creates a Discord embed for the suggestion
                embed = discord.Embed(
                    description=f"**Suggestion:**\n{self.suggestion_input.value}\n\n**Suggested by:** {interaction.user.mention}",
                    timestamp=datetime.datetime.utcnow(),
                    color=0xFFA500
                )
                embed.set_footer(text=f"{self.bot.user.display_name} • Suggestion ID: {suggestion_id}")
                embed.set_thumbnail(url=interaction.user.display_avatar.url)

                # Sends the suggestion message
                bot_message = await channel.send(embed=embed)
                tick_custom_emoji = self.bot.get_emoji(tick_emoji_id)
                cross_custom_emoji = self.bot.get_emoji(cross_emoji_id)
                await bot_message.add_reaction(tick_custom_emoji)
                await bot_message.add_reaction(cross_custom_emoji)

                # Saves suggestion to JSON storage
                data = load_data()
                data["suggestions"].append({
                    "id": suggestion_id,
                    "message_id": bot_message.id,
                    "author_id": interaction.user.id,
                    "content": self.suggestion_input.value,
                    "votes": {tick_emoji: [], cross_emoji: []},
                    "status": "pending",
                    "staff_response": None
                })
                save_data(data)

                # Makes a new suggestion panel
                panel_embed = discord.Embed(
                    description=f"**Make a Suggestion**\n\nIf you have something you would like to suggest relating to TLOU Esports, feel free to press the button below and type in your suggestion on the pop-up screen that follows.",
                    color=0x00FF00
                )
                reviewed_suggestions = self.bot.get_channel(reviewed_suggestions_channel)
                new_panel = await channel.send(f"```yaml\n\nWelcome to Suggestions!\n\n```\n• Before making a suggestion, be sure to check the messages __above__ this one to see suggestions that other members have posted.\n\n• Use the {tick_emoji}/{cross_emoji} reaction buttons to cast your votes! This will help us in the decision-making process when we come to review the community's suggestions.\n\n• It's also a good idea to check {reviewed_suggestions.mention} to view suggestions that have already been approved/rejected by staff.\n\n*Please avoid duplicating any suggestion that has been previously made within a short space of time & try to stick to one suggestion per use, as this will streamline the voting & reviewal processes. Any message that has not been made using the bot is automatically removed from this channel. Usual server rules apply.*", embed=panel_embed, view=Suggestions.SuggestionsPanelButton(self.bot))
                set_panel_id(new_panel.id)

                # Respond to user that sent a modal
                await interaction.followup.send(f"Thanks for your suggestion, {interaction.user.mention}!", ephemeral=True)
            except Exception as e:
                print(f"Error in SuggestModal.on_submit: {e}")
                await interaction.followup.send("❌ Something went wrong while submitting your suggestion.", ephemeral=True)

    # Panel button for users to submit a suggestion
    class SuggestionsPanelButton(discord.ui.View):
        def __init__(self, bot):
            super().__init__(timeout=None)
            self.bot = bot

        @discord.ui.button(label="Send a Suggestion", style=discord.ButtonStyle.green, custom_id="suggest_button")
        async def suggest_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.send_modal(Suggestions.SuggestModal(self.bot))

    # --- SLASH COMMANDS---

    # A back-up slash command '/suggest' that users can make suggestions with, in case the panel fails to work
    @app_commands.command(name="suggest", description="Make a suggestion for the server")
    async def suggest(self, interaction: discord.Interaction):
        await interaction.response.send_modal(Suggestions.SuggestModal(self.bot))
    
    # A command for staff to manually send the suggestion panel
    @app_commands.command(name="suggestion_panel", description="Send the suggestion panel to the suggestions channel")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def suggestion_panel(self, interaction: discord.Interaction):
        channel = self.bot.get_channel(suggestions_channel)

        # Create panel embed
        panel_embed = discord.Embed(
            description=f"**Make a Suggestion**\n\nIf you have something you would like to suggest relating to TLOU Esports, feel free to press the button below and type in your suggestion on the pop-up screen that follows.",
            color=0x00FF00
        )
        reviewed_suggestions = self.bot.get_channel(reviewed_suggestions_channel)

        panel_message = await channel.send(f"```yaml\n\nWelcome to Suggestions!\n\n```\n• Before making a suggestion, be sure to check the messages __above__ this one to see suggestions that other members have posted.\n\n• Use the {tick_emoji}/{cross_emoji} reaction buttons to cast your votes! This will help us in the decision-making process when we come to review the community's suggestions.\n\n• It's also a good idea to check {reviewed_suggestions.mention} to view suggestions that have already been approved/rejected by staff.\n\n*Please avoid duplicating any suggestion that has been previously made within a short space of time & try to stick to one suggestion per use, as this will streamline the voting & reviewal processes. Any message that has not been made using the bot is automatically removed from this channel. Usual server rules apply.*", embed=panel_embed, view=Suggestions.SuggestionsPanelButton(self.bot))

        set_panel_id(panel_message.id)
        await interaction.response.send_message(f"{interaction.user.mention}, the suggestion panel has been sent!", ephemeral=True)

# Setup cog and add it to the bot
async def setup(bot):
    await bot.add_cog(Suggestions(bot))