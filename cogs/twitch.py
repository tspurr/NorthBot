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


class twitch(commands.Cog, name='Twitch/YouTube'):

    def __init__(self, client):
        self.client = client

    """###################################################
    #                      Events                        #
    ###################################################"""

    # Event Showing serverStatistics is loaded
    @commands.Cog.listener()
    async def on_ready(self):
        print('\t- Loaded twitch')

    # Checks for people in a discord server who went live and makes a notification about it
    @commands.Cog.listener()
    async def my_background_task(self):
        # Variables
        twitchColor = discord.Color(value=int('6441A5', 16))
        youtubeColor = discord.Color(value=int('FF0000', 16))
        guilds = self.client.guilds

        # Returns what color the embed should be based on the platform
        def embedColor(website):
            if website == 'Twitch':
                return twitchColor
            elif website == 'YouTube':
                return youtubeColor

        # Loop through all the guilds the bot is apart of
        for guild in guilds:
            members = guild.members

            serverID = guild.id
            dataBase = cluster[str(serverID)]

            # Grabs the server info document all in one step instead of spreading it out
            serverInfo = dataBase['serverInfo'].find_one({'_id': serverID})

            # If the server has announcements turned on
            if serverInfo['announceStreams']:

                # Loop through all the members in a server
                for member in members:

                    # Getting the activity type of the member in the server
                    activity = member.Activity()

                    # If they are streaming
                    if activity.type == 'Streaming':

                        # If there is no stream announcement channel set
                        if serverInfo['streamChannel'] == '':

                            if serverInfo['modChat'] != '':
                                modChannel = self.client.get_channel(serverInfo['modChat'])
                                await modChannel.send('There is no announcement channel set, please set one using .setStreamChannel')
                            else:
                                return

                        # The streaming function in discord.py
                        memberStream = member.Streaming()
                        platform = memberStream.platform
                        streamName = memberStream.name
                        streamGame = memberStream.game
                        streamURL = memberStream.URL

                        announcementChannel = self.client.get_channel(serverInfo['streamChannel'])
                        embed = discord.Embed(
                            color=embedColor(platform)  # Should return what color to use for the embed
                        )

                        # Setting the member info into the embed
                        embed.set_image(url=streamURL)
                        embed.set_author(name=member.name, icon_url=member.avatar_url)
                        embed.add_field(name=streamName, value=streamURL, inline=False)
                        embed.add_field(name='Game', value=streamGame, inline=True)
                        embed.add_field(name='Viewers', value='7', inline=True)

                        # Send the message to the announcement channel
                        await announcementChannel.send(embed=embed)

    """###################################################
    #                     Commands                       #
    ###################################################"""

    @commands.command(hidden=True)
    async def testEmbed(self, ctx):
        embed = discord.Embed(
            title='title',
            description='This is a description',
            color=discord.Color(value=int('FFCB05', 16)),
        )

        embed.set_footer(text='fooooter')
        embed.set_image(url='https://media.discordapp.net/attachments/630891280670654517/742556048153509898/UofMOverwatchLogo16.png?width=611&height=611')
        embed.set_author(name='Author Name', icon_url='https://media.discordapp.net/attachments/630891280670654517/742556048153509898/UofMOverwatchLogo16.png?width=611&height=611')
        embed.add_field(name='Field Name', value='Description', inline=False)
        embed.add_field(name='Field Name', value='Description', inline=True)
        embed.add_field(name='Field Name', value='Description', inline=True)
        embed.add_field(name='Field Name', value='Description', inline=True)
        embed.add_field(name='Field Name', value='Description', inline=True)
        embed.add_field(name='Field Name', value='Description', inline=True)
        embed.add_field(name='Field Name', value='Description', inline=True)

        await ctx.send(embed=embed)

    # Rep on/off
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def streamAnnounceOnOff(self, ctx, onOff):
        dataBase = cluster[str(ctx.guild.id)]
        serverInfo = dataBase['serverInfo']

        if onOff.lower() == 'on':
            serverInfo.update_one({'_id': ctx.guild.id}, {'$set': {'announceStreams': True}})
            await ctx.channel.send('Stream Announcements Turned **On**!')

            # If there is no channel set remind them to set one
            if serverInfo['streamChannel'] == int():
                await ctx.channel.send('Make sure to assign a channel to announce streams!\n.setStreamChannel [ID]')

        elif onOff.lower == 'off':
            serverInfo.update_one({'_id': ctx.guild.id}, {'$set': {'announceStreams': False}})
            await ctx.channel.send('Stream Announcements Turned **Off**!')

        else:
            await ctx.channel.send('Invalid use of command, use .help if you need to know more')

    # Updates the channel that streams are to be announced in
    @commands.command()
    async def setStreamChannel(self, ctx, channelID):
        serverID = ctx.guild.id
        dataBase = cluster[str(serverID)]
        serverInfo = dataBase['serverInfo']

        serverInfo.update_one({'_id': serverID}, {'$set': {'streamChannel': channelID}})

    # Ping command to see if the file is loaded
    @commands.command(hidden=True)
    async def ping1(self, ctx):
        await ctx.channel.send('Pong! EM')


def setup(client):
    client.add_cog(twitch(client))
