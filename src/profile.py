from datetime import datetime

import discord
from discord.ext import commands

from database import DatabaseDeck, DatabaseIdol
from roll import min_until_next_claim

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
        # TODO: show if idol is already claimed
        description = ''
        for id_idol in ids_deck:
            idol = DatabaseIdol.get().get_idol_information(id_idol)
            description += f'**{idol["name"]}** *{idol["group"]}*\n'

        embed = discord.Embed(title=user.name if user.nick is None else user.nick, description=description)
        embed.set_thumbnail(url=user.avatar_url)

        await ctx.send(embed=embed)

    @commands.command(aliases=['tu'], description='Show time before next rolls and claim reset.')
    async def time(self, ctx):
        next_claim = min_until_next_claim(ctx.guild.id, ctx.author.id)

        username = ctx.author.name if ctx.author.nick is None else ctx.author.nick

        msg = f'{username}, you '
        if next_claim == 0:
            msg += f'can claim right now!'
        else:
            time = divmod(next_claim, 60)
            msg += f'can\'t claim for another **' + \
                   (str(time[0]) + 'h ' if time[0] != 0 else '') + f'{str(time[1])} min**.'

        user_nb_rolls = DatabaseDeck.get().get_nb_rolls(ctx.guild.id, ctx.author.id)
        max_rolls = DatabaseDeck.get().get_rolls_per_hour(ctx.guild.id)

        last_roll = DatabaseDeck.get().get_last_roll(ctx.guild.id, ctx.author.id)
        if not last_roll:
            user_nb_rolls = 0
        else:
            last_roll = datetime.strptime(last_roll, '%Y-%m-%d %H:%M:%S')
            now = datetime.now()

            # If a new hour began
            if now.date() != last_roll.date() or (now.date() == last_roll.date() and now.hour != last_roll.hour):
                user_nb_rolls = 0

        msg += f'\nYou have **{max_rolls - user_nb_rolls}** rolls left.\n' \
               f'Next rolls reset in **{60 - datetime.now().minute} min**.'

        await ctx.send(msg)
