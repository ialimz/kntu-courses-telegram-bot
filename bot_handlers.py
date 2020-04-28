import os
import selenium_utils as sel_util
import bot_states as states
import bot_logger

from telegram.ext import ConversationHandler
from telegram.ext.dispatcher import run_async
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


@run_async
def start_bot(update, context):
    context.user_data['browser'] = sel_util.setup_selenium()
    update.message.reply_text('نام کاربری(ایمیل):')
    return states.ENTERING_USERNAME


def enter_password(update, context):
    user_data = context.user_data
    user_data['username'] = update.message.text
    update.message.reply_text('رمز عبور:')
    return states.ENTERING_PASSWORD


def login_user(update, context):
    user_data = context.user_data
    user_data['password'] = update.message.text
    browser = user_data['browser']
    sel_util.open_courses_login(browser)
    username = user_data['username']
    password = user_data['password']
    sel_util.login(browser, username, password)
    items = [('انتخاب درس', 'select_course')]
    markup = keyboards_markup(items, False)
    update.message.reply_text('گزینه مورد نظر را انتخاب کنید:', reply_markup=markup)
    return states.LOGIN_FINISHED


def select_course(update, context):
    browser = context.user_data['browser']
    sel_util.open_course_home(browser)
    courses = sel_util.find_courses(browser)
    markup = keyboards_markup(courses, False)
    if update.callback_query is not None:
        update.callback_query.answer()
        update.callback_query.edit_message_text('درس مورد نظر را انتخاب کنید:', reply_markup=markup)
    else:
        update.message.reply_text('درس مورد نظر را انتخاب کنید:', reply_markup=markup)
    return states.SELECTING_COURSE


def show_selected_course_topics(update, context):
    browser = context.user_data['browser']
    query = update.callback_query
    query.answer()
    if query.data != 'back':
        context.user_data['course_link'] = query.data

    link = context.user_data['course_link']
    topics = sel_util.find_topics(browser, link)
    markup = keyboards_markup(topics, True)
    query.edit_message_text(text='موضوع مورد نظر را انتخاب کنید:', reply_markup=markup)
    return states.SELECTING_TOPIC


def selecting_activity(update, context):
    browser = context.user_data['browser']
    query = update.callback_query
    query.answer()
    topic_id = query.data

    activities = sel_util.topic_activities(browser, topic_id)
    markup = keyboards_markup(activities, True)
    query.edit_message_text(text='یک گزینه را انتخاب کنید:', reply_markup=markup)
    return states.SELECTING_TOPIC_ACTIVITY


def show_topic_activity(update, context):
    browser = context.user_data['browser']
    query = update.callback_query
    query.answer()
    link = query.data
    mod = link.split('mod/')[1].split('/view')[0]

    def resource():
        path = sel_util.download_resource(browser, link)[0]
        context.bot.send_document(chat_id=query.message.chat.id, document=open(path, 'rb'))
        os.remove(path)
        sel_util.clear_recent_downloads(browser)

    def assign():
        status = sel_util.get_assignment_status(browser, link)
        query.message.reply_text(status, parse_mode='HTML')

    def forum():
        query.message.reply_text('<b‌>بخش تالار اخبار به زودی فعال می‌شود</b>', parse_mode='HTML')

    switcher = {
        'resource': resource,
        'assign': assign,
        'forum': forum
    }

    switcher[mod]()

    return states.SHOWING_TOPIC_ACTIVITY


def cancel(update, context):
    user_data = context.user_data
    user_data.clear()
    return ConversationHandler.END


def error(update, context):
    bot_logger.logger.warning('Update "%s" caused error "%s"', update, context.error)


def keyboards_markup(items, should_add_back):
    keyboard = []
    for item in items:
        keyboard.append([InlineKeyboardButton(item[0], callback_data=item[1])])
    reply_markup = InlineKeyboardMarkup(keyboard)
    if should_add_back:
        keyboard.append([InlineKeyboardButton('بازگشت', callback_data='back')])
    return reply_markup
