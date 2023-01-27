import os
import discord

# Constants
VERIFIED_ROLE_NAME = "verified"

# Temporary array of allowed users. Should get these from the google sheet in the future.
temp_allowed_users = [
	"EdZ123#8965",
	"RZ Music#5601"
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
async def on_member_join(member):
	guild = member.guild
	verified_role = discord.utils.get(guild.roles, name=VERIFIED_ROLE_NAME)
	
	if guild.system_channel is not None:
		if f'{member.name}#{member.discriminator}' in temp_allowed_users:
			try:
				await member.add_roles(verified_role)
			except Exception as e:
				print(e)
				to_send = "Error assigning roles."
			else:
				to_send = f'Welcome {member.mention} to {guild.name}, you have been verified!'
		else:
			to_send = f'Hello {member.mention}, your username and tag are not in our allowed list. If you changed your username or tag after registering, please email us.'
			
	await guild.system_channel.send(to_send)

client.run(os.getenv('TOKEN'))
