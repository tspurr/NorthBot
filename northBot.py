import os
import discord
from discord.ext import commands

# Getting the bot token
file = open("discordToken.txt")
TOKEN = file.read()
file.close()

# Turns the Bot Online
client = commands.Bot(command_prefix='.')


# On Startup the bot prints that it has logged in
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Game("With Myself"), status=discord.Status.idle)


@client.command(hidden=True)
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')


@client.command(hidden=True)
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


# Terminates the bot so that the python program stops running when code needs to be updated
@client.command(hidden=True)
@commands.is_owner()
async def shutdown(ctx):
    await client.close()
    print('Bot closed')


# Token to Identify which bot is being called, and running the code
client.run(TOKEN)
