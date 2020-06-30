import random
import discord
from database import DatabaseIdol

from discord.ext import commands

class Roll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #### Commands ####

    @commands.command(description='Roll a random idom and get the possibility to claim it.')
    async def roll(self, ctx):
        idol = DatabaseIdol.get().get_idol_information(DatabaseIdol.get().get_random_idol_id())
        if not idol:
            ctx.send("An error occurred. If this message is exceptional, please try again. Otherwise, contact the administrator.")

        embed = discord.Embed(title=idol['name'], description=idol['group'], colour=random.randint(0, 0xffffff))
        embed.set_image(url=idol['image'])

        await ctx.send(embed=embed)
