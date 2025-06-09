import discord
from discord.ext import commands

OWNER_IDS = {1076200413503701072, 862239588391321600, 1135837895496847503}
NAME_PREFIX = "TL "
GUILD_ROLE_NAME = "Guild Members"
tracked_guild_id = None
enabled = True

class NameChanger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_owner(self, user_id):
        return user_id in OWNER_IDS

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if not enabled or after.bot:
            return

        if tracked_guild_id and after.guild.id != tracked_guild_id:
            return

        before_roles = set(before.roles)
        after_roles = set(after.roles)

        gained_roles = after_roles - before_roles
        guild_member_role = discord.utils.get(after.guild.roles, name=GUILD_ROLE_NAME)

        if guild_member_role in gained_roles:
            try:
                if not after.display_name.startswith(NAME_PREFIX):
                    new_name = NAME_PREFIX + after.display_name
                    await after.edit(nick=new_name[:32])
                    print(f"Renamed {after} to {new_name}")
            except discord.Forbidden:
                print(f"Missing permissions to rename {after}")
            except Exception as e:
                print(f"Error renaming {after}: {e}")

    @commands.command()
    async def setguild(self, ctx):
        global tracked_guild_id
        if not self.is_owner(ctx.author.id):
            return await ctx.send("❌ You don't have permission.")
        tracked_guild_id = ctx.guild.id
        await ctx.send(f"✅ Auto rename enabled for server `{ctx.guild.name}`.")

    @commands.command()
    async def setprefix(self, ctx, *, prefix: str):
        global NAME_PREFIX
        if not self.is_owner(ctx.author.id):
            return await ctx.send("❌ You don't have permission.")
        NAME_PREFIX = prefix
        await ctx.send(f"✅ Prefix changed to `{prefix}`")

    @commands.command()
    async def setrolename(self, ctx, *, role_name: str):
        global GUILD_ROLE_NAME
        if not self.is_owner(ctx.author.id):
            return await ctx.send("❌ You don't have permission.")
        GUILD_ROLE_NAME = role_name
        await ctx.send(f"✅ Guild role name set to `{role_name}`")

    @commands.command()
    async def toggleauto(self, ctx):
        global enabled
        if not self.is_owner(ctx.author.id):
            return await ctx.send("❌ You don't have permission.")
        enabled = not enabled
        status = "enabled" if enabled else "disabled"
        await ctx.send(f"✅ Auto rename system {status}.")

    @commands.command()
    async def renameall(self, ctx):
        if not self.is_owner(ctx.author.id):
            return await ctx.send("❌ You don't have permission.")

        guild = ctx.guild
        role = discord.utils.get(guild.roles, name=GUILD_ROLE_NAME)
        if not role:
            return await ctx.send(f"❌ Role `{GUILD_ROLE_NAME}` not found.")

        count = 0
        for member in role.members:
            if not member.bot and not member.display_name.startswith(NAME_PREFIX):
                try:
                    await member.edit(nick=(NAME_PREFIX + member.display_name)[:32])
                    count += 1
                except:
                    pass
        await ctx.send(f"✅ Renamed `{count}` members with `{NAME_PREFIX}` prefix.")

async def setup(bot):
    await bot.add_cog(NameChanger(bot))
