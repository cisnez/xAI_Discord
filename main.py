# main.py
import os
import sys
import yaml
import asyncio
from openai import OpenAI
from B07_C0R3 import D15C0R6

# Bot name used for init file and Discord token
bot_name = sys.argv[1].lower()

# Get key and token from the OS environment
xai_api_key = os.getenv("XAI_API_KEY")
bot_discord_token = os.environ.get(f'DISCORD_TOKEN')

# Create xAI API Client
xai_client = OpenAI(
    api_key=xai_api_key,
    base_url="https://api.x.ai/v1",
)

# Coroutine to run a bot instance
async def run_bot(bot):
    try:
        await bot.start(bot.discord_token)
    except KeyboardInterrupt:
        await bot.close()

# Define function to run the main() coroutine
# Main function to create, configure and run the bot instances
async def run_bot_main():
    # Load all required YAML files to initialize Discord Bot.
    # Merge the global and child YAML files
    config_files = ["_init__global.yaml", f"_init_{bot_name}.yaml"]
    merged_config = merge_yaml_files(config_files)
    bot_init_data = merged_config
    # Create a new bot object using the YAML _init_bot file...
    # and the D15C0R6 constructor class from B07_C0R3.py
    bot = D15C0R6(xai_client, bot_discord_token, bot_init_data, bot_name)
   
    # Await the run_bot coroutine
    await run_bot(bot)

    # End the main method
    quit()

# Define function to merge global and personal configuration files
def merge_yaml_files(file_paths):
    merged_data = {}
    for file_path in file_paths:
        with open(file_path, "r", encoding='utf-8') as f:
            data = yaml.safe_load(f)
            for key, value in data.items():
                if key not in merged_data:
                    merged_data[key] = value
                else:
                    if value is None:  # If the value is None, do nothing.
                        pass
                    elif isinstance(value, list):
                        if merged_data[key] is None:
                            merged_data[key] = value
                        else:
                            merged_data[key] += value
                    elif isinstance(value, dict):
                        if merged_data[key] is None:
                            merged_data[key] = value
                        else:
                            merged_data[key].update(value)
                    else:  # If the value is not None, list, or dict, set the value.
                        merged_data[key] = value
    return merged_data

if __name__ == "__main__":
    asyncio.run(run_bot_main())
