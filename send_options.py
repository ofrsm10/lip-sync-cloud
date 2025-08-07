import requests
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from lambda_function import chat_id, gender, get_file_url, state
from texts import CONFIG, VIP_USER_CALIB, VIP_USER_SENTENCE, MALE, FEMALE, ACCENT1, ACCENT2, ACCENT3, ACCENT4, ACCENT5, \
    ACCENT6, ACCENT7, OK_TERMS, OK_NTH, IM_DONE, OK_TERMS_FEMALE, QUIT, WHAT, RESET, BRIEF1, LETSTART, TOKEN, \
    DEMO1_VIDEO_ID, DEMO2_VIDEO_ID, INITIAL_VIP_USER, ASK_PLACE, ASK_COLOR, ASK_INTENSITY, ASK_STEP, CALIB_INSTRUCTIONS, \
    GET_SENTENCE_INSTRUCTIONS, RECEIVED_VIDEO, ASK_GENDER, OFFER_BRIEF, OFFER_BRIEF_FEMALE, BRIEF_TEXT, \
    BRIEF_TEXT_FEMALE, TERMS_TEXT, TERMS_TEXT_FEMALE, ASK_ACCENT, ASK_ACCENT_FEMALE, ASK_ACCENT_SPECIFIC, \
    ASK_ACCENT_SPECIFIC_FEMALE, FIRST_VIDEO_TEXT2, FIRST_VIDEO_TEXT2_FEMALE, ASK_NTH_VIDEO, ASK_NTH_VIDEO_FEMALE, \
    GOODBYE_TEXT, GOODBYE_TEXT_FEMALE, WRONG_ACTION_TEXT, WRONG_REPLY_TEXT


async def send_vip_user_sentence_video_instructions(sentence):
    bot = Bot(TOKEN)
    await bot.send_message(chat_id, text=f"*צלם את עצמך חוזר אחרי המשפט: {sentence}*", parse_mode='Markdown')


async def send_vip_user_sentence_instructions():
    bot = Bot(TOKEN)
    await bot.send_message(chat_id, text=GET_SENTENCE_INSTRUCTIONS, parse_mode='Markdown')


