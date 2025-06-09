import discord
from discord.ext import commands
import json
import os

DM_LIST_FILE = "dmlist.json"

class DMServerAdder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dmlist = set()
        self.load_dmlist()

    def load_dmlist(self):
        if os.path.exists(DM_LIST_FILE):
            with open(DM_LIST_FILE, "r") as f:
                try:
                    self.dmlist = set(json.load(f))
                except json.JSONDecodeError:
                    self.dmlist = set()

    def save_dmlist(self):
        with open(DM_LIST_FILE, "w") as f:
            json.dump(list(self.dmlist), f)

    @commands.command(name="adddmserver")
    async def add_dm_server(self, ctx, server_id: int):
        if ctx.author.id not in {1076200413503701072, 862239588391321600, 1135837895496847503}:
            return await ctx.send("❌ You do not have permission to use this command.")

        guild = self.bot.get_guild(server_id)
        if not guild:
            return await ctx.send("❌ I'm not in that server or it's an invalid ID.")

        added = 0
        for member in guild.members:
            if not member.bot:
                if member.id not in self.dmlist:
                    self.dmlist.add(member.id)
                    added += 1

        self.save_dmlist()
        await ctx.send(f"✅ Added {added} users from `{guild.name}` to the DM list.")

async def setup(bot):
    await bot.add_cog(DMServerAdder(bot))
