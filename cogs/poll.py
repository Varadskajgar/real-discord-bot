import discord
from discord.ext import commands

OWNER_IDS = {1076200413503701072, 862239588391321600, 1135837895496847503}

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def poll(self, ctx, *, question: str = None):
        if ctx.author.id not in OWNER_IDS:
            await ctx.send("❌ You are not allowed to use this command.")
            return

        if not question:
            await ctx.send("❌ Please provide a question for the poll.")
            return

        yes_voters = set()
        no_voters = set()

        embed = discord.Embed(title="📊 Poll", description=question, color=discord.Color.teal())
        embed.add_field(name="✅ Yes", value="No votes yet", inline=True)
        embed.add_field(name="❌ No", value="No votes yet", inline=True)
        embed.set_footer(text=f"Poll created by {ctx.author.display_name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

        message = await ctx.send(embed=embed)

        class PollView(discord.ui.View):
            @discord.ui.button(label="Yes", style=discord.ButtonStyle.success)
            async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                user = interaction.user

                if user.id in yes_voters or user.id in no_voters:
                    await interaction.response.send_message("❌ You have already voted!", ephemeral=True)
                    return

                yes_voters.add(user.id)
                await interaction.response.send_message(f"{user.mention} voted ✅ Yes!", ephemeral=True)
                await update_embed()

            @discord.ui.button(label="No", style=discord.ButtonStyle.danger)
            async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                user = interaction.user

                if user.id in yes_voters or user.id in no_voters:
                    await interaction.response.send_message("❌ You have already voted!", ephemeral=True)
                    return

                no_voters.add(user.id)
                await interaction.response.send_message(f"{user.mention} voted ❌ No!", ephemeral=True)
                await update_embed()

        async def update_embed():
            yes_names = [f"<@{uid}>" for uid in yes_voters] or ["No votes yet"]
            no_names = [f"<@{uid}>" for uid in no_voters] or ["No votes yet"]

            embed.set_field_at(0, name="✅ Yes", value="\n".join(yes_names), inline=True)
            embed.set_field_at(1, name="❌ No", value="\n".join(no_names), inline=True)

            await message.edit(embed=embed)

        await message.edit(view=PollView())

async def setup(bot):
    await bot.add_cog(Poll(bot))
