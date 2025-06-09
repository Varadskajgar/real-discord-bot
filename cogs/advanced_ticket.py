import discord
from discord.ext import commands
from discord.utils import get
import json
import os

TICKET_FILE = "ticket_data.json"
if not os.path.exists(TICKET_FILE):
    with open(TICKET_FILE, "w") as f:
        json.dump({"channel_id": None}, f)

OWNER_IDS = {1076200413503701072, 862239588391321600, 1135837895496847503}

def load_ticket_channel():
    with open(TICKET_FILE) as f:
        return json.load(f).get("channel_id")

def save_ticket_channel(channel_id):
    with open(TICKET_FILE, "w") as f:
        json.dump({"channel_id": channel_id}, f)

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setticketchannel(self, ctx):
        if ctx.author.id not in OWNER_IDS:
            return
        save_ticket_channel(ctx.channel.id)
        embed = discord.Embed(
            title="🎟️ Support Tickets",
            description="Click the button below to open a ticket.\nSupport will respond soon.",
            color=discord.Color.blurple()
        )
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Open Ticket", style=discord.ButtonStyle.blurple, custom_id="open_ticket"))
        await ctx.send(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component and interaction.data["custom_id"] == "open_ticket":
            guild = interaction.guild
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True),
                guild.me: discord.PermissionOverwrite(view_channel=True)
            }
            category = get(guild.categories, name="🎫 Tickets") or await guild.create_category(name="🎫 Tickets")
            channel = await guild.create_text_channel(
                name=f"ticket-{interaction.user.name}",
                overwrites=overwrites,
                category=category
            )
            await channel.send(f"{interaction.user.mention}, welcome! Support will be with you shortly.")
            await interaction.response.send_message(f"🎟️ Ticket created: {channel.mention}", ephemeral=True)

    @commands.command()
    async def close(self, ctx):
        if "ticket" in ctx.channel.name:
            await ctx.send("🔒 Ticket closed.")
            await ctx.channel.set_permissions(ctx.author, view_channel=False)

    @commands.command()
    async def reopen(self, ctx):
        if "ticket" in ctx.channel.name:
            await ctx.channel.set_permissions(ctx.author, view_channel=True)
            await ctx.send("🔓 Ticket reopened.")

    @commands.command()
    async def perclose(self, ctx):
        if ctx.author.id not in OWNER_IDS:
            return
        if "ticket" in ctx.channel.name:
            await ctx.send("🗑️ Ticket permanently closed.")
            await ctx.channel.delete()

    @commands.command()
    async def add(self, ctx, member: discord.Member):
        if "ticket" in ctx.channel.name:
            await ctx.channel.set_permissions(member, view_channel=True, send_messages=True)
            await ctx.send(f"✅ {member.mention} added to the ticket.")

    @commands.command()
    async def remove(self, ctx, member: discord.Member):
        if "ticket" in ctx.channel.name:
            await ctx.channel.set_permissions(member, view_channel=False)
            await ctx.send(f"❌ {member.mention} removed from the ticket.")

async def setup(bot):
    await bot.add_cog(Ticket(bot))
