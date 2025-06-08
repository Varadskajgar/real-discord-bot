import discord
from discord.ext import commands
import os

# Your 3 owner IDs for permission checks
OWNER_IDS = {1076200413503701072, 862239588391321600, 1135837895496847503}

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='?', intents=intents, help_command=None)

# Check if author is owner
def is_owner():
    def predicate(ctx):
        return ctx.author.id in OWNER_IDS
    return commands.check(predicate)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

# Custom help command that only owners can use
@bot.command(name='needhelp')
@is_owner()
async def needhelp(ctx):
    embed = discord.Embed(title="Bot Commands Help", color=discord.Color.blue())
    embed.add_field(name="?role @user <role_key>", value="Assign roles", inline=False)
    embed.add_field(name="?poll <question>", value="Create poll", inline=False)
    embed.add_field(name="?dm <user/all> <message>", value="Send DM", inline=False)
    embed.add_field(name="?joiners", value="List tournament joiners", inline=False)
    embed.add_field(name="?announce #channel", value="Send tournament announcement", inline=False)
    embed.add_field(name="?say <message>", value="Bot repeats message", inline=False)
    embed.add_field(name="?ticket commands", value="Use ticket related commands", inline=False)
    embed.add_field(name="?style <text>", value="Send styled text message", inline=False)
    await ctx.send(embed=embed)

# Load all cogs
async def load_all_cogs():
    cogs = [
        "cogs.advanced_autoresponder",
        "cogs.advanced_ticket",
        "cogs.dm_manager",
        "cogs.poll",
        "cogs.role",
        "cogs.styled_responder",
        "cogs.tournament",
        "cogs.utility",
    ]
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f"Loaded {cog}")
        except Exception as e:
            print(f"Failed to load {cog}: {e}")

async def main():
    await load_all_cogs()
    token = os.getenv("TOKEN")
    if not token:
        print("Error: TOKEN environment variable not set")
        return
    await bot.start(token)

import asyncio
asyncio.run(main())
