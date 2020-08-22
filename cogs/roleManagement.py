import discord
from discord.ext import commands
from pymongo import MongoClient

# Getting the NorthBot mongoDB connection URL
file = open("mongoURL.txt")
connectionURL = file.read()
file.close()

# MongoDB initialization
cluster = MongoClient(connectionURL)


class roleManagement(commands.Cog):

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
    async def createRG(self, ctx, *args):
        guildID = ctx.guild.id
        dataBase = cluster[str(guildID)]
        collection = dataBase["roleGroups"]

        myquery = {"_id": args[0]}

        if collection.count_documents(myquery) == 0:  # Checks if the server has a group with that name already
            post = {"_id": args[0], 'roleNames': args[1:]}
            collection.insert_one(post)
            await ctx.channel.send(f'Role Group {args[0]} created!')
        else:
            await ctx.channel.send(f'Already a Role Group created called {args[0]}!'
                                   f'\nTry running .deleteRG {args[0]}')

    # Deletes a Role Group
    @commands.command()
    async def deleteRG(self, ctx, *args):
        guildID = ctx.guild.id
        dataBase = cluster[str(guildID)]
        collection = dataBase["roleGroup"]

        myquery = {"_id": args[0]}

        if collection.count_documents(myquery) == 1:
            collection.delete_one(myquery)
            await ctx.channel.send(f'Role Group {args[0]} deleted!')
        else:
            await ctx.channel.send(f'No Role Group named {args[0]}!')

    # Ping command to see if the file is loaded
    @commands.command(hidden=True)
    async def ping4(self, ctx):
        await ctx.channel.send('Pong! RMe')


def setup(client):
    client.add_cog(roleManagement(client))