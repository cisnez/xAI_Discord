# main.py
import os
import sys
import asyncio
from openai import OpenAI
from B07_C0R3 import D15C0R6
from B07_Y4M7 import merge_yaml_files

# Bot name used for init file and Discord token
bot_name = sys.argv[1].lower()

# Get key and token from the OS environment
xai_api_key = os.getenv("XAI_API_KEY")
bot_discord_token = os.environ.get(f'{bot_name.upper()}_TOKEN')

# Create xAI API Client
xai_client = OpenAI(
    api_key=xai_api_key,
    base_url="https://api.x.ai/v1",
)

# Coroutine to run a bot instance
async def run_bot(bot):
    await bot.start(bot.discord_token)

# Define function to run the main() coroutine
# Main function to create, configure and run the bot instances
async def bot_main():
    # Load all required YAML files to initialize Discord Bot.
    # Merge the global and child YAML files
    config_files = ["_init__global.yaml", f"_init_{bot_name}.yaml"]
    bot_init_data = merge_yaml_files(config_files)
    # Create a new bot object using the YAML _init_bot file...
    # and the D15C0R6 constructor class from B07_C0R3.py
    bot = D15C0R6(xai_client, bot_discord_token, bot_init_data, bot_name)
   
    # Create the run_bot asyncio task
    bot_task = asyncio.create_task(run_bot(bot))

    while not bot_task.done():
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(bot_main())
