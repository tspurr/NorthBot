import discord
from discord.ext import commands


class roleManagement(commands.Cog):

    def __init__(self, client):
        self.client = client

    ######################################################
    #                      Events                        #
    ######################################################

    # Event Showing roleManagement is loaded
    @commands.Cog.listener()
    async def on_ready(self):
        print('\t- Loaded roleManagement')

    ######################################################
    #                     Commands                       #
    ######################################################


def setup(client):
    client.add_cog(roleManagement(client))