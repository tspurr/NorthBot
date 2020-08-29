"""
The MIT License (MIT)

Copyright (c) 2020 Tyler Spurr

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import os
import discord
from discord.ext import commands

# Getting the bot token
file = open('discordToken.txt')
TOKEN = file.read()
file.close()

# Turns the Bot Online
client = commands.Bot(command_prefix=commands.when_mentioned_or('.'))  # When the bot is mentioned or the . is used
client.remove_command('help')


# On Startup the bot prints that it has logged in
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Game('With Myself'), status=discord.Status.idle)


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
