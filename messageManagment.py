import discord
client = discord.Client()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('~hello'):
        await message.channel.send('Hello!')

client.run('NzQzMTQyNjI1Mjk2Nzc3MzI3.XzQXgA.qS-jl0p8OYGlnUki0ff8244wjIw')