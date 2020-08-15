import discord
from discord.ext import commands


class messageManagment(commands.Cog):

    def __init__(self, client):
        self.client = client

    ######################################################
    #                      Events                        #
    ######################################################

    # Showing messageManagment is loaded
    @commands.Cog.listener()
    async def on_ready(self):
        print('\t- Loaded messageManagment')

    # Deleting all TEXT messages in a specific channel
    @commands.Cog.listener()
    async def on_message(self, message):
        if str(message.channel) == "pics" and message.content != "":
            await message.channel.purge(limit=1)

    ######################################################
    #                     Commands                       #
    ######################################################

    # Saying Hello to anyone who wants to say hi
    @commands.command()
    async def hello(self, ctx):
        await ctx.send('Hello')

    # Deleting a specific NUMBER of messages anywhere
    @commands.command(name='delete', description='Delete 1-100 messages in a channel')
    async def delete(self, ctx, arg):
        if ctx.message.author.server_permissions.administrator:  # Have to be an administrator to run
            if int(arg) > 100:
                await ctx.channel.purge(limit=100)
                await ctx.channel.send('Limit 100 deletions!')
            else:
                await ctx.channel.purge(limit=int(arg))
        else:
            await ctx.channel.send (f'Sorry {ctx.message.author} you do not have permissions!')


def setup(client):
    client.add_cog(messageManagment(client))

