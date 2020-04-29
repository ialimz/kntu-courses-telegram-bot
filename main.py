import bot_states as states
import bot_handlers as handlers

from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)


not_back_patter = '^(?!back$).*$'
back_pattern = 'back'


def main():
    setup_bot()


def setup_bot():
    updater = Updater('1211259965:AAEyefnhcd-llrS9g45tzxfFmL4gWZLybn0', use_context=True)

    dp = updater.dispatcher

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', handlers.start_bot)],

        states={
            states.ENTERING_USERNAME: [MessageHandler(Filters.text, handlers.enter_password)],

            states.ENTERING_PASSWORD: [MessageHandler(Filters.text, handlers.login_user)],

            states.LOGIN_FINISHED: [CallbackQueryHandler(handlers.select_course)],

            states.SELECTING_COURSE: [CallbackQueryHandler(handlers.show_selected_course_topics)],

            states.SELECTING_TOPIC: [CallbackQueryHandler(handlers.selecting_activity, pattern=not_back_patter),
                                     CallbackQueryHandler(handlers.select_course, pattern=back_pattern)],

            states.SELECTING_TOPIC_ACTIVITY: [CallbackQueryHandler(handlers.show_topic_activity, pattern=not_back_patter),
                                              CallbackQueryHandler(handlers.show_selected_course_topics, pattern=back_pattern)],

            states.SHOWING_TOPIC_ACTIVITY: [CallbackQueryHandler(handlers.show_topic_activity, pattern=not_back_patter),
                                            CallbackQueryHandler(handlers.show_selected_course_topics, pattern=back_pattern)]

        },

        fallbacks=[CommandHandler('cancel', handlers.cancel)]
    )

    dp.add_handler(conversation_handler)
    dp.add_error_handler(handlers.error)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
