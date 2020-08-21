import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient

# Getting the NorthBot mongoDB connection URL
file = open("mongoURL.txt")
connectionURL = file.read()
file.close()

# MongoDB initialization
cluster = MongoClient(connectionURL)

# Embed Color
embedColor = discord.Color.green()


class serverStatistics(commands.Cog):

    def __init__(self, client):
        self.client = client

    """###################################################
    #                      Events                        #
    ###################################################"""

    # Event Showing serverStatistics is loaded
    @commands.Cog.listener()
    async def on_ready(self):
        print('\t- Loaded serverStatistics')

    # Keeps track of all the messages sent in servers and adds them to a mongoDB
    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author.bot:
            return

        dataBase = cluster[str(ctx.guild.id)]
        channelCollection = dataBase["channelData"]

        print(f"{ctx.channel}: {ctx.author}: {ctx.author.name}: {ctx.content}")

        myquery = {"_id": ctx.channel.id}
        if channelCollection.count_documents(myquery) == 0:
            post = {"_id": ctx.channel.id, "cName": ctx.channel.name, "numMessages": 1}
            channelCollection.insert_one(post)
        else:
            channelCollection.update_one({"_id": ctx.channel.id}, {"$inc": {"numMessages": 1}})

    """###################################################
    #                     Commands                       #
    ###################################################"""

    # TODO Gets the most talked in channel

    # TODO Gets the least talked in channel

    # TODO Gets general server statistics (responds in embed)

    # Ping command to see the latency of the bot
    @commands.command()
    async def ping(self, ctx):
        embed = discord.Embed(
            description='Pong!',
            color=embedColor
        )
        embed.set_footer(text=f'{round (self.client.latency * 1000)}ms')
        await ctx.channel.send(embed=embed)

    # Ping command to see if the file is loaded
    @commands.command(hidden=True)
    async def ping2(self, ctx):
        embed = discord.Embed(
            description='Pong!',
            color=embedColor
        )
        embed.set_footer(text=f'serverStatistics.py online')
        await ctx.channel.send(embed=embed)


def setup(client):
    client.add_cog(serverStatistics(client))
