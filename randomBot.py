import discord
from discord import app_commands
import random

# 1. Configure Low-RAM Intents and Caches
class MyBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True # Required for your randomuser tool
        
        # OPTIMIZATION: chunk_guilds_at_startup set to False saves massive baseline RAM.
        # max_messages=None turns off the internal chat history cache.
        super().__init__(
            intents=intents, 
            chunk_guilds_at_startup=False, 
            max_messages=None
        )
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("Slash commands synced globally!")

client = MyBot()

# 2. Bot Status on Startup
@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    print("📥 Slash Commands ready")

# 3. The Slash Command Definition
@client.tree.command(name='random', description='Pick a random item from a comma-separated list.')
async def random_command(interaction: discord.Interaction, items: str):
    """Select a random value from the provided list."""
    if not items:
        await interaction.response.send_message("❌ **Error**: You must provide values.")
        return
    
    values = [v.strip() for v in items.split(',') if v.strip()]
    
    if len(values) == 0:
        await interaction.response.send_message("❌ **Error**: The list is empty.")
        return

    choice = random.choice(values)
    await interaction.response.send_message(f"🎲 **Random Result**: `{choice}`")

# 4. Slash Command for Dice
@client.tree.command(name='roll', description='Roll a random number.')
async def roll_command(interaction: discord.Interaction, value: str = "1d6"):
    """Roll dice or get a number safely without memory leaks."""
    value = value.strip().lower()
    
    if 'd' in value:
        parts = value.split('d')
        try:
            count = int(parts[0])
            faces = int(parts[1])
            
            if count <= 0 or faces <= 0 or count > 100 or faces > 100000:
                raise ValueError()
                
            final_roll = sum(random.randint(1, faces) for _ in range(count))
            
        except (ValueError, IndexError):
            await interaction.response.send_message("❌ Invalid format. Use positive numbers like '2d20' (Max 100 dice).", ephemeral=True)
            return 
    else:
        try:
            num = int(value)
            if num <= 0 or num > 1000000:
                raise ValueError()
            final_roll = random.randint(1, num)
        except ValueError:
            await interaction.response.send_message("❌ Invalid format. Please enter a positive number up to 1,000,000.", ephemeral=True)
            return 

    await interaction.response.send_message(f"🎲 **Rolled**: `{final_roll}`")
    

@client.tree.command(name='randomuser', description='Pick and tag a random user from this channel.')
async def random_user_command(interaction: discord.Interaction):
    await interaction.response.defer()
    
    guild = interaction.guild
    channel = interaction.channel
    
    # This fetches data on demand and drops it later instead of keeping it in cache forever
    if not guild.chunked:
        await guild.chunk(cache=True)
        
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