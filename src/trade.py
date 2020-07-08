import discord
from discord.ext import commands

from database import DatabaseIdol, DatabaseDeck


class Trade(commands.Cog):
    def __init__(self, bot):
        """Initial the cog with the bot."""
        self.bot = bot

    #### Commands ####
    @commands.command(description='Trade one idol for another.')
    async def trade(self, ctx):
        await ctx.send('WIP')
