import discord
from discord.ext import commands


class roleMenu(commands.Cog):

    def __init__(self, client):
        self.client = client

    ######################################################
    #                      Events                        #
    ######################################################

    # Event Showing roleMenu is loaded
    @commands.Cog.listener()
    async def on_ready(self):
        print('\t- Loaded roleMenu')

    ######################################################
    #                     Commands                       #
    ######################################################


def setup(client):
    client.add_cog(roleMenu(client))