# -*- coding: utf-8 -*-
# shard_id = (guild_id >> 22) % num_shards
# Discord Shard IDs start at 0

# Discord API Config
GATEWAY = 'wss://gateway.discord.gg/?v=10&encoding=json&compress=zlib-stream'

# Modules
import os
import json
import httpx
import websockets
import asyncio
import zlib
import base64
import random

from time import monotonic
from inspect import signature, Parameter

class Color:
    ''' This class contains colors for embeds that can be used in the color field of the `crumb.Embed` object. '''

    blurple = 0x5865F2
    red = 0xED4245 
    yellow = 0xFEE75C 
    green = 0x57F287 


class Debug:
    def print_json(data):
        if isinstance(data, dict):
            print(json.dumps(data, indent=4))
        else:
            print(json.dumps(json.loads(data), indent=4))

class Embed(object):
    title:str
    description:str
    color:int

    class Footer:
        text=None

    def __init__(self, title=None, description=None, footer_text=None, color=None):
        self.title = title
        self.description = description
        self.color=color
        self.Footer.text = footer_text

    def to_dict(self):
        cdict =  {
            "title": self.title,
            "description": self.description,
            "color": self.color,
            "footer": {
                "text": self.Footer.text
            }
        }

        r = {} 

        for key,value in cdict.items():
            if value != None:
                r[key] = value

        return r


class User(object):
    id:int
    display_name:str
    name:str
    def __init__(self,id:int, name:str, display_name:str=None):
        self.id = id
        self.name = name
        self.display_name = display_name

class Interaction(object):
    type:int
    token:str
    member:User
    guild_id:int
    interaction_id:int

    def __init__(self, type, token, interaction_id, member, guild_id:int=None):
        self.type=type
        self.token=token
        self.member=member
        self.guild_id=guild_id
        self.interaction_id = interaction_id

    async def reply(self, content="", embeds=None, ephemeral=True, embed=None):

        if embed != None:
            embeds = embed

        ENDPOINT = f"https://discord.com/api/v10/interactions/{self.interaction_id}/{self.token}/callback"

        content = {
                    "type": 4,
                    "data": {
                        "content": content,
                        "flags": (64 if ephemeral else 0),
                        "allowed_mentions": {"parse": []}
                    }
                }
        

        if embeds != None:
            if isinstance(embeds, list):
                content["data"]["embeds"] = []

                for embed in embeds:
                    content["data"]["embeds"].append(embed.to_dict())
            else:
                
                content["data"]["embeds"] = [embed.to_dict()]

        print(content)

        # flags = 64 means ephemeral
        async with httpx.AsyncClient() as httpx_client:
            res = await httpx_client.post(
                url=ENDPOINT,
                json=content
            )

            print(res.text)


class InteractionAttachment(object):
    id:int
    name:str
    url:str
    def __init__(self, id:int, name:str, url:str):
        self.id = id
        self.name = name
        self.url = url
    
    async def save(self, path):
        async with httpx.AsyncClient() as httpx_client:
            res = await httpx_client.get(self.url)
            with open(path, "wb") as f:
                f.write(res.content)


