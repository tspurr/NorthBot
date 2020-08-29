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
import random

# Getting the NorthBot mongoDB connection URL
file = open('mongoURL.txt')
connectionURL = file.read()
file.close()

# MongoDB initialization
cluster = MongoClient(connectionURL)


# If someone uses a good word in their message
def extra(content):
    goodWords = {'thanks', 'thank', 'phara-nough', 'ana-ostly', 'welcome', ''}

    return any(word in content for word in goodWords)


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
        newUser = {'_id': member.id, 'name': member.name, 'badMessages': badMessages, 'warnings': 0, 'numMessages': 0, 'reputation': 0}
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
        userData = dataBase['userData']

        # Going through all the members in a server when the bot is added
        for member in server.members:
            badMessages = dict()
            newUser = {'_id': member.id, 'name': member.name, 'badMessages': badMessages, 'warnings': 0, 'numMessages': 0, 'reputation': 0}
            userData.insert_one(newUser)


    @commands.Cog.listener()
    async def on_message(self, ctx):
        # Don't count bot messages in server statistics
        if ctx.author.bot:
            return

        serverID = ctx.guild.id
        dataBase = cluster[str(serverID)]
        userData = dataBase['userData']
        messageContent = ctx.content.split(' ')

        # Update the number of messages by one when the user talks
        userData.update_one({'_id': ctx.author.id}, {'$inc': {'numMessages': 1}})
        userData.update_one({'_id': ctx.author.id}, {'$inc': {'reputation': 1}})

        # If someone says something good/extra they'll get extra reputation
        if extra(messageContent):
            userData.update_one({'_id': ctx.author.id}, {'$inc': {'reputation': random.randint(0, 20)}})



    """###################################################
    #                     Commands                       #
    ###################################################"""

    # Rep on/off
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def repOnOff(self, ctx, onOff):
        dataBase = cluster[str(ctx.guild.id)]
        serverInfo = dataBase['serverInfo']

        if onOff.lower() == 'on':
            serverInfo.update_one({'_id': ctx.guild.id}, {'$set': {'reputation': True}})
        elif onOff.lower == 'off':
            serverInfo.update_one({'_id': ctx.guild.id}, {'$set': {'reputation': False}})
        else:
            await ctx.channel.send('Invalid use of command, use .help if you need to know more')

    # Gambling points
    @commands.command()
    async def gamble(self, ctx, amount):
        randomNum = random.randint(0, amount)
        addSub = random.randint(1, 2)
        dataBase = cluster[str(ctx.guild.id)]
        userID = ctx.author.id
        userData = dataBase['userData']

        # Add the number
        if addSub == 1:
            userData.find_one({'_id': userID}, {'$inc': {reputation: randomNum}})
            await ctx.channel.send(f'{ctx.author} has gotten {randomNum} added!')

        # Subtract the number
        elif addSub == 2:
            userData.find_one({'_id': userID}, {'$inc': {reputation: -randomNum}})
            await ctx.channel.send(f'{ctx.author} has gotten {randomNum} subtracted!')

        else:
            await ctx.channel.send('Oops something went wrong, please submit an error report')

    # Rep remove
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def repRemove(self, ctx, member, amount):
        dataBase = cluster[str(ctx.guild.id)]
        userData = dataBase['userData']
        memberData = userData.find_one({'_id': member.id})

        if memberData['reputation'] == 0:
            await ctx.channel.send(f'{member} has no reputation to remove :(')
        elif amount > memberData['reputation']:
            userData.update_one({'_id': member.id}, {'$set': {'reputation': 0}})
        else:
            userData.update_one({'_id': member.id}, {'$inc': {'reputation': -amount}})

    # Rep give
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def repGive(self, ctx, member, amount):
        dataBase = cluster[str(ctx.guild.id)]
        userData = dataBase['userData']

        userData.update_one({'_id': member.id}, {'$inc': {'reputation': amount}})

    # Refreshes the user list in case the data was deleted in the database
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def refreshUsers(self, ctx):
        serverID = ctx.guild.id
        members = ctx.guild.members

        dataBase = cluster[str(serverID)]
        userData = dataBase['userData']

        # Going through all the members in a server when the bot is added
        for member in members:
            # If the member is a bot ignore the member
            if member.bot:
                continue

            badMessages = dict()
            newUser = {'_id': member.id, 'name': member.name, 'badMessages': badMessages, 'warnings': 0,
                       'numMessages': 0, 'reputation': 0}
            userData.insert_one(newUser)

        await ctx.channel.send('User refresh done!')

    @commands.command(hidden=True)
    async def ping6(self, ctx):
        await ctx.channel.send('Pong! Rep')


def setup(client):
    client.add_cog(reputation(client))
