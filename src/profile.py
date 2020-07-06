import discord
import asyncio

from discord.ext import commands
from database import DatabaseDeck, DatabaseIdol


class Profile(commands.Cog):
    def __init__(self, bot):
        """Initial the cog with the bot."""
        self.bot = bot

    #### Commands ####

    @commands.command(aliases=['pr'], description='Show the user profile or yours if no user given.')
    async def profile(self, ctx):
        user = ctx.author if not ctx.message.mentions else ctx.message.mentions[0]

        ids_deck = DatabaseDeck.get().get_user_deck(ctx.guild.id, user.id)

        # TODO: handle long messages (>2000 letters) with pages
        description = ''
        for id_idol in ids_deck:
            idol = DatabaseIdol.get().get_idol_information(id_idol)
            description += f'**{idol["name"]}** (*{idol["group"]}*)\n'

        embed = discord.Embed(title=user.name if user.nick is None else user.nick, description=description)
        embed.set_thumbnail(url=user.avatar_url)

        await ctx.send(embed=embed)
