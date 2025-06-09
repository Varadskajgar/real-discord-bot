import discord
from discord.ext import commands

class NameChanger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_role_id = None
        self.guild_tag = None

    @commands.command(name="setguildrole")
    @commands.has_permissions(administrator=True)
    async def set_guild_role(self, ctx, role: discord.Role = None):
        if role is None:
            await ctx.send("❌ Please mention a valid role. Usage: `+setguildrole @role`")
            return
        self.guild_role_id = role.id
        await ctx.send(f"✅ Guild role set to **{role.name}**.")

    @commands.command(name="setguildtag")
    @commands.has_permissions(administrator=True)
    async def set_guild_tag(self, ctx, *, tag: str = None):
        if tag is None:
            await ctx.send("❌ Please provide a tag. Usage: `+setguildtag <tag>`")
            return
        self.guild_tag = tag
        await ctx.send(f"✅ Guild tag set to **{tag}**.")

    @commands.command(name="namenchange")
    async def name_change(self, ctx):
        # Check if both are set
        if not self.guild_role_id or not self.guild_tag:
            await ctx.send("❌ Guild role or tag not set. Use `+setguildrole` and `+setguildtag` first.")
            return
        
        guild_role = ctx.guild.get_role(self.guild_role_id)
        if not guild_role:
            await ctx.send("❌ The saved guild role does not exist on this server. Please set it again.")
            return

        count = 0
        for member in ctx.guild.members:
            if guild_role in member.roles:
                try:
                    # If tag already in name, skip
                    if not member.display_name.startswith(self.guild_tag):
                        new_name = f"{self.guild_tag} {member.display_name}"
                        await member.edit(nick=new_name)
                        count += 1
                except discord.Forbidden:
                    await ctx.send(f"❌ I don't have permission to change nickname of {member.mention}.")
                except Exception as e:
                    await ctx.send(f"❌ Failed to change nickname for {member.mention}: {e}")

        await ctx.send(f"✅ Updated nicknames for {count} members with the role **{guild_role.name}**.")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Missing arguments. Please check the command usage.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid argument provided. Please check the command usage.")
        elif isinstance(error, commands.CheckFailure):
            await ctx.send("❌ You don't have permission to use this command.")
        else:
            # For unexpected errors, you can print or ignore
            print(f"Error in command {ctx.command}: {error}")

async def setup(bot):
    await bot.add_cog(NameChanger(bot))
