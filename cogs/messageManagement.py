import discord
from discord.ext import commands
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

    # Returns true if a word in the message matches words in badWords.txt
    # The word[:-1] is to get rid of the \n that comes from readLines() function
    return any(word[:-1] in message for word in badWords)


class messageManagement(commands.Cog):

    def __init__(self, client):
        self.client = client

    """###################################################
    #                      Events                        #
    ###################################################"""

    # Sends the new member a welcome message
    @commands.Cog.listener()
    async def on_member_join(self, member):
        await member.create_dm()
        await member.dm_channel.send(f'HI {member.name} welcome to {member.guild.name}!\nMake sure to go check out rules and roles!\nLastly make sure to have fun!')

    # TODO on_server_join() serverStats?

    # TODO on_server_remove() serverStats?

    # Showing messageManagment is loaded
    @commands.Cog.listener()
    async def on_ready(self):
        print('\t- Loaded messageManagement')

        # TODO This should be an on_server_join or something, won't update when it joins a new server
        servers = self.client.guilds
        serverNames = discord.Guild.name

        for server in servers:
            dataBase = cluster[str(server.id)]
            collection = dataBase["serverInfo"]

            query = {"_id": server.id}
            if collection.count_documents(query) == 0:
                post = {"_id": server.id, "serverName": server.name, "messageRestrictions": False, "reputation": False}
                collection.insert_one(post)

    # Deleting all TEXT messages in a specific channel
    @commands.Cog.listener()
    async def on_message(self, ctx):
        # Does not count bot messages
        if ctx.author.bot:
            return

        # Makes it so you cannot send anything besides pictures to the channel pictures
        if str(ctx.channel) == "pics" and ctx.content != "":
            await ctx.channel.purge(limit=1)

        serverID = ctx.guild.id
        messageContent = ctx.content.split(" ")

        dataBase = cluster[str(serverID)]
        serverInfo = dataBase["serverInfo"]
        userData = dataBase["userData"]

        # Update the number of messages a user has sent in the server
        # TODO ask gregory about upsert (can't find it)
        query = serverInfo.find_one({"_id": serverID})
        if query['messageRestrictions']:
            if badWord(messageContent):

                # Adds one to the number of warnings and numMessages given to a user in the server
                if userData.count_documents({"_id": int(ctx.author.id)}) == 0:
                    badMessages = dict()
                    badMessages[str(ctx.id)] = ctx.content
                    post = {"_id": ctx.author.id, "name": ctx.author.name, "badMessages": badMessages, "warnings": 1, "numMessages": 1}
                    userData.insert_one(post)
                else:
                    # increments the warnings and number of messages the user sent by one
                    userData.update_one({"_id": int(ctx.author.id)}, {"$inc": {"warnings": 1, "numMessages": 1}})
                    # updates the badMessages dictionary in the database
                    userData.update_one({"_id": int(ctx.author.id)}, {"$set": {f'badMessages.{str(ctx.id)}': ctx.content}})

                await ctx.channel.purge(limit=1)

                embed = discord.Embed(
                    title='BAD WORD! WATCH YOUR LANGUAGE!',
                    color=discord.Color.red()
                )
                embed.set_footer(text=f'{ctx.author}')

                # Sends the embed and will delete it after 240 seconds
                await ctx.channel.send(embed=embed, delete_after=240)
            else:
                # increments the numMessages by one, if there are no bad words
                userData.update_one({"_id": int(ctx.author.id)}, {"$inc": {"numMessages": 1}})

    """###################################################
    #                     Commands                       #
    ###################################################"""

    # Saying Hello to anyone who wants to say hi
    @commands.command()
    async def hello(self, ctx):
        await ctx.send('Hello')

    # Deleting a specific NUMBER of messages anywhere
    @commands.command()
    async def delete(self, ctx, arg):
        if ctx.message.author.guild_permissions.administrator:  # Have to be an administrator to run
            if int(arg) > 100:
                await ctx.channel.purge(limit=100)
                await ctx.channel.send('Limit 100 deletions!')
            else:
                await ctx.channel.purge(limit=int(arg)+1)
        else:
            await ctx.channel.send (f'Sorry {ctx.message.author} you do not have permissions!')

    # Turning on/off message restrictions
    @commands.command()
    async def profanityFilter(self, ctx, onOff):
        serverID = ctx.guild.id

        dataBase = cluster[str(serverID)]
        serverInfo = dataBase["serverInfo"]

        if onOff:
            serverInfo.update_one({"_id": serverID}, {"$set": {"messageRestrictions": True}})
        else:
            serverInfo.update_one({"_id": serverID}, {"$set": {"messageRestrictions": False}})

    # Ping command to see if the file is loaded
    @commands.command(hidden=True)
    async def ping5(self, ctx):
        await ctx.channel.send('Pong! MM')


def setup(client):
    client.add_cog(messageManagement(client))

