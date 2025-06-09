import discord
from discord.ext import commands
import asyncio

OWNER_IDS = {1076200413503701072, 862239588391321600, 1135837895496847503}

class NameChanger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def name(self, ctx, subcommand=None, prefix=None, role: discord.Role = None):
        if ctx.author.id not in OWNER_IDS:
            return

        if subcommand != "recreate" or not prefix or not role:
            return await ctx.send("❌ Usage: `+name recreate TL @role`")

        changed = 0
        skipped = 0
        no_permission = 0
        report_lines = []

        await ctx.send(f"🔄 Checking members in role `{role.name}`...")

        for member in role.members:
            current_name = member.display_name
            if current_name.startswith(prefix):
                skipped += 1
                continue

            new_name = f"{prefix} {current_name}"
            try:
                await member.edit(nick=new_name)
                changed += 1
                report_lines.append(f"✅ {member.mention}: `{current_name}` → `{new_name}`")
            except discord.Forbidden:
                no_permission += 1
                report_lines.append(f"❌ {member.mention}: Missing permission")

            await asyncio.sleep(1)  # prevent rate limits

        await ctx.send(
            f"✅ Done!\n🔁 Changed: {changed}\n⏩ Skipped: {skipped}\n❌ No permission: {no_permission}"
        )

        for chunk in [report_lines[i:i+20] for i in range(0, len(report_lines), 20)]:
            await ctx.send("\n".join(chunk))

async def setup(bot):
    await bot.add_cog(NameChanger(bot))
