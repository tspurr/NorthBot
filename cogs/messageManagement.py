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


def badWord(message):
    badWords = None

    with open('badWords.txt') as inFile:
        badWords = inFile.readlines()
    inFile.close()

    # Returns true if a word in the message matches words in badWords.txt
    # The word[:-1] is to get rid of the \n that comes from readLines() function
    return any(word[:-1] in message for word in badWords)


class messageManagement(commands.Cog, name='Message Management'):

    def __init__(self, client):
        self.client = client

    """###################################################
    #                      Events                        #
    ###################################################"""

    # Showing messageManagement is loaded
    @commands.Cog.listener()
    async def on_ready(self):
        print('\t- Loaded messageManagement')

    # Deleting all TEXT messages in a specific channel
    # Checks for bad messages DOES NOT CREATE USER INFO
    @commands.Cog.listener()
    async def on_message(self, ctx):
        # Does not count bot messages
        if ctx.author.bot:
            return

        # Makes it so you cannot send anything besides pictures to the channel pictures
        if str(ctx.channel) == 'pics' and ctx.content != "":
            await ctx.channel.purge(limit=1)

        serverID = ctx.guild.id
        messageContent = ctx.content.split(' ')

        dataBase = cluster[str(serverID)]
        serverInfo = dataBase['serverInfo']
        userData = dataBase['userData']

        # Find if the server has message restrictions on and if they do check the message for bad words and give a warning
        query = serverInfo.find_one({'_id': serverID})
        if query['messageRestrictions']:

            if badWord(messageContent):

                # increments the warnings and number of messages the user sent by one
                userData.update_one({'_id': int(ctx.author.id)}, {'$inc': {'warnings': 1}})
                # updates the badMessages dictionary in the database
                userData.update_one({'_id': int(ctx.author.id)}, {'$set': {f'badMessages.{str(ctx.id)}': ctx.content}})

                await ctx.channel.purge(limit=1)

                embed = discord.Embed(
                    title='Bad Word! Watch Your Language!',
                    color=discord.Color.red()
                )
                embed.set_footer(text=f'{ctx.author}')

                # Sends the embed and will delete it after 240 seconds
                await ctx.channel.send(embed=embed, delete_after=240)

    """###################################################
    #                     Commands                       #
    ###################################################"""

    # Saying Hello to anyone who wants to say hi
    @commands.command()
    async def hello(self, ctx):
        await ctx.send('Hello')

    # Deleting a specific NUMBER of messages anywhere
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def delete(self, ctx, arg):
        if ctx.message.author.guild_permissions.administrator:  # Have to be an administrator to run
            if int(arg) > 100:
                await ctx.channel.purge(limit=100)
                await ctx.channel.send('Limit 100 deletions!')
            else:
                await ctx.channel.purge(limit=int(arg)+1)
        else:
            await ctx.channel.send(f'Sorry {ctx.message.author} you do not have permissions!')

    # Turning on/off message restrictions
    # TODO Make this command administrator only
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def profanityFilter(self, ctx, onOff):
        serverID = ctx.guild.id

        dataBase = cluster[str(serverID)]
        serverInfo = dataBase['serverInfo']

        if onOff:
            serverInfo.update_one({'_id': serverID}, {'$set': {'messageRestrictions': True}})
        else:
            serverInfo.update_one({'_id': serverID}, {'$set': {'messageRestrictions': False}})

    # Ping command to see if the file is loaded
    @commands.command(hidden=True)
    async def ping5(self, ctx):
        await ctx.channel.send('Pong! MM')


def setup(client):
    client.add_cog(messageManagement(client))

