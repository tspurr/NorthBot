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


class guildStatistics(commands.Cog, name='Server Statistics'):

    def __init__(self, client):
        self.client = client

    """###################################################
    #                      Events                        #
    ###################################################"""

    # Event Showing guildStatistics is loaded
    @commands.Cog.listener()
    async def on_ready(self):
        print('\t- Loaded guildStatistics')

    # Creates the dataBase for when the bot joins a discord guild
    @commands.Cog.listener()
    async def on_guild_join(self, guild):

        guildID = guild.id
        members = guild.members
        guildName = guild.Name
        guildOwner = guild.owner

        print(f'Joined {guildName}!')

        dataBase = cluster[guildID]
        guildInfo = dataBase['guildInfo']
        channelData = dataBase['channelData']

        # Creates default information for a guild on join
        post = {'_id': guildID, 'guildName': guildName,
                'numMembers': len(members), 'streamChannel': int(), 'modChat': int(), 'baseRole': str(),
                'messageRestrictions': False, 'reputation': False, 'announceStreams': False, 'defaultRole': False}
        guildInfo.insert_one(post)

        # Goes through and checks/adds the channelData documents for every channel
        for channel in guild.channels:
            if channelData.count_documents({'_id': channel.id}) == 0:
                post = {'_id': channel.id, 'cName': channel.name, 'numMessages': 0}
                channelData.insert_one(post)

        await guildOwner.create_dm()
        await guildOwner.dm_channel.send(
            f'Hi {guildOwner.mention} thank you for adding me to your guild!'
            f'\nMake sure to do a few things first:'
            f'\n - .setModChat'
            f'\n - .profanityFilterOnOff [On/Off]'
            f'\n - .repOnOff [On/Off]'
            f'\n - .streamAnnounceOnOff [On/Off]'
            f'\n - ')

    # Deletes the data base for the guild?!?
    @commands.Cog.listener()
    async def on_guild_leave(self, guild):
        guildID = guild.id
        guildName = guild.Name

        print(f'Left {guildName}!')

        # This should delete the guild data
        cluster.drop_database(guildID)

    # If a guild updates any relevant information
    @commands.Cog.listener()
    async def on_guild_update(self, guild):
        guildID = guild.id
        guildName = guild.Name

        dataBase = cluster[str(guildID)]
        guildInfo = dataBase['guildInfo']
        guildData = guildInfo.find_one({'_id': guildID})

        if guildName != guildData['guildName']:
            guildInfo.update_one({'_id': guildID}, {'$set': {'guildName': guildName}})

    # Add one to numMembers on guild
    @commands.Cog.listener()
    async def on_member_join(self, member):
        guildID = member.guild.id
        dataBase = cluster[guildID]
        guildInfo = dataBase['guildInfo']
        modChannel = self.client.get_channel(guildInfo['modChat'])

        guildInfo.update_one({'_id': guildID}, {'$inc': {'numMembers': 1}})

        await modChannel.send(f'{member.mention} has joined the guild!')

    # Subtract one on member leave
    @commands.Cog.listener()
    async def on_member_leave(self, member):
        guildID = member.guild.id
        dataBase = cluster[guildID]
        guildInfo = dataBase['guildInfo']
        modChannel = self.client.get_channel(guildInfo['modChat'])

        guildInfo.update_one({'_id': guildID}, {'$inc': {'numMembers': -1}})

        await modChannel.send(f'{member} has left the guild... :(')

    # Keeps track of all the messages sent in guilds and adds them to a mongoDB
    # DOES NOT TRACK USER MESSAGES THAT THEY SEND
    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author.bot:
            return

        dataBase = cluster[str(ctx.guild.id)]
        channelData = dataBase['channelData']

        print(f'{ctx.channel}: {ctx.author}: {ctx.author.name}: {ctx.content}')

        channelData.update_one({'_id': ctx.channel.id}, {'$inc': {'numMessages': 1}})

    # When a channel is created in the guild
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        channelID = channel.id
        channelName = channel.name

        dataBase = cluster[str(channelID)]
        channelData = dataBase['channelData']

        channelData.insert_one({'_id': channelID, 'cName': channelName, 'numMessages': 0})

    # When a channel is deleted from the guild
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

    # TODO Gets general guild statistics (responds in embed)
    @commands.command()
    async def guildStats(self, ctx):
        guildID = ctx.guild.id
        guildName = ctx.guild.id

        dataBase = cluster[str(guildID)]
        channelData = dataBase['channelData']
        memberData = dataBase['memberData']

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        guildID = ctx.guild.id
        guildName = ctx.guild.name

        await member.create_dm()
        await member.dm_channel.send(f'You have been banned from {guildName} for reason: {reason}')
        await member.ban(reason=reason)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        guildID = ctx.guild.id
        guildName = ctx.guild.name

        await member.create_dm()
        await member.dm_channel.send(f'You have been kicked from {guildName} for reason: {reason}')
        await member.kick(reason=reason)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def guildRefresh(self, ctx):
        guildID = ctx.guild.id
        guildName = ctx.guild.name
        members = ctx.guild.members  # This probably doesn't work
        channels = ctx.guild.channels
        dataBase = cluster[str(guildID)]
        guildInfo = dataBase['guildInfo']
        channelData = dataBase['channelData']
        query = {'_id': guildID}

        # If the guild document is not found in the collection then we insert a new one
        if guildInfo.count_documents(query) == 0:
            post = {'_id': guildID, 'guildName': guildName,
                    'numMembers': len(members), 'streamChannel': int(), 'modChat': int(), 'baseRole': str(),
                    'messageRestrictions': False, 'reputation': False, 'announceStreams': False, 'defaultRole': False}
            guildInfo.insert_one(post)

            await ctx.channel.send('Server info refreshed')
        else:
            return

        # Gets all the channel data put back in if some was deleted
        for channel in channels:
            if channelData.count_documents({'_id': channel.id}) == 0:
                post = {'_id': ctx.channel.id, 'cName': ctx.channel.name, 'numMessages': 0}
                channelData.insert_one(post)

    # Setting the modChat channel
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setModChat(self, ctx, channel):
        channelID = channel.id
        guildID = ctx.guild.id

        dataBase = cluster[str(guildID)]
        guildInfo = dataBase['guildInfo']

        guildInfo.update_one({'id': guildID}, {'$set': {'modChat': channelID}})

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
        embed.set_footer(text=f'guildStatistics.py online')
        await ctx.channel.send(embed=embed)


def setup(client):
    client.add_cog(guildStatistics(client))
