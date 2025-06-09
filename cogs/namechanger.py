import discord
from discord.ext import commands

OWNER_IDS = {1076200413503701072, 862239588391321600, 1135837895496847503}
guild_role_id = None  # Will be set using command

class NameChanger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setguildrole(self, ctx, role: discord.Role):
        """Owner command to set the role used for name changes."""
        global guild_role_id
        if ctx.author.id not in OWNER_IDS:
            return await ctx.send("❌ You don't have permission.")
        guild_role_id = role.id
        await ctx.send(f"✅ Guild role set to `{role.name}`.")

    @commands.command()
    async def namechanges(self, ctx):
        """Change names of all users with the set role by adding 'TL ' prefix."""
        if ctx.author.id not in OWNER_IDS:
            return await ctx.send("❌ You don't have permission.")

        global guild_role_id
        if not guild_role_id:
            return await ctx.send("❌ Guild role not set. Use `+setguildrole @role` first.")

        role = ctx.guild.get_role(guild_role_id)
        if not role:
            return await ctx.send("❌ The saved role ID is invalid. Set it again using `+setguildrole @role`.")

        changed = []
        failed = []

        for member in role.members:
            new_name = f"TL {member.display_name}" if not member.nick else f"TL {member.nick}"
            if member.nick and member.nick.startswith("TL "):
                continue  # Already updated
            try:
                await member.edit(nick=new_name)
                changed.append(member.mention)
            except:
                failed.append(member.mention)

        await ctx.send(
            f"✅ Nicknames changed for {len(changed)} members:\n{', '.join(changed) or 'None'}\n\n"
            f"❌ Failed to change for {len(failed)} members:\n{', '.join(failed) or 'None'}"
        )

async def setup(bot):
    await bot.add_cog(NameChanger(bot))
