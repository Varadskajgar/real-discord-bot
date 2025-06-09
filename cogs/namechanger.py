import discord
from discord.ext import commands

OWNER_IDS = {1076200413503701072, 862239588391321600, 1135837895496847503}

class NameChanger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="namechanges")
    async def name_changes(self, ctx):
        if ctx.author.id not in OWNER_IDS:
            return await ctx.send("❌ You don't have permission to use this command.")

        role = discord.utils.get(ctx.guild.roles, name="Guild Members")
        if not role:
            return await ctx.send("❌ Role 'Guild Members' not found.")

        successfully_changed = []
        failed_to_change = []

        for member in role.members:
            try:
                # Skip if already changed (nick starts with "TL ")
                if member.nick and member.nick.startswith("TL "):
                    continue
                
                new_nick = f"TL {member.nick if member.nick else member.name}"
                await member.edit(nick=new_nick)
                successfully_changed.append(member)
            except discord.Forbidden:
                failed_to_change.append(member)
            except discord.HTTPException:
                failed_to_change.append(member)

        msg = f"✅ Nicknames changed for {len(successfully_changed)} members:\n"
        if successfully_changed:
            msg += ", ".join(m.mention for m in successfully_changed) + "\n"

        if failed_to_change:
            msg += f"❌ Failed to change nickname for {len(failed_to_change)} members:\n"
            msg += ", ".join(m.mention for m in failed_to_change)

        await ctx.send(msg or "No nicknames were changed.")

async def setup(bot):
    await bot.add_cog(NameChanger(bot))
