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


def badWord(message):
    badWords = None

    with open('badWords.txt') as inFile:
        badWords = inFile.readlines()
    inFile.close()

    return any(word[:-1] in message for word in badWords)


class messageManagement(commands.Cog):

    def __init__(self, client):
        self.client = client

    ######################################################
    #                      Events                        #
    ######################################################

    # Showing messageManagment is loaded
    @commands.Cog.listener()
    async def on_ready(self):
        print('\t- Loaded messageManagement')

        servers = self.client.guilds
        serverNames = discord.Guild.name

        for server in servers:
            dataBase = cluster[str(server.id)]
            collection = dataBase["serverInfo"]

            query = {"_id": server.id}
            if collection.count_documents(query) == 0:
                post = {"_id": server.id, "serverName": server.name, "messageRestrictions": False}
                collection.insert_one(post)

    # Deleting all TEXT messages in a specific channel
    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author.bot:
            return

        if str(ctx.channel) == "pics" and ctx.content != "":
            await ctx.channel.purge(limit=1)

        serverID = ctx.guild.id
        messageContent = ctx.content.split(" ")

        dataBase = cluster[str(serverID)]
        collection = dataBase["serverInfo"]

        query = collection.find_one({"_id": serverID}, {"_id": 0, "messageRestrictions": 1})
        print(query['messageRestrictions'])
        if query['messageRestrictions']:
            if badWord(messageContent):
                await ctx.channel.purge(limit=1)
                await ctx.channel.send("^^ BAD WORD! WATCH YOUR LANGUAGE!")

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
    client.add_cog(messageManagement(client))

