import discord
from discord.ext import commands
import os
import asyncio

# Owner IDs
OWNER_IDS = {1076200413503701072, 862239588391321600, 1135837895496847503}

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="+", intents=intents)
bot.remove_command("help")

# Custom help command only for owners
@bot.command()
async def help(ctx):
    if ctx.author.id not in OWNER_IDS:
        return

    embed = discord.Embed(
        title="📘 All Bot Commands",
        description="Here's a list of all commands available to owners.",
        color=discord.Color.blue()
    )

    embed.add_field(name="🎟️ Ticket Commands", value=(
        "`+setticketchannel`\n"
        "`+add <user>`\n"
        "`+remove <user>`\n"
        "`+close`\n"
        "`+reopen`\n"
        "`+perclose`"
    ), inline=False)

    embed.add_field(name="⚙️ Utility", value="`+say <message>`", inline=False)
    embed.add_field(name="📢 Polls", value="`+poll <question>`", inline=False)
    embed.add_field(name="🔐 Role", value="`+role @user <role_key>`", inline=False)
    embed.add_field(name="📨 DM Manager", value=(
        "`+dm all <message>`\n"
        "`+dm <@user> <message>`"
    ), inline=False)

    embed.add_field(name="🏆 Tournament", value=(
        "`+announce`\n"
        "`+joiners`\n"
        "`+clearjoiners`\n"
        "`+match <info>`\n"
        "`+dm joiners <id/pass>`"
    ), inline=False)

    embed.add_field(name="🅰️ Styled Responder", value="`+name change <text>`", inline=False)
    embed.add_field(name="🤖 Autoresponder", value="Automatic reply on specific trigger words", inline=False)

    await ctx.send(embed=embed)

async def main():
    token = os.getenv("TOKEN")

    extensions = [
        "cogs.advanced_autoresponder",
        "cogs.advanced_ticket",
        "cogs.dm_manager",
        "cogs.poll",
        "cogs.role",
        "cogs.styled_responder",
        "cogs.tournament",
        "cogs.utility",
        "auto_namechange.py",
    ]

    for ext in extensions:
        try:
            await bot.load_extension(ext)
            print(f"✅ Loaded {ext}")
        except Exception as e:
            print(f"❌ Failed to load {ext}: {e}")

    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
