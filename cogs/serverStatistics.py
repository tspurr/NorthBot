import discord
from discord.ext import commands


class serverStatistics(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Event Showing messageManagment is loaded
    @commands.Cog.listener()
    async def on_ready(self):
        print('\t- Loaded serverStatistics')


def setup(client):
    client.add_cog(serverStatistics(client))
