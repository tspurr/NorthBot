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


# Checking if the user's reaction is in the roleMenu
async def menuReaction(userReactionEmoji, menu):
    for emoji in menu:
        if userReactionEmoji == emoji:
            return True
    return False


class roleMenu(commands.Cog, name='Role Menu'):

    def __init__(self, client):
        self.client = client

    """###################################################
    #                      Events                        #
    ###################################################"""

    # Event Showing roleMenu is loaded
    @commands.Cog.listener()
    async def on_ready(self):
        print('\t- Loaded roleMenu')

    # If the user is removing their reaction to the role menu it takes the role associated with the emoji away, if the message is a role menu
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        reaction = payload.emoji
        messageID = payload.message_id
        userID = payload.user_id
        guildID = payload.guild_id
        guild = discord.utils.find(lambda g: g.id == guildID, self.client.guilds)

        # Grabs the roleMenu collection from MongoDB
        db = cluster[str(guildID)]
        menu = db['roleMenus']

        # Checks to see if the collection exists
        if menu.count() != 0:
            query = menu.find_one({'_id': int(messageID)})

            # If the messages being reacted to is a roleMenu
            if menu.count_documents({'_id': int(messageID)}) == 1:

                # Gets the dictionary to define what role name results from the emoji reacted
                reactionRoles = query['reactionRole']

                # Reaction roles returns the name of the role that is supposed to be returned based off the emoji used
                # This function gets the role that is supposed to be used
                role = discord.utils.get(guild.roles, name=reactionRoles[reaction.name])

                if role is not None:
                    # Find the member based off the user ID
                    member = discord.utils.find(lambda m: m.id == userID, guild.members)
                    if member is not None:
                        # Adds the role to the member
                        await member.add_roles(role)
            else:
                return
        else:
            return

    # If the user is removing their reaction to the role menu it takes the role associated with the emoji away, if the message is a role menu
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        reaction = payload.emoji
        messageID = payload.message_id
        userID = payload.user_id
        guildID = payload.guild_id
        guild = discord.utils.find(lambda g: g.id == guildID, self.client.guilds)

        db = cluster[str(guildID)]
        menu = db['roleMenus']

        # Checks to see if the collection exists
        if menu.count() != 0:
            query = menu.find_one({'_id': int(messageID)})

            # If the messages being reacted to is a roleMenu
            if menu.count_documents({'_id': int(messageID)}) == 1:

                # Gets the dictionary to define what role name results from the emoji reacted
                reactionRoles = query['reactionRole']

                # Reaction roles returns the name of the role that is supposed to be returned based off the emoji used
                # This function gets the role that is supposed to be used
                role = discord.utils.get(guild.roles, name=reactionRoles[reaction.name])

                if role is not None:
                    # Find the member based off the user ID
                    member = discord.utils.find(lambda m: m.id == userID, guild.members)
                    if member is not None:
                        # Adds the role to the member
                        await member.remove_roles(role)
            else:
                return
        else:
            return

    """###################################################
    #                     Commands                       #
    ###################################################"""
    # Reaction role menu creation
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def createRM(self, ctx, messageID, roleGroup):
        # Variables
        reactionRole = dict()
        guildID = ctx.message.guild.id
        reactionMenu = await ctx.channel.fetch_message(messageID)  # should get the reaction menu message

        # Database access and pulling
        dataBase = cluster[str(guildID)]
        menus = dataBase['roleMenus']

        # Checks if the role group exists
        if dataBase['roleGroups'].find_one({'_id': roleGroup}, {'_id': 0, 'roleNames': 1}):  # Gets the mongo object
            rolesQuery = dataBase['roleGroups'].find_one({'_id': roleGroup}, {'_id': 0, 'roleNames': 1})
        else:
            await ctx.channel.send(f'No role group {roleGroup} found!')
            return

        roles = rolesQuery['roleNames']  # Get the array of roles from the mongo object

        # Reaction Handling
        if menus.count_documents({'_id': messageID}) == 0:
            # Sends the message to react to
            await ctx.channel.send(f'Add reaction to this message for: ```[{roles[0]}]```')

            # Grabs the messageID of the last message sent by the bot
            reactionMsg = ctx.channel.history(limit=1).messageable.last_message

            userReaction, user = await self.client.wait_for('reaction_add', timeout=60.0)  # Gets the users reaction to the reaction message
            reactionRole[userReaction.emoji] = roles[0]  # Adds the reaction and role to the reactionRole dictionary
            await reactionMenu.add_reaction(userReaction)  # Adds the reaction to the reaction menu
            await reactionMsg.clear_reactions()  # Clear the reactions on the reaction menu for the next role

            # Cycling through all the roles that are in the roleGroup if there is more than one role
            if len(roles) > 1:
                for role in roles[1:]:
                    # Edits the message to change the role that is being edited
                    await reactionMsg.edit(content=f'Add reaction to this message for: ```[{role}]```')

                    userReaction, user = await self.client.wait_for('reaction_add', timeout=60.0)
                    reactionRole[userReaction.emoji] = role  # Adds the reaction and role to the reactionRole dictionary
                    await reactionMenu.add_reaction(userReaction)  # Adds the reaction to the reaction menu
                    await reactionMsg.clear_reactions()  # Clear the reactions on the reaction menu for the next role

            # Adds the role menu to the roleMenus collection in the data base
            post = {'_id': int(messageID), 'cName': ctx.channel.name, 'reactionRole': reactionRole}
            menus.insert_one(post)

        else:
            await ctx.channel.send(f'There is already a role menu on that message! ID: {messageID}')

        # Deletes all roleMenu setup messages
        await ctx.channel.purge(limit=2)
        await ctx.channel.send(content='Role Menu Create!', delete_after=3)  # Tells the user that the menu has been created and then deletes the message

    # Ping command to see if the file is loaded
    @commands.command(hidden=True)
    async def ping3(self, ctx):
        await ctx.channel.send('Pong! RMe')


def setup(client):
    client.add_cog(roleMenu(client))
