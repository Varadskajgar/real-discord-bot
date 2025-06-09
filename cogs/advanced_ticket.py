import discord
from discord.ext import commands
from discord.utils import get

OWNER_IDS = {1076200413503701072, 862239588391321600, 1135837895496847503}

ticket_counter = 1
open_tickets = {}
ticket_category_id = None
ticket_message_id = None
ticket_channel_id = None

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎟️ Create Ticket", style=discord.ButtonStyle.blurple, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        global ticket_counter

        if interaction.user.id in open_tickets:
            await interaction.response.send_message("❌ You already have an open ticket.", ephemeral=True)
            return

        guild = interaction.guild
        category = get(guild.categories, id=ticket_category_id)

        if not category:
            category = await guild.create_category("Tickets")
            global ticket_category_id
            ticket_category_id = category.id

        ticket_name = f"ticket-{ticket_counter:03d}"
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }

        ticket_channel = await guild.create_text_channel(ticket_name, category=category, overwrites=overwrites)
        await ticket_channel.send(f"{interaction.user.mention}, welcome! Our team will assist you shortly.")
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
            title="🎫 Need Help?",
            description="Click the button below to create a ticket.\nOur team will assist you shortly!",
            color=discord.Color.blurple()
        )
        await channel.send(embed=embed, view=view)
        await ctx.send(f"✅ Ticket panel sent to {channel.mention}.")

    @commands.command()
    async def close(self, ctx):
        if ctx.channel.category and ctx.channel.category.id == ticket_category_id:
            await ctx.send("🔒 Ticket closed. Use `?reopen` to reopen or `?perclose` to delete.")
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
        user_id = None
        for uid, cid in open_tickets.items():
            if cid == ctx.channel.id:
                user_id = uid
                break

        if user_id:
            del open_tickets[user_id]

        await ctx.send("🗑️ Ticket will be deleted in 5 seconds.")
        await asyncio.sleep(5)
        await ctx.channel.delete()

    @commands.command()
    async def add(self, ctx, member: discord.Member):
        await ctx.channel.set_permissions(member, view_channel=True, send_messages=True)
        await ctx.send(f"✅ {member.mention} added to the ticket.")

    @commands.command()
    async def remove(self, ctx, member: discord.Member):
        await ctx.channel.set_permissions(member, overwrite=None)
        await ctx.send(f"✅ {member.mention} removed from the ticket.")

async def setup(bot):
    await bot.add_cog(AdvancedTicket(bot))
