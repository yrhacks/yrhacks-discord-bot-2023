import os
import discord

# Constants
VERIFIED_ROLE_NAME = "verified"

# Temporary array of allowed users. Should get these from the google sheet in the future.
temp_allowed_users = [
	"EdZ123#8965"
]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

# Verify new members
@client.event
async def on_member_join(self, member):
	guild = member.guild
	verified_role = discord.utils.get(guild.roles, name=VERIFIED_ROLE_NAME)
	
	if guild.system_channel is not None:
		if f'{member.username}#{member.id}' in temp_allowed_users:
			await member.add_roles(verified_role, reason="Member is verified")
			to_send = f'Welcome {member.mention} to {guild.name}!'
		else:
			to_send = f'Hello {member.mention}, your username and ID are not in our allowed list. If you changed your username or ID after registering, please email us.'
	await guild.system_channel.send(to_send)

client.run(os.getenv('TOKEN'))
