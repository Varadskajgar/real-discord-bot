import discord
from discord.ext import commands

GUILD_MEMBERS_ROLE_NAME = "Guild Members"
PREFIX = "TL "

class AutoNickname(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        before_roles = set(before.roles)
        after_roles = set(after.roles)

        guild_members_role = discord.utils.get(after.guild.roles, name=GUILD_MEMBERS_ROLE_NAME)
        if guild_members_role is None:
            return  # Role not found

        if guild_members_role not in before_roles and guild_members_role in after_roles:
            current_nick = after.nick if after.nick else after.name
            if not current_nick.startswith(PREFIX):
                new_nick = PREFIX + current_nick
                try:
                    await after.edit(nick=new_nick)
                except discord.Forbidden:
                    print("No permission to change nickname.")
                except Exception as e:
                    print(f"Error changing nickname: {e}")

        elif guild_members_role in before_roles and guild_members_role not in after_roles:
            current_nick = after.nick if after.nick else after.name
            if current_nick.startswith(PREFIX):
                new_nick = current_nick[len(PREFIX):]
                try:
                    await after.edit(nick=new_nick)
                except discord.Forbidden:
                    print("No permission to change nickname.")
                except Exception as e:
                    print(f"Error changing nickname: {e}")

async def setup(bot):
    await bot.add_cog(AutoNickname(bot))
