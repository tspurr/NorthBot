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


class roleManagement(commands.Cog, name='Role Management'):

    def __init__(self, client):
        self.client = client

    """###################################################
    #                      Events                        #
    ###################################################"""

    # Event Showing roleManagement is loaded
    @commands.Cog.listener()
    async def on_ready(self):
        print('\t- Loaded roleManagement')

    """###################################################
    #                     Commands                       #
    ###################################################"""

    #  Create a Role Group
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def createRG(self, ctx, *args):
        guildID = ctx.guild.id
        dataBase = cluster[str(guildID)]
        collection = dataBase['roleGroups']

        myquery = {'_id': args[0]}

        if collection.count_documents(myquery) == 0:  # Checks if the server has a group with that name already
            post = {'_id': args[0], 'roleNames': args[1:]}
            collection.insert_one(post)
            await ctx.channel.send(f'Role Group {args[0]} created!')
        else:
            await ctx.channel.send(f'Already a Role Group created called {args[0]}!'
                                   f'\nTry running .deleteRG {args[0]}')

    # Deletes a Role Group
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def deleteRG(self, ctx, *args):
        guildID = ctx.guild.id
        dataBase = cluster[str(guildID)]
        collection = dataBase['roleGroup']

        myquery = {'_id': args[0]}

        if collection.count_documents(myquery) == 1:
            collection.delete_one(myquery)
            await ctx.channel.send(f'Role Group {args[0]} deleted!')
        else:
            await ctx.channel.send(f'No Role Group named {args[0]}!')


    # TODO insertOneRG (insert a role into a role group)

    # TODO deleteOneRG (delete a role from a role group)

    # Ping command to see if the file is loaded
    @commands.command(hidden=True)
    async def ping4(self, ctx):
        await ctx.channel.send('Pong! RMe')


def setup(client):
    client.add_cog(roleManagement(client))