async def send_vip_user_menu():
    button_option_a = InlineKeyboardButton(VIP_USER_CALIB, callback_data=VIP_USER_CALIB)
    button_option_b = InlineKeyboardButton(VIP_USER_SENTENCE, callback_data=VIP_USER_SENTENCE)

    keyboard = [[button_option_a],
                [button_option_b]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    bot = Bot(TOKEN)
    await bot.send_message(chat_id=chat_id, text=ASK_STEP, reply_markup=reply_markup, parse_mode='Markdown')


async def send_initial_vip_user():
    bot = Bot(TOKEN)
    await bot.send_message(chat_id=chat_id, text=INITIAL_VIP_USER, parse_mode='Markdown')


async def send_place_question():
    bot = Bot(TOKEN)
    await bot.send_message(chat_id=chat_id, text=ASK_PLACE, parse_mode='Markdown')


async def send_vip_user_calib_instructions():
    bot = Bot(TOKEN)
    await bot.send_message(chat_id=chat_id, text=CALIB_INSTRUCTIONS, parse_mode='Markdown')


async def send_lighting_color_question():
    bot = Bot(TOKEN)
    await bot.send_message(chat_id=chat_id, text=ASK_COLOR, parse_mode='Markdown')


async def send_lighting_intensity_question():
    bot = Bot(TOKEN)
    await bot.send_message(chat_id=chat_id, text=ASK_INTENSITY, parse_mode='Markdown')


async def send_vip_user_goodbye():
    bot = Bot(TOKEN)
    await bot.send_message(chat_id=chat_id, text=RECEIVED_VIDEO, parse_mode='Markdown')


async def send_briefing_menu():
    print("Sending Brief menu..")
    bot = Bot(TOKEN)
    button_option_a = InlineKeyboardButton(BRIEF1, callback_data=BRIEF1)
    # button_option_b = InlineKeyboardButton(BRIEF2, callback_data=BRIEF2)
    # button_option_c = InlineKeyboardButton("ספר לי עוד על הפרויקט", callback_data=BRIEF3)
    button_option_d = InlineKeyboardButton(LETSTART, callback_data=LETSTART)

    keyboard = [[button_option_a], [button_option_d]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = OFFER_BRIEF
    if gender == FEMALE:
        text = OFFER_BRIEF_FEMALE
    await bot.send_message(chat_id=chat_id,
                           text=text,
                           reply_markup=reply_markup, parse_mode='Markdown')


async def send_brief():
    print("Sending brief message..")
    bot = Bot(TOKEN)
    # button_option_a = InlineKeyboardButton(BRIEF1, callback_data=BRIEF1)
    # button_option_b = InlineKeyboardButton(BRIEF2, callback_data=BRIEF2)
    # button_option_c = InlineKeyboardButton("ספר לי עוד על הפרויקט", callback_data=BRIEF3)
    # button_option_d = InlineKeyboardButton(LETSTART, callback_data=LETSTART)
    button_option_e = InlineKeyboardButton('כן!', callback_data=LETSTART)

    keyboard = [[button_option_e]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if gender == MALE:
        await bot.send_message(chat_id=chat_id, text=BRIEF_TEXT, reply_markup=reply_markup,
                               parse_mode='Markdown')
    else:
        await bot.send_message(chat_id=chat_id, text=BRIEF_TEXT_FEMALE, reply_markup=reply_markup,
                               parse_mode='Markdown')


async def send_terms():
    print("Sending agreement message..")
    bot = Bot(TOKEN)
    button_option_a = InlineKeyboardButton(OK_TERMS, callback_data=OK_TERMS)
    button_option_b = InlineKeyboardButton(OK_TERMS_FEMALE, callback_data=OK_TERMS)

    if gender == MALE:
        keyboard = [[button_option_a]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await bot.send_message(chat_id=chat_id, text=TERMS_TEXT, reply_markup=reply_markup)
    else:
        keyboard = [[button_option_b]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await bot.send_message(chat_id=chat_id, text=TERMS_TEXT_FEMALE, reply_markup=reply_markup)


async def send_gender_question():
    print("Sending gender question..")
    bot = Bot(TOKEN)
    text_message = ASK_GENDER
    button_option_a = InlineKeyboardButton(MALE, callback_data=MALE)
    button_option_b = InlineKeyboardButton(FEMALE, callback_data=FEMALE)
    keyboard = [[button_option_a], [button_option_b]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot.send_message(chat_id=chat_id, text=text_message, reply_markup=reply_markup, parse_mode='Markdown')


async def send_age_question(text):
    print("Sending age question..")
    bot = Bot(TOKEN)
    await bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')


async def send_pdf():
    print("Sending email question..")
    bot = Bot(TOKEN)
    text = 'איזה כיף!\n הנה קובץ אשר סוקר את הפרויקט. במידה ויש לך שאלות נוספות, את מוזמן לפנות לעופר :)'
    if gender == FEMALE:
        text = 'איזה כיף!\n ת הנה קובץ אשר סוקר את הפרויקט.  במידה ויש לך שאלות נוספות, את מוזמנת לפנות לעופר :)'

    await bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')


async def send_accent_question():
    print("Sending accent question..")
    bot = Bot(TOKEN)
    button_option_a = InlineKeyboardButton(ACCENT1, callback_data=ACCENT1)
    button_option_b = InlineKeyboardButton(ACCENT2, callback_data=ACCENT2)

    keyboard = [[button_option_a],
                [button_option_b]]
    text = ASK_ACCENT
    if gender == FEMALE:
        text = ASK_ACCENT_FEMALE
    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode='Markdown')


async def send_accent_specific():
    print("Sending accent specific..")
    bot = Bot(TOKEN)
    button_option_a = InlineKeyboardButton(ACCENT3, callback_data=ACCENT3)
    button_option_b = InlineKeyboardButton(ACCENT4, callback_data=ACCENT4)
    button_option_c = InlineKeyboardButton(ACCENT5, callback_data=ACCENT5)
    button_option_d = InlineKeyboardButton(ACCENT6, callback_data=ACCENT6)
    button_option_e = InlineKeyboardButton(ACCENT7, callback_data=ACCENT7)

    keyboard = [[button_option_a],
                [button_option_b],
                [button_option_c],
                [button_option_d],
                [button_option_e]]
    text = ASK_ACCENT_SPECIFIC
    if gender == FEMALE:
        text = ASK_ACCENT_SPECIFIC_FEMALE
    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode='Markdown')


async def send_first_video_instructions():
    print("Sending instructions for calibration video..")
    bot = Bot(TOKEN)

    url = get_file_url(DEMO1_VIDEO_ID)
    response = requests.get(url, stream=True)

    # await bot.send_message(chat_id=chat_id, text=FIRST_VIDEO_TEXT1, parse_mode='Markdown')
    if gender == MALE:
        await bot.send_message(chat_id=chat_id, text=FIRST_VIDEO_TEXT2, parse_mode='Markdown')
    else:
        await bot.send_message(chat_id=chat_id, text=FIRST_VIDEO_TEXT2_FEMALE, parse_mode='Markdown')
    await bot.send_video(chat_id=chat_id, video=response.raw)


async def send_second_video_instructions(sentence):
    print("Sending instructions for video..")
    bot = Bot(TOKEN)

    text_message = "קיבלתי!\nהו וואו.. איזה חיוך!\n" \
                   "אוקיי, כדור הארץ לאלפרד. \U0001F916\n\n\n" \
                   "*סרטון שני*\n\n" \
                   "*הקפד על דיקציה* מודגשת אך טבעית.\n\n" \
                   "*קח הפסקות ברורות* בין המילים, סגור את הפה לחלוטין כחצי שניה.\n\n" \
                   "*לא לזוז*, הבט ישר למצלמה והחזק את הפלפאון בגובה העיניים.\n\n" \
                   "*צלם מקרוב,* הפנים שלך צריכות לכסות את רוב המסך.\n\n" \
                   "*הפעל את מצלמת הסלפי מתוך טלגרם,* לחץ על כפתור השיתוף ואז על החלון שמראה תמונה חיה.  \n\n" \
                   "צלם את עצמך אומר את המשפט: " \
                   f"*{sentence}*\n\n" \
                   "*כשסיימת*, צפה בסרטון, וודא שעמדת בכללים בדיוק כמו בסרטון ששלחתי, ושלח!"

    if gender == FEMALE:
        text_message = "קיבלתי!\nהו וואו.. איזה חיוך!\n" \
                       "אוקיי, כדור הארץ לאלפרד. \U0001F916\n\n\n" \
                       "*סרטון שני*\n\n" \
                       "*הקפידי על דיקציה* מודגשת אך טבעית.\n\n" \
                       "*קחי הפסקות ברורות* בין המילים, סגרי את הפה לחלוטין כחצי שניה.\n\n" \
                       "*לא לזוז,* הביטי ישר למצלמה והחזיקי את הפלפאון בגובה העיניים.\n\n" \
                       "*צלמי מקרוב,* הפנים שלך צריכות לכסות את רוב המסך.\n\n" \
                       "*הפעילי את מצלמת הסלפי מתוך טלגרם,* לחצי על כפתור השיתוף ואז על החלון שמראה תמונה חיה.  \n\n" \
                       "צלמי את עצמך אומרת את המשפט: " \
                       f"*{sentence}*\n\n" \
                       "*כשסיימת,* צפי בסרטון, וודאי שעמדת בכללים בדיוק כמו בסרטון ששלחתי, ושלחי!"

    url = get_file_url(DEMO2_VIDEO_ID)
    response = requests.get(url, stream=True)
    await bot.send_message(chat_id=chat_id, text=text_message, parse_mode='Markdown')
    await bot.send_video(chat_id=chat_id, video=response.raw)


async def send_nth_video_instructions(sentence):
    print("Sending instructions for video..")
    bot = Bot(TOKEN)

    text_message = "יש! תודה!\n אוקיי, רק תזכורת לגבי הכללים: \n\n" \
                   "*דיקציה מודגשת* אך טבעית.\n\n" \
                   "*לקחת הפסקות ברורות* בין המילים, לסגור את הפה לחלוטין כחצי שניה.\n\n" \
                   "*לא לזוז,* הבט ישר למצלמה והחזק את הפלפאון בגובה העיניים.\n\n" \
                   "*צלם מקרוב,* הפנים שלך צריכות לכסות את רוב המסך.\n\n" \
                   "*הפעל את מצלמת הסלפי מתוך טלגרם,* לחץ על כפתור השיתוף ואז על החלון שמראה תמונה חיה.  \n\n" \
                   "צלם את עצמך אומר את המשפט: " \
                   f"*{sentence}*\n\n" \
                   "*כשסיימת,* צפה בסרטון, וודא שעמדת בכללים, ושלח."

    if gender == FEMALE:
        text_message = "יש! תודה!\n אוקיי, רק תזכורת לגבי הכללים: \n\n" \
                       "*דיקציה מודגשת* אך טבעית.\n\n" \
                       "*לקחת הפסקות ברורות* בין המילים, לסגור את הפה לחלוטין כחצי שניה.\n\n" \
                       "*לא לזוז,* הביטי ישר למצלמה והחזיקי את הפלפאון בגובה העיניים.\n\n" \
                       "*צלמי מקרוב,* הפנים שלך צריכות לכסות את רוב המסך.\n\n" \
                       "*הפעילי את מצלמת הסלפי מתוך טלגרם,* לחצי על כפתור השיתוף ואז על החלון שמראה תמונה חיה.  \n\n" \
                       "צלמי את עצמך אומרת את המשפט: " \
                       f"*{sentence}*\n\n" \
                       "*כשסיימת,* צפי בסרטון, וודאי שעמדת בכללים, ושלחי."

    await bot.send_message(chat_id=chat_id, text=text_message, parse_mode='Markdown')


async def send_nth_video_menu():
    print("Sending n'th video menu..")
    bot = Bot(TOKEN)

    keyboard = [[InlineKeyboardButton(OK_NTH, callback_data=OK_NTH)],
                [InlineKeyboardButton(IM_DONE, callback_data=IM_DONE)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if gender == MALE:
        await bot.send_message(chat_id=chat_id, text=ASK_NTH_VIDEO, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await bot.send_message(chat_id=chat_id, text=ASK_NTH_VIDEO_FEMALE, reply_markup=reply_markup,
                               parse_mode='Markdown')


async def send_config_message():
    print("Sending config message..")
    bot = Bot(TOKEN)
    text_message1 = "Hi Admin, it's good to see you"
    text_message2 = "Exiting Configuration"
    message = text_message1 if state == CONFIG else text_message2
    await bot.send_message(chat_id, message)


async def send_config_menu():
    print("Sending config menu..")
    bot = Bot(TOKEN)

    keyboard = [[InlineKeyboardButton("Clear Chat DB", callback_data="clear_chat_table")],
                [InlineKeyboardButton("Reset Text DB", callback_data="reset_sentence_table")],
                [InlineKeyboardButton("Clear S3", callback_data="clear_bucket")],
                [InlineKeyboardButton("Quit config", callback_data=QUIT)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text_message = "What action would you like to take?"

    await bot.send_message(chat_id=chat_id, text=text_message, reply_markup=reply_markup)


async def send_goodbye():
    print("Sending success message..")
    bot = Bot(TOKEN)

    if gender == MALE:
        button_option_a = InlineKeyboardButton("התחל שיחה חדשה", callback_data=RESET)
        keyboard = [[button_option_a]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await bot.send_message(chat_id=chat_id, text=GOODBYE_TEXT,
                               reply_markup=reply_markup, parse_mode='Markdown')
    else:
        button_option_a = InlineKeyboardButton("התחילי שיחה חדשה", callback_data=RESET)
        keyboard = [[button_option_a]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await bot.send_message(chat_id=chat_id, text=GOODBYE_TEXT_FEMALE,
                               reply_markup=reply_markup, parse_mode='Markdown')


async def send_success_message():
    print("Sending success message..")
    bot = Bot(TOKEN)
    text_message = "Done!"

    await bot.send_message(chat_id=chat_id, text=text_message)


async def send_wrong_response_message():
    bot = Bot(TOKEN)

    button_option_a = InlineKeyboardButton(WHAT, callback_data=WHAT)
    button_option_b = InlineKeyboardButton(RESET, callback_data=RESET)

    keyboard = [[button_option_a], [button_option_b]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot.send_message(chat_id=chat_id, text=WRONG_ACTION_TEXT, reply_markup=reply_markup)


async def send_default_response():
    print("Sending default fault response..")
    bot = Bot(TOKEN)
    await bot.send_message(chat_id=chat_id, text=WRONG_REPLY_TEXT)


async def send_failed_response():
    bot = Bot(TOKEN)
    await bot.send_message(chat_id, 'Failed to download your file, please send again.')


async def send_shefy_stom():
    bot = Bot(TOKEN)
    await bot.send_message(chat_id, 'Shefy Ne..'
                                    '\nאתה יכול רק ללחוץ על quit')
