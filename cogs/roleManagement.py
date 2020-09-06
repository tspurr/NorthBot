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

    # Turns on and off the default role system
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def defaultRoleOnOff(self, ctx, OnOff):
        guildID = ctx.guild.id
        dataBase = cluster[str(guildID)]
        collection = dataBase['serverInfo']
        # serverInfo = collection.find_one({'_id': guildID})

        if OnOff.lower() == 'on':
            collection.update_one({'_id': guildID}, {'$set': {'defaultRole': True}})
            await ctx.channel.send('Default Role Turned **On**!\nMake sure you set a default role if you have not already with .setDefaultRole')
        elif OnOff.lower() == 'off':
            collection.update_one({'_id': guildID}, {'$set': {'defaultRole': False}})
            await ctx.channel.send('Default Role Turned **Off**!')

    # Set a default role
    # WILL OVERRIDE DEFAULT ROLE ALREADY SET
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setDefaultRole(self, ctx, roleName):
        guildID = ctx.guild.id
        dataBase = cluster[str(guildID)]
        collection = dataBase['serverInfo']

        collection.update_one({'_id': guildID}, {'$set': {'baseRole': roleName}})

    # Create a Role Group
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def createRG(self, ctx, *args):
        guildID = ctx.guild.id
        dataBase = cluster[str(guildID)]
        collection = dataBase['roleGroups']

        if collection.count_documents({'_id': args[0]}) == 0:  # Checks if the server has a group with that name already
            post = {'_id': args[0], 'roleNames': args[1:]}
            collection.insert_one(post)
            await ctx.channel.send(f'Role Group {args[0]} created!')
        else:
            await ctx.channel.send(f'Already a Role Group created called {args[0]}!'
                                   f'\nTry running .deleteRG {args[0]}')

    # Deletes a Role Group
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def deleteRG(self, ctx, roleGroup):
        guildID = ctx.guild.id
        dataBase = cluster[str(guildID)]
        collection = dataBase['roleGroup']

        if collection.count_documents({'_id': roleGroup}) == 1:
            collection.delete_one({'_id': roleGroup})
            await ctx.channel.send(f'Role Group {roleGroup} deleted!')
        else:
            await ctx.channel.send(f'No Role Group named {roleGroup}!')

    # Update role group
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def updateRG(self, ctx, name, edit, *args):
        guildID = ctx.guild.id
        dataBase = cluster[str(guildID)]
        collection = dataBase['roleGroup']
        num = 0

        # If the role group does not exist
        if collection.count_documents({'_id': name}) == 0:
            await ctx.channel.send(f'Role group {name} not found!\nMake sure you type the name correctly')

        roleGroup = collection.find_one({'_id': name})
        array = roleGroup['roleNames']

        # If the user wants to remove roles
        if edit.lower() == 'r':

            # Loop through the amount of roles to be removed from the group
            for x in args:

                # If the role is in the array remove it
                if x in array:
                    array.pop(x)
                    num += 1

                # If the role is not in the array we skip it
                else:
                    await ctx.channel.send(f'{x} is not in the role group! Skipping')
                    continue

            # Updating the document to reflect the new array
            collection.update_one({'_id': name}, {'$set': {'roleNames': array}})
            await ctx.channel.send(f'Removed {num} roles')

        # If the user wants to insert roles
        elif edit.lower() == "i":

            # Inserting the role into the role group
            for role in args:

                # If the role is already in the group we skip adding it
                if role in array:
                    await ctx.channel.send(f'{role} is already in the group! Skipping')
                    continue

                # Adding the role to the array
                array.append(role)
                num += 1

            # Should update the array in the document to
            collection.update_one({'_id': name}, {'$set': {'roleNames': array}})
            await ctx.channel.send(f'Inserted {num} roles')
        else:
            await ctx.channel.send('Invalid Use of Command!\nMake sure indicator is \"I\" (insert) or \"R\" (remove).')

    # Ping command to see if the file is loaded
    @commands.command(hidden=True)
    async def ping4(self, ctx):
        await ctx.channel.send('Pong! RMe')


def setup(client):
    client.add_cog(roleManagement(client))