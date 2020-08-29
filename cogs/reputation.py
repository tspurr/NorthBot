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


class reputation(commands.Cog, name='Reputation'):

    def __init__(self, client):
        self.client = client

    """###################################################
    #                      Events                        #
    ###################################################"""

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'\t- Loaded Reputation')

    # Sends the new member a message about joining the server
    @commands.Cog.listener()
    async def on_member_join(self, member):
        await member.create_dm()
        await member.dm_channel.send(f'HI {member.name} welcome to {member.guild.name}!\nMake sure to go check out rules and roles!\nLastly make sure to have fun!')

        dataBase = cluster[member.guild.id]
        userData = dataBase['userData']

        # Creates a default user for a member in the data base
        badMessages = dict()
        newUser = {'_id': member.id, 'name': member.name, 'badMessages': badMessages, 'warnings': 0, 'numMessages': 0}
        userData.insert_one(newUser)

    # Sends the leaving member a message about leaving the server
    @commands.Cog.listener()
    async def on_member_leave(self, member):
        await member.create_dm()
        await member.dm_channel.send(f'Sorry to see you leave {member.guild.name}!')

        dataBase = cluster[member.guild.id]
        userData = dataBase['userData']

        # Find the user and delete all the information about them (may not keep this)
        # userData.find_one_and_delete({"_id": member.id})
        query = {'_id': member.id}
        if userData.count_documents(query) == 1:
            userData.delete_one(query)

    # Go through and create files for every member on a server to insert into the data base
    @commands.Cog.listener()
    async def on_server_join(self, server):
        serverID = server.id

        dataBase = cluster[serverID]
        userData = dataBase['userInfo']

        # Going through all the members in a server when the bot is added
        for member in server.members:
            badMessages = dict()
            newUser = {'_id': member.id, 'name': member.name, 'badMessages': badMessages, 'warnings': 0, 'numMessages': 0}
            userData.insert_one(newUser)


    @commands.Cog.listener()
    async def on_message(self, ctx):
        # Don't count bot messages in server statistics
        if ctx.author.bot:
            return

        serverID = ctx.guild.id

        dataBase = cluster[str(serverID)]
        userData = dataBase['userData']

        # Update the number of messages by one when the user talks
        userData.update_one({'_id': ctx.author.id}, {'$inc': {'numMessages': 1}})



    """###################################################
    #                     Commands                       #
    ###################################################"""

    # TODO Rep on/off

    # TODO Gambling

    # TODO Rep remove

    # TODO Rep give

    # TODO Extra points

    # Refreshes the user list incase the data was deleted in the database
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def refreshUsers(self, ctx):
        serverID = ctx.guild.id
        members = ctx.guild.members

        dataBase = cluster[serverID]
        userData = dataBase['userInfo']

        # Going through all the members in a server when the bot is added
        for member in members:
            badMessages = dict()
            newUser = {'_id': member.id, 'name': member.name, 'badMessages': badMessages, 'warnings': 0,
                       'numMessages': 0}
            userData.insert_one(newUser)

    @commands.command(hidden=True)
    async def ping6(self, ctx):
        await ctx.channel.send('Pong! Rep')


def setup(client):
    client.add_cog(reputation(client))
