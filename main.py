import os
import re

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, Filters, MessageHandler, Updater)

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

TRANSLIT_RU_EN = {
    'а': 'a',
    'б': 'b',
    'в': 'v',
    'г': 'g',
    'д': 'd',
    'е': 'e',
    'ё': 'yo',
    'ж': 'zh',
    'з': 'z',
    'и': 'i',
    'й': 'j',
    'к': 'k',
    'л': 'l',
    'м': 'm',
    'н': 'n',
    'о': 'o',
    'п': 'p',
    'р': 'r',
    'с': 's',
    'т': 't',
    'у': 'u',
    'ф': 'f',
    'х': ('h', 'kh'),
    'ц': 'c',
    'ч': 'ch',
    'ш': 'sh',
    'щ': 'shch',
    'ъ': '',
    'ы': 'y',
    'ь': '',
    'э': 'eh',
    'ю': 'yu',
    'я': 'ya',
    ' ': ' ',
}

x_change = ('k', 'z', 'c', 's', 'e', 'h')


def translit_ru_to_eng(phrase: str):
    phrase_list = list(phrase.lower().strip())
    translited_phrase = []
    for symbol in phrase_list:
        if symbol in TRANSLIT_RU_EN.keys():
            if symbol != 'х':
                translit_symbol = TRANSLIT_RU_EN[symbol]
                translited_phrase.append(translit_symbol)
            else:
                if translited_phrase[:-2:-1] in x_change:
                    translit_symbol = TRANSLIT_RU_EN[symbol][1]
                    translited_phrase.append(translit_symbol)
                else:
                    translit_symbol = TRANSLIT_RU_EN[symbol][0]
                    translited_phrase.append(translit_symbol)
        elif re.findall(r'\d+', symbol):
            translited_phrase.append(symbol)

    result = ''.join(translited_phrase)

    return result


def space_replace(phrase: str):
    phrase_list = list(phrase.lower().strip())
    full_phrase = []
    for symbol in phrase_list:
        if re.findall(r' ', symbol):
            new_symbol = '-'
            full_phrase.append(new_symbol)
        else:
            full_phrase.append(symbol)

    result = ''.join(full_phrase)

    return result


def dash_replace(phrase: str):
    phrase_list = list(phrase.lower().strip())
    full_phrase = []
    for symbol in phrase_list:
        if re.findall(r'-', symbol):
            new_symbol = ' '
            full_phrase.append(new_symbol)
        else:
            full_phrase.append(symbol)

    result = ''.join(full_phrase)

    return result


def get_keyboard_space_replace():
    keyboard = [
        [
            InlineKeyboardButton(
                'Заменить пробел на тире "-"', callback_data='button_space'
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


def get_keyboard_dash_replace():
    keyboard = [
        [
            InlineKeyboardButton(
                'Заменить тире "-" на пробел', callback_data='button_dash'
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


def keyboard_callback_handler(
    update: Update, context: CallbackContext, chat_data=None, **kwargs
):
    query = update.callback_query
    data = query.data

    current_text = update.effective_message.text

    if data == 'button_space':
        query.edit_message_text(
            text=space_replace(current_text),
            reply_markup=get_keyboard_dash_replace(),
        )
    elif data == 'button_dash':
        query.edit_message_text(
            text=dash_replace(current_text),
            reply_markup=get_keyboard_space_replace(),
        )


def command_start_handler(update: Update, context: CallbackContext):
    update.message.reply_text(
        text=(
            'Это простой бот, который поможет провести транслитерацию '
            'из кириллицы в латиницу по правилам Яндекса.'
        )
    )


def text_handler(update: Update, context: CallbackContext):
    update.message.reply_text(
        text=translit_ru_to_eng(update.message.text),
        reply_markup=get_keyboard_space_replace(),
    )


def main():
    updater = Updater(
        token=TELEGRAM_TOKEN,
        use_context=True,
    )

    updater.dispatcher.add_handler(
        CommandHandler(command='start', callback=command_start_handler)
    )
    updater.dispatcher.add_handler(
        MessageHandler(filters=Filters.text, callback=text_handler)
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(
            callback=keyboard_callback_handler, pass_chat_data=True
        )
    )

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
