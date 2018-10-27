from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from instaparser.agents import Agent
from instaparser.entities import Account

import logging
import os
import os.path

agent = Agent()
account = Account("pravda.kp")

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TASK, POST, SUBSCR = range(3)


def start(bot, update):
    reply_keyboard = [['Го пост замутим, хулі', 'Скіки там подп, а']]

    update.message.reply_text(
        'Прівєт, підар\n\n'
        'І шо тобі нада, а?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return TASK


def task(bot, update):
    currentTask = update.message.text
    print(currentTask)
    if currentTask == 'Го пост замутим, хулі' or 'Давай ше пару штук їбанем':
        update.message.reply_text('Вобше безб\n\nДавай сюда свою спи***ну історію',
                                  reply_markup=ReplyKeyboardRemove())
        return POST


def post(bot, update):
    text = update.message.text

    img = Image.open("sample_in.jpg")
    lineHeight = 34
    boxSizes = [630, 1000]
    lines = []
    words = text.split()
    font = ImageFont.truetype("12144.ttf", 34)
    draw = ImageDraw.Draw(img)

    spaceWidth = font.getsize(' ')[0]
    currentLine = ''
    currentLineWidth = 0
    maxLineWidth = boxSizes[0]
    for word in words:
        w, h = font.getsize(word)
        currentLineWidth += (w + spaceWidth)
        # print(currentLine+word+str(currentLineWidth))
        if currentLineWidth < maxLineWidth:
            currentLine += word + ' '
        else:
            lines.append([currentLine, currentLineWidth - w])
            currentLineWidth = (w + spaceWidth)
            currentLine = word + ' '
    lines.append([currentLine, currentLineWidth])

    # print(lines)

    i = 0
    for line in lines:
        x = (boxSizes[0] - line[1]) / 2
        draw.text((345 + x, 220 + (i * lineHeight)), line[0], font=font, fill=(0, 0, 0))
        i += 1

    img.save('sample_out.jpg')
    # tmp = len([name for name in os.listdir('./images') if os.path.isfile(os.path.join('./images', name))])
    # img.save('images/' + str(tmp) + '.jpg')

    file = open('sample_out.jpg', 'rb')

    update.message.reply_text('Готово, лови свою хєрню')
    bot.send_document(update.message.chat_id, file)

    reply_keyboard = [['Давай ше пару штук їбанем', 'Нєа']]
    update.message.reply_text(
        'Доволєн?\n'
        'Шось ше нада?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return TASK


def subscr(bot, update):
    update.message.reply_text('Ща чекну, пожди секунду',
                              reply_markup=ReplyKeyboardRemove())

    agent.update(account)
    subscrCount = account.followers_count

    reply_keyboard = [['Го пост замутим, хулі', 'Нєа']]
    update.message.reply_text(str(subscrCount) + '\n\nШото ше нада?',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return TASK


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Ну і іди нахуй.\n\nЄслі передумаєш - тикай вот сюда ➡️ /start ',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("630625129:AAGGazo24G7QhhhnqupN5eLqS7v9ejEwdt4")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            TASK: [RegexHandler('^(Го пост замутим, хулі|Давай ше пару штук їбанем)$', task),
                   RegexHandler('^(Скіки там подп, а)$', subscr),
                   RegexHandler('^(Нєа)$', cancel)],

            POST: [MessageHandler(Filters.text, post)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
