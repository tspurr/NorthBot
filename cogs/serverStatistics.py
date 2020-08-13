import discord
from discord.ext import commands

class channelMessages:
    def __int__(self, name, numMessages):
        self.name = name
        self.numMessages = numMessages

        def addMessage(self):
            self.numMessages = self.numMessages + 1

class serverStatistics(commands.Cog):

    def __init__(self, client):
        self.client = client

    ######################################################
    #                      Events                        #
    ######################################################

    # Event Showing serverStatistics is loaded
    @commands.Cog.listener()
    async def on_ready(self):
        print('\t- Loaded serverStatistics')
    

    ######################################################
    #                     Commands                       #
    ######################################################


def setup(client):
    client.add_cog(serverStatistics(client))
