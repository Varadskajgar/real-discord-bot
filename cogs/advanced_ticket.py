import discord
from discord.ext import commands
import json
import os

OWNER_IDS = {1076200413503701072, 862239588391321600, 1135837895496847503}
FILE_PATH = "data/autoresponses.json"

class AutoResponder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.responses = {}
        self.load_responses()

    def load_responses(self):
        if not os.path.exists("data"):
            os.makedirs("data")
        if not os.path.exists(FILE_PATH):
            with open(FILE_PATH, "w") as f:
                json.dump({}, f)
        with open(FILE_PATH, "r") as f:
            self.responses = json.load(f)

    def save_responses(self):
        with open(FILE_PATH, "w") as f:
            json.dump(self.responses, f, indent=4)

    @commands.command()
    async def addresponse(self, ctx, trigger: str, *, response: str):
        if ctx.author.id not in OWNER_IDS:
            return
        trigger = trigger.lower()
        self.responses[trigger] = response
        self.save_responses()
        await ctx.send(f"✅ Added auto-response for `{trigger}`.")

    @commands.command()
    async def removeresponse(self, ctx, trigger: str):
        if ctx.author.id not in OWNER_IDS:
            return
        trigger = trigger.lower()
        if trigger in self.responses:
            del self.responses[trigger]
            self.save_responses()
            await ctx.send(f"🗑️ Removed auto-response for `{trigger}`.")
        else:
            await ctx.send(f"❌ No auto-response found for `{trigger}`.")

    @commands.command()
    async def listresponses(self, ctx):
        if ctx.author.id not in OWNER_IDS:
            return
        if not self.responses:
            await ctx.send("📭 No auto-responses set.")
        else:
            text = "\n".join(f"`{k}` → {v}" for k, v in self.responses.items())
            await ctx.send(f"📋 **Auto-responses:**\n{text}")

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
