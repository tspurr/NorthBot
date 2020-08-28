import discord
from discord.ext import commands
from pymongo import MongoClient

# Getting the NorthBot mongoDB connection URL
file = open('mongoURL.txt')
connectionURL = file.read()
file.close()

# MongoDB initialization
cluster = MongoClient(connectionURL)

# Embed Color
embedColor = discord.Color.green()


class serverStatistics(commands.Cog, name='Server Statistics'):

    def __init__(self, client):
        self.client = client

    """###################################################
    #                      Events                        #
    ###################################################"""

    # Event Showing serverStatistics is loaded
    @commands.Cog.listener()
    async def on_ready(self):
        print('\t- Loaded serverStatistics')

    # Creates the dataBase for when the bot joins a discord server
    @commands.Cog.listener()
    async def on_server_join(self, server):

        serverID = server.id
        serverName = server.Name
        numMembers = 0

        # Counting the number of members in a server
        # Might be a server.member.size or something
        # TODO look into if members is a list then you can use len(server.members)
        for members in server.members:
            numMembers += 1

        print(f'Joined {serverName}!')

        dataBase = cluster[serverID]
        collection = dataBase['serverInfo']

        # Creates default information for a server on join
        post = {'_id': server.id, 'serverName': server.name, 'numMembers': numMembers, 'streamChannel': '', 'modChat': '',
                'messageRestrictions': False, 'reputation': False, 'announceStreams': False}
        collection.insert_one(post)

    # Deletes the data base for the server?!?
    @commands.Cog.listener()
    async def on_server_leave(self, server):
        serverID = server.id
        serverName = server.Name

        print(f'Left {serverName}!')

        # This should delete the server data
        cluster.drop_database(serverID)

    # Add one to numMembers on server
    @commands.Cog.listener()
    async def on_member_join(self, member):
        serverID = member.guild.id
        dataBase = cluster[serverID]
        collection = dataBase['serverInfo']

        collection.update_one({'_id': serverID}, {'$inc': {'numMembers': 1}})

    # Subtract one on member leave
    @commands.Cog.listener()
    async def on_member_leave(self, member):
        serverID = member.guild.id
        dataBase = cluster[serverID]
        collection = dataBase['serverInfo']

        collection.update_one({'_id': serverID}, {'$inc': {'numMembers': -1}})

    # Keeps track of all the messages sent in servers and adds them to a mongoDB
    # DOES NOT TRACK USER MESSAGES THAT THEY SEND
    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author.bot:
            return

        dataBase = cluster[str(ctx.guild.id)]
        channelData = dataBase['channelData']

        print(f'{ctx.channel}: {ctx.author}: {ctx.author.name}: {ctx.content}')

        myquery = {'_id': ctx.channel.id}
        if channelData.count_documents(myquery) == 0:
            post = {'_id': ctx.channel.id, 'cName': ctx.channel.name, 'numMessages': 1}
            channelData.insert_one(post)
        else:
            channelData.update_one({'_id': ctx.channel.id}, {'$inc': {'numMessages': 1}})

    """###################################################
    #                     Commands                       #
    ###################################################"""

    # TODO Gets the most talked in channel

    # TODO Gets the least talked in channel

    # TODO Gets general server statistics (responds in embed)

    @commands.command(hidden=True)
    async def serverRefresh(self, ctx):
        serverID = ctx.guild.id
        serverName = ctx.guild.name
        members = ctx.guild.members  # This probably doesn't work
        numMembers = 0
        dataBase = cluster[str(serverID)]
        collection = dataBase['serverInfo']
        query = {'_id': serverID}

        for member in members:
            numMembers += 1

        # If the server document is not found in the collection then we insert a new one
        if collection.count_documents(query) == 0:
            post = {'_id': serverID, 'serverName': serverName, 'numMembers': numMembers, 'streamChannel': '', 'modChat': '',
                    'messageRestrictions': False, 'reputation': False, 'announceStreams': False}
            collection.insert_one(post)

            await ctx.channel.send('Server info refreshed')
        else:
            return

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
