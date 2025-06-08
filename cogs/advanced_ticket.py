# advanced_ticket.py

import discord
from discord.ext import commands
from discord.ui import View, Button
import asyncio

OWNER_IDS = {1076200413503701072, 862239588391321600, 1135837895496847503}

class AdvancedTicket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ticket_channel_id = None  # store channel ID for ticket creation
        self.tickets = {}  # ticket_number: channel_id
        self.ticket_counter = 0

    @commands.command()
    async def setticketchannel(self, ctx, channel: discord.TextChannel):
        """Set the channel where ticket buttons will be sent."""
        if ctx.author.id not in OWNER_IDS:
            await ctx.send("❌ You don't have permission to use this command.")
            return
        self.ticket_channel_id = channel.id
        await ctx.send(f"✅ Ticket channel set to {channel.mention}")

    @commands.command()
    async def ticket(self, ctx):
        """Create a ticket with a button for users."""
        if self.ticket_channel_id is None:
            await ctx.send("❌ Ticket channel is not set yet. Use ?setticketchannel first.")
            return
        channel = self.bot.get_channel(self.ticket_channel_id)
        if channel is None:
            await ctx.send("❌ Ticket channel not found or bot doesn't have access.")
            return

        embed = discord.Embed(
            title="🎫 Support Ticket",
            description="Click the button below to create a new support ticket.",
            color=discord.Color.blue()
        )
        view = View()
        button = Button(label="Create Ticket", style=discord.ButtonStyle.green, custom_id="create_ticket")
        view.add_item(button)

        await channel.send(embed=embed, view=view)
        await ctx.send(f"✅ Ticket creation message sent in {channel.mention}")

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.component:
            return

        if interaction.data.get("custom_id") == "create_ticket":
            guild = interaction.guild
            author = interaction.user
            # Create unique ticket number
            self.ticket_counter += 1
            ticket_num = f"{self.ticket_counter:03d}"

            # Create new text channel for the ticket
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            }

            ticket_channel = await guild.create_text_channel(
                name=f"ticket-{ticket_num}",
                overwrites=overwrites,
                topic=f"Support ticket for {author} (ID: {author.id})"
            )

            self.tickets[ticket_num] = ticket_channel.id

            await interaction.response.send_message(
                f"🎟️ Ticket created: {ticket_channel.mention}", ephemeral=True
            )

            embed = discord.Embed(
                title=f"Ticket {ticket_num}",
                description=f"Hello {author.mention}, support will be with you shortly.",
                color=discord.Color.green()
            )

            close_button = Button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
            view = View()
            view.add_item(close_button)

            await ticket_channel.send(content=author.mention, embed=embed, view=view)

        elif interaction.data.get("custom_id") == "close_ticket":
            channel = interaction.channel
            ticket_num = None

            # Find ticket number by channel id
            for num, chan_id in self.tickets.items():
                if chan_id == channel.id:
                    ticket_num = num
                    break

            if ticket_num is None:
                await interaction.response.send_message("❌ This channel is not a recognized ticket.", ephemeral=True)
                return

            # Only ticket creator or owner can close
            member = interaction.user
            permissions = channel.permissions_for(member)
            if member.id not in OWNER_IDS and permissions.manage_channels is False:
                await interaction.response.send_message("❌ You don't have permission to close this ticket.", ephemeral=True)
                return

            await interaction.response.send_message(f"🗑️ Closing ticket {ticket_num} in 5 seconds...", ephemeral=True)
            await asyncio.sleep(5)
            await channel.delete()
            self.tickets.pop(ticket_num, None)

    @commands.command()
    async def add(self, ctx, user: discord.Member):
        """Add a user to the ticket channel."""
        if ctx.channel.name.startswith("ticket-"):
            overwrites = ctx.channel.overwrites
            overwrites[user] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            await ctx.channel.edit(overwrites=overwrites)
            await ctx.send(f"✅ Added {user.mention} to the ticket.")
        else:
            await ctx.send("❌ This command can only be used inside a ticket channel.")

    @commands.command()
    async def remove(self, ctx, user: discord.Member):
        """Remove a user from the ticket channel."""
        if ctx.channel.name.startswith("ticket-"):
            overwrites = ctx.channel.overwrites
            if user in overwrites:
                overwrites.pop(user)
                await ctx.channel.edit(overwrites=overwrites)
                await ctx.send(f"✅ Removed {user.mention} from the ticket.")
            else:
                await ctx.send(f"❌ {user.mention} is not in this ticket.")
        else:
            await ctx.send("❌ This command can only be used inside a ticket channel.")

    @commands.command()
    async def reopen(self, ctx):
        """Reopen a closed ticket (owner only)."""
        if ctx.author.id not in OWNER_IDS:
            await ctx.send("❌ You don't have permission to use this command.")
            return
        # For simplicity, this feature requires you to manually recreate ticket channels.
        await ctx.send("⚠️ Reopen feature requires manual ticket channel creation.")

    @commands.command()
    async def perclose(self, ctx):
        """Permanently close ticket and delete it (owner only)."""
        if ctx.author.id not in OWNER_IDS:
            await ctx.send("❌ You don't have permission to use this command.")
            return

        if ctx.channel.name.startswith("ticket-"):
            ticket_num = ctx.channel.name.split("-")[1]
            await ctx.send(f"🗑️ Permanently closing ticket {ticket_num} in 5 seconds...")
            await asyncio.sleep(5)
            await ctx.channel.delete()
            self.tickets.pop(ticket_num, None)
        else:
            await ctx.send("❌ This command can only be used inside a ticket channel.")

async def setup(bot):
    await bot.add_cog(AdvancedTicket(bot))
