# Ω*
#               ■          ■■■■■  
#               ■         ■■   ■■ 
#               ■        ■■     ■ 
#               ■        ■■       
#     ■■■■■     ■        ■■■      
#    ■■   ■■    ■         ■■■     
#   ■■     ■■   ■          ■■■■   
#   ■■     ■■   ■            ■■■■ 
#   ■■■■■■■■■   ■              ■■■
#   ■■          ■               ■■
#   ■■          ■               ■■
#   ■■     ■    ■        ■■     ■■
#    ■■   ■■    ■   ■■■  ■■■   ■■ 
#     ■■■■■     ■   ■■■    ■■■■■


# -- Imports --------------------------------------------------------------------------

import discord
from moca_config import MocaConfig
from moca_core import get_children_file_list
from pathlib import Path
from moca_bot import MocaBot

# -------------------------------------------------------------------------- Imports --

# -- Variables --------------------------------------------------------------------------

bot_config = MocaConfig('bot_config', Path(__file__).parent, 'bot_config.json', reload_interval=-1)

TOKEN = bot_config.get('token', str, '')

debug = bot_config.get('debug', bool, False)

show_responder = bot_config.get('show_responder', bool, False)

client = discord.Client()

shirotako_bot = MocaBot('shirotako')

# -------------------------------------------------------------------------- Variables --

# -- Setup Bot --------------------------------------------------------------------------

for data_file in get_children_file_list(Path(__file__).parent.joinpath('twitter_data')):
    shirotako_bot.study_from_file(data_file, True)

# -------------------------------------------------------------------------- Setup Bot --

# -- Main --------------------------------------------------------------------------


@client.event
async def on_ready():
    print('しろたこちゃんDiscordボット、バージョン0.0.1起動しました。')


@client.event
async def on_message(message):
    try:
        if message.author.bot:
            return None
        elif message.content.startswith('#mendako#'):
            response = shirotako_bot.dialogue(message.content[9:])
            if show_responder:
                await message.channel.send(f'{shirotako_bot.responder_name}: {response}')
            else:
                await message.channel.send(response)
            if debug:
                print(f'メッセージ受信: {message.content[9:]}')
                print(f'返事: {response}')
        elif message.content.startswith('#shirotako#'):
            response = shirotako_bot.dialogue(message.content[11:])
            if show_responder:
                await message.channel.send(f'{shirotako_bot.responder_name}: {response}')
            else:
                await message.channel.send(response)
            if debug:
                print(f'メッセージ受信: {message.content[9:]}')
                print(f'返事: {response}')
        elif client.user in message.mentions:
            response = shirotako_bot.dialogue(message.content[message.content.find('>') + 1:])
            if show_responder:
                await message.channel.send(f'{message.author.mention} {shirotako_bot.responder_name}: {response}')
            else:
                await message.channel.send(f'{message.author.mention} {response}')
            if debug:
                print(f'メンション受信: {message.content.find(">") + 1:]}')
                print(f'返事: {response}')
    except Exception:
        pass

client.run(TOKEN)

# -------------------------------------------------------------------------- Main --
