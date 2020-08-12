import discord
import messageManagment

# Turns the Bot Online
client = discord.Client()

# On Startup the bot prints that it has logged in
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


# Token to Identify which bot is being called, and running the code
client.run('NzQzMTQyNjI1Mjk2Nzc3MzI3.XzQXgA.qS-jl0p8OYGlnUki0ff8244wjIw')