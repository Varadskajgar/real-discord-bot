import discord
from discord.ext import commands
import asyncio

OWNER_IDS = {1076200413503701072, 862239588391321600, 1135837895496847503}
open_tickets = {}
ticket_counter = 1
ticket_category_id = None
ticket_channel_id = None

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎟️ Create Ticket", style=discord.ButtonStyle.blurple, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        global ticket_counter

        if interaction.user.id in open_tickets:
            channel = interaction.guild.get_channel(open_tickets[interaction.user.id])
            if channel:
                await interaction.response.send_message(f"❗ You already have an open ticket: {channel.mention}", ephemeral=True)
                return

        category = interaction.guild.get_channel(ticket_category_id)
        if not category:
            category = await interaction.guild.create_category("Tickets")
            global ticket_category_id
            ticket_category_id = category.id

        ticket_name = f"ticket-{ticket_counter:03d}"
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }

        ticket_channel = await interaction.guild.create_text_channel(ticket_name, category=category, overwrites=overwrites)
        await ticket_channel.send(f"Hello {interaction.user.mention}, our staff will be with you shortly.")

        await interaction.response.send_message(f"✅ Ticket created: {ticket_channel.mention}", ephemeral=True)
        open_tickets[interaction.user.id] = ticket_channel.id
        ticket_counter += 1

class AdvancedTicket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setticketchannel(self, ctx, channel: discord.TextChannel):
        global ticket_channel_id
        if ctx.author.id not in OWNER_IDS:
            return await ctx.send("❌ You don't have permission.")
        ticket_channel_id = channel.id
        view = TicketView()
        embed = discord.Embed(
            title="🎫 Support Ticket",
            description="Click the button below to open a support ticket.",
            color=discord.Color.blurple()
        )
        await channel.send(embed=embed, view=view)
        await ctx.send(f"✅ Ticket panel sent to {channel.mention}.")

    @commands.command()
    async def close(self, ctx):
        if ctx.channel.category and ctx.channel.category.id == ticket_category_id:
            await ctx.send("🔒 This ticket is now closed. Use `?reopen` or `?perclose`.")
        else:
            await ctx.send("❌ This is not a ticket channel.")

    @commands.command()
    async def reopen(self, ctx):
        if ctx.channel.category and ctx.channel.category.id == ticket_category_id:
            await ctx.send("🔓 Ticket reopened.")
        else:
            await ctx.send("❌ This is not a ticket channel.")

    @commands.command()
    async def perclose(self, ctx):
        for uid, cid in list(open_tickets.items()):
            if cid == ctx.channel.id:
                del open_tickets[uid]
        await ctx.send("🗑️ Deleting this ticket in 5 seconds...")
        await asyncio.sleep(5)
        await ctx.channel.delete()

    @commands.command()
    async def add(self, ctx, member: discord.Member):
        await ctx.channel.set_permissions(member, view_channel=True, send_messages=True)
        await ctx.send(f"✅ {member.mention} has been added to the ticket.")

    @commands.command()
    async def remove(self, ctx, member: discord.Member):
        await ctx.channel.set_permissions(member, overwrite=None)
        await ctx.send(f"✅ {member.mention} has been removed from the ticket.")

async def setup(bot):
    await bot.add_cog(AdvancedTicket(bot))
