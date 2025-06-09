import discord
from discord.ext import commands
import json
import os

DM_LIST_FILE = "dmlist.json"
OWNER_IDS = {1076200413503701072, 862239588391321600, 1135837895496847503}

class DMManager(commands.Cog):
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
        if ctx.author.id not in OWNER_IDS:
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

    @commands.command(name="dm")
    async def dm(self, ctx, target: str = None, *, message: str = None):
        if ctx.author.id not in OWNER_IDS:
            return await ctx.send("❌ You do not have permission to use this command.")
        
        if not target or not message:
            return await ctx.send("❌ Usage: `+dm all <message>` or `+dm @user <message>` or `+dm dmlist <message>`")

        if target.lower() == "all":
            # DM all guild members of the current guild except bots
            guild = ctx.guild
            if not guild:
                return await ctx.send("❌ This command can only be used in a server.")
            count = 0
            for member in guild.members:
                if not member.bot:
                    try:
                        await member.send(message)
                        count += 1
                    except:
                        pass
            await ctx.send(f"✅ Sent DMs to {count} members of this server.")
        
        elif target.lower() == "dmlist":
            # DM all users in the saved dmlist
            count = 0
            for user_id in self.dmlist:
                user = self.bot.get_user(user_id)
                if not user:
                    try:
                        user = await self.bot.fetch_user(user_id)
                    except:
                        continue
                try:
                    await user.send(message)
                    count += 1
                except:
                    pass
            await ctx.send(f"✅ Sent DMs to {count} users in the DM list.")

        else:
            # DM specific user by mention or ID
            # Try to get user from mention or ID
            try:
                user = None
                if len(ctx.message.mentions) > 0:
                    user = ctx.message.mentions[0]
                else:
                    user_id = int(target)
                    user = self.bot.get_user(user_id)
                    if not user:
                        user = await self.bot.fetch_user(user_id)
                if not user:
                    return await ctx.send("❌ User not found.")
                await user.send(message)
                await ctx.send(f"✅ Sent DM to {user.mention}.")
            except Exception as e:
                await ctx.send(f"❌ Could not send DM: {e}")

async def setup(bot):
    await bot.add_cog(DMManager(bot))
