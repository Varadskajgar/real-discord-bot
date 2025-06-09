from discord.ext import commands
import discord

OWNER_IDS = {1076200413503701072, 862239588391321600, 1135837895496847503}
dm_user_ids = set()

class DMManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def dmlist(self, ctx, action: str, *members_or_ids):
        if ctx.author.id not in OWNER_IDS:
            return await ctx.send("❌ You don't have permission to use this command.")

        updated = []

        if action.lower() == "add":
            for item in members_or_ids:
                member = await self._get_user(ctx, item)
                if member:
                    dm_user_ids.add(member.id)
                    updated.append(f"✅ Added: {member} (`{member.id}`)")
            if updated:
                await ctx.send("\n".join(updated))
            else:
                await ctx.send("⚠️ No valid users or IDs provided.")

        elif action.lower() == "remove":
            for item in members_or_ids:
                member = await self._get_user(ctx, item)
                if member and member.id in dm_user_ids:
                    dm_user_ids.remove(member.id)
                    updated.append(f"❌ Removed: {member} (`{member.id}`)")
            if updated:
                await ctx.send("\n".join(updated))
            else:
                await ctx.send("⚠️ No matching users or IDs found in DM list.")

        elif action.lower() == "show":
            if dm_user_ids:
                desc = "\n".join(f"<@{uid}> (`{uid}`)" for uid in dm_user_ids)
                await ctx.send(f"📬 **DM List:**\n{desc}")
            else:
                await ctx.send("📭 DM list is currently empty.")

        else:
            await ctx.send("❌ Invalid action. Use `add`, `remove`, or `show`.")

    async def _get_user(self, ctx, value):
        try:
            if value.isdigit():
                return await self.bot.fetch_user(int(value))
            elif value.startswith("<@") and value.endswith(">"):
                uid = int(value.strip("<@!>"))
                return await self.bot.fetch_user(uid)
        except:
            return None

async def setup(bot):
    await bot.add_cog(DMManager(bot))
