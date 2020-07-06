import discord
import asyncio

from discord.ext import commands
from discord.ext.commands import has_permissions
from database import DatabaseDeck


class Admin(commands.Cog):
    def __init__(self, bot):
        """Initial the cog with the bot."""
        self.bot = bot

    #### Commands ####

    @commands.command(description='Set the claiming interval in minutes for all users.')
    @has_permissions(administrator=True)
    async def set_claiming_interval(self, ctx, interval):
        try:
            interval = int(interval)
        except ValueError:
            await ctx.send('Please enter as minutes as number.')
            await ctx.message.add_reaction(u"\u274C")
            return

        DatabaseDeck.get().set_claiming_interval(ctx.guild.id, interval)
        await ctx.message.add_reaction(u"\u2705")
