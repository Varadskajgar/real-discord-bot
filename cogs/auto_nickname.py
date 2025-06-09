import discord
from discord.ext import commands

GUILD_ROLE_ID = 1213510959742591016  # 🔁 Replace this with your actual role ID
PREFIX = "TL "
name_changes_log = []  # Optional: Used to track nickname changes

class AutoNameChanger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        has_role = any(role.id == GUILD_ROLE_ID for role in after.roles)
        had_role = any(role.id == GUILD_ROLE_ID for role in before.roles)

        if has_role and not had_role:
            current_name = after.nick or after.name
            if not current_name.startswith(PREFIX):
                try:
                    new_nick = PREFIX + current_name
                    await after.edit(nick=new_nick)
                    name_changes_log.append(f"{after} → `{new_nick}`")
                    print(f"Nickname updated: {after} -> {new_nick}")
                except discord.Forbidden:
                    print(f"⚠️ Missing permission to change nickname for {after}")
                except Exception as e:
                    print(f"⚠️ Error changing nickname for {after}: {e}")

    @commands.command()
    async def namechangelog(self, ctx):
        if ctx.author.id not in {1076200413503701072, 862239588391321600, 1135837895496847503}:
            return
        if not name_changes_log:
            await ctx.send("No nickname changes recorded.")
        else:
            await ctx.send("📜 Nickname changes:\n" + "\n".join(name_changes_log[-10:]))

async def setup(bot):
    await bot.add_cog(AutoNameChanger(bot))
