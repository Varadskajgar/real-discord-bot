import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
from discord import Interaction, TextStyle

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CreateTicketButton())

class CreateTicketButton(Button):
    def __init__(self):
        super().__init__(label="Create Ticket 🎟️", style=discord.ButtonStyle.green, custom_id="create_ticket")

    async def callback(self, interaction: Interaction):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, id=self.view.cog.ticket_category_id)

        # Check if user already has ticket open
        existing = discord.utils.get(guild.text_channels, name=f"ticket-{interaction.user.id}")
        if existing:
            await interaction.response.send_message("❌ You already have an open ticket!", ephemeral=True)
            return

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.id}",
            category=category,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
        )

        await ticket_channel.send(
            content=f"{interaction.user.mention}, welcome to your ticket!",
            embed=discord.Embed(
                description="Our team will be with you shortly. Use the buttons below to manage this ticket.",
                color=discord.Color.blue()
            ),
            view=ManageTicketButtons()
        )
        await interaction.response.send_message(f"✅ Ticket created: {ticket_channel.mention}", ephemeral=True)

class ManageTicketButtons(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CloseButton())
        self.add_item(ReopenButton())
        self.add_item(AddUserButton())
        self.add_item(RemoveUserButton())
        self.add_item(PermCloseButton())

class CloseButton(Button):
    def __init__(self):
        super().__init__(emoji="🔒", style=discord.ButtonStyle.danger, custom_id="close_ticket")

    async def callback(self, interaction: Interaction):
        await interaction.channel.set_permissions(interaction.user, read_messages=False)
        await interaction.response.send_message("🔒 Ticket closed.", ephemeral=False)

class ReopenButton(Button):
    def __init__(self):
        super().__init__(emoji="🔓", style=discord.ButtonStyle.success, custom_id="reopen_ticket")

    async def callback(self, interaction: Interaction):
        await interaction.channel.set_permissions(interaction.user, read_messages=True)
        await interaction.response.send_message("🔓 Ticket reopened.", ephemeral=False)

class AddUserButton(Button):
    def __init__(self):
        super().__init__(emoji="➕", style=discord.ButtonStyle.primary, custom_id="add_user")

    async def callback(self, interaction: Interaction):
        modal = AddRemoveUserModal(title="Add User", add=True)
        await interaction.response.send_modal(modal)

class RemoveUserButton(Button):
    def __init__(self):
        super().__init__(emoji="➖", style=discord.ButtonStyle.secondary, custom_id="remove_user")

    async def callback(self, interaction: Interaction):
        modal = AddRemoveUserModal(title="Remove User", add=False)
        await interaction.response.send_modal(modal)

class AddRemoveUserModal(Modal):
    def __init__(self, title: str, add: bool):
        super().__init__(title=title)
        self.add = add
        self.user_id = TextInput(label="User ID", style=TextStyle.short)
        self.add_item(self.user_id)

    async def on_submit(self, interaction: Interaction):
        try:
            user = await interaction.guild.fetch_member(int(self.user_id.value))
            perms = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            await interaction.channel.set_permissions(user, overwrite=perms if self.add else None)
            action = "added to" if self.add else "removed from"
            await interaction.response.send_message(f"✅ {user.mention} {action} the ticket.", ephemeral=False)
        except:
            await interaction.response.send_message("❌ Invalid user ID.", ephemeral=True)

class PermCloseButton(Button):
    def __init__(self):
        super().__init__(emoji="🗑️", style=discord.ButtonStyle.red, custom_id="perm_close")

    async def callback(self, interaction: Interaction):
        await interaction.response.send_message("🗑️ Ticket will be deleted in 5 seconds.")
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.timedelta(seconds=5))
        await interaction.channel.delete()

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ticket_category_id = None

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setticketchannel(self, ctx, category: discord.CategoryChannel):
        self.ticket_category_id = category.id
        embed = discord.Embed(
            title="🎫 Support Tickets",
            description="Click the button below to create a ticket. Our support team will assist you shortly.",
            color=discord.Color.blurple()
        )
        embed.set_footer(text="Powered by TL ESPORT")
        await ctx.send(embed=embed, view=TicketView())

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ticket(self, ctx):
        if not self.ticket_category_id:
            await ctx.send("Please set a ticket category first with `?setticketchannel`.")
            return

        embed = discord.Embed(
            title="🎟️ Need Help?",
            description="Click the button below to create a support ticket.\nOur team will help you shortly.",
            color=discord.Color.green()
        )
        embed.set_footer(text="Ticket Tool UI • TL ESPORT")
        await ctx.send(embed=embed, view=TicketView())

async def setup(bot):
    cog = TicketSystem(bot)
    bot.add_view(TicketView())  # Persistent button view
    bot.add_view(ManageTicketButtons())
    await bot.add_cog(cog)
