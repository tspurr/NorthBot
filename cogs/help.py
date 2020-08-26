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
        directMessage = await author.dm_channel.send(embed=pages[pageNumber])

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

        # Delete the help menu in the DM
        await author.dm_channel.purge(limit=1)



def setup(client):
    client.add_cog(help(client))
