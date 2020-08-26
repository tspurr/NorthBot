import discord
from discord.ext import commands
from pymongo import MongoClient

# Getting the NorthBot mongoDB connection URL
file = open("mongoURL.txt")
connectionURL = file.read()
file.close()

# MongoDB initialization
cluster = MongoClient(connectionURL)


class twitch(commands.Cog, name='Twitch/YouTube'):

    def __init__(self, client):
        self.client = client

    """###################################################
    #                      Events                        #
    ###################################################"""

    # Event Showing serverStatistics is loaded
    @commands.Cog.listener()
    async def on_ready(self):
        print('\t- Loaded twitch')

    # Checks for people in a discord server who went live and makes a notification about it
    @commands.Cog.listener()
    async def my_background_task(self):
        # Variables
        twitchColor = discord.colour()
        youtubeColor = discord.color()

        # TODO Gets the serverID and the channel that it should notify streams to
        dataBase = cluster[serverID]

        # TODO Check to see if user activity has changed (ON DESKTOP)

            # TODO if the activity is streaming

                # TODO create and embed (Twitch and YouTube Color difference)

                # TODO put all stream info into the embed

                # TODO check database for stream announcement changes for specific servers
                # TODO could be different general saying or for specific people different sayings

    """###################################################
    #                     Commands                       #
    ###################################################"""

    @commands.command(hidden=True)
    async def testEmbed(self, ctx):
        embed = discord.Embed(
            title='title',
            description='This is a description',
            color=discord.Color(value=int('FFCB05', 16)),
        )

        embed.set_footer(text='fooooter')
        embed.set_image(url="https://media.discordapp.net/attachments/630891280670654517/742556048153509898/UofMOverwatchLogo16.png?width=611&height=611")
        embed.set_author(name='Author Name', icon_url="https://media.discordapp.net/attachments/630891280670654517/742556048153509898/UofMOverwatchLogo16.png?width=611&height=611")
        embed.add_field(name='Field Name', value='Description', inline=False)
        embed.add_field(name='Field Name', value='Description', inline=True)
        embed.add_field(name='Field Name', value='Description', inline=True)

        await ctx.send(embed=embed)

    # Ping command to see if the file is loaded
    @commands.command(hidden=True)
    async def ping1(self, ctx):
        await ctx.channel.send('Pong! EM')


def setup(client):
    client.add_cog(twitch(client))
