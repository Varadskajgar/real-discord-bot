import discord
from discord.ext import commands

OWNER_IDS = {1076200413503701072, 862239588391321600, 1135837895496847503}

class AutoNameChange(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_data = {}  # {guild_id: {'role_id': int, 'prefix': str}}

    @commands.command()
    async def setguildrole(self, ctx, role: discord.Role):
        if ctx.author.id not in OWNER_IDS:
            return await ctx.send("❌ You don't have permission.")
        guild_id = ctx.guild.id
        if guild_id not in self.guild_data:
            self.guild_data[guild_id] = {}
        self.guild_data[guild_id]['role_id'] = role.id
        await ctx.send(f"✅ Guild member role set to {role.name}")

    @commands.command()
    async def setprefix(self, ctx, *, prefix: str):
        if ctx.author.id not in OWNER_IDS:
            return await ctx.send("❌ You don't have permission.")
        guild_id = ctx.guild.id
        if guild_id not in self.guild_data:
            self.guild_data[guild_id] = {}
        self.guild_data[guild_id]['prefix'] = prefix
        await ctx.send(f"✅ Prefix set to '{prefix}'")

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        guild_id = after.guild.id
        if guild_id not in self.guild_data:
            return
        data = self.guild_data[guild_id]
        role_id = data.get('role_id')
        prefix = data.get('prefix', 'TL ')

        if role_id is None:
            return

        had_role_before = before.get_role(role_id) is not None
        has_role_after = after.get_role(role_id) is not None

        # Only proceed if role was added (not removed)
        if not had_role_before and has_role_after:
            # Add prefix if not already present
            if not after.display_name.startswith(prefix):
                new_name = prefix + after.display_name
                try:
                    await after.edit(nick=new_name, reason="Auto prefix added on role")
                except discord.Forbidden:
                    print(f"Missing permission to change nickname for {after.display_name}")
                except Exception as e:
                    print(f"Error changing nickname for {after.display_name}: {e}")

    @commands.command()
    async def namelist(self, ctx):
        """Shows list of users with the prefix"""
        guild_id = ctx.guild.id
        if guild_id not in self.guild_data:
            return await ctx.send("No guild role or prefix set.")

        data = self.guild_data[guild_id]
        role_id = data.get('role_id')
        prefix = data.get('prefix', 'TL ')

        if role_id is None:
            return await ctx.send("Guild role not set.")

        role = ctx.guild.get_role(role_id)
        if not role:
            return await ctx.send("Role not found.")

        members = [m for m in role.members if m.nick and m.nick.startswith(prefix)]
        if not members:
            await ctx.send("No members with the prefix found.")
            return

        msg = "**Members with prefix:**\n"
        for m in members:
            msg += f"- {m.display_name} (ID: {m.id})\n"
        await ctx.send(msg)

async def setup(bot):
    await bot.add_cog(AutoNameChange(bot))
