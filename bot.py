import discord
import requests
from pathlib import Path
import time

name = "Maintenance Bot :robot:"
description = "An open-source Discord bot to put your server on maintenance. :jigsaw:"
color = 0x00ff00

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if message.content.startswith('$help'):
        await message.channel.send('Hello, I am {}, I\'ll help you to monitor your server ! :computer:'.format(name))
        embedVar = discord.Embed(title=name, description=description, color=color)
        embedVar.add_field(name="Configuration", value="To configure myself, run the command `$config #channel_to_create; @Role_That_Can_Use_Me`.\n **You must tag only one role**.", inline=False)
        embedVar.add_field(name="How to enable maintenance mod ? :lock:", value="To **enable** the maintenance mod, you need to run the command `$lock Message`.\nIf you want to specify roles to lock, add `;` behind your message and identify them.\n Example : `$lock Sorry, this server is now on maintenance; @Members` will lock the server for **all users who have the @Members role**. \n`$lock Sorry, this server is now on maintenance` will lock the server for **all users of the server**.", inline=False)
        embedVar.add_field(name="How to disable maintenance mod ? :unlock:", value="To **disable** the maintenance mod, you need to run the command `$unlock`.\nIf you specified roles when you locked the server, **identify them**.\n Example : `$unlock` will unlock the server for **all users** if you didn't specified roles when running `$lock`.\n`$unlock @Members` will unlock the server for **all users who have the role `@Members`** (only work if you specified the `Members` when you locked the server.).", inline=False)
        await message.channel.send(embed=embedVar)

    elif message.content.startswith('$config'):
        if "#" in message.content:
            try:
                channel_name = message.content.split('#')[1].split(';')[0]
                allowedRole = message.content.split(channel_name + ';')[1]
                await message.channel.send('Updating bot configuration :white_check_mark:\nChannel name : #{}\nAllowed role : {}'.format(channel_name, allowedRole))

                with open('servers/' + str(message.guild.id) + '.txt', 'w+', encoding="utf-8") as file:
                    file.write(channel_name + '|' + allowedRole)

            except IndexError:
                await message.channel.send('Arguments missing. :x:')

    elif message.content.startswith('$lock'):
        if not Path('servers/' + str(message.guild.id) + '.txt').is_file():
            await message.channel.send('You must configure me before using that command. :robot:')
        else:
            allChannels = message.guild.channels # Get all channels (voice & text) of server
            channel_name = ''
            global x
            with open('servers/' + str(message.guild.id) + '.txt', 'r', encoding="utf-8") as file:
                lines = file.readlines()
                for line in lines:
                    channel_name = line.split('|')[0].replace(' ', '')
                    enabledRole = line.split('|')[1].replace(' ', '').replace('<@&', '').replace('>', '')

            if enabledRole not in str(message.author.roles):
                await message.channel.send('You don\'t have the right to use this command. :x:')
            else:
                try:
                    if "@" in message.content:
                        lockMessage = message.content.split('$lock ')[1].split(';')[0]
                        x = message.content.split(';')[1]
                        await message.channel.send('Roles that will get server locked : {}. :lock:'.format(x))
                    else:
                        x = ''
                        lockMessage = message.content.split('$lock ')[1]
                        await message.channel.send('All roles will get server locked. :lock:')
                    try:
                        await message.guild.create_text_channel(channel_name) # Create new channel
                        newChan = discord.utils.get(message.guild.text_channels, name=channel_name)
                        await newChan.send(lockMessage)

                        if x != '':
                            await message.channel.send('Locking your server with the message : {}. :robot:\nCreating the channel : #{}. :white_check_mark:'.format(lockMessage, channel_name))
                            for channelToLock in allChannels:
                                for role in message.guild.roles:
                                    if str(role.id) in str(x):
                                        await channelToLock.set_permissions(role, send_messages=False, read_messages=False) # Disable messages sending & messages reading
                        else:
                            await message.channel.send('Locking your server with the message : {}. :robot:\nCreating the channel : #{}. :white_check_mark:'.format(lockMessage, channel_name))
                            for channelToLock in allChannels:
                                for role in message.guild.roles:
                                    await channelToLock.set_permissions(role, send_messages=False, read_messages=False) # Disable messages sending & messages reading

                    except discord.errors.Forbidden:
                        await message.channel.send('I don\'t have the permission to do that ! :robot:')

                except IndexError:
                    await message.channel.send('Arguments missing. :x:')

        

    elif message.content.startswith('$unlock'):
        if not Path('servers/' + str(message.guild.id) + '.txt').is_file():
            await message.channel.send('You must configure me before using that command. :robot:')
        else:
            with open('servers/' + str(message.guild.id) + '.txt', 'r', encoding="utf-8") as file:
                lines = file.readlines()
                for line in lines:
                    channel_name = line.split('|')[0].replace(' ', '')
                    enabledRole = line.split('|')[1].replace(' ', '').replace('<@&', '').replace('>', '')
    
            global e

            if enabledRole not in str(message.author.roles):
                await message.channel.send('You don\'t have the right to use this command. :x:')
            else:
                if "@" in message.content:
                        e = message.content.split('$unlock ')[1]
                        await message.channel.send('Roles that will get server unlocked : {}. :unlock:'.format(e))
                else:
                    e = ''
                    await message.channel.send('All roles will get server unlocked. :unlock:')
                
                try:
                    allChannels = message.guild.channels # Get all channels (voice & text) of server
                    if e != '':
                        await message.channel.send('Unlocking server... :white_check_mark:')
                        for channelToUnlock in allChannels:
                            for role in message.guild.roles:
                                if str(role.id) in str(e):
                                    await channelToUnlock.set_permissions(role, send_messages=True, read_messages=True) # Enable messages sending & messages reading

                    else:
                        await message.channel.send('Unlocking server... :white_check_mark:')
                        for channelToUnlock in allChannels:
                            for role in message.guild.roles:
                                await channelToUnlock.set_permissions(role, send_messages=True, read_messages=True) # Enable messages sending & messages reading

                    oldChan = discord.utils.get(message.guild.text_channels, name=channel_name)
                    await oldChan.delete()

                except discord.errors.Forbidden:
                    await message.channel.send('I don\'t have the permission to do that ! :x:')

client.run('your-token')
