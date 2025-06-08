import discord
from discord.ext import commands
import asyncio

class Tournament(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.joiners = set()
        self.dm_queue = []
        self.dm_task = None

    async def setup_hook(self):
        self.dm_task = self.bot.loop.create_task(self.dm_worker())

    def cog_unload(self):
        if self.dm_task:
            self.dm_task.cancel()

    @commands.command()
    async def announce(self, ctx, channel: discord.TextChannel):
        embed = discord.Embed(
            title="🏆 FREE FIRE TOURNAMENT ANNOUNCEMENT 🏆",
            description=(
                "**🔥 FREE & PAID EVENTS ARE HERE! 🔥**\n\n"
                "🎯 **FREE TOURNAMENTS**\n"
                "➤ No Entry Fee!\n"
                "➤ Open to all players.\n\n"
                "💰 **PAID TOURNAMENTS**\n"
                "➤ Entry Fee: ₹5 only\n"
                "➤ Win ₹10 (double reward!)\n\n"
                "🎮 **HOW TO JOIN?**\n"
                "Click the **Join Tournament** button below!\n"
                "We’ll DM you all match details after joining.\n\n"
                "⚔️ Fight Hard, Win Big!"
            ),
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )

        join_button = discord.ui.Button(
            label="🎯 Join Tournament",
            style=discord.ButtonStyle.green,
            custom_id="join_tournament"
        )
        view = discord.ui.View()
        view.add_item(join_button)

        await channel.send(embed=embed, view=view)
        await ctx.send(f"✅ Tournament announcement sent to {channel.mention}")

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component:
            if interaction.data.get("custom_id") == "join_tournament":
                user_id = interaction.user.id
                if user_id in self.joiners:
                    await interaction.response.send_message("You already joined the tournament!", ephemeral=True)
                else:
                    self.joiners.add(user_id)
                    await interaction.response.send_message("You have joined the tournament! You will get DM updates.", ephemeral=True)

    @commands.command()
    async def joiners(self, ctx):
        if self.joiners:
            mentions = [f"<@{uid}>" for uid in self.joiners]
            await ctx.send("Tournament Joiners:\n" + "\n".join(mentions))
        else:
            await ctx.send("No one has joined the tournament yet.")

    @commands.command()
    async def clearjoiners(self, ctx):
        self.joiners.clear()
        await ctx.send("All joiners have been cleared.")

    @commands.command()
    async def dm_joiners(self, ctx, *, message: str):
        if not self.joiners:
            await ctx.send("No joiners to DM.")
            return

        for user_id in self.joiners:
            self.dm_queue.append((user_id, message))
        await ctx.send(f"Queued message to {len(self.joiners)} joiners.")

    async def dm_worker(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            if self.dm_queue:
                user_id, message = self.dm_queue.pop(0)
                user = self.bot.get_user(user_id)
                if user:
                    try:
                        await user.send(message)
                    except Exception:
                        pass
                await asyncio.sleep(1)  # Rate-limit DMs
            else:
                await asyncio.sleep(5)

async def setup(bot):
    await bot.add_cog(Tournament(bot))
