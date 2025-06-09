import discord
from discord.ext import commands
from discord.utils import get
import json
import os

TICKET_FILE = "ticket_data.json"
if not os.path.exists(TICKET_FILE):
    with open(TICKET_FILE, "w") as f:
        json.dump({"channel_id": None, "active_tickets": {}}, f)

OWNER_IDS = {1076200413503701072, 862239588391321600, 1135837895496847503}


def load_data():
    with open(TICKET_FILE) as f:
        return json.load(f)


def save_data(data):
    with open(TICKET_FILE, "w") as f:
        json.dump(data, f)


class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setticketchannel(self, ctx, channel: discord.TextChannel = None):
        if ctx.author.id not in OWNER_IDS:
            return await ctx.send("❌ You are not authorized to use this command.")
        if not channel:
            return await ctx.send("⚠️ Mention a channel like `?setticketchannel #channel`")

        data = load_data()
        data["channel_id"] = channel.id
        save_data(data)

        embed = discord.Embed(
            title="🎟️ Create a Support Ticket",
            description="Click the button below to open a ticket.\nSupport will assist you shortly.",
            color=discord.Color.blurple()
        )
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Open Ticket", style=discord.ButtonStyle.blurple, custom_id="open_ticket"))
        await channel.send(embed=embed, view=view)
        await ctx.send(f"✅ Ticket panel sent to {channel.mention}")

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component and interaction.data["custom_id"] == "open_ticket":
            user = interaction.user
            guild = interaction.guild
            data = load_data()
            active_tickets = data.get("active_tickets", {})

            if str(user.id) in active_tickets:
                existing_channel_id = active_tickets[str(user.id)]
                existing_channel = guild.get_channel(existing_channel_id)
                if existing_channel:
                    await interaction.response.send_message(
                        f"❌ You already have an open ticket: {existing_channel.mention}", ephemeral=True
                    )
                    return
                else:
                    # If the channel no longer exists, remove from active
                    del active_tickets[str(user.id)]
                    save_data(data)

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True),
                guild.me: discord.PermissionOverwrite(view_channel=True)
            }

            category = get(guild.categories, name="🎫 Tickets") or await guild.create_category(name="🎫 Tickets")
            channel = await guild.create_text_channel(
                name=f"ticket-{user.name}",
                overwrites=overwrites,
                category=category
            )

            await channel.send(f"{user.mention}, welcome! Support will be with you shortly.")
            await interaction.response.send_message(f"🎟️ Ticket created: {channel.mention}", ephemeral=True)

            data["active_tickets"][str(user.id)] = channel.id
            save_data(data)

    @commands.command()
    async def close(self, ctx):
        if "ticket" in ctx.channel.name:
            data = load_data()
            for user_id, channel_id in list(data["active_tickets"].items()):
                if channel_id == ctx.channel.id:
                    del data["active_tickets"][user_id]
                    break
            save_data(data)
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
            data = load_data()
            for user_id, channel_id in list(data["active_tickets"].items()):
                if channel_id == ctx.channel.id:
                    del data["active_tickets"][user_id]
                    break
            save_data(data)
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
