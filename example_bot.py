import discord

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

client.run('ODQyNTMxMDE3MzM2NDIyNDQw.YJ2qKA.G4KD_3eFs1HGWpDDNY0qipvjVkE')
