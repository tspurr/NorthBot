import discord
import os
from discord.ext import commands

# Turns the Bot Online
client = commands.Bot(command_prefix = '.')

# On Startup the bot prints that it has logged in
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.command()
async def load(ctx, extension):
    client.load_extension('cogs.' + extension)

@client.command()
async def unload(ctx, extension):
    client.unload_extension('cogs.' + extension)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension('cogs.' + (filename[:-3]))

# Token to Identify which bot is being called, and running the code
client.run('NzQzMTQyNjI1Mjk2Nzc3MzI3.XzQXgA.qS-jl0p8OYGlnUki0ff8244wjIw')