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
    async def roleMenu(self, ctx):
        dataBase = cluster[str(ctx.guild.id)]
        menus = dataBase["roleMenus"]

        myquery = {"_id": ctx.message.id}
        if menus.count_documents(myquery) == 0:
            post = {"_id": ctx.message.id, "cName": ctx.channel.name}
            menus.insert_one(post)
            await ctx.channel.send('added RM')
        else:
            query = {"_id": ctx.channel.id}
            user = channelCollection.find(query)
            for result in user:
                numMessages = result["numMessages"]
            numMessages += 1
            channelCollection.update_one({"_id": ctx.channel.id}, {"$set": {"numMessages": numMessages}})
            await ctx.channel.send('plus one')


def setup(client):
    client.add_cog(roleMenu(client))