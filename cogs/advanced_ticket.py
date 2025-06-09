import discord
from discord.ext import commands
from discord.utils import get

TICKET_CATEGORY_NAME = "Tickets"
OWNER_IDS = {1076200413503701072, 862239588391321600, 1135837895496847503}

class AdvancedTicket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ticket_message_id = None
        self.ticket_category = None

    @commands.command()
    async def setticketchannel(self, ctx):
        if ctx.author.id not in OWNER_IDS:
            return await ctx.send("❌ You don't have permission to use this command.")
        
        embed = discord.Embed(
            title="🎫 Need Help? Open a Ticket!",
            description="Click the button below to create a support ticket. Our team will assist you shortly.",
            color=discord.Color.green()
        )
        embed.set_footer(text="Ticket System | TL ESPORT", icon_url=ctx.guild.icon.url)

        view = TicketOpenView(self.bot)
        msg = await ctx.send(embed=embed, view=view)
        self.ticket_message_id = msg.id

    async def create_ticket(self, interaction: discord.Interaction):
        guild = interaction.guild
        author = interaction.user

        category = get(guild.categories, name=TICKET_CATEGORY_NAME)
        if not category:
            category = await guild.create_category(TICKET_CATEGORY_NAME)

        existing = discord.utils.get(category.channels, name=f"ticket-{author.name.lower().replace(' ', '-')}")
        if existing:
            return await interaction.response.send_message("❌ You already have an open ticket.", ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            author: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }

        ticket_channel = await guild.create_text_channel(name=f"ticket-{author.name}", category=category, overwrites=overwrites)
        await interaction.response.send_message(f"✅ Ticket created: {ticket_channel.mention}", ephemeral=True)

        embed = discord.Embed(
            title="🎫 Ticket Opened",
            description="Support will be with you shortly.\nUse buttons below to manage your ticket.",
            color=discord.Color.blue()
        )
        view = TicketControlView(self.bot, ticket_channel, author)
        await ticket_channel.send(content=author.mention, embed=embed, view=view)

class TicketOpenView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="🎟️ Create Ticket", style=discord.ButtonStyle.blurple)
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.bot.get_cog("AdvancedTicket").create_ticket(interaction)

class TicketControlView(discord.ui.View):
    def __init__(self, bot, channel, author):
        super().__init__(timeout=None)
        self.bot = bot
        self.channel = channel
        self.author = author

    @discord.ui.button(label="🔒 Close", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author and interaction.user.id not in OWNER_IDS:
            return await interaction.response.send_message("❌ Only the ticket owner or staff can close this ticket.", ephemeral=True)
        await self.channel.edit(name=f"closed-{self.channel.name}")
        await interaction.response.send_message("✅ Ticket closed. Use 🔓 to reopen.", ephemeral=True)

    @discord.ui.button(label="🔓 Reopen", style=discord.ButtonStyle.green)
    async def reopen(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.channel.edit(name=f"ticket-{self.author.name}")
        await interaction.response.send_message("✅ Ticket reopened.", ephemeral=True)

    @discord.ui.button(label="📝 Transcript", style=discord.ButtonStyle.grey)
    async def transcript(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("📄 Transcript feature coming soon.", ephemeral=True)

    @discord.ui.button(label="➕ Add", style=discord.ButtonStyle.blurple)
    async def add(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("👤 Mention the user to add them.", ephemeral=True)

    @discord.ui.button(label="➖ Remove", style=discord.ButtonStyle.blurple)
    async def remove(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("👤 Mention the user to remove them.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdvancedTicket(bot))
