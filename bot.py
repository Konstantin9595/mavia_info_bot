from telethon import TelegramClient, events, types, Button

import dotenv
import logging
import json
import re

ENV_PATH = '.env'
API_ID = dotenv.get_key(ENV_PATH, 'API_ID')
API_HASH = dotenv.get_key(ENV_PATH, 'API_HASH')
BOT_TOKEN = dotenv.get_key(ENV_PATH, 'BOT_TOKEN')

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.WARNING)

bot = TelegramClient('mavia_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

bot_reply_lang = {
    "lang": "en"
}

def get_section_by_lang(lang):
    with open('./commands/commands.json', encoding='utf-8') as f:
        command_list = json.loads(f.read())

    return command_list.get(lang)

def get_commands():
    command_sections = get_section_by_lang(bot_reply_lang.get("lang"))
    commands = command_sections.get('commands')

    return list(set(map(lambda command: command.get('command'), commands)))


def get_command_full_desc(type):
    command_sections = get_section_by_lang(bot_reply_lang.get("lang"))
    type = re.sub("\/", "", type)

    return command_sections.get('full_command_desc').get(type)

def get_help_commands():
    section = get_section_by_lang(bot_reply_lang.get("lang"))
    commands = section.get('commands')
    title =  "\n**{}**\n".format(section.get('title'))

    reply_massage = [title]

    for command in commands:
        desc = "{} - {}\n".format(command.get("command"), command.get("short_desc"))
        reply_massage = [*reply_massage, desc]

    return ''.join(reply_massage)


# Initial start command
@bot.on(events.NewMessage(pattern="/start"))
async def start_command_handler(event):
    sender = await event.get_input_sender()

    buttons = bot.build_reply_markup([
        Button.text("🇬🇧", resize=True, single_use=True),
        Button.text("🇷🇺", resize=True, single_use=True)
    ])

    await bot.send_message(sender, 'Chose your primary language', buttons=buttons)

# language switcher
@bot.on(events.NewMessage(pattern=lambda lang: lang in ["🇬🇧", "🇷🇺"]))
async def any(event):
    sender = await event.get_input_sender()
    lang = event.raw_text

    lang_dict = {
        "🇬🇧": "en",
        "🇷🇺": "ru"
    }

    bot_reply_lang['lang'] = lang_dict.get(lang)

    await bot.send_message(sender, get_help_commands())

# Help command (show all list of commands)    
@bot.on(events.NewMessage(pattern='/help'))
async def help_command_handler(event):
    sender = await event.get_input_sender()

    await bot.send_message(sender, get_help_commands())

# Handle each command from commands.json
@bot.on(events.NewMessage(pattern=lambda command: command in get_commands() ))
async def commands_handler(event):
    sender = await event.get_sender()
    command = event.raw_text
    command_desc = get_command_full_desc(command)
    
    await bot.send_message(sender, command_desc)

bot.run_until_disconnected()
