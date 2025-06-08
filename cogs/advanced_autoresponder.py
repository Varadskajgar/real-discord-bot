from discord.ext import commands
import discord
import json
import os

OWNER_IDS = {1076200413503701072, 862239588391321600, 1135837895496847503}

RESPONSES_FILE = "responses.json"

def load_responses():
    if not os.path.isfile(RESPONSES_FILE):
        with open(RESPONSES_FILE, "w") as f:
            json.dump({}, f)
    with open(RESPONSES_FILE, "r") as f:
        return json.load(f)

def save_responses(data):
    with open(RESPONSES_FILE, "w") as f:
        json.dump(data, f, indent=4)

class AdvancedAutoResponder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.responses = load_responses()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        for keyword, reply in self.responses.items():
            if keyword.lower() in message.content.lower():
                await message.channel.send(reply)
                break

    @commands.command()
    async def addresponse(self, ctx, keyword: str, *, reply: str):
        if ctx.author.id not in OWNER_IDS:
            return
        self.responses[keyword.lower()] = reply
        save_responses(self.responses)
        await ctx.send(f"Added response for keyword `{keyword}`.")

    @commands.command()
    async def delresponse(self, ctx, keyword: str):
        if ctx.author.id not in OWNER_IDS:
            return
        if keyword.lower() in self.responses:
            del self.responses[keyword.lower()]
            save_responses(self.responses)
            await ctx.send(f"Deleted response for keyword `{keyword}`.")
        else:
            await ctx.send(f"No response found for keyword `{keyword}`.")

    @commands.command()
    async def listresponses(self, ctx):
        if ctx.author.id not in OWNER_IDS:
            return
        if not self.responses:
            await ctx.send("No auto-responses set.")
            return
        embed = discord.Embed(title="Auto Responses", color=discord.Color.green())
        for k, v in self.responses.items():
            embed.add_field(name=k, value=v, inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AdvancedAutoResponder(bot))
