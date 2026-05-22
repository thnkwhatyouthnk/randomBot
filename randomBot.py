import discord
from discord import app_commands
import random

# 1. Configure Intents
class MyBot(discord.Client):
    def __init__(self):
        # Setting all intents is required for command syncing
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents, chunk_guilds_at_startup=True)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # This forces the bot to sync commands globally on startup
        await self.tree.sync()
        print("Slash commands synced globally!")

# client = commands.Bot(command_prefix='!', intents=intents)
client = MyBot()

# 2. Bot Status on Startup
@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    print("📥 Slash Commands ready (Must be registered in Developer Portal)")

# 3. The Slash Command Definition
@client.tree.command(name='random', description='Pick a random item from a comma-separated list.')
async def random_command(interaction: discord.Interaction, items: str):
    """Select a random value from the provided list."""
    
    # Parse the input string
    if not items:
        await interaction.response.send_message("❌ **Error**: You must provide values.")
        return
    
    # Split by comma and strip whitespace
    values = [v.strip() for v in items.split(',') if v.strip()]
    
    if len(values) == 0:
        await interaction.response.send_message("❌ **Error**: The list is empty.")
        return

    # Random Selection
    choice = random.choice(values)
    
    # Send Result
    await interaction.response.send_message(f"🎲 **Random Result**: `{choice}`")

# 4. Optional: Slash Command for Dice (Extra Utility)
@client.tree.command(name='roll', description='Roll a random number.')
async def roll_command(interaction: discord.Interaction, value: str = "1d6"):
    """Roll dice or get a number safely without memory leaks."""
    
    # Clean the input to prevent basic string manipulation exploits
    value = value.strip().lower()
    
    if 'd' in value:
        parts = value.split('d')
        try:
            count = int(parts[0])
            faces = int(parts[1])
            
            # Put an upper ceiling to protect your 1GB RAM machine from abuse (e.g., 999999d999999)
            if count <= 0 or faces <= 0 or count > 100 or faces > 100000:
                raise ValueError()
                
            # If you want to simulate rolling 'count' times, sum them up
            final_roll = sum(random.randint(1, faces) for _ in range(count))
            
        except (ValueError, IndexError):
            await interaction.response.send_message("❌ Invalid format. Use positive numbers like '2d20' (Max 100 dice).", ephemeral=True)
            return # <-- CRITICAL: Stops execution and saves RAM
    else:
        try:
            num = int(value)
            if num <= 0 or num > 1000000:
                raise ValueError()
            final_roll = random.randint(1, num)
        except ValueError:
            await interaction.response.send_message("❌ Invalid format. Please enter a positive number up to 1,000,000.", ephemeral=True)
            return # <-- CRITICAL: Stops execution and saves RAM

    # Only one response path can ever be reached now
    await interaction.response.send_message(f"🎲 **Rolled**: `{final_roll}`")
    

@client.tree.command(name='randomuser', description='Pick and tag a random user from this channel.')
async def random_user_command(interaction: discord.Interaction):
    await interaction.response.defer()
    
    guild = interaction.guild
    channel = interaction.channel
    
    # Safely pull member lists if your 1GB instance hasn't loaded them yet
    if not guild.chunked:
        await guild.chunk(cache=True)
        
    # Check if the member can view/read this specific text channel
    eligible_users = [
        member for member in channel.members 
        if not member.bot and channel.permissions_for(member).read_messages
    ]
    
    if not eligible_users:
        await interaction.followup.send("❌ Could not find any active human users with read access in this channel.")
        return

    chosen_user = random.choice(eligible_users)
    await interaction.followup.send(f"🎯 The chosen one is {chosen_user.mention}!")


# 5. Run the Bot
client.run('YOUR_BOT_TOKEN_HERE')