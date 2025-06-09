import discord
from discord.ext import commands
import json
import os

OWNER_IDS = {1076200413503701072, 862239588391321600, 1135837895496847503}
DM_LIST_FILE = "dm_list.json"

def load_dm_list():
    if os.path.exists(DM_LIST_FILE):
        with open(DM_LIST_FILE, "r") as f:
            return json.load(f)
    return []

def save_dm_list(dm_list):
    with open(DM_LIST_FILE, "w") as f:
        json.dump(dm_list, f)

class DMManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dm_list = load_dm_list()

    @commands.command()
    async def adddm(self, ctx, member: discord.Member):
        if ctx.author.id not in OWNER_IDS:
            return
        if member.id not in self.dm_list:
            self.dm_list.append(member.id)
            save_dm_list(self.dm_list)
            await ctx.send(f"✅ {member.mention} added to DM list.")
        else:
            await ctx.send("ℹ️ User already in DM list.")

    @commands.command()
    async def removedm(self, ctx, member: discord.Member):
        if ctx.author.id not in OWNER_IDS:
            return
        if member.id in self.dm_list:
            self.dm_list.remove(member.id)
            save_dm_list(self.dm_list)
            await ctx.send(f"❌ {member.mention} removed from DM list.")
        else:
            await ctx.send("ℹ️ User not found in DM list.")

    @commands.command()
    async def dmall(self, ctx, *, message):
        if ctx.author.id not in OWNER_IDS:
            return
        sent = 0
        for user_id in self.dm_list:
            user = self.bot.get_user(user_id)
            if user:
                try:
                    await user.send(message)
                    sent += 1
                except:
                    pass
        await ctx.send(f"📤 Message sent to {sent} users.")

async def setup(bot):
    await bot.add_cog(DMManager(bot))
