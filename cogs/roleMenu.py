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
    async def on_reaction_add(self, reaction, user):
        print(f'{user.name} reacted with {reaction.emoji}')
        dataBase = cluster[str(ctx.guild.id)]
        menus = dataBase["roleMenus"]

        myquery = {"_id": reaction.message.id}
        if menus.count_documents(myquery) == 1:  # If reaction menu exist
            emojiRole = menus.find({myquery}, {"_id": 0, "cName": 0, "content": 0,
                                               "emojiRole": 1})  # Only returns the emojiRole dictionary
            if emojiRole.has_key(reaction.emoji):  # Check to see if the key exists
                user.add_role(emojiRole[reaction.emoji])  # Adds the role associated with the reaction on the menu
            else:
                return
        else:
            return

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        print(f'{user.name} removed reaction with {reaction.emoji}')
        dataBase = cluster[str(ctx.guild.id)]
        menus = dataBase["roleMenus"]

        myquery = {"_id": reaction.message.id}
        if menus.count_documents(myquery) == 1:  # If reaction menu exist
            emojiRole = menus.find({myquery}, {"_id": 0, "cName": 0, "content": 0,
                                               "emojiRole": 1})  # Only returns the emojiRole dictionary
            if emojiRole.has_key(reaction.emoji):  # Check to see if the key exists
                user.remove_role(emojiRole[reaction.emoji])  # Removes the role associated with the reaction on the menu
            else:
                return
        else:
            return

    ######################################################
    #                     Commands                       #
    ######################################################

    @commands.command(name='Role Menu', description='Menu to allow users to select a role in the server from one menu')
    async def roleMenu(self, ctx, messageID, roleGroup):
        dataBase = cluster[str(ctx.guild.id)]
        menus = dataBase["roleMenus"]
        group = dataBase["roleGroups"].find(str(roleGroup))
        global emojiRole

        myquery = {"_id": messageID}
        if menus.count_documents(myquery) == 0:

            await ctx.channel.send(f'Add reaction to this message for: ```css{roleGroup[0]}```')
            reactionMsg = ctx.channel.message(limit=1).history
            reaction = await ctx.wait_for_reaction(emoji)

            for role in group[1:]:
                reactionMsg.edit(f'Add reaction to this message for: ```css{role}```')

            post = {"_id": messageID, "cName": ctx.channel.name, "content": ctx.message, "emojiRole": emojiRole}
            menus.insert_one(post)
        else:
            await ctx.channel.send(f'There is already a role menu on that message! ID: {messageID}')


def setup(client):
    client.add_cog(roleMenu(client))