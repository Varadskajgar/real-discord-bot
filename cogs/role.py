import discord
from discord.ext import commands

ROLE_MAP = {
    "gm": 1213510959742591016,  # example ID for Guild Member
    "mod": 116832234567890123,
    "vip": 116832345678901234
}

class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def role(self, ctx, user: discord.Member, role_key: str):
        role_id = ROLE_MAP.get(role_key.lower())
        if not role_id:
            await ctx.send(f"❌ Unknown role key: `{role_key}`")
            return

        role = ctx.guild.get_role(role_id)
        if not role:
            await ctx.send(f"❌ Role ID `{role_id}` not found in this server.")
            return

        try:
            await user.add_roles(role)
            await ctx.send(f"✅ {user.mention} was given the **{role.name}** role.")
        except discord.Forbidden:
            await ctx.send("❌ I don’t have permission to assign that role.")
        except Exception as e:
            await ctx.send(f"⚠️ Error: `{e}`")

async def setup(bot):
    await bot.add_cog(RoleManager(bot))