class Message(object):
    id:int
    author:User
    channel_id:int
    guild_id:int
    content:str
    attachments:list
    reference:int
    _token:str

    def __init__(self, id, author, channel_id, guild_id=None, content=None, attachments=None, reference=None,token:str=None):
        self.id = id
        self.author = author
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.content = content
        self.attachments = attachments
        self.reference = reference
        self._token = token

    async def send_in_channel(self, content=None, embeds=None):
        url = f"https://discord.com/api/v10/channels/{self.channel_id}/messages"
        headers = {"authorization": "Bot " + self._token}

        content = {
            "content": content,
            "allowed_mentions": {
                "parse": [],
            }
        }

        if embeds != None:
            if isinstance(embeds, list):
                content["embeds"] = []

                for embed in embeds:
                    content["embeds"].append(embed.to_dict())
            else:
                
                content["embeds"] = [embed.to_dict()]


        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=content)
            response.raise_for_status()
            return response

    async def send_voice_message(self, file_location):
        data = None

        audiotools = __import__("ext.audiotools", fromlist=['*'])

        duration_secs = 0

        if file_location[::-1].split(".")[0][::-1].lower() != "ogg":
            export_to = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=15)) + "." + file_location[::-1].split(".")[0][::-1]

            await audiotools.convert_to_ogg(file_location, export_to)

            data = open(export_to, 'rb').read()

            os.remove(export_to)

            duration_secs = await audiotools.get_audio_length(file_location)
        else:
            data = open(file_location, 'rb').read()
            duration_secs = await audiotools.get_audio_length(file_location)

        # waveform = await audiotools.ogg_to_waveform(file_location)

        del audiotools

        await self._send_voice_message(data, duration_secs)

    async def _send_voice_message(self, data, duration_secs, waveform='S0FEMEdEMERHRCNOPj4+UVQ+UUtON1FLRE5OUTRLTktLUUs0S05LS05LLWh/eF5oaFh1b2teaGVhUVRRPk5LSzpOS0FRS1FBdWVHXnVvW4l1TluCf2FvaFtBUUs6YWVYR3JydWV8XkROTktRZVhBZWh1VHJhR15lTi1UVEdETkQnEwkDAAA6R0QjTj5EMEs+MERHRCdOTk5HVEs3R05RR05ONEtLWEFOSz5HTlE+VEdEQX+CXm9lYVt4a15vZWhRTk5HR1FLNEdOTkdOTjB4aFRLcnJeeIVePoVydWhyXkFRS05LZVtEaHKFXm9rTk5RTjplYU5Ua3JRcmVYR2tUOg=='):

        # the waveform is just a placeholder as discord doesnt actually check if its valid and is just filler waveform

        channel = self.channel_id
        headers = {
            'accept': '*/*',
            "authorization": "Bot " + self._token,
            'content-type': 'application/json',
        }

        json_data = {
            'files': [
                {
                    'filename': 'voice-message.ogg',
                    'file_size': 6986,
                    'id': '4',
                    'is_clip': False,
                },
            ],
        }

        response = httpx.post(
            f'https://discord.com/api/v10/channels/{channel}/attachments',
            headers=headers,
            json=json_data,
        )

        attachment_data = response.json()
        upload_id = attachment_data['attachments'][0]['upload_url'].split("upload_id=")[1]

        params = {
            'upload_id': upload_id,
        }

        response = httpx.put(
            'https://discord-attachments-uploads-prd.storage.googleapis.com/' + attachment_data['attachments'][0]["upload_filename"],
            headers=headers,
            data=data,
            params=params
        )


        json_data = {
            'flags': 8192,
            'channel_id': f'{channel}',
            'content': '',
            'sticker_ids': [],
            'type': 0,
            'attachments': [
                {
                    'id': '0',
                    'filename': 'voice-message.ogg',
                    'uploaded_filename': attachment_data['attachments'][0]["upload_filename"],
                    'waveform': waveform,
                    'duration_secs': duration_secs,
                },
            ],
            'message_reference': None,
        }

        response = httpx.post(
            f'https://discord.com/api/v10/channels/{channel}/messages',
            headers=headers,
            json=json_data,
        )

        return response.json()['id']
        
    async def reply(self, content=None, mention_author=True, embeds=None):
        url = f"https://discord.com/api/v10/channels/{self.channel_id}/messages"
        headers = {"authorization": "Bot " + self._token}
        content = {
            "content": content,
            "message_reference": {"message_id": self.id},
            "allowed_mentions": {
                "parse": [],
                "replied_user": mention_author,
            }
        }

        if embeds != None:
            if isinstance(embeds, list):
                content["embeds"] = []

                for embed in embeds:
                    content["embeds"].append(embed.to_dict())
            else:
                print("SINGLE EMBED, SETTING content['EMBEDS'] to EMBED.to_dict")
                content["embeds"] = [embeds.to_dict()]


        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=content)
            response.raise_for_status()
            return response

