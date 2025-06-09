import discord
from discord.ext import commands

OWNER_IDS = {1076200413503701072, 862239588391321600, 1135837895496847503}
guild_role_id = None  # Set via command
auto_namechange_enabled = True

class NameChanger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if not guild_role_id or not auto_namechange_enabled:
            return

        guild = after.guild
        role = guild.get_role(guild_role_id)
        if not role:
            return

        # Check if user gained the guild role
        if role in after.roles and role not in before.roles:
            try:
                current_nick = after.nick or after.name
                new_nick = f"TL {current_nick}" if not current_nick.startswith("TL ") else current_nick
                await after.edit(nick=new_nick)
                channel = discord.utils.get(guild.text_channels, name="general") or guild.system_channel
                if channel:
                    await channel.send(f"✅ {after.mention}'s name changed from `{current_nick}` to `{new_nick}`.")
            except discord.Forbidden:
                pass

    @commands.command()
    async def setguildrole(self, ctx, role: discord.Role):
        global guild_role_id
        if ctx.author.id not in OWNER_IDS:
            return await ctx.send("❌ You don't have permission.")
        guild_role_id = role.id
        await ctx.send(f"✅ Guild role set to `{role.name}`.")

    @commands.command()
    async def namechanges(self, ctx):
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
                continue
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
