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

    # Sends the new member a message about joining the guild
    @commands.Cog.listener()
    async def on_member_join(self, member):
        await member.create_dm()
        await member.dm_channel.send(f'HI {member.name} welcome to {member.guild.name}!\nMake sure to go check out rules and roles!\nLastly make sure to have fun!')

        guildID = member.guild.id

        dataBase = cluster[str(guildID)]
        memberData = dataBase['memberData']

        # Creates a default member for a member in the data base
        badMessages = dict()
        newUser = {'_id': member.id, 'name': member.name, 'badMessages': badMessages, 'warnings': 0, 'numMessages': 0, 'reputation': 0}
        memberData.insert_one(newUser)

    # Sends the leaving member a message about leaving the guild
    @commands.Cog.listener()
    async def on_member_leave(self, member):
        await member.create_dm()
        await member.dm_channel.send(f'Sorry to see you leave {member.guild.name}!')

        guildID = member.guild.id

        dataBase = cluster[str(guildID)]
        memberData = dataBase['memberData']

        # Find the member and delete all the information about them (may not keep this)
        # memberData.find_one_and_delete({"_id": member.id})
        query = {'_id': member.id}
        if memberData.count_documents(query) == 1:
            memberData.delete_one(query)

    # If a member updates any relevant information\
    @commands.Cog.listener()
    async def on_member_update(self, member):
        guildID = member.guild.id
        memberID = member.id
        memberName = member.name

        dataBase = cluster[str(guildID)]
        memberData = dataBase['memberData']

        update = memberData.find_one({'_id': memberID})

        # If the names are different update the one in the database
        if update['name'] != memberName:
            memberData.update_one({'_id': memberID}, {'$set': {'name': memberName}})

    # Go through and create files for every member on a guild to insert into the data base
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        guildID = guild.id

        dataBase = cluster[guildID]
        memberData = dataBase['memberData']

        # Going through all the members in a guild when the bot is added
        for member in guild.members:
            badMessages = dict()
            newUser = {'_id': member.id, 'name': member.name, 'badMessages': badMessages, 'warnings': 0, 'numMessages': 0, 'reputation': 0}
            memberData.insert_one(newUser)


    @commands.Cog.listener()
    async def on_message(self, ctx):
        # Don't count bot messages in guild statistics
        if ctx.author.bot:
            return

        guildID = ctx.guild.id
        dataBase = cluster[str(guildID)]
        memberData = dataBase['memberData']
        messageContent = ctx.content.split(' ')

        # Update the number of messages by one when the member talks
        memberData.update_one({'_id': ctx.author.id}, {'$inc': {'numMessages': 1}})
        memberData.update_one({'_id': ctx.author.id}, {'$inc': {'reputation': 1}})

        # If someone says something good/extra they'll get extra reputation
        if extra(messageContent):
            memberData.update_one({'_id': ctx.author.id}, {'$inc': {'reputation': random.randint(0, 20)}})



    """###################################################
    #                     Commands                       #
    ###################################################"""

    # Rep on/off
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def repOnOff(self, ctx, onOff):
        dataBase = cluster[str(ctx.guild.id)]
        guildInfo = dataBase['guildInfo']

        if onOff.lower() == 'on':
            guildInfo.update_one({'_id': ctx.guild.id}, {'$set': {'reputation': True}})
            await ctx.channel.send('Reputation Turned **On**!')

        elif onOff.lower == 'off':
            guildInfo.update_one({'_id': ctx.guild.id}, {'$set': {'reputation': False}})
            await ctx.channel.send('Reputation Turned **Off**!')

        else:
            await ctx.channel.send('Invalid use of command, use .help if you need to know more')

    # Gambling points
    @commands.command()
    async def gamble(self, ctx, amount):
        addSub = random.randint(1, 2)
        dataBase = cluster[str(ctx.guild.id)]
        memberID = ctx.author.id
        memberData = dataBase['memberData']

        member = memberData.find_one({'_id': memberID})
        rep = member['reputation']

        # If the member does not have the amount that they want to gamble away return
        if rep < amount:
            await ctx.channel.send(f'You cannot gamble {amount} points, you only have {rep}!\nTry again!')
            return

        randomNum = random.randint(0, amount)

        # Add the number
        if addSub == 1:
            memberData.update_one({'_id': memberID}, {'$inc': {reputation: randomNum}})
            await ctx.channel.send(f'{ctx.author} has gotten {randomNum} added!')

        # Subtract the number
        elif addSub == 2:
            memberData.update_one({'_id': memberID}, {'$inc': {reputation: -randomNum}})
            await ctx.channel.send(f'{ctx.author} has gotten {randomNum} subtracted!')

        else:
            await ctx.channel.send('Oops something went wrong, please submit an error report')

    # Rep remove
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def repRemove(self, ctx, member, amount):
        dataBase = cluster[str(ctx.guild.id)]
        memberData = dataBase['memberData']
        memberData = memberData.find_one({'_id': member.id})

        if memberData['reputation'] == 0:
            await ctx.channel.send(f'{member} has no reputation to remove :(')
        elif amount > memberData['reputation']:
            memberData.update_one({'_id': member.id}, {'$set': {'reputation': 0}})
        else:
            memberData.update_one({'_id': member.id}, {'$inc': {'reputation': -amount}})

    # Rep give
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def repGive(self, ctx, member, amount):
        dataBase = cluster[str(ctx.guild.id)]
        memberData = dataBase['memberData']

        memberData.update_one({'_id': member.id}, {'$inc': {'reputation': amount}})

    # Refreshes the member list in case the data was deleted in the database
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def refreshUsers(self, ctx):
        guildID = ctx.guild.id
        members = ctx.guild.members

        dataBase = cluster[str(guildID)]
        memberData = dataBase['memberData']

        # Going through all the members in a guild when the bot is added
        for member in members:
            # If the member is a bot ignore the member
            if member.bot:
                continue

            badMessages = dict()
            newUser = {'_id': member.id, 'name': member.name, 'badMessages': badMessages, 'warnings': 0,
                       'numMessages': 0, 'reputation': 0}
            memberData.insert_one(newUser)

        await ctx.channel.send('User refresh done!')

    @commands.command(hidden=True)
    async def ping6(self, ctx):
        await ctx.channel.send('Pong! Rep')


def setup(client):
    client.add_cog(reputation(client))
