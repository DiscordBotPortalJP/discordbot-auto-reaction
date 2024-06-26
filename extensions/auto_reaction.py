import discord
from discord.ext import commands
from utils import extract_emojis
from utils.database import cache_emojis
from utils.database import get_emojis
from utils.database import upsert_emojis
from utils.database import delete_emojis
from daug.utils.dpyexcept import excepter
from daug.constants import COLOUR_EMBED_GRAY


class AutoReactionCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    @excepter
    async def on_ready(self):
        await cache_emojis()

    @commands.Cog.listener()
    @excepter
    async def on_message(self, message: discord.Message):
        if message.content:
            strings = message.content.split()
            if strings[0] == self.bot.user.mention and not message.author.bot:
                if message.author.guild_permissions.manage_channels:
                    if len(strings) == 1:
                        await delete_emojis(message.channel.id)
                        await message.reply('自動リアクション設定を解除しました', delete_after=10)
                        return
                    else:
                        emojis = extract_emojis(message.content)
                        if len(emojis) > 0:
                            await upsert_emojis(message.channel.id, emojis)
                            await message.reply(
                                '自動リアクション設定を追加しました',
                                embed=discord.Embed(title='設定した絵文字', description=' '.join(emojis), colour=COLOUR_EMBED_GRAY),
                                delete_after=10
                            )
                            return
        emojis = get_emojis(message.channel.id)
        if emojis is None:
            return
        for emoji in emojis:
            try:
                await message.add_reaction(emoji)
            except discord.errors.HTTPException:
                pass


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AutoReactionCog(bot))
