import telebot

def is_member_chanel(chat_id, user_id, token):
    """
    True - подписан
    False - не подписан
    """
    bot = telebot.TeleBot(token)

    result = bot.get_chat_member(chat_id, user_id)

    try:
        if result.status == "member" or result.status == "owner" or result.status == "creator":
            return True
        else:
            return False
    except:
        return False