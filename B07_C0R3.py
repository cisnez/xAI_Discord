# B07_C0R3.py
import asyncio
from colorama import Fore
import logging
from discord.ext import commands as commANDs
from discord import Intents as InTeNTs
from discord import utils as UtIls
from discord import errors

class D15C0R6(commANDs.Bot):
    def __init__(self, xai_client, discord_token, bot_init_data, bot_name):
        self.name = bot_name
        self.xai_client = xai_client
        self.response_tokens = bot_init_data["response_tokens"]
        self.discord_token = discord_token
        self.command_prefix = bot_init_data["command_prefix"]
        
        # Assign all yaml values within the __init__ method
        self.ignored_prefixes = bot_init_data["ignored_prefixes"]
        self.llm_model = bot_init_data["llm_model"]
        self.system_message = [{"role": "system", "content": bot_init_data["system_message"]}]
        self.home_channel_id = bot_init_data["home_channel_id"]
        # A set ensures that these collections only store unique elements
        self.allow_author_ids = set(bot_init_data["allow_author_ids"])
        self.allow_channel_ids = set(bot_init_data["allow_channel_ids"])
        self.ignore_author_ids = set(bot_init_data["ignore_author_ids"])
        self.ignore_channel_ids = set(bot_init_data["ignore_channel_ids"])
        # Create a messages dictionary
        self.messages_by_channel = {}
        # Parent class assignments for: super().__init__()
        in_tents = InTeNTs(**bot_init_data["intents"])
        super().__init__(command_prefix=self.command_prefix, intents=in_tents)

    async def close(self):
        await super().close()
    
    async def on_connect(self):
        logging.info(f"{self.user} has connected to Discord.")

    async def on_disconnect(self):
        logging.info(f"{self.user} has disconnected from Discord.")

    async def on_ready(self):
        logging.info(f"{self.user} ready to receive commands.")

    async def on_resumed(self):
        logging.info(f"{self.user} has reconnected to Discord; ready to receive commands.")

    # If you define an on_message event, the bot will not process commands automatically unless you explicitly call `await self.process_commands(message)`. This is because the `on_message`` event is processed before the command, so if you don't call `process_commands`, the command processing stops at `on_message`.
    async def on_message(self, message):
        logging.debug(f"\n-- BEGIN ON_MESSAGE --")

        if message.author == self.user:
            logging.info("Ignoring message from self...")

        elif message.channel.id in self.ignore_channel_ids:
            logging.info(f"Ignored Channel ID: {message.channel.name}\n")

        elif message.author.id in self.ignore_author_ids:
            logging.info(f"Ignoring message due to ignored author: {message.author.name}")
 
        elif message.content.startswith(".delete") and (message.author.id in self.allow_author_ids):
            if message.reference:  # Check if the message is a reply
                try:
                    referenced_message = await message.channel.fetch_message(message.reference.message_id)
                    if referenced_message.author == self.user:
                        await referenced_message.delete()
                        logging.info(f"Deleted message from self, ID: {referenced_message.author.id}.")
                        # await message.delete()  # Delete the command message
                        # logging.info(f"Deleted command meessage from: {message.author.id}.")
                    else:
                        logging.info(f"Delete request for other user ID: {referenced_message.author.id}.")
                except Exception as e:
                    await message.channel.send(f"Error deleting message: {e}")
                    logging.error(f"Error deleting message: {e}")
        
        elif message.content.startswith(".hello"):
            logging.info(".hello")
            await message.channel.send("Hello Channel!")

        elif message.content.startswith('.pin') and (message.author.id in self.allow_author_ids):
            await self.handle_message_pin(message, action='pin')
 
        elif message.content.startswith('.unpin') and (message.author.id in self.allow_author_ids):
            await self.handle_message_pin(message, action='unpin')

        elif message.content.startswith('.guilds'):
            await self.list(message)

        elif message.content.startswith('.leave') and (message.author.id in self.allow_author_ids):
            await self.leave(message)

        elif message.content.startswith('.delete') and (message.author.id in self.allow_author_ids):
            if message.reference:  # Check if the message is a reply
                await self.delete_referenced_message(message)
            else:
                await message.channel.send('What message do you want me to delete?')

        elif message.content.startswith(".shutdown") and (message.author.id in self.allow_author_ids):
            await message.channel.send("Shutting down...")
            await self.close()
            logging.info(".shutdown command executed.")

        elif any(message.content.startswith(prefix) for prefix in self.ignored_prefixes):
            logging.debug(self.ignored_prefixes)
            for prefix in self.ignored_prefixes:
                if message.content.startswith(prefix):
                    logging.info(f"Ignoring message due to prefix: {prefix}\n")

        elif message.channel.id in self.allow_channel_ids or self.user in message.mentions:
            logging.info(f"\nMessage from {message.author.name} received:\n{message.content}\n")
            # The bot will show as typing while executing the code inside this block
            # So place your logic that takes time inside this block
            member = message.author
            nickname = member.nick if member.nick is not None else member.display_name
            async with message.channel.typing():
                messages = self.add_to_messages(message.channel.id, nickname, message.content, "user")
                # Add context to the prompt
                logging.debug(f"\nSending usr_prompt to Grok\n{messages}\n")
                response_text = self.get_response(messages, self.llm_model, self.response_tokens, 1, 0.55)
                if response_text:
                    self.add_to_messages(message.channel.id, self.name, response_text, "assistant")
                    logging.debug(f"\nMessage history:\n{self.messages_by_channel[message.channel.id]}\n")
                    await message.channel.send(response_text)
                else:
                    logging.error("No response from get_response")

        else:
            logging.info(f"-----\n`message.author.name`: `{message.author.name}`\n`message.channel.id`: `{message.channel.id}`,\n`message.channel.name`: `{message.channel.name}`,\n`message.id`: `{message.id}`,\n`message.author.id`: `{message.author.id}`")

        # Always process commands at the end of the on_message event
        await self.process_commands(message)
        logging.debug(f"\n-- END ON_MESSAGE --\n")

    def add_to_messages(self, channel, nickname, message, role):
        if channel not in self.messages_by_channel:
           self.messages_by_channel[channel] = []
           self.messages_by_channel[channel].extend(self.system_message)
        if role == "assistant":
            self.messages_by_channel[channel].append({
                "role": "assistant",
                "content": f"{message}"
            })
        elif role == "user":
            self.messages_by_channel[channel].append({
                "role": "user",
                "content": f"{nickname} says, `{message}`"
            })
        if len(self.messages_by_channel[channel]) > 11:  # Keep 7 messages for example
            self.messages_by_channel[channel].pop(1)
        return self.messages_by_channel[channel]

    def get_response(self, messages, model, max_response_tokens, n_responses, creativity):
        try:
            completions = self.xai_client.chat.completions.create(
                # "grok-beta" set in the init file
                model=model,
                # messages=[
                #     {"role": "system", "content": sys_prompt},
                #     {"role": "user", "content": usr_prompt},
                # ],
                messages = messages,  # from build_messages method
                max_tokens = max_response_tokens,
                n=n_responses,
                stop=None,
                # specifity < 0.5 > creativity
                temperature=creativity,
            )
            response = completions.choices[0].message.content
            return response
        except Exception as e:
            exception_error = (f"Error in get_response: {e}")
            logging.error(exception_error)
            return exception_error

    async def handle_message_pin(self, message, action):
        if message.reference:
            try:
                replied_message = await message.channel.fetch_message(message.reference.message_id)
                logging.info(f'{Fore.YELLOW}{action.capitalize()}ning Message: {Fore.CYAN}{replied_message.content}')
                if action == 'pin':
                    await replied_message.pin()
                else:  # action == 'unpin'
                    await replied_message.unpin()
            except errors.Forbidden:
                await message.channel.send(f"I don't have permission to {action} that message.")  # Notify the user in the channel
                logging.error(f"{Fore.YELLOW}Failed to {Fore.RED}{action} {Fore.YELLOW}message due to Error:\n{Fore.RED}Forbidden error (50013): Missing Permissions")
            except Exception as e:  # Optional: Catch other unexpected errors for robustness
                logging.error(f"{Fore.RED}An unexpected error occurred while {Fore.GREEN}{action}ning the message: {Fore.RED}{e}")
                await message.channel.send(f"Something went wrong while trying to {action} the message. Please check logs.")
        else:
            await message.channel.send(f'Please reply to a message to {action} it.')

    async def list(self, message):
        guilds = self.guilds  # Get the list of guilds
        if guilds:  # Check if there are any guilds
            guild_list = []  # Create a list to store formatted strings
            for guild in guilds:
                guild_list.append(f"{guild.name} (ID: {guild.id})")  # Format as "Name (ID: 123456789012345678)"
            await message.channel.send(f"**Guilds:**\n{'\n'.join(guild_list)}")  # Send as a multi-line string
        else:
            await message.channel.send("No guilds found.")
    
    async def leave(self, message):
        try:
            parts = message.content.split()
            if len(parts) < 2:
                await message.channel.send("Usage: .leave <server_id>")
                return
            server_id = int(parts[1])
            guild = self.get_guild(server_id)
            if guild:
                await guild.leave()
                await message.channel.send(f"Successfully left the guild: {guild.name}")
            else:
                await message.channel.send("I'm not in that guild or the ID is invalid.")
        except ValueError:
            await message.channel.send("Invalid server ID. Please provide a valid numeric ID.")
        except Exception as e:
            await message.channel.send(f"An error occurred: {str(e)}")

    async def delete_referenced_message(self, message):
        try:
            referenced_message = await message.channel.fetch_message(message.reference.message_id)
            logging.info(f'{Fore.YELLOW}Deleting message by: {Fore.BLUE}{referenced_message.author}.')
            await referenced_message.delete()
        except Exception as e:
            await message.channel.send(f'Error deleting message: {e}')
            logging.error(f'{Fore.YELLOW}Error deleting message: {Fore.RED}{e}')
