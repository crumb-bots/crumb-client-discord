# CrumbClient

> [!WARNING]
> This library is still under developement and is not yet ready for production.

A lightweight bare minimum API wrapper for Discord's v10 API made in python.

## Install
```sh
git clone https://github.com/crumb-bots/crumb-client-discord && cd crumb-client-discord
pip install .
```

## Example Usage
```py
import random
import CrumbClient

client = CrumbClient.Client()

@client.event
async def on_ready():
    print("Logged in as %s (%s)" % (client.user.name, client.user.id))

    await client.update_avatar(file="rizz.gif")
    await client.update_banner(file="rizz.gif")
    await client.update_pronouns(new_pronoun="i am silly willy v2!")

    await client.sync_global_commands()

@client.slash(name="music", desc="Sends a song!", admin_only=True)
async def send_random_song(interaction: CrumbClient.Interaction):
    await interaction.send_voice_message(file_location="song.mp3")

@client.command(name="poll", desc="Sends a poll")
async def send_poll(message: CrumbClient.Message):

    poll = CrumbClient.Poll(
        question="whats your favorite color?",
        multiselect=True,
        duration_hours=CrumbClient.Polls.max_time
    )

    poll.add_option(CrumbClient.PollOption("red", emoji=CrumbClient.Emoji(id=1093318271899549806)))
    poll.add_option(CrumbClient.PollOption("blue"))
    poll.add_option(CrumbClient.PollOption("green"))

    await message.send_in_channel(poll=poll)

@client.command(name="audio", desc="sends a voice message!")
async def send_audio(message: CrumbClient.Message):
    # this function automatically converts non ogg files to ogg files
    await message.send_voice_message(file_location="song.mp3")

client.login("YOUR_TOKEN_HERE")
```

## Implemented
- zlib transport compression
- Changing Bot Pronouns and avatar (Including Animated gifs)
- on_message, on_ready, slash commands, text commands
- User, Message, Channel, Interaction objects
- AllowedMentions
- Embeds (Partial Implementation)
- Voice Message Sending (With automatic to ogg conversion)
- Descriptions for slash commands and options
- Loading modules in `ext` dynamically, offloading when not needed
- Discord Polls! 

## TODO
- Buttons, Modals, App commands, User commands
- Permissions checking
- Better verbose, error handling
- Automatic lossless image compression
