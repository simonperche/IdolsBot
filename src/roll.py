import secrets
import discord
import asyncio
from datetime import datetime

from database import DatabaseIdol, DatabaseDeck
from discord.ext import commands


class Roll(commands.Cog):
    CLAIM_TIMEOUT = 5.0

    def __init__(self, bot):
        """Initial the cog with the bot."""
        self.bot = bot

    #### Commands ####

    @commands.command(description='Roll a random idom and get the possibility to claim it.')
    async def roll(self, ctx):
        idol = DatabaseIdol.get().get_idol_information(DatabaseIdol.get().get_random_idol_id())
        if not idol:
            ctx.send("An error occurred. If this message is exceptional, "
                     "please try again. Otherwise, contact the administrator.")

        embed = discord.Embed(title=idol['name'], description=idol['group'], colour=secrets.randbelow(0xffffff))
        embed.set_image(url=idol['image'])

        msg = await ctx.send(embed=embed)
        emoji = '\N{TWO HEARTS}'
        await msg.add_reaction(emoji)

        def check(reaction, user):
            return user != self.bot.user and str(reaction.emoji) == emoji and reaction.message.id == msg.id

        is_claimed_or_timeout = False

        while not is_claimed_or_timeout:
            try:
                _, user = await self.bot.wait_for('reaction_add', timeout=Roll.CLAIM_TIMEOUT, check=check)
            except asyncio.TimeoutError:
                # Temporary message
                await msg.remove_reaction(emoji, self.bot.user)
                is_claimed_or_timeout = True
            else:
                is_claimed_or_timeout = await claim(ctx, user, idol)


#### Utilities functions ####

async def claim(ctx, user, idol):
    """Add idol to user's deck if he can claim."""
    id_server = ctx.guild.id
    can_claim = False

    last_claim = DatabaseDeck.get().get_last_claim(id_server, user.id)

    time_until_claim = 0

    # User never claimed an idol
    if last_claim == -1:
        can_claim = True
    else:
        claim_interval = DatabaseDeck.get().get_claim_interval(id_server)
        date_last_claim = datetime.strptime(last_claim, '%Y-%m-%d %H:%M:%S')
        minute_since_last_claim = divmod((datetime.now() - date_last_claim).seconds, 60)[0]

        if minute_since_last_claim >= claim_interval:
            can_claim = True
        else:
            time_until_claim = claim_interval - minute_since_last_claim

    username = user.name if user.nick is None else user.nick
    if can_claim:
        DatabaseDeck.get().add_to_deck(id_server, idol['id'], user.id)
        await ctx.send(f'{username} claims {idol["name"]}!')
    else:
        time = divmod(time_until_claim, 60)
        await ctx.send(f'{username}, you can\'t claim right now. '
                       f'Please wait {str(time[0])} h {str(time[1])} min.')

    return can_claim
