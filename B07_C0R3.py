# B07_C0R3.py
import logging
# Set logging.DEBUG to see ALL logs; set logging.INFO for less
logging.basicConfig(level=logging.INFO)

import asyncio
import openai
from discord.ext import commands as commANDs
from discord import Intents as InTeNTs
from discord import utils as UtIls

class D15C0R6(commANDs.Bot):
    def __init__(self, xai_client, discord_token, bot_init_data, bot_name):
        in_tents = InTeNTs(**bot_init_data["intents"])
        self.name = bot_name
        self.xai_client = xai_client
        self.xai_api_key = xai_client.api_key
        self.response_tokens = bot_init_data["response_tokens"]
        self.discord_token = discord_token
        self.command_prefix = bot_init_data["command_prefix"]
        
        # Assign all yaml values within the __init__ method
        self.ignored_prefixes = bot_init_data["ignored_prefixes"]
        self.username = bot_init_data["username"]
        self.gpt_model = bot_init_data["gpt_model"]
        self.home_channel_id = bot_init_data["home_channel_id"]
        self.self_channel_id = bot_init_data["self_channel_id"]
        self.self_author_id = bot_init_data["self_author_id"]
        self.self_author_name = bot_init_data["self_author_name"]
        self.bot_channel_id = bot_init_data["bot_channel_id"]
        self.hello_channel_id = bot_init_data["hello_channel_id"]
        # A set ensures that these collections only store unique elements
        self.allow_author_ids = set(bot_init_data["allow_author_ids"])
        self.allow_channel_ids = set(bot_init_data["allow_channel_ids"])
        self.ignore_author_ids = set(bot_init_data["ignore_author_ids"])
        self.ignore_channel_ids = set(bot_init_data["ignore_channel_ids"])
        #Set the first message in messages array
        self.messages = [{
        "role": "system", "content": f"You are my pithy friend. Keep your response under {self.response_tokens} tokens."
            }]
        # Parent class assignments for: super().__init__()
        super().__init__(command_prefix=self.command_prefix, intents=in_tents)

        # Set a variable for run_until_disconnected method
        self.should_continue = True

    async def close(self):
        await super().close()
    
    async def on_ready(self):
        logging.info(f"{self.user} is connected to Discord and ready to receive commands.")

    async def run_until_disconnected(self):
        while self.should_continue:
            try:
                await self.start(self.discord_token)
            except Exception as e:
                logging.info(f"Error: {e}")
            if self.should_continue:
                await asyncio.sleep(5)
            else:
                await self.wait_for("close")  # Wait for the close event to complete
    
    # If you define an on_message event, the bot will not process commands automatically unless you explicitly call `await self.process_commands(message)`. This is because the `on_message`` event is processed before the command, so if you don't call `process_commands`, the command processing stops at `on_message`.
    async def on_message(self, message):
        logging.debug(f'\n-- BEGIN ON_MESSAGE --')
        if message.channel.id in self.ignore_channel_ids:
            logging.info(f'Ignored Channel ID: {message.channel.name}\n')

        elif message.author.id in self.ignore_author_ids:
            logging.info(f'Ignoring message due to ignored author: {message.author.name}')

        elif any(message.content.startswith(prefix) for prefix in self.ignored_prefixes):
            for prefix in self.ignored_prefixes:
                if message.content.startswith(prefix):
                    logging.info(f'Ignoring message due to prefix: {prefix}\n')
                
        elif message.content.startswith('.delete') and (message.author.id in self.allow_author_ids):
            if message.reference:  # Check if the message is a reply
                try:
                    referenced_message = await message.channel.fetch_message(message.reference.message_id)
                    await referenced_message.delete()
                except Exception as e:
                    await message.channel.send(f"Error deleting message: {e}")
                    logging.error(f"Error deleting message: {e}")
            await message.delete()  # Delete the command message
        
        elif message.content.startswith('.hello'):
            logging.info('.hello')
            await message.channel.send("Hello Channel!")
        
        elif message.author.id in self.allow_author_ids:
            logging.info(f"Message from {message.author.name} received:\n{message.content}")
            # The bot will show as typing while executing the code inside this block
            # So place your logic that takes time inside this block
            async with message.channel.typing():
                # Remove bot's mention from the message
                clean_message = UtIls.remove_markdown(str(self.user.mention))
                prompt_without_mention = message.content.replace(clean_message, "").strip()
                prompt_without_mention = self.add_to_messages(prompt_without_mention, "user")
                # Add context to the prompt
                logging.debug(f"Sending usr_prompt to ChatGPT\n{prompt_without_mention}")
                logging.debug(f"Sending messages\n{self.messages}")
                response_text = self.get_gpt_response(self.messages, self.gpt_model, self.response_tokens, 2, 0.55)
                if response_text:
                    self.add_to_messages(response_text, "assistant")
                    logging.debug(f"Message history:\n{self.messages}")
                    await message.channel.send(response_text)
                else:
                    logging.error("No response from get_gpt_response")
        else:
            if (message.author.id != self.self_author_id):
                logging.info('message from else')
                logging.info(f'-----\n`message.author.name`: `{message.author.name}`\n`message.channel.id`: `{message.channel.id}`,\n`message.channel.name`: `{message.channel.name}`,\n`message.id`: `{message.id}`,\n`message.author.id`: `{message.author.id}`\n')
            else:
                logging.info = 'message from self . . . how did the code even get here !?'
                logging.info(f'-----\n`message.author.name`: `{message.author.name}`\n`message.channel.id`: `{message.channel.id}`,\n`message.channel.name`: `{message.channel.name}`,\n`message.id`: `{message.id}`,\n`message.author.id`: `{message.author.id}`\n')
        # Always process commands at the end of the on_message event
        await self.process_commands(message)
        logging.debug(f'\n-- END ON_MESSAGE --\n')

    def add_to_messages(self, message, role):
        if role == "assistant":
            self.messages.append({
                "role": "assistant",
                "content": message
            })
        elif role == "user":
            self.messages.append({
                "role": "user",
                "content": message
            })
        if len(self.messages) > 7:  # Keep 7 messages for example
            del self.messages[1:2]
        return self.messages

    def get_gpt_response(self, messages, model, max_response_tokens, n_responses, creativity):
        try:
            completions = self.xai_client.chat.completions.create(
                # "grok-beta" set in the init file
                model=model,
                messages = messages,  # from build_messages method
                # messages=[
                #     {"role": "system", "content": sys_prompt},
                #     {"role": "user", "content": usr_prompt},
                # ],
                max_tokens = max_response_tokens,
                n=n_responses,
                stop=None,
                # specifity < 0.5 > creativity
                temperature=creativity,
            )
            response = completions.choices[0].message.content
            return response
        except Exception as e:
            exception_error = (f"Error in get_gpt_response: {e}")
            logging.error(exception_error)
            return exception_error
