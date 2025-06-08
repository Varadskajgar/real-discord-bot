import discord
from discord.ext import commands

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def poll(self, ctx, *, question: str):
        embed = discord.Embed(title="📊 Poll", description=question, color=0x00FFFF)
        embed.set_footer(text=f"Poll created by {ctx.author.display_name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

        class PollView(discord.ui.View):
            @discord.ui.button(label="Yes", style=discord.ButtonStyle.green, emoji="<a:YesYes:1380877812050956340>")
            async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.send_message(f"{interaction.user.mention} voted **Yes**!", ephemeral=True)

            @discord.ui.button(label="No", style=discord.ButtonStyle.red, emoji="<a:NoNo:1380877904275312811>")
            async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.send_message(f"{interaction.user.mention} voted **No**!", ephemeral=True)

        await ctx.send(embed=embed, view=PollView())

async def setup(bot):
    await bot.add_cog(Poll(bot))