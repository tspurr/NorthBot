"""
The MIT License (MIT)

Copyright (c) 2020 Tyler Spurr

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import discord
from discord.ext import commands


class help(commands.Cog, name='Help'):

    def __init__(self, client):
        self.client = client

    """###################################################
    #                      Events                        #
    ###################################################"""

    @commands.Cog.listener()
    async def on_ready(self):
        print('\t- Loaded help')

    """###################################################
    #                     Commands                       #
    ###################################################"""

    @commands.command()
    async def help(self, ctx):

        # Help menu page for messageManagement
        embedMM = discord.Embed(
            title='Help Message Management',
            color=discord.Color.red()
        )

        # Help menu page for reputation
        embedRep = discord.Embed(
            title='Help Reputation',
            color=discord.Color.orange()
        )

        # Help menu page for roleManagement
        embedRMa = discord.Embed(
            title='Help Role Management',
            color=discord.Color.teal()  # No Yellow Color
        )

        # Help menu page for roleMenu
        embedRMe = discord.Embed(
            title='Help Role Menu',
            color=discord.Color.green()
        )

        # Help menu page for serverStatistics
        embedSS = discord.Embed(
            title='Help Server Statistics',
            color=discord.Color.blue()
        )

        # Help menu page for twitch
        embedTW = discord.Embed(
            title='Help Twitch',
            color=discord.Color.purple()
        )

        # Array of embeds
        pages = {embedMM, embedRep, embedRMa, embedRMe, embedSS, embedTW}
        # Author of the command
        author = ctx.author
        pageNumber = 0

        # Creating a DM with the author
        await author.create_dm()
        directMessage = await author.dm_channel.send(embed=pages)

        # Adding navigation arrows to message
        await directMessage.add_reaction('⬅')  # Arrow Left
        await directMessage.add_reaction('➡')  # Arrow Right
        await directMessage.add_reaction('🗑️')  # Waste Basket

        # Waiting for the user to react
        userReaction, user = await self.client.wait_for('reaction_add', timeout=120.0)

        # while the user is looking through the reaction menu
        while userReaction != '🗑️':

            # Going back a page if we are not on the first page
            if userReaction == '⬅' and pageNumber != 0:
                pageNumber += -1
                await directMessage.edit(embed=pages[pageNumber])
                await directMessage.remove_reaction('⬅', author)

            # Going back a page if we are at the first page
            elif userReaction == '⬅' and pageNumber == 0:
                pageNumber = len(pages) - 1
                await directMessage.edit(embed=pages[pageNumber])
                await directMessage.remove_reaction('⬅', author)

            # Going forward a page if we are not at the last page
            elif userReaction == '➡' and pageNumber != len(pages) - 1:
                pageNumber += 1
                await directMessage.edit(embed=pages[pageNumber])
                await directMessage.remove_reaction('➡', author)

            # Going forward a page if we are at the last page
            elif userReaction == '➡' and pageNumber == len(pages) - 1:
                pageNumber = 0
                await directMessage.edit(embed=pages[pageNumber])
                await directMessage.remove_reaction('➡', author)

            # Waiting for the user to react
            userReaction, user = await self.client.wait_for('reaction_add', timeout=120.0)

        # Delete the help menu in the DM
        await author.dm_channel.purge(limit=1)



def setup(client):
    client.add_cog(help(client))
