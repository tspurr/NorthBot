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


async def badWord(message):
    global badWords

    with open('badWords.txt') as inFile:
        badWords = inFile.readlines()

    if any(word in badWords for word in message):
        return True
    else:
        return False

class messageManagment(commands.Cog):

    def __init__(self, client):
        self.client = client

    ######################################################
    #                      Events                        #
    ######################################################

    # Showing messageManagment is loaded
    @commands.Cog.listener()
    async def on_ready(self):
        print('\t- Loaded messageManagment')

        serverID = self.client.guild.id
        serverName = self.client.guild.name

        dataBase = cluster[str(serverID)]
        collection = dataBase["serverInfo"]

        query = {"_id": serverID}
        if collection.count_documents(query) == 0:
            post = {"_id": serverID, "serverName": serverName, "messageRestrictions": False}
        else:
            return

    # Deleting all TEXT messages in a specific channel
    @commands.Cog.listener()
    async def on_message(self, ctx, message):
        if str(message.channel) == "pics" and message.content != "":
            await message.channel.purge(limit=1)
        serverID = ctx.guild.id
        messageContent = ctx.message.split(" ")

        dataBase = cluster[str(serverID)]
        collection = dataBase["serverInfo"]

        if collection.find({"_id": serverID}, {"_id": 0, "serverName": 0, "messageRestrictions": 1}):
            if badWord(messageContent):
                await ctx.channel.send("^^ BAD WORD! WATCH YOUR LANGUAGE!")
            else:
                return
        else:
            return

    ######################################################
    #                     Commands                       #
    ######################################################

    # Saying Hello to anyone who wants to say hi
    @commands.command()
    async def hello(self, ctx):
        await ctx.send('Hello')

    # Deleting a specific NUMBER of messages anywhere
    @commands.command(name='delete', description='Delete 1-100 messages in a channel')
    async def delete(self, ctx, arg):
        if ctx.message.author.server_permissions.administrator:  # Have to be an administrator to run
            if int(arg) > 100:
                await ctx.channel.purge(limit=100)
                await ctx.channel.send('Limit 100 deletions!')
            else:
                await ctx.channel.purge(limit=int(arg))
        else:
            await ctx.channel.send (f'Sorry {ctx.message.author} you do not have permissions!')

    # Turning on message restrictions
    @commands.command(name='Enable Message Restrictions', description='Doesn\'t allow users to use fowl language')
    async def profanityFilter(self, ctx, onOff):
        serverID = ctx.guild.id

        dataBase = cluster[str(serverID)]
        collection = dataBase["serverInfo"]

        if onOff:
            query = {"_id": serverID}
            newValue = {"$set", {"messageRestrictions": True}}
            collection.update_one(query, newValue)
        else:
            query = {"_id": serverID}
            newValue = {"$set", {"messageRestrictions": False}}
            collection.update_one(query, newValue)


def setup(client):
    client.add_cog(messageManagment(client))

