import discord
from discord.ext import commands
import json
import os

OWNER_IDS = {1076200413503701072, 862239588391321600, 1135837895496847503}
DM_LIST_FILE = "dm_list.json"

def load_dm_list():
    if not os.path.exists(DM_LIST_FILE):
        return []
    with open(DM_LIST_FILE, "r") as f:
        return json.load(f)

def save_dm_list(dm_list):
    with open(DM_LIST_FILE, "w") as f:
        json.dump(dm_list, f)

class DMManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dm_list = load_dm_list()

    @commands.command()
    async def dm(self, ctx, target: discord.Member, *, message: str):
        if ctx.author.id not in OWNER_IDS:
            return await ctx.send("❌ You don't have permission.")
        try:
            await target.send(message)
            await ctx.send(f"✅ Message sent to {target.mention}")
        except:
            await ctx.send(f"❌ Failed to DM {target.mention}")

    @commands.command()
    async def dmall(self, ctx, *, message: str):
        if ctx.author.id not in OWNER_IDS:
            return await ctx.send("❌ You don't have permission.")

        total = len(self.dm_list)
        if total == 0:
            return await ctx.send("⚠️ DM list is empty.")

        success = 0
        fail = 0
        msg = await ctx.send(f"📤 Sending messages: `0%` (0/{total})")

        for i, user_id in enumerate(self.dm_list, 1):
            try:
                user = await self.bot.fetch_user(user_id)
                await user.send(message)
                success += 1
            except:
                fail += 1

            if i % 10 == 0 or i == total:
                percent = int(i / total * 100)
                await msg.edit(content=f"📤 Sending messages: `{percent}%` ({i}/{total})")

        await ctx.send(f"✅ Finished sending.\n✅ Sent: {success}\n❌ Failed: {fail}")

    @commands.group()
    async def dmlist(self, ctx):
        if ctx.author.id not in OWNER_IDS:
            return await ctx.send("❌ You don't have permission.")
        if ctx.invoked_subcommand is None:
            await ctx.send("⚠️ Invalid subcommand. Use `add`, `remove`, `show`, or `addserver`.")

    @dmlist.command(name="add")
    async def dmlist_add(self, ctx, user: discord.User):
        if user.id not in self.dm_list:
            self.dm_list.append(user.id)
            save_dm_list(self.dm_list)
            await ctx.send(f"✅ Added {user.mention} to DM list.")
        else:
            await ctx.send(f"❗ {user.mention} is already in the DM list.")

    @dmlist.command(name="remove")
    async def dmlist_remove(self, ctx, user: discord.User):
        if user.id in self.dm_list:
            self.dm_list.remove(user.id)
            save_dm_list(self.dm_list)
            await ctx.send(f"✅ Removed {user.mention} from DM list.")
        else:
            await ctx.send(f"❗ {user.mention} is not in the DM list.")

    @dmlist.command(name="show")
    async def dmlist_show(self, ctx):
        if not self.dm_list:
            return await ctx.send("📭 DM list is currently empty.")
        mentions = []
        for uid in self.dm_list:
            user = await self.bot.fetch_user(uid)
            mentions.append(user.mention)
        await ctx.send("📨 DM List:\n" + "\n".join(mentions))

    @dmlist.command(name="addserver")
    async def dmlist_addserver(self, ctx, server_id: int):
        guild = self.bot.get_guild(server_id)
        if not guild:
            return await ctx.send("❌ I'm not in that server or the ID is incorrect.")

        await ctx.send(f"⏳ Starting to fetch users from **{guild.name}**...")

        members = [m for m in guild.members if not m.bot]
        total = len(members)
        if total == 0:
            return await ctx.send("⚠️ No human members found in that server.")

        count = 0
        msg = await ctx.send("Progress: `0%` (0/0)")
        for i, member in enumerate(members, 1):
            if member.id not in self.dm_list:
                self.dm_list.append(member.id)
                count += 1

            if i % 10 == 0 or i == total:
                percent = int(i / total * 100)
                await msg.edit(content=f"Progress: `{percent}%` ({i}/{total})")

        save_dm_list(self.dm_list)
        await ctx.send(f"✅ Finished. `{count}` new users added from `{guild.name}`.")

async def setup(bot):
    await bot.add_cog(DMManager(bot))
