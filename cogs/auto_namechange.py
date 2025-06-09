import discord
from discord.ext import commands

guild_role_id = None
name_prefix = "TL "  # Default prefix

class AutoNameChanger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command to set the guild member role that will trigger renaming
    @commands.command()
    async def setguildrole(self, ctx, role: discord.Role):
        global guild_role_id
        if ctx.author.id not in {1076200413503701072, 862239588391321600, 1135837895496847503}:
            return await ctx.send("❌ You don't have permission.")
        guild_role_id = role.id
        await ctx.send(f"✅ Guild role set to {role.name}.")

    # Command to set the prefix for name change
    @commands.command()
    async def setprefix(self, ctx, *, prefix: str):
        global name_prefix
        if ctx.author.id not in {1076200413503701072, 862239588391321600, 1135837895496847503}:
            return await ctx.send("❌ You don't have permission.")
        name_prefix = prefix
        await ctx.send(f"✅ Prefix set to `{prefix}`")

    # Command to list members with the prefix
    @commands.command()
    async def namelist(self, ctx):
        if not guild_role_id:
            return await ctx.send("❌ Guild role not set.")
        role = ctx.guild.get_role(guild_role_id)
        if not role:
            return await ctx.send("❌ Role not found.")
        members = [m.display_name for m in role.members if m.display_name.startswith(name_prefix)]
        if not members:
            return await ctx.send("❌ No members found with the prefix.")
        await ctx.send("👥 Members with prefix:\n" + "\n".join(members))

    # Event listener for role updates (auto rename)
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        global guild_role_id, name_prefix
        if not guild_role_id:
            return
        role = after.guild.get_role(guild_role_id)
        if role in after.roles and not before.nick == after.nick:
            expected_name = f"{name_prefix}{after.name}"
            try:
                if not after.display_name.startswith(name_prefix):
                    await after.edit(nick=expected_name)
            except discord.Forbidden:
                pass

async def setup(bot):
    await bot.add_cog(AutoNameChanger(bot))
