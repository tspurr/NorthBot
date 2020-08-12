import discord
from discord.ext import commands


class messageManagment(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Event Showing messageManagment is loaded
    @commands.Cog.listener()
    async def on_ready(self):
        print('\t- Loaded messageManagment')

    # Saying Hello to anyone who wants to say hi
    @commands.command()
    async def hello(self, ctx):
        await ctx.send('Hello')

    # Deleting all TEXT messages in a specific channel
    @commands.Cog.listener()
    async def on_message(self, message):
        if str(message.channel) == "pics" and message.content != "":
            await message.channel.purge(limit=1)

    # Deleting a specific NUMBER of messages anywhere
    @commands.command()
    async def delete(self, ctx, arg):
        await ctx.channel.purge(limit=int(arg))


def setup(client):
    client.add_cog(messageManagment(client))

