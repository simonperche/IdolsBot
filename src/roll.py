import random
import discord
import asyncio
from database import DatabaseIdol

from discord.ext import commands


class Roll(commands.Cog):
    CLAIM_TIMEOUT = 5.0

    def __init__(self, bot):
        self.bot = bot

    #### Commands ####

    @commands.command(description='Roll a random idom and get the possibility to claim it.')
    async def roll(self, ctx):
        idol = DatabaseIdol.get().get_idol_information(DatabaseIdol.get().get_random_idol_id())
        if not idol:
            ctx.send("An error occurred. If this message is exceptional, "
                     "please try again. Otherwise, contact the administrator.")

        embed = discord.Embed(title=idol['name'], description=idol['group'], colour=random.randint(0, 0xffffff))
        embed.set_image(url=idol['image'])

        msg = await ctx.send(embed=embed)
        await msg.add_reaction('\N{TWO HEARTS}')

        def check(reaction, user):
            return user != self.bot.user and str(reaction.emoji) == '\N{TWO HEARTS}' and reaction.message.id == msg.id

        try:
            _, user = await self.bot.wait_for('reaction_add', timeout=Roll.CLAIM_TIMEOUT, check=check)
        except asyncio.TimeoutError:
            # Temporary message
            await ctx.send('Too late to claim ' + idol['name'] + '...')
        else:
            # Temporary message. Will add to deck if user is able to claim.
            await ctx.send(user.name + ' claims ' + idol['name'] + ' !')
