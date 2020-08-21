import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient

# Getting the NorthBot mongoDB connection URL
file = open("mongoURL.txt")
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


class roleMenu(commands.Cog):

    def __init__(self, client):
        self.client = client

    """###################################################
    #                      Events                        #
    ###################################################"""

    # Event Showing roleMenu is loaded
    @commands.Cog.listener()
    async def on_ready(self):
        print('\t- Loaded roleMenu')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        reactionName = payload.emoji
        messageID = payload.message_id
        userID = payload.user_id
        guildID = payload.guild_id
        guild = discord.utils.find(lambda g: g.id == guildID, self.client.guilds)

        db = cluster[str(guildID)]
        menu = db["roleMenus"]

        # Checks to see if the collection exists
        if menu.count() != 0:
            query = menu.find_one({"_id": messageID})

            # If the messages being reacted to is a roleMenu
            if menu.count_documents(query) == 1:

                # Gets the dictionary to define what role name results from the emoji reacted
                reactionRoles = query['reactionRole']

                # Reaction roles returns the name of the role that is supposed to be returned based off the emoji used
                # This function gets the role that is supposed to be used
                role = discord.utils.get(guild.roles, name=reactionRoles[reactionName])

                print('Role Menu Found')
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

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        reactionName = payload.emoji.name
        messageID = payload.message_id
        userID = payload.user_id
        guildID = payload.guild_id
        guild = discord.utils.find(lambda g: g.id == guildID, self.client.guilds)

        db = cluster[str(guildID)]
        menu = db["roleMenus"]

        # Checks to see if the collection exists
        if menu.count() != 0:
            query = menu.find_one({"_id": messageID})

            # If the messages being reacted to is a roleMenu
            if menu.count_documents(query) == 1:

                # Gets the dictionary to define what role name results from the emoji reacted
                reactionRoles = query['reactionRole']

                # Reaction roles returns the name of the role that is supposed to be returned based off the emoji used
                # This function gets the role that is supposed to be used
                role = discord.utils.get(guild.roles, name=reactionRoles[reactionName])

                print('Role Menu Found')
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
    @commands.command()
    async def createRM(self, ctx, messageID, roleGroup):
        # Variables
        reactionRole = {"": ""}
        guildID = ctx.message.guild.id
        reactionMenu = await ctx.channel.fetch_message(messageID)  # should get the reaction menu message

        # Database access and pulling
        dataBase = cluster[str(guildID)]
        menus = dataBase["roleMenus"]

        # Checks if the role group exists
        if dataBase["roleGroups"].find_one({"_id": roleGroup}, {"_id": 0, "roleNames": 1}):  # Gets the mongo object
            rolesQuery = dataBase["roleGroups"].find_one({"_id": roleGroup}, {"_id": 0, "roleNames": 1})
        else:
            await ctx.channel.send(f'No role group {roleGroup} found!')
            return

        roles = rolesQuery['roleNames']  # Get the array of roles from the mongo object

        # Reaction Handling
        if menus.count_documents({"_id": messageID}) == 0:
            # Sends the message to react to
            await ctx.channel.send(f'Add reaction to this message for: ```[{roles[0]}]```')

            # Grabs the messageID of the last message sent by the bot
            reactionMsg = ctx.channel.history(limit=1).messageable.last_message
            print(f'Reaction Message ID: {reactionMsg.id}')

            userReaction, user = await self.client.wait_for('reaction_add', timeout=60.0)  # Gets the users reaction to the reaction message
            reactionRole[userReaction] = roles[0]  # Adds the reaction and role to the reactionRole dictionary
            await reactionMenu.add_reaction(userReaction)  # Adds the reaction to the reaction menu
            await reactionMsg.clear_reactions()  # Clear the reactions on the reaction menu for the next role

            # Cycling through all the roles that are in the roleGroup if there is more than one role
            if len(roles) > 1:
                for role in roles[1:]:
                    # Edits the message to change the role that is being edited
                    await reactionMsg.edit(content=f'Add reaction to this message for: ```[{role}]```')

                    userReaction, user = await self.client.wait_for('reaction_add', timeout=60.0)
                    reactionRole[userReaction] = role  # Adds the reaction and role to the reactionRole dictionary
                    await reactionMenu.add_reaction(userReaction)  # Adds the reaction to the reaction menu
                    await reactionMsg.clear_reactions()  # Clear the reactions on the reaction menu for the next role

            # Adds the role menu to the roleMenus collection in the data base
            post = {"_id": messageID, "cName": ctx.channel.name, "reactionRole": reactionRole}
            menus.insert_one(post)

        else:
            await ctx.channel.send(f'There is already a role menu on that message! ID: {messageID}')

        # Deletes all roleMenu setup messages
        await ctx.channel.purge(limit=2)

    @commands.command(hidden=True)
    async def ping3(self, ctx):
        await ctx.channel.send('Pong! RMe')


def setup(client):
    client.add_cog(roleMenu(client))