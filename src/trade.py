import discord
import asyncio
from discord.ext import commands

from database import DatabaseIdol, DatabaseDeck


class Trade(commands.Cog):
    def __init__(self, bot):
        """Initial the cog with the bot."""
        self.bot = bot

    #### Commands ####
    @commands.command(description='Trade one idol for another.\n  *trade @someone idolname [group]')
    async def trade(self, ctx, name, group=None):
        if not ctx.message.mentions:
            await ctx.send('Please specify another user.')
            return

        user = ctx.message.mentions[0]

    @commands.command(description='Give one idol to someone.\n  *give @someone idolname [group]')
    async def give(self, ctx, user, name, group=None):
        if not ctx.message.mentions:
            await ctx.message.add_reaction(u"\u274C")
            await ctx.send('Please specify another user.')
            return

        user = ctx.message.mentions[0]

        ## Find idol id
        name = name.strip()

        if group:
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

        ## Check if idol belongs to author
        owner = DatabaseDeck.get().idol_belongs_to(ctx.guild.id, id_idol)
        if not owner or owner != ctx.author.id:
            await ctx.message.add_reaction(u"\u274C")
            await ctx.send(f'You don\'t own **{name}**{" from *" + group + "* " if group else ""}...')
            return

        def check(message):
            return message.author == user and (message.content.lower() == 'yes' or message.content.lower() == 'y' or
                                               message.content.lower() == 'no' or message.content.lower() == 'n')

        await ctx.send(f'{user.mention}, type \'y|yes\' or \'n|no\'.')
        try:
            msg = await self.bot.wait_for('message', timeout=30, check=check)
        except asyncio.TimeoutError:
            await ctx.message.add_reaction(u"\u274C")
            await ctx.send('Too late... Give is cancelled.')
        else:
            if msg.content.lower() == 'y' or msg.content.lower() == 'yes':
                DatabaseDeck.get().give_to(ctx.guild.id, id_idol, ctx.author.id, user.id)
                await msg.add_reaction(u"\u2705")
            else:
                await ctx.send('Give is cancelled.')
