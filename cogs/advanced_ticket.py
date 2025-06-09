import discord
from discord.ext import commands
import asyncio

OWNER_IDS = {1076200413503701072, 862239588391321600, 1135837895496847503}

# Data storage per guild
open_tickets = {}        # {guild_id: {user_id: channel_id}}
ticket_counters = {}     # {guild_id: counter}
ticket_category_ids = {} # {guild_id: category_id}
ticket_channel_ids = {}  # {guild_id: ticket_panel_channel_id}
high_role_ids = {}       # {guild_id: [role_ids]}

class TicketView(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__(timeout=None)
        self.guild_id = guild_id

    @discord.ui.button(label="🎟️ Create Ticket", style=discord.ButtonStyle.blurple, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = self.guild_id
        user_id = interaction.user.id
        guild = interaction.guild

        # Initialize dicts if not exist
        if guild_id not in open_tickets:
            open_tickets[guild_id] = {}
        if guild_id not in ticket_counters:
            ticket_counters[guild_id] = 1
        if guild_id not in ticket_category_ids:
            # If no category set, create default Tickets category
            category = await guild.create_category("Tickets")
            ticket_category_ids[guild_id] = category.id
        else:
            category = guild.get_channel(ticket_category_ids[guild_id])
            if category is None:
                category = await guild.create_category("Tickets")
                ticket_category_ids[guild_id] = category.id

        # Check if user already has open ticket
        if user_id in open_tickets[guild_id]:
            channel = guild.get_channel(open_tickets[guild_id][user_id])
            if channel:
                await interaction.response.send_message(f"❗ You already have an open ticket: {channel.mention}", ephemeral=True)
                return

        # Create ticket name with padded number
        ticket_number = ticket_counters[guild_id]
        ticket_name = f"ticket-{ticket_number:03d}"
        ticket_counters[guild_id] += 1

        # Permission overwrites: default no view, user & bot view, high roles view
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }

        # Add high roles permissions
        roles = high_role_ids.get(guild_id, [])
        for role_id in roles:
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        # Create ticket channel
        ticket_channel = await guild.create_text_channel(ticket_name, category=category, overwrites=overwrites)
        await ticket_channel.send(f"Hello {interaction.user.mention}, our staff will be with you shortly.")

        # Save open ticket
        open_tickets[guild_id][user_id] = ticket_channel.id

        await interaction.response.send_message(f"✅ Ticket created: {ticket_channel.mention}", ephemeral=True)

class AdvancedTicket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setticketchannel(self, ctx, channel: discord.TextChannel):
        if ctx.author.id not in OWNER_IDS:
            return await ctx.send("❌ You don't have permission.")
        ticket_channel_ids[ctx.guild.id] = channel.id
        view = TicketView(ctx.guild.id)
        embed = discord.Embed(
            title="🎫 Support Ticket",
            description="Click the button below to open a support ticket.",
            color=discord.Color.blurple()
        )
        await channel.send(embed=embed, view=view)
        await ctx.send(f"✅ Ticket panel sent to {channel.mention}.")

    @commands.command()
    async def sethighrole(self, ctx, role: discord.Role):
        if ctx.author.id not in OWNER_IDS:
            return await ctx.send("❌ You don't have permission.")
        guild_roles = high_role_ids.setdefault(ctx.guild.id, [])
        if role.id not in guild_roles:
            guild_roles.append(role.id)
            await ctx.send(f"✅ {role.name} added to high-role access for tickets.")
        else:
            await ctx.send("❗ This role is already set as high access.")

    @commands.command()
    async def checkticketchannel(self, ctx):
        channel_id = ticket_channel_ids.get(ctx.guild.id)
        if channel_id:
            channel = ctx.guild.get_channel(channel_id)
            await ctx.send(f"✅ Ticket panel is set in {channel.mention}")
        else:
            await ctx.send("❌ Ticket panel channel is not set.")

    @commands.command()
    async def close(self, ctx):
        category_id = ticket_category_ids.get(ctx.guild.id)
        if ctx.channel.category and ctx.channel.category.id == category_id:
            await ctx.send("🔒 This ticket is now closed. Use `+reopen` or `+perclose`.")
        else:
            await ctx.send("❌ This is not a ticket channel.")

    @commands.command()
    async def reopen(self, ctx):
        category_id = ticket_category_ids.get(ctx.guild.id)
        if ctx.channel.category and ctx.channel.category.id == category_id:
            await ctx.send("🔓 Ticket reopened.")
        else:
            await ctx.send("❌ This is not a ticket channel.")

    @commands.command()
    async def perclose(self, ctx):
        guild_id = ctx.guild.id
        if guild_id in open_tickets:
            to_remove = None
            for uid, cid in open_tickets[guild_id].items():
                if cid == ctx.channel.id:
                    to_remove = uid
                    break
            if to_remove:
                del open_tickets[guild_id][to_remove]

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
