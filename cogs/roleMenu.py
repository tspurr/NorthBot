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

    ######################################################
    #                      Events                        #
    ######################################################

    # Event Showing roleMenu is loaded
    @commands.Cog.listener()
    async def on_ready(self):
        print('\t- Loaded roleMenu')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        reaction = str(payload.emoji)
        messageID = payload.message_id
        channelID = payload.channel_id
        userID = payload.user_id
        guildID = payload.guild_id

        db = cluster[str(guildID)]
        menu = db["roleMenus"]

        if menu.count_documents({"_id": messageID}) == 1:
            print('Role Menu Found')

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        reaction = str(payload.emoji)
        messageID = payload.message_id
        channelID = payload.channel_id
        userID = payload.user_id
        guildID = payload.guild_id

        db = cluster[str(guildID)]
        menu = db["roleMenus"]

        if menu.count_documents({"_id": messageID}) == 1:
            print('Role Menu Found')

    """###################################################
    #                     Commands                       #
    ###################################################"""
    @commands.command(name='Role Menu', description='Menu to allow users to select a role in the server from one menu')
    async def roleMenu(self, ctx, messageID, roleGroup):
        # Variables
        reactionRole = None
        userID = ctx.user.id
        guildID = ctx.guild.id
        reactionMenu = ctx.channel.messages.fetchMessage(messageID)  # should get the reaction menu message

        # Database access and pulling
        dataBase = cluster[str(guildID)]
        menus = dataBase["roleMenus"]
        rolesQuery = dataBase["roleGroups"].find({"_id": roleGroup}, {"_id": 0, "roleNames": 1})  # Gets the mongo object
        roles = rolesQuery['roleNames']  # Get the array of roles from the mongo object

        # Reaction Handling
        if menus.count_documents({"_id": messageID}) == 0:
            # Sends the message to react to
            await ctx.channel.send(f'Add reaction to this message for: ```css{roles[0]}```')

            # Grabs the messageID of the last message sent by the bot
            reactionMsg = ctx.channel.history(limit=1)
            print(f'Reaction Message ID: {reactionMsg}')

            userReaction = reactionMsg.reaction()  # Gets the users reaction to the reaction message
            reactionRole[userReaction] = roles[0]  # Adds the reaction and role to the reactionRole dictionary
            await reactionMenu.add_reaction(userReaction)  # Adds the reaction to the reaction menu
            reactionMsg.clear_reactions()  # Clear the reactions on the reaction menu for the next role

            # Cycling through all the roles that are in the roleGroup if there is more than one role
            if roles.length() > 1:
                for role in roles[1:]:
                    reactionMsg.edit(f'Add reaction to this message for: ```css{role}```')  # Edits the message to change the role that is being edited
                    userReaction = reactionMsg.reaction()  # Gets the user reaction to the message
                    reactionRole[userReaction] = role  # Adds the reaction and role to the reactionRole dictionary
                    reactionMsg.clear_reactions()  # Clear the reactions on the reaction menu for the next role

            # Adds the role menu to the roleMenus collection in the data base
            post = {"_id": messageID, "cName": ctx.channel.name, "content": ctx.message, "reactionRole": reactionRole}
            menus.insert_one(post)

        else:
            await ctx.channel.send(f'There is already a role menu on that message! ID: {messageID}')

        # Deletes all roleMenu setup messages
        await ctx.channel.purge(limit=2)


def setup(client):
    client.add_cog(roleMenu(client))