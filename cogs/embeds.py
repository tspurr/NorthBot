import discord
from discord.ext import commands

# Todo rename this file to something more useful

class embeds(commands.Cog):

    def __init__(self, client):
        self.client = client

    """###################################################
    #                      Events                        #
    ###################################################"""

    # Event Showing serverStatistics is loaded
    @commands.Cog.listener()
    async def on_ready(self):
        print('\t- Loaded embeds')

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

    @commands.command(hidden=True)
    async def ping1(self, ctx):
        await ctx.channel.send('Pong! EM')


def setup(client):
    client.add_cog(embeds(client))
