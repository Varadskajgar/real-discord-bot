import discord
from discord.ext import commands
import os

USER_IDS_FILE = "user_ids.txt"

def load_user_ids():
    if not os.path.exists(USER_IDS_FILE):
        return []
    with open(USER_IDS_FILE, "r") as f:
        return f.read().splitlines()

def save_user_id(user_id):
    ids = load_user_ids()
    if str(user_id) not in ids:
        ids.append(str(user_id))
        with open(USER_IDS_FILE, "w") as f:
            f.write("\n".join(ids))

class DMManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def adddm(self, ctx, *users: discord.User):
        if not users:
            await ctx.send("❌ Please mention at least one user or provide user IDs.")
            return

        added = []
        for user in users:
            save_user_id(user.id)
            added.append(user.mention)

        await ctx.send(f"✅ Added to DM list: {', '.join(added)}")

    @commands.command()
    @commands.is_owner()
    async def dm(self, ctx, target: str, *, message: str = None):
        if target.lower() != "all":
            await ctx.send("❌ Use: `?dm all <message>`")
            return
        if not message:
            await ctx.send("❌ Please provide a message to send.")
            return

        user_ids = load_user_ids()
        if not user_ids:
            await ctx.send("❌ DM list is empty!")
            return

        sent_count = 0
        for user_id in user_ids:
            try:
                user = await self.bot.fetch_user(int(user_id))
                await user.send(message)
                sent_count += 1
            except:
                pass

        await ctx.send(f"✅ Message sent to {sent_count} users.")

    @commands.command()
    async def dmlist(self, ctx):
        user_ids = load_user_ids()
        if not user_ids:
            await ctx.send("DM list is empty!")
            return

        mentions = []
        for uid in user_ids:
            user = self.bot.get_user(int(uid))
            mentions.append(f"<@{uid}>")
        await ctx.send("Users in DM list:\n" + ", ".join(mentions))

async def setup(bot):
    await bot.add_cog(DMManager(bot))