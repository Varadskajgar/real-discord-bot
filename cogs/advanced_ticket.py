import discord
from discord.ext import commands
import json
import os

OWNER_IDS = {1076200413503701072, 862239588391321600, 1135837895496847503}
RESPONSES_FILE = "data/autoresponses.json"

# Ensure file exists
if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.isfile(RESPONSES_FILE):
    with open(RESPONSES_FILE, "w") as f:
        json.dump({}, f)


class AutoResponder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.load_responses()

    def load_responses(self):
        with open(RESPONSES_FILE, "r") as f:
            self.responses = json.load(f)

    def save_responses(self):
        with open(RESPONSES_FILE, "w") as f:
            json.dump(self.responses, f, indent=4)

    @commands.command()
    async def addresponse(self, ctx, trigger: str, *, reply: str):
        if ctx.author.id not in OWNER_IDS:
            return
        self.responses[trigger.lower()] = reply
        self.save_responses()
        await ctx.send(f"✅ Auto response added for trigger `{trigger}`.")

    @commands.command()
    async def removeresponse(self, ctx, trigger: str):
        if ctx.author.id not in OWNER_IDS:
            return
        if trigger.lower() in self.responses:
            del self.responses[trigger.lower()]
            self.save_responses()
            await ctx.send(f"🗑️ Removed auto response for trigger `{trigger}`.")
        else:
            await ctx.send(f"❌ Trigger `{trigger}` not found.")

    @commands.command()
    async def listresponses(self, ctx):
        if ctx.author.id not in OWNER_IDS:
            return
        if not self.responses:
            await ctx.send("📭 No autoresponses set.")
        else:
            msg = "\n".join(f"`{k}` → {v}" for k, v in self.responses.items())
            await ctx.send(f"📋 **Autoresponses:**\n{msg}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        content = message.content.lower()
        for trigger, reply in self.responses.items():
            if trigger in content:
                await message.channel.send(reply)
                break


async def setup(bot):
    await bot.add_cog(AutoResponder(bot))
