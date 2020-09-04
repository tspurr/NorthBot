"""
The MIT License (MIT)

Copyright (c) 2020 Tyler Spurr

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

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
    async def on_guild_join(self, guild):

        serverID = guild.id
        serverName = guild.Name

        print(f'Joined {serverName}!')

        dataBase = cluster[serverID]
        serverInfo = dataBase['serverInfo']
        channelData = dataBase['channelData']

        # Creates default information for a server on join
        post = {'_id': serverID, 'serverName': serverName, 'numMembers': len(guild.members), 'streamChannel': '', 'modChat': '',
                'messageRestrictions': False, 'reputation': False, 'announceStreams': False}
        serverInfo.insert_one(post)

        # Goes through and checks/adds the channelData documents for every channel
        for channel in guild.channels:
            if channelData.count_documents({'_id': channel.id}) == 0:
                post = {'_id': channel.id, 'cName': channel.name, 'numMessages': 0}
                channelData.insert_one(post)

    # Deletes the data base for the server?!?
    @commands.Cog.listener()
    async def on_guild_leave(self, guild):
        serverID = guild.id
        serverName = guild.Name

        print(f'Left {serverName}!')

        # This should delete the server data
        cluster.drop_database(serverID)

    # If a server updates any relevant information
    @commands.Cog.listener()
    async def on_guild_update(self, guild):
        serverID = guild.id
        serverName = guild.Name

        dataBase = cluster[str(serverID)]
        serverInfo = dataBase['serverInfo']
        serverData = serverInfo.find_one({'_id': serverID})

        if serverName != serverData['serverName']:
            serverInfo.update_one({'_id': serverID}, {'$set': {'serverName': serverName}})

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

        channelData.update_one({'_id': ctx.channel.id}, {'$inc': {'numMessages': 1}})

    # When a channel is created in the server
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        channelID = channel.id
        channelName = channel.name

        dataBase = cluster[str(channelID)]
        channelData = dataBase['channelData']

        channelData.insert_one({'_id': channelID, 'cName': channelName, 'numMessages': 0})

    # When a channel is deleted from the server
    @commands.Cog.listener()
    async def on_guild_channel_remove(self, channel):
        channelID = channel.id
        channelName = channel.name

        dataBase = cluster[str(channelID)]
        channelData = dataBase['channelData']

        channelData.delete_one({'_id': channelID, 'cName': channelName, 'numMessages': 0})

    # If there was any relevant information changed on the channel
    @commands.Cog.listener()
    async def on_guild_channel_update(self, channel):
        channelID = channel.id
        channelName = channel.name

        dataBase = cluster[str(channelID)]
        channelData = dataBase['channelData']

        update = channelData.find_one({'_id': channelID})

        # If the channel name was changed
        if update['cName'] != channelName:
            channelData.update_one({'_id': channelID}, {'$set': {'cName': channelName}})

    """###################################################
    #                     Commands                       #
    ###################################################"""

    # TODO Gets the most talked in channel

    # TODO Gets the least talked in channel

    # TODO Gets general server statistics (responds in embed)
    @commands.command()
    async def serverStats(self, ctx):
        serverID = ctx.guild.id
        serverName = ctx.guild.id

        dataBase = cluster[str(serverID)]
        channelData = dataBase['channelData']
        userData = dataBase['userData']

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        serverID = ctx.guild.id
        serverName = ctx.guild.name

        await member.create_dm()
        await member.dm_channel.send(f'You have been banned from {serverName} for reason: {reason}')
        await member.ban(reason=reason)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        serverID = ctx.guild.id
        serverName = ctx.guild.name

        await member.create_dm()
        await member.dm_channel.send(f'You have been kicked from {serverName} for reason: {reason}')
        await member.kick(reason=reason)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def serverRefresh(self, ctx):
        serverID = ctx.guild.id
        serverName = ctx.guild.name
        members = ctx.guild.members  # This probably doesn't work
        channels = ctx.guild.channels
        dataBase = cluster[str(serverID)]
        serverInfo = dataBase['serverInfo']
        channelData = dataBase['channelData']
        query = {'_id': serverID}

        # If the server document is not found in the collection then we insert a new one
        if serverInfo.count_documents(query) == 0:
            post = {'_id': serverID, 'serverName': serverName, 'numMembers': len(members), 'streamChannel': int(), 'modChat': int(),
                    'messageRestrictions': False, 'reputation': False, 'announceStreams': False}
            serverInfo.insert_one(post)

            await ctx.channel.send('Server info refreshed')
        else:
            return

        # Gets all the channel data put back in if some was deleted
        for channel in channels:
            if channelData.count_documents({'_id': channel.id}) == 0:
                post = {'_id': ctx.channel.id, 'cName': ctx.channel.name, 'numMessages': 0}
                channelData.insert_one(post)

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
