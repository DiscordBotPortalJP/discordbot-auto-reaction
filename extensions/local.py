import discord
from discord.ext import commands
from daug.utils.dpyexcept import excepter

REGEXP_CUSTOM_EMOJI = r'<:[-_.!~*\'()a-zA-Z0-9;\/?:\@&=+\$,%#]+:[0-9]+>'


class LocalCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    @excepter
    async def on_message(self, message: discord.Message):
        print(message.content)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(LocalCog(bot))
