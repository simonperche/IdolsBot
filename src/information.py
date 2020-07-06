import discord
import asyncio
import secrets

from discord.ext import commands
from database import DatabaseIdol


class Information(commands.Cog):
    def __init__(self, bot):
        """Initial the cog with the bot."""
        self.bot = bot

    #### Commands ####

    @commands.command(aliases=['info'], description='Show information about an idol. '
                                                    'Please enter the name of the idol '
                                                    'with group in parentheses (optional).\n'
                                                    'Take the first corresponding idol.'
                                                    'See list command for all idols.')
    async def information(self, ctx, *, parameters):
        # Parse parameters
        first_parenthesis = parameters.find('(')
        last_parenthesis = parameters.rfind(')')

        name = ''
        group = ''

        if first_parenthesis != -1 and last_parenthesis != -1:
            group = parameters[first_parenthesis + 1:last_parenthesis]
            name = parameters[0:first_parenthesis]
        else:
            name = parameters

        name = name.strip()
        group = group.strip()

        id_idol = None

        if group:
            id_idol = DatabaseIdol.get().get_idol_group_id(name, group)
        else:
            ids = DatabaseIdol.get().get_idol_ids(name)
            if ids:
                id_idol = ids[0]

        if not id_idol:
            msg = f'I searched everywhere for **{name}**'
            if group:
                msg += f' in the group *{group}*'
            msg += ' and I couldn\'t find anything.\nPlease check the command.'
            await ctx.send(msg)
            return

        idol = DatabaseIdol.get().get_idol_information(id_idol)

        # TODO: Add message if idol belongs to a member
        embed = discord.Embed(title=idol['name'], description=idol['group'], colour=secrets.randbelow(0xffffff))

        # TODO: add pages to go through images
        embed.set_image(url=idol['image'])

        await ctx.send(embed=embed)
