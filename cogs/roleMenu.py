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
        # if reaction message ID is role menu (in specific server)
            # if reaction is in role menu
                # give user role associated
            # else
                # return
        # else
            # return

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        print(f'{user.name} removed reaction with {reaction.emoji}')
        # if reaction message ID is role menu (in specific server)
            # if reaction is in role menu
                # give user role associated
            # else
                # return
        # else
            # return

    ######################################################
    #                     Commands                       #
    ######################################################

    @commands.command(name='Role Menu', description='Menu to allow users to select a role in the server from one menu')
    async def roleMenu(self, ctx, messageID, roleGroup):
        dataBase = cluster[str(ctx.guild.id)]
        menus = dataBase["roleMenus"]
        group = dataBase[str(roleGroup)]  # TODO create role groups in roleMenu.py
        global emojiRole

        myquery = {"_id": messageID}
        if menus.count_documents(myquery) == 0:
            for role in group:
                await ctx.channel.send(f'Add reaction to this message for: ```css{role}```')
                ctx.on_reaction()
                lastMessage = ctx.channel.history().id
                ctx.add_reaction()
                emojiRole[str(userReaction)] = role

            post = {"_id": messageID, "cName": ctx.channel.name, "emojiRole": emojiRole}
            menus.insert_one(post)
        else:
            await ctx.channel.send(f'There is already a role menu on that message! ID: {messageID}')


def setup(client):
    client.add_cog(roleMenu(client))