class Client(object):
    slash_command_descriptors = {}

    user:User
    latency:float

    _seq = None
    _websocket = None
    _heartbeat_interval = None
    _token = None
    _last_ping = None

    def get_pre(self):
        """
        Returns a formatted string containing the user's ID.
        """
        return f"<@{self.user.id}>"

    def __init__(self, shard_id=0, num_shards=1):
        self.events = {}
        self.commands = {}
        self.slash_commands = {}
        self.command_prefix = self.get_pre

        self.shard_id=shard_id
        self.num_shards=num_shards

    async def heartbeat(self):
        """
        Asynchronous function to send a heartbeat payload to the websocket at regular intervals.
        """
        while True:

            payload = json.dumps({"op": 1, "d": self._seq})

            self._last_ping = monotonic()

            await self._websocket.send(payload)

            await asyncio.sleep(self._heartbeat_interval / 1000)

    async def run(self, token):
        """
        Asynchronous function to run the client with the provided token.

        Args:
            token (str): The token to authenticate the client.
        """
        print("Connecting to gateway...")
        self._token = token

        buffer = bytearray()

        response = None

        inflator = zlib.decompressobj()

        ZLIB_SUFFIX = b'\x00\x00\xff\xff'

        async with websockets.connect(GATEWAY) as websocket:
            self._websocket = websocket

            while True:
                data = await websocket.recv()
                buffer.extend(data)
                            
                if not (len(data) < 4 or data[-4:] != ZLIB_SUFFIX):
                    response = inflator.decompress(buffer)
                    buffer.clear()

                    break

            response = json.loads(response)
            
            if response["op"] == 10:
                heartbeat_interval = response["d"]["heartbeat_interval"]

                self._heartbeat_interval = heartbeat_interval

                asyncio.create_task(self.heartbeat())

            # IDENTIFY Payload

            payload = {
                "op": 2,
                "d": {
                    "token": self._token,

                    "properties": {
                        "os": "linux",
                        "browser": "disco",
                        "device": "disco"
                    },
                    "presence": {
                        "activities": [], # "activities": [{"name": "Sleeping","type": 1}]
                        "status": "online",
                        "afk": False
                    },
                    "intents": 55936,
                    "shard": [self.shard_id, self.num_shards]
                }
            }

            await websocket.send(json.dumps(payload))

            print("Client Authenticated: Shard " + str(self.shard_id+1) + "/" + str(self.num_shards))

            del buffer

            buffer = bytearray()

            while True:

                while True:
                    data = await websocket.recv()
                    buffer.extend(data)
                                
                    if not (len(data) < 4 or data[-4:] != ZLIB_SUFFIX):
                        response = inflator.decompress(buffer)
                        buffer.clear()
                        break

                response = json.loads(response)

                if response["op"] == 11:
                    self.latency = (monotonic() - self._last_ping) / 2

                elif "t" in response:

                    event_type = response["t"]
                    event_data = response["d"]

                    print(event_type)
                    Debug.print_json(event_data)

                    # print(event_type, event_data)

                    if event_type == "READY":
                        # {'t': 'READY', 's': 1, 'op': 0, 'd': {'v': 10, 'user_settings': {}, 'user': {'verified': True, 'username': 'Testing Utilities', 'mfa_enabled': True, 'id': '', 'global_name': None, 'flags': 0, 'email': None, 'discriminator': '', 'bot': True, 'avatar': ''}, 'session_type': 'normal', 'session_id': ', 'resume_gateway_url': 'wss://gateway-us-east1-c.discord.gg', 'relationships': [], 'private_channels': [], 'presences': [], 'guilds': [{'unavailable': True, 'id': ''}], 'guild_join_requests': [], 'geo_ordered_rtc_regions': ['seattle', 'santa-clara', 'us-west', 'us-central', 'us-south'], 'current_location': ['CA', 'CA:BC'], 'auth': {}, 'application': {'id': '1203803535372976229', 'flags': 8953856}, '_trace': ['["gateway-prd-us-east1-c-r6cd",{"micros":66110,"calls":["id_created",{"micros":829,"calls":[]},"session_lookup_time",{"micros":342,"calls":[]},"session_lookup_finished",{"micros":14,"calls":[]},"discord-sessions-prd-2-275",{"micros":64425,"calls":["start_session",{"micros":55335,"calls":["discord-api-677679599-hmx6r",{"micros":48439,"calls":["get_user",{"micros":8118},"get_guilds",{"micros":5537},"send_scheduled_deletion_message",{"micros":14},"guild_join_requests",{"micros":2},"authorized_ip_coro",{"micros":17}]}]},"starting_guild_connect",{"micros":66,"calls":[]},"presence_started",{"micros":308,"calls":[]},"guilds_started",{"micros":100,"calls":[]},"guilds_connect",{"micros":2,"calls":[]},"presence_connect",{"micros":8559,"calls":[]},"connect_finished",{"micros":8564,"calls":[]},"build_ready",{"micros":28,"calls":[]},"clean_ready",{"micros":0,"calls":[]},"optimize_ready",{"micros":23,"calls":[]},"split_ready",{"micros":0,"calls":[]}]}]}]']}}
                        self.user = User(
                            id=event_data["user"]["id"],
                            name=event_data["user"]["username"] + "#" + event_data["user"]["discriminator"],
                            display_name=event_data["user"]["username"]
                        )

                        await self.dispatch_event("on_ready")

                    elif event_type == "MESSAGE_CREATE":
                        if response["d"]["type"] == 0 or response["d"]["type"] == 14:
                            channel_id = event_data["channel_id"]

                            author = User(
                                id=int(event_data["author"]["id"]),
                                name=event_data["author"]["username"],
                                display_name=event_data["author"]["global_name"]
                            )

                            guild_id = (event_data["guild_id"] if "guild_id" in event_data else None)

                            message = Message(
                                id = event_data["id"],
                                author=author,
                                channel_id=channel_id,
                                content=event_data["content"],
                                token=self._token,
                                guild_id=guild_id
                            )

                            command_prefix = self.command_prefix()
                            run = True

                            if message.content:
                                if message.content.startswith(command_prefix):
                                    command = message.content.split(command_prefix,1)[1].strip()
                                    if " " in command:
                                        command = command.split(" ",1)[0]
                                    if command in self.commands:
                                        await self.dispatch_command(command, message)
                                        run = False

                            if run: await self.dispatch_event("on_message", message)

                    # INTERACTION_CREATE {'version': 1, 'type': 2, 'token': 'interaction token', 'member': {'user': {'username': 'ericpan.xyz', 'public_flags': 4194432, 'id': '746446670228619414', 'global_name': 'Eric', 'discriminator': '0', 'avatar_decoration_data': {'sku_id': '1144056139584127058', 'asset': 'a_911e48f3a695c7f6c267843ab6a96f2f'}, 'avatar': 'c1a2750b45fdf88c898a317111855548'}, 'unusual_dm_activity_until': None, 'roles': ['1179594094985625710', '1203797222265852046'], 'premium_since': None, 'permissions': '562949953421311', 'pending': False, 'nick': None, 'mute': False, 'joined_at': '2023-11-07T02:04:29.866000+00:00', 'flags': 0, 'deaf': False, 'communication_disabled_until': None, 'avatar': None}, 'locale': 'en-GB', 'id': '1206835818526937130', 'guild_locale': 'en-US', 'guild_id': '1171268912462168154', 'guild': {'locale': 'en-US', 'id': '1171268912462168154', 'features': ['CHANNEL_ICON_EMOJIS_GENERATED', 'COMMUNITY', 'NEWS']}, 'entitlements': [], 'entitlement_sku_ids': [], 'data': {'type': 1, 'options': [{'value': 'animal_dog', 'type': 3, 'name': 'wrapper'}], 'name': 'blep', 'id': '1206834813538017300'}, 'channel_id': '1203791167741755444', 'channel': {'type': 0, 'topic': None, 'theme_color': None, 'rate_limit_per_user': 0, 'position': 4, 'permissions': '562949953421311', 'parent_id': '1171268912999055371', 'nsfw': False, 'name': 'submissions', 'last_message_id': '1206835659877384242', 'id': '1203791167741755444', 'icon_emoji': {'name': '📥', 'id': None}, 'guild_id': '1171268912462168154', 'flags': 0}, 'application_id': '1203803535372976229', 'app_permissions': '562949953421311'}

                    elif event_type == "INTERACTION_CREATE":
                        Member = User(
                            id=event_data['member']['user']['id'],
                            name=event_data['member']['user']['username'],
                            display_name=event_data['member']['user']['global_name']
                        )

                        interaction = Interaction(
                            type=event_data['type'],
                            token=event_data['token'],
                            interaction_id=event_data['id'],
                            member=Member,
                            guild_id=(event_data['guild_id'] if 'guild_id' in event_data else None)
                        )

                        args = {}

                        for arg in event_data['data']['options']:
                            args[arg["name"]] = arg["value"]

                        await self.dispatch_slash(event_data['data']['name'], interaction, **args)

    def login(self, token):
        asyncio.get_event_loop().run_until_complete(self.run(token))

    def event(self, func):
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            return result

        self.events[func.__name__] = wrapper
        return wrapper

    async def dispatch_event(self, func_name, *args, **kwargs):
        if func_name in self.events:
            await self.events[func_name](*args, **kwargs)

    def command(self, name, *args, **kwargs):
        def decorator(func):
            async def wrapper(context, *args, **kwargs):
                result = await func(context, *args, **kwargs)
                return result

            self.commands[name] = wrapper
            return wrapper

        return decorator

    async def dispatch_command(self, name, context, *args, **kwargs):
        if name in self.commands:
            await self.commands[name](context, *args, **kwargs)
        else:
            print(f"Command '{name}' not found.")

    def slash(self, name, desc="...", *args, **kwargs):
        def decorator(func):
            async def wrapper(context, *args, **kwargs):
                result = await func(context, *args, **kwargs)
                return result

            func_parameters = signature(func).parameters

            param_types = {param_name: (param.annotation, param.default != Parameter.empty) 
              for param_name, param in func_parameters.items()}

            new_data = {}

            for param, (dtype, param_has_default) in param_types.items():
                if dtype != Interaction:
                    if dtype is not Parameter.empty:
                        new_data[param] = [dtype, not param_has_default]

            self.slash_commands[name] = {"func": wrapper, "desc": desc, "parameters": new_data, "org_func": func}

            print(param_types)

            return wrapper
        return decorator
    
    @classmethod
    def describe(cls, **kwargs):
        def decorator(func):
            func_name = func.__name__
            cls.slash_command_descriptors[func_name] = kwargs
            return func
        return decorator
    
    async def dispatch_slash(self, name, context, *args, **kwargs):

        if name in self.slash_commands:
            await self.slash_commands[name]["func"](context, *args, **kwargs)
        else:
            print("User attempted to run the command `%s` which does not exist." % name)

    async def add_slash_module_to(self, commands, guild_id):
        # TODO: Finish this
        ...
    
    async def sync_global_commands(self):
        """
        Asynchronously synchronizes global commands with the Discord API. 
        """

        print("DESCRIPTORS", self.slash_command_descriptors)

        # TODO: Finish this
        
        url = "https://discord.com/api/v10/applications/%s/commands" % self.user.id

        for key, slash_command in self.slash_commands.items(): 

            # {"id":"0000","application_id":"000000","version":"00000","default_member_permissions":null,"type":1,"name":"blep","name_localizations":null,"description":"Send a random adorable animal photo","description_localizations":null,"dm_permission":true,"contexts":null,"integration_types":[0],"options":[{"type":3,"name":"wrapper","name_localizations":null,"description":"hi","description_localizations":null,"required":true,"choices":[{"name":"Dog","name_localizations":null,"value":"animal_dog"},{"name":"Cat","name_localizations":null,"value":"animal_cat"},{"name":"Penguin","name_localizations":null,"value":"animal_penguin"}]},{"type":5,"name":"only_smol","name_localizations":null,"description":"Whether to show only baby animals","description_localizations":null}],"nsfw":false}

            slash_name = key
            slash_desc = slash_command["desc"]
            params = slash_command["parameters"]
        
            opts = []

            for func, data in params.items():

                option_desc = "..."

                function_name = slash_command["org_func"].__name__

                print("FUNC NAME", function_name)

                if function_name in self.slash_command_descriptors:
                    if func in self.slash_command_descriptors[function_name]:
                        option_desc = self.slash_command_descriptors[function_name][func]

                print(f"SET OPTION DESCRIPTION TO", option_desc, "for", func)

                dtype = data[0]
                required = data[1]
                
                opts.append(
                    {
                        "name": func,
                        "description": option_desc,
                        "required": required,
                        "type": {bool:5,int:4,str:3,InteractionAttachment:11}[dtype]
                    }
                )

            opts = sorted(opts, key=lambda x: not x["required"])

            post_data = {
                "name": slash_name,
                "type": 1,
                "description": slash_desc,
                "options": opts
                    # "options": [
                    #     {
                    #         "name": "hi",
                    #         "description": "gaming",
                    #         "type": 3,
                    #         "required": True,
                    #         "choices": [
                    #             {
                    #                 "name": "Dog",
                    #                 "value": "animal_dog"
                    #             },
                    #             {
                    #                 "name": "Cat",
                    #                 "value": "animal_cat"
                    #             },
                    #             {
                    #                 "name": "Penguin",
                    #                 "value": "animal_penguin"
                    #             }
                    #         ]
                    #     },
                    #     {
                    #         "name": "only_smol",
                    #         "description": "Whether to show only baby animals",
                    #         "type": 5,
                    #         "required": False
                    #     }
                    # ]
            }

            headers = {
                "authorization": "Bot " + self._token
            }

            res = httpx.post(url, headers=headers, json=post_data)

            print(res.text)

    
    async def purge_all_slash_commands(self):
        # TODO: Finish this
        ...
    
    async def list_guilds(self, ids_only=True) -> list:
        async with httpx.AsyncClient() as client:
            headers = {
                'Authorization': f'Bot {self._token}'
            }

            res = await client.get(
                'https://discord.com/api/v10/users/@me/guilds',
                headers=headers
            )

            res = res.json()

            return [guild["id"] for guild in res]

    async def edit_pronouns(self, new_pronoun):
        guilds = await self.list_guilds(ids_only=True)

        headers = {
            "content-type": "application/json",
            "authorization": "Bot " + self._token
        }

        post_data = {
            "pronouns": new_pronoun
        }

        async with httpx.AsyncClient() as client:

            for gid in guilds:

                e = await client.patch(
                    "https://canary.discord.com/api/v10/guilds/%s/members/@me" % gid,
                    headers=headers,
                    json=post_data
                )

                print("RESPONSE", e.json(), "https://canary.discord.com/api/v10/guilds/%s/members/@me" % gid)

    async def update_profile_picture(self, new_profile_data: str = "", file: str = ""):

        if file:
            with open(file, "rb") as f:
                new_profile_data = f.read()

        types = {
            "png": "image/png",
            "apng": "image/apng",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "gif": "image/gif",
            "webp": "image/webp",
        }

        btype = types[file[::-1].split(".",1)[0][::-1].lower()]

        if btype == "image/gif":

            imagetools = __import__("ext.imagetools", fromlist=['*'])

            new_profile_data = imagetools.compress_gif_bytes(new_profile_data)

            del imagetools

        new_profile_data = base64.b64encode(new_profile_data).decode('utf-8')

        url = "https://discord.com/api/v10/users/@me"

        headers = {
            "Authorization": f"Bot {self._token}",
            "Content-Type": "application/json",
        }

        payload = {
            "avatar": "data:" + btype + ";base64," + new_profile_data,
        }

        async with httpx.AsyncClient() as client:
            response = await client.patch(url, headers=headers, json=payload, timeout=30)

            print("API RESPONSE", response.text)
