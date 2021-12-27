# dont use discord.py use the fork `pip install discord.py-self`

discord_token = '' # do not expose the TOKEN
channelIds_forward = [] # never put this in the channelIds_listen List
channelIds_listen = []


import discord # use the discord.py-self verrsion !

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        # check if message channel is monitored
        if str(message.channel.id) not in channelIds_listen:
            return

        # create embed
        embed = discord.Embed(title="redirected from `" + message.channel.name + "`", description=str(message.content), color=0x00ff00)
        embed.set_author(name=str(message.author), icon_url=message.author.avatar_url)
        embed.set_footer(text="# " + str(message.id)) # set message id as footer 

        for channelId in channelIds_forward:
            channel = self.get_channel(int(channelId))
            await channel.send(embed=embed)

    async def on_raw_message_edit(self, rawMessageUpdateEvent):
        # check if message channel is monitored
        if str(rawMessageUpdateEvent.channel_id) not in channelIds_listen:
            return

        channel = self.get_channel(int(rawMessageUpdateEvent.channel_id))
        messages = await channel.history(limit=50).flatten()
        for message in messages:
            if rawMessageUpdateEvent.message_id == message.id:
                # got monitored message now get messege to update
                # search for messasge with its embed footer
                for channelId in channelIds_forward:
                    channel_forward = self.get_channel(int(channelId))
                    messages_forward = await channel_forward.history(limit=50).flatten()
                    for messageToUpdate in messages_forward:
                        for embed in messageToUpdate.embeds:
                            # if has embed no footer skip message
                            if embed.footer.text is discord.Embed.Empty:
                                continue

                            if embed.footer.text.split()[1].strip() == str(message.id):
                                # edit the embed
                                embed = discord.Embed(title="redirected from `" + message.channel.name + "`", description=str(message.content), color=0x00ff00)
                                embed.set_author(name=str(message.author), icon_url=message.author.avatar_url)
                                embed.set_footer(text="# " + str(message.id)) # set message id as footer 
                                await messageToUpdate.edit(embed=embed)

    async def on_raw_message_delete(self, rawMessageDeleteEvent):
        # check if message channel is monitored
        if str(rawMessageDeleteEvent.channel_id) not in channelIds_listen:
            return

        # got monitored message now get messege to update
        # search for messasge with its embed footer
        for channelId in channelIds_forward:
            channel_forward = self.get_channel(int(channelId))
            messages_forward = await channel_forward.history(limit=50).flatten()
            for message in messages_forward:
                for embed in message.embeds:
                    # if has embed no footer skip message
                    if embed.footer.text is discord.Embed.Empty:
                        continue

                    if embed.footer.text.split()[1].strip() == str(rawMessageDeleteEvent.message_id):
                        await message.delete()

MyClient().run(discord_token)
