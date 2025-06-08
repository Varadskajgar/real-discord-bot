import discord
from discord.ext import commands

class HelpAll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owner_ids = {1076200413503701072, 862239588391321600, 1135837895496847503}  # Your owner IDs here

    @commands.command(name="needhelp")
    async def needhelp(self, ctx):
        if ctx.author.id not in self.owner_ids:
            return await ctx.send("❌ You do not have permission to use this command.")

        embed = discord.Embed(
            title="📚 All Bot Commands & Usage",
            description="Here are all the important commands you can use with examples:",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="Role Commands",
            value=(
                "`?role @user <role_key>`\n"
                "Example: `?role @Varad PRO`\n"
                "Assigns roles based on predefined keys."
            ),
            inline=False
        )

        embed.add_field(
            name="Poll Commands",
            value=(
                "`?poll <question>`\n"
                "Example: `?poll Do you like Free Fire?`\n"
                "Creates a poll with animated buttons."
            ),
            inline=False
        )

        embed.add_field(
            name="DM Commands",
            value=(
                "`?dm all <message>` - Sends DM to all users.\n"
                "`?dm <user_id> <message>` - Sends DM to a specific user.\n"
                "Example: `?dm all Hello everyone!`"
            ),
            inline=False
        )

        embed.add_field(
            name="Tournament Commands",
            value=(
                "`?announce #channel` - Announces a tournament.\n"
                "`?joiners` - Shows all joiners.\n"
                "`?clearjoiners` - Clears joiners list.\n"
                "`?dm_joiners <message>` - DM message to all joiners.\n"
                "Example: `?dm_joiners Match at 10 PM!`"
            ),
            inline=False
        )

        embed.add_field(
            name="Ticket Commands",
            value=(
                "`?setticketchannel #channel` - Set the ticket channel.\n"
                "`?add @user` - Add user to ticket.\n"
                "`?remove @user` - Remove user from ticket.\n"
                "`?close` - Close current ticket.\n"
                "`?reopen` - Reopen ticket.\n"
                "`?perclose` - Permanently close ticket.\n"
                "Example: `?add @Moderator`"
            ),
            inline=False
        )

        embed.set_footer(text="Seiko Creator • Bot Help")

        try:
            await ctx.author.send(embed=embed)
            await ctx.send("📩 I have sent you all commands in DM!")
        except discord.Forbidden:
            await ctx.send("❌ I cannot send you DMs. Please check your privacy settings.")

async def setup(bot):
    await bot.add_cog(HelpAll(bot))
