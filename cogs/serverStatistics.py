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
            query = {"_id": ctx.channel.id}
            user = channelCollection.find(query)
            for result in user:
                numMessages = result["numMessages"]
            numMessages += 1
            channelCollection.update_one({"_id": ctx.channel.id}, {"$set": {"numMessages": numMessages}})

    ######################################################
    #                     Commands                       #
    ######################################################


def setup(client):
    client.add_cog(serverStatistics(client))
