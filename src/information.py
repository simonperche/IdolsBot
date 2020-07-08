import asyncio
import secrets

import discord
from discord.ext import commands

from database import DatabaseIdol, DatabaseDeck


class Information(commands.Cog):

    def parse_int(self, content):
        try:
            return int(content)
        except ValueError:
            return 0

    def __init__(self, bot):
        """Initial the cog with the bot."""
        self.bot = bot

    #### Commands ####

    @commands.command(aliases=['info'], description='Show information about an idol. '
                                                    'Please enter the name of the idol '
                                                    'with group (optional). Please add ""'
                                                    'if it has spaces\n'
                                                    'Take the first corresponding idol.'
                                                    'See list command for all idols.\n'
                                                    'Example:\n'
                                                    '   *info heejin loona'
                                                    '   *info joy "red velvet"')
    async def information(self, ctx, name, group=None):
        # TODO: add more information to the card (all groups...)
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

        idol = DatabaseIdol.get().get_idol_information(id_idol, ctx.guild.id)

        embed = discord.Embed(title=idol['name'], description=idol['group'], colour=secrets.randbelow(0xffffff))

        id_owner = DatabaseDeck.get().idol_belongs_to(ctx.guild.id, id_idol)

        # Counter variables
        total_images = DatabaseIdol.get().get_idol_images_count(id_idol)
        current_image = self.parse_int(DatabaseDeck().get().get_idol_current_image(ctx.guild.id, id_idol)) + 1

        # Footer have always the picture counter, and eventually the owner info
        text = f'{current_image} \\ {total_images} \n'
        if id_owner:
            owner = ctx.guild.get_member(id_owner)
            if owner:
                text = f'{text}Belongs to {owner.name if not owner.nick else owner.nick}'
                embed.set_footer(icon_url=owner.avatar_url, text=text)
        else:
            embed.set_footer(text=text)

        embed.set_image(url=idol['image'])

        msg = await ctx.send(embed=embed)

        left_emoji = '\U00002B05'
        right_emoji = '\U000027A1'
        await msg.add_reaction(left_emoji)
        await msg.add_reaction(right_emoji)

        def check(reaction, user):
            return user != self.bot.user and (str(reaction.emoji) == left_emoji or str(reaction.emoji) == right_emoji) \
                   and reaction.message.id == msg.id

        timeout = False

        while not timeout:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=10, check=check)
            except asyncio.TimeoutError:
                await msg.clear_reaction(left_emoji)
                await msg.clear_reaction(right_emoji)
                timeout = True
            else:
                old_image = current_image
                if reaction.emoji == left_emoji:
                    DatabaseDeck.get().decrement_idol_current_image(ctx.guild.id, id_idol)

                if reaction.emoji == right_emoji:
                    DatabaseDeck.get().increment_idol_current_image(ctx.guild.id, id_idol)

                current_image = self.parse_int(DatabaseDeck().get().get_idol_current_image(ctx.guild.id, id_idol)) + 1
                await msg.remove_reaction(reaction.emoji, user)

                # Refresh embed message with the new picture if changed
                if old_image != current_image:
                    # Redo the query because image link changed
                    idol = DatabaseIdol.get().get_idol_information(id_idol, ctx.guild.id)
                    embed.set_image(url=idol['image'])
                    text = f'{current_image} \\ {total_images} \n'
                    if id_owner and owner:
                        text = f'{text}Belongs to {owner.name if not owner.nick else owner.nick}'
                        embed.set_footer(icon_url=owner.avatar_url, text=text)
                    else:
                        embed.set_footer(text=text)

                    await msg.edit(embed=embed)

    @commands.command(description='List all idols with its name')
    async def list(self, ctx, *, name):
        ids = DatabaseIdol.get().get_idol_ids(name)

        description = '' if ids else 'No idols found'
        for id_idol in ids:
            idol = DatabaseIdol.get().get_idol_information(id_idol, ctx.guild.id)
            description += f'**{idol["name"]}** *{idol["group"]}*\n'

        embed = discord.Embed(title=f'{name} idols', description=description)
        await ctx.send(embed=embed)

    @commands.command(description='Show all members of a group')
    async def group(self, ctx, *, group_name):
        group = DatabaseIdol.get().get_group_members(group_name)

        if not group:
            ctx.send(f'No *{group_name}* group found.')
            return

        embed = discord.Embed(title=f'*{group["name"]}* group',
                              description='\n'.join([f'**{member}**' for member in group['members']]))

        await ctx.send(embed=embed)
