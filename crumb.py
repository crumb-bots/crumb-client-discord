# Discord API Config
GATEWAY = 'wss://gateway.discord.gg/?v=10&encoding=json'

# Modules
import json
import httpx
import websockets
import asyncio

from time import monotonic

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

    async def reply(self, content="", ephemeral=True):
        ENDPOINT = f"https://discord.com/api/v10/interactions/{self.interaction_id}/{self.token}/callback"

        # flags = 64 means ephemeral
        async with httpx.AsyncClient() as httpx_client:
            res = await httpx_client.post(
                url=ENDPOINT,
                json={
                    "type": 4,
                    "data": {
                        "content": content,
                        "flags": (64 if ephemeral else 0)
                    }
                }
            )


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

    async def send_in_channel(self, content=None):
        url = f"https://discord.com/api/v9/channels/{self.channel_id}/messages"
        headers = {"authorization": "Bot " + self._token}

        content = {
            "content": content,
            "allowed_mentions": {
                "parse": [],
            },
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=content)
            response.raise_for_status()
            return response
        
    async def reply(self, content=None, mention_author=True):
        url = f"https://discord.com/api/v9/channels/{self.channel_id}/messages"
        headers = {"authorization": "Bot " + self._token}
        content = {
            "content": content,
            "message_reference": {"message_id": self.id},
            "allowed_mentions": {
                "parse": [],
                "replied_user": mention_author,
            },
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=content)
            response.raise_for_status()
            return response

class Client(object):
    def get_pre(self):
        return f"<@{self.user.id}>"

    def __init__(self):
        self.events = {}
        self.commands = {}
        self.slash_commands = {}
        self.command_prefix = self.get_pre

    user:User
    latency:int

    _seq = None
    _websocket = None
    _heartbeat_interval = None
    _token = None
    _last_ping = None

    async def heartbeat(self):
        while True:

            payload = json.dumps({"op": 1, "d": self._seq})

            self._last_ping = monotonic()

            await self._websocket.send(payload)

            await asyncio.sleep(self._heartbeat_interval / 1000)

    async def run(self, token):
        print("Connecting to gateway...")
        self._token = token
        async with websockets.connect(GATEWAY) as websocket:
            self._websocket = websocket
            response = await websocket.recv()
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
                    "intents": 55936
                }
            }

            await websocket.send(json.dumps(payload))

            print("Client Authenticated")
            while True:
                response = await websocket.recv()
                response = json.loads(response)

                if response["op"] == 11:
                    self.latency = (monotonic() - self._last_ping) / 2

                elif "t" in response:

                    event_type = response["t"]
                    event_data = response["d"]

                    # print(event_type, event_data)

                    if event_type == "READY":
                        
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
                                display_name=event_data["author"]["username"]
                            )

                            message = Message(
                                id = event_data["id"],
                                author=author,
                                channel_id=channel_id,
                                content=event_data["content"],
                                token=self._token
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

                        await self.dispatch_slash(event_data['data']['name'], interaction)

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

    def slash(self, name, desc, *args, **kwargs):
        def decorator(func):
            async def wrapper(context, *args, **kwargs):
                result = await func(context, *args, **kwargs)
                return result
            
            self.slash_commands[name] = {"func": wrapper, "desc": desc}
            return wrapper
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
        # TODO: Finish this
        
        url = "https://discord.com/api/v10/applications/%s/commands" % self.user.id

        for key, slash_command in self.slash_commands.items(): 

            # {"id":"1206834813538017300","application_id":"1203803535372976229","version":"1206834813538017301","default_member_permissions":null,"type":1,"name":"blep","name_localizations":null,"description":"Send a random adorable animal photo","description_localizations":null,"dm_permission":true,"contexts":null,"integration_types":[0],"options":[{"type":3,"name":"wrapper","name_localizations":null,"description":"hi","description_localizations":null,"required":true,"choices":[{"name":"Dog","name_localizations":null,"value":"animal_dog"},{"name":"Cat","name_localizations":null,"value":"animal_cat"},{"name":"Penguin","name_localizations":null,"value":"animal_penguin"}]},{"type":5,"name":"only_smol","name_localizations":null,"description":"Whether to show only baby animals","description_localizations":null}],"nsfw":false}



            slash_name = key
            slash_desc = slash_command["desc"]

        
            post_data = {
                "name": slash_name,
                "type": 1,
                "description": slash_desc,
                "options": [
                    {
                        "name": "hi",
                        "description": "gaming",
                        "type": 3,
                        "required": True,
                        "choices": [
                            {
                                "name": "Dog",
                                "value": "animal_dog"
                            },
                            {
                                "name": "Cat",
                                "value": "animal_cat"
                            },
                            {
                                "name": "Penguin",
                                "value": "animal_penguin"
                            }
                        ]
                    },
                    {
                        "name": "only_smol",
                        "description": "Whether to show only baby animals",
                        "type": 5,
                        "required": False
                    }
                ]
            }

            headers = {
                "authorization": "Bot " + self._token
            }

            res = httpx.post(url, headers=headers, json=post_data)

            print(res.text)

    
    async def purge_all_slash_commands(self):
        # TODO: Finish this
        ...
    
    async def list_guilds(self) -> list:
        # TODO: Finish this
        ...

    async def edit_pronouns(self, new_pronoun):
        guilds = await self.list_guilds()

        headers = {
            "content-type": "application/json",
            "authorization": "Bot " + self._token
        }

        post_data = {
            "pronoun": new_pronoun
        }

        for gid in guilds:

            httpx.patch(
                "https://canary.discord.com/api/v9/guilds/%s/members/@me" % gid,
                headers=headers,
                json=post_data
            )

    async def send_voice_message(self, channel_id):
        # TODO: Finish this
        ...

    async def _to_raw_bytes(self, url):
        # TODO: Finish this
        ...

    async def update_profile_picture(self, new_profile_data:str):
        if new_profile_data.startswith("http"):
            new_profile_data = await self._to_raw_bytes(new_profile_data)
        
        # TODO: Finish this
