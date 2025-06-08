from discord.ext import commands

OWNER_IDS = {1076200413503701072, 862239588391321600, 1135837895496847503}

def stylize_text(text: str) -> str:
    mapping = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ',
        'f': 'ꜰ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ',
        'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ',
        'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ',
        'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ',
        'z': 'ᴢ', ' ': ' '
    }
    return ''.join(mapping.get(c, c) for c in text.lower())

class StyledResponder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def name(self, ctx, action=None, *, text=None):
        if ctx.author.id not in OWNER_IDS:
            return
        if action == "change" and text:
            styled = stylize_text(text)
            await ctx.send(f"ᴛʟ  {styled}࿐")  # No space before symbol
        else:
            await ctx.send("Usage: ?name change <text>")

async def setup(bot):
    await bot.add_cog(StyledResponder(bot))
