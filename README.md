# CrumbClient

> [!WARNING]
> This library is still under developement and is not yet ready for production.

A lightweight bare minimum API wrapper for Discord's v10 API made in python.

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

## TODO
- Buttons, Modals, App commands, User commands
- Permissions checking
- Better verbose, error handling
- Automatic lossless image compression
