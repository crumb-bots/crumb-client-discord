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
import CrumbClient

...
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
