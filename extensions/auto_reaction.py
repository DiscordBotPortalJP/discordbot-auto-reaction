import discord
from discord import app_commands
from discord.ext import commands
from utils import extract_emojis
from utils.database import get_emojis
from utils.database import upsert_emojis
from utils.database import delete_emojis
from daug.utils.dpyexcept import excepter
from daug.utils.dpylog import dpylogger
from daug.constants import COLOUR_EMBED_GRAY


class AutoReactionCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name='リアクション補完',
            callback=self.reaction_for_single_message_from_menu,
        )
        self.bot.tree.add_command(self.ctx_menu)

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

    @app_commands.command(name='リアクション設定確認', description='現在設定されているリアクションを確認します')
    @app_commands.default_permissions(administrator=True)
    @app_commands.guild_only()
    @excepter
    @dpylogger
    async def _check_setting_reaction_app_command(self, interaction: discord.Interaction):
        emojis = get_emojis(interaction.channel.id)
        await interaction.response.send_message(
            embed=discord.Embed(title='設定した絵文字', description=' '.join(emojis), colour=COLOUR_EMBED_GRAY),
        )

    @app_commands.command(name='リアクション補完', description='チャンネル内のすべてのメッセージにリアクションを付けます')
    @app_commands.default_permissions(administrator=True)
    @app_commands.guild_only()
    @excepter
    @dpylogger
    async def _reaction_for_channel_app_command(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        emojis = get_emojis(interaction.channel.id)
        await interaction.followup.send(
            'チャンネル内のすべてのメッセージにリアクションを付けます',
            embed=discord.Embed(title='設定中の絵文字', description=' '.join(emojis), colour=COLOUR_EMBED_GRAY),
            ephemeral=True,
        )
        async for message in interaction.channel.history(limit=None):
            for emoji in emojis:
                try:
                    await message.add_reaction(emoji)
                except discord.errors.HTTPException:
                    pass
        await interaction.followup.send(
            'チャンネル内のすべてのメッセージにリアクションを付けました',
            embed=discord.Embed(title='設定中の絵文字', description=' '.join(emojis), colour=COLOUR_EMBED_GRAY),
            ephemeral=True,
        )

    @app_commands.default_permissions(administrator=True)
    @app_commands.guild_only()
    @excepter
    @dpylogger
    async def reaction_for_single_message_from_menu(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        emojis = get_emojis(interaction.channel.id)
        for emoji in get_emojis(interaction.channel.id):
            try:
                await interaction.message.add_reaction(emoji)
            except discord.errors.HTTPException:
                pass
        await interaction.followup.send(
            f'メッセージ {interaction.message.jump_url} にリアクションを付けました',
            embed=discord.Embed(title='設定中の絵文字', description=' '.join(emojis), colour=COLOUR_EMBED_GRAY),
            ephemeral=True,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AutoReactionCog(bot))
