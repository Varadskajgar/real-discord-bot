import discord
from discord.ext import commands

class NicknameChanger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="nickname")
    async def nickname(self, ctx, prefix: str, role: discord.Role):
        changed = []
        skipped = []
        errors = []

        for member in role.members:
            if member.bot:
                continue

            current_name = member.nick or member.name
            if current_name.startswith(prefix):
                skipped.append(member.mention)
                continue

            new_name = f"{prefix} {current_name}"
            try:
                await member.edit(nick=new_name)
                changed.append(f"{member.mention} → `{new_name}`")
            except discord.Forbidden:
                errors.append(f"❌ I don't have permission to change nickname of {member.mention}.")
            except Exception as e:
                errors.append(f"❌ Failed to change nickname of {member.mention}: {e}")

        summary = ""
        if changed:
            summary += f"✅ Changed nicknames:\n" + "\n".join(changed[:20]) + "\n"
        if skipped:
            summary += f"⏩ Already had prefix:\n" + ", ".join(skipped[:20]) + "\n"
        if errors:
            summary += "\n".join(errors[:5]) + "\n"

        if not summary:
            summary = "❗ No members were affected."

        await ctx.send(summary)

async def setup(bot):
    await bot.add_cog(NicknameChanger(bot))
