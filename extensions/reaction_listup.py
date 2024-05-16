import datetime
import discord
from discord import app_commands
from discord.ext import commands
from daug.utils.dpyexcept import excepter
from daug.utils.dpylog import dpylogger


class ReactionListCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name='リアクション確認',
            callback=self._listup_reaction_app_command,
        )
        self.bot.tree.add_command(self.ctx_menu)

    @app_commands.guild_only()
    @excepter
    @dpylogger
    async def _listup_reaction_app_command(self, interaction: discord.Interaction, message: discord.Message):
        if message.author != interaction.user:
            await interaction.response.send_message('自分のメッセージのみ確認することができます', ephemeral=True)
            return
        await interaction.response.send_message('DMにリアクションの内訳を送信します', ephemeral=True)
        now_jst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        embed = discord.Embed(colour=discord.Colour.yellow(), timestamp=now_jst)
        for reaction in message.reactions:
            reaction_users = [user async for user in reaction.users() if not user.bot]
            reaction_users = sorted(reaction_users, key=lambda user: user.name)
            if len(reaction_users) > 10:
                large_embeds = []
                for n in range(len(reaction_users) // 25 + 1):
                    display_users = reaction_users[n * 25: n * 25 + 25]
                    large_embed = discord.Embed(
                        title=f'{str(reaction.emoji)} {(len(reaction_users))}',
                        colour=discord.Colour.yellow(),
                        timestamp=now_jst,
                    )
                    for display_user in display_users:
                        large_embed.add_field(
                            name=display_user.display_name,
                            value=f'{display_user.mention} {display_user.name}',
                            inline=True
                        )
                    large_embed.set_footer(
                        text=f'{interaction.guild.name} | {interaction.channel.name}',
                        icon_url=interaction.guild.icon.url,
                    )
                    large_embeds.append(large_embed)
                    if len(large_embeds) >= 4:
                        await interaction.user.send(f'{message.jump_url} {str(reaction.emoji)}', embeds=large_embeds)
                        large_embeds = []
                if large_embeds:
                    await interaction.user.send(f'{message.jump_url} {str(reaction.emoji)}', embeds=large_embeds)
                continue
            embed.add_field(
                name=f'{str(reaction.emoji)}({len(reaction_users)})',
                value='\n'.join([f'{u.mention} {u.display_name.replace("`", "")} `{u.name}`' for u in reaction_users]),
                inline=False,
            )
            embed.set_footer(
                text=f'{interaction.guild.name} | {interaction.channel.name}',
                icon_url=interaction.guild.icon.url,
            )
        if len(embed.fields) > 0:
            await interaction.user.send(f'{message.jump_url} {str(reaction.emoji)}', embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ReactionListCog(bot))
