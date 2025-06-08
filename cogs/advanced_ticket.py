import discord
from discord.ext import commands
from discord.ui import Button, View
from discord.utils import get

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="🎫 Create Ticket", style=discord.ButtonStyle.blurple, custom_id="create_ticket"))

class ManageTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="🔒 Close", style=discord.ButtonStyle.red, custom_id="close_ticket"))
        self.add_item(Button(label="🔓 Reopen", style=discord.ButtonStyle.green, custom_id="reopen_ticket"))
        self.add_item(Button(label="➕ Add User", style=discord.ButtonStyle.gray, custom_id="add_user"))
        self.add_item(Button(label="➖ Remove User", style=discord.ButtonStyle.gray, custom_id="remove_user"))

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ticket_category_id = None  # set this with ?setticketchannel
        self.ticket_log_channel_id = None

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setticketchannel(self, ctx, category: discord.CategoryChannel):
        self.ticket_category_id = category.id
        embed = discord.Embed(
            title="Need Help? 🎟️",
            description="Click the button below to create a ticket.\nA staff member will assist you shortly.",
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/2972/2972185.png")
        embed.set_footer(text="Ticket Tool System • Powered by TL ESPORT")
        await ctx.send(embed=embed, view=TicketView())

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if not interaction.type == discord.InteractionType.component:
            return

        if interaction.data["custom_id"] == "create_ticket":
            if not self.ticket_category_id:
                await interaction.response.send_message("Ticket system not configured.", ephemeral=True)
                return

            guild = interaction.guild
            category = guild.get_channel(self.ticket_category_id)
            existing_channel = get(guild.text_channels, name=f"ticket-{interaction.user.name.lower().replace(' ', '-')}")
            if existing_channel:
                await interaction.response.send_message(f"You already have a ticket: {existing_channel.mention}", ephemeral=True)
                return

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
                guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
            }

            channel = await guild.create_text_channel(
                name=f"ticket-{interaction.user.name}",
                category=category,
                overwrites=overwrites,
                reason="Ticket created"
            )

            embed = discord.Embed(
                title=f"🎫 Ticket - {interaction.user}",
                description="Please describe your issue. A staff member will reply soon.",
                color=discord.Color.blurple()
            )
            embed.set_footer(text="Use the buttons below to manage this ticket.")
            await channel.send(content=f"{interaction.user.mention}", embed=embed, view=ManageTicketView())
            await interaction.response.send_message(f"Ticket created: {channel.mention}", ephemeral=True)

        elif interaction.data["custom_id"] == "close_ticket":
            await interaction.channel.edit(locked=True, reason="Ticket closed")
            await interaction.response.send_message("🔒 Ticket closed.")

        elif interaction.data["custom_id"] == "reopen_ticket":
            await interaction.channel.edit(locked=False, reason="Ticket reopened")
            await interaction.response.send_message("🔓 Ticket reopened.")

        elif interaction.data["custom_id"] == "add_user":
            await interaction.response.send_message("Mention a user to add them.", ephemeral=True)

        elif interaction.data["custom_id"] == "remove_user":
            await interaction.response.send_message("Mention a user to remove them.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
