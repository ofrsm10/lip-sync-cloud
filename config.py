import os
from typing import Optional


def get_env_var(var_name: str, default: Optional[str] = None) -> str:
    """
    Get environment variable value with optional default.
    
    Args:
        var_name: Name of the environment variable
        default: Default value if environment variable is not set
        
    Returns:
        Environment variable value or default
        
    Raises:
        ValueError: If environment variable is not set and no default provided
    """
    value = os.getenv(var_name, default)
    if value is None:
        raise ValueError(f"Environment variable {var_name} is required but not set")
    return value


# Configuration constants - these should remain the same
CONFIG = 'config'
GENDER = 'gender'
TERMS = 'terms'
INIT = 'init'
VIP_USER_MENU = 'VIP_USER_MENU'
VIP_USER_CALIB = "קליברציה"
VIP_USER_SENTENCE = "משפט"
BRIEF = 'briefing'
AGE = 'age'
ACCENT = 'accent'
RULES = 'rules'
FIRST_VIDEO = 'first_video'
GET_SENTENCE = 'get sentence'
VIP_USER_GET_SENTENCE = 'VIP_USER_GET_SENTENCE'
SECOND_VIDEO = 'second_video'
LAST_CHOICE = 'last_choice'
NTH_VIDEO = 'nth_video'
CURIOUS = 'corious'
STATE = 'state'
USER_NAME = 'user_name'
SENTENCE = 'sentence'
SESSION_ID = 'session_id'
LIGHTING_COLOR = 'LIGHTING_COLOR'
LIGHTING_INTENSITY = 'LIGHTING_INTENSITY'
PLACE = 'place'
TTL = 'ttl'

# Gender options
MALE = "זכר"
FEMALE = "נקבה"

# Accent options
ACCENT1 = 'לא'
ACCENT2 = 'כן'
ACCENT3 = 'צרפתי'
ACCENT4 = 'סלאבי'
ACCENT5 = 'אמריקאי'
ACCENT6 = 'לטיני'
ACCENT7 = 'אחר'

# Button responses
OK_TERMS = "אני מאשר"
OK_NTH = "יאללה, למה לא"
IM_DONE = "בהזדמנות אחרת"
OK_TERMS_FEMALE = "אני מאשרת"
QUIT = 'quit'
WHAT = "רגע, איפה היינו?"
RESET = "בוא נתחיל את השיחה מחדש"
BRIEF1 = "כן בקצרה, מה נעשה עכשיו?"
LETSTART = "לא, בוא נתחיל"

# Environment-based configuration
VIP_USER = get_env_var('VIP_USER_ID', 'vip_user')
ADMIN = get_env_var('ADMIN_USER_ID', 'admin_user')
GUEST = get_env_var('GUEST_USER_ID', 'guest_user')

# AWS Resources
CHAT_TABLE = get_env_var('CHAT_TABLE_NAME', 'ChatDB')
TEXT_TABLE = get_env_var('TEXT_TABLE_NAME', 'TextDB')
S3_BUCKET_NAME = get_env_var('S3_BUCKET_NAME')
QUEUE_URL = get_env_var('SQS_QUEUE_URL')
WEBHOOK_URL = get_env_var('WEBHOOK_URL')

# Telegram Configuration
TOKEN = get_env_var('TELEGRAM_BOT_TOKEN')

# Demo video file IDs
DEMO1_VIDEO_ID = get_env_var('DEMO1_VIDEO_ID', 'BAACAgQAAxkBAAIMSWSIRhdtrXCHEUCMH2Py8I6_q9j3AAK9EwACkApAUHbMxGUWd6bsLwQ')
DEMO2_VIDEO_ID = get_env_var('DEMO2_VIDEO_ID', 'BAACAgQAAxkBAAIMamSIR_-YIoh2BhEkfR-70qwxiptzAALIEwACkApAUJgbgCttnWbGLwQ')

# Static text content (Hebrew text for the bot responses)
INITIAL_VIP_USER = "הו שלום לך אדוני!\n\n" \
                   "ברוך בואך, " \
                   "כאן אלפרד לשירותך \U0001F916\n"
ASK_PLACE = "איפה אתה עומד לצלם כרגע?"
ASK_COLOR = "מה הצבע הדומיננטי של התאורה סביבך?"
ASK_INTENSITY = "מאחד עד עשר, כמה מואר סביבך? (עשר זה אור יום)"
ASK_STEP = "איזה סרטון אתה רוצה לשלוח?"
CALIB_INSTRUCTIONS = "תשלח סרטון שלך מוציא לשון במשך שניה, ואז מחייך עם שיניים במשך שניה נוספת"
GET_SENTENCE_INSTRUCTIONS = f"תשלח בהודעה, את המשפט שאתה עומד להקליט"
RECEIVED_VIDEO = 'קיבלתי!\n אם אתה רוצה לשלוח עוד סרטונים אני פה, רק תשלח הודעה :)'
ASK_GENDER = "מיד נתחיל\n\nסמנ/י את המין שלך\n\n"
OFFER_BRIEF = "*ברוך הבא ל-Project lipSync*\n\n" \
              "אני אלפרד \U0001F916\nעבדו הנאמן של עופר ומנהל הדאטה של הפרויקט.\n\n" \
              "קודם כל, תודה ענקית שבאת לתרום מזמנך, זה לא מובן מאליו.\n" \
              "בתקווה, נצליח לקחת את המילים שלך ולהעניק אותן חזרה לאלו שאיבדו אותן.\n" \
              "התרומה שלך יקרה מפז!\n\n" \
              "האם תרצה לשמוע קצת על התהליך? "
OFFER_BRIEF_FEMALE = "*ברוכה הבאה ל-Project lipSync*\n\n" \
                     "אני אלפרד \U0001F916\nעבדו הנאמן של עופר ומנהל הדאטה של הפרויקט.\n\n" \
                     "קודם כל, תודה ענקית שבאת לתרום מזמנך, זה לא מובן מאליו.\n" \
                     "בתקווה, נצליח לקחת את המילים שלך ולהעניק אותן חזרה לאלו שאיבדו אותן.\n" \
                     "התרומה שלך יקרה מפז!\n\n" \
                     "האם תרצי לשמוע קצת על התהליך?"
BRIEF_TEXT = "*אז מה הולך להיות לנו?*\n\n" \
             "קודם כל, נרגיע את הפאניקה- יש לנו רק 3 דקות יחד וזה נגמר. אני אשאל 2 שאלות, אתה תצלם 2 סרטונים וסיימנו!\n\n" \
             "*סרטון ראשון* נועד כדי ללמוד את הנתונים הוויזואלים שלך ולהתאים את המערכת אליהם.\n\n" \
             "*סרטון שני* נועד כדי להרחיב את אוצר המילים של המערכת.\n\n" \
             "וזהו! אחרי זה תוכל להישאר ולהמשיך לתרום כמה שרק בא לך.\n\n" \
             "*מוכן לזה?*"
BRIEF_TEXT_FEMALE = "*אז מה הולך להיות לנו?*\n\n" \
                    "קודם כל, נרגיע את הפאניקה- יש לנו רק 3 דקות יחד וזה נגמר. אני אשאל 2 שאלות, את תצלמי 2 סרטונים וסיימנו!\n\n" \
                    "*סרטון ראשון* נועד כדי ללמוד את הנתונים הוויזואלים שלך ולהתאים את המערכת אליהם.\n\n" \
                    "*סרטון שני* נועד כדי להרחיב את אוצר המילים של המערכת.\n\n" \
                    "וזהו! אחרי זה תוכלי להישאר ולהמשיך לתרום כמה שרק בא לך.\n\n" \
                    "*מוכנה לזה?*"
TERMS_TEXT = "בלחיצה על הכפתור, אתה נותן לי את האישור להשתמש בסרטונים שאקבל ממך בשיחה זו, לטובת קריאת " \
             "שפתיים מוידאו."
TERMS_TEXT_FEMALE = "בלחיצה על הכפתור, את נותנת לי את האישור להשתמש בסרטונים שאקבל ממך בשיחה זו, לטובת קריאת " \
                    "שפתיים מוידאו."
RECEIVE_OK_TERMS = "נהדר! בוא נתחיל.\n" \
                   "מה הגיל שלך?"
RECEIVE_OK_TERMS_FEMALE = "נהדר! בואי נתחיל.\n" \
                          "מה הגיל שלך?"
ASK_ACCENT = "\n\nהאם אדוני מדבר עם מבטא זר?"
ASK_ACCENT_FEMALE = "\n\nהאם גברתי מדברת עם מבטא זר?"
ASK_ACCENT_SPECIFIC = "בחר את המבטא מתוך הרשימה"
ASK_ACCENT_SPECIFIC_FEMALE = "בחרי את המבטא מתוך הרשימה"
FIRST_VIDEO_TEXT1 = "השלב הבא ישמע קצת מוזר, אבל הוא *חיוני* להתאמת המערכת " \
                    "לאנשים בעלי מאפיינים ויזואלים שונים זה מזה. \n\nלמה? כי חלק מהמידע שאני שואב מהוידאו, טמון בצבעים של הלשון והשיניים שלך.\n\n"
FIRST_VIDEO_TEXT2 = "*סרטון ראשון*\n\n" \
                    "*נקה* את העדשה של מצלמת הסלפי בעזרת בד.\n\n" \
                    "*הדלק תאורה חזקה,* עדיף אור לבן. \n\n" \
                    "*הקפד לא לזוז במהלך הצילום*, הבט ישר למצלמה והחזק את הפלפאון בגובה העיניים.\n\n" \
                    "*צלם מקרוב,* הפנים שלך צריכות לכסות את רוב המסך.\n\n" \
                    "*הפעל את מצלמת הסלפי מתוך טלגרם,* לחץ על כפתור השיתוף ואז על החלון שמראה תמונה חיה.  \n\n" \
                    "*צלם את עצמך* מוציא לשון במשך שניה ואז מחייך חיוך גדול עם שיניים במשך שניה נוספת. סגור את הפה בין הפעולות, בדיוק כמו בסרטון ששלחתי.\n\n" \
                    "*כשסיימת*, צפה בסרטון, וודא שעמדת בכללים, ושלח.\n\n"
FIRST_VIDEO_TEXT2_FEMALE = "*סרטון ראשון*\n\n" \
                           "*נקי* את העדשה של מצלמת הסלפי בעזרת בד.\n\n" \
                           "*הדליקי תאורה חזקה,* עדיף אור לבן. \n\n" \
                           "*הקפידי לא לזוז במהלך הצילום*, הביטי ישר למצלמה והחזיקי את הפלפאון בגובה העיניים.\n\n" \
                           "*צלמי מקרוב,* הפנים שלך צריכות לכסות את רוב המסך.\n\n" \
                           "*הפעילי את מצלמת הסלפי מתוך טלגרם,* לחצי על כפתור השיתוף ואז על החלון שמראה תמונה חיה.  \n\n" \
                           "*צלמי את עצמך* מוציאה לשון במשך במשך שניה ואז מחייכת חיוך גדול עם שיניים במשך שניה נוספת. סגרי את הפה בין הפעולות, בדיוק כמו בסרטון ששלחתי.\n\n" \
                           "*כשסיימת*, צפי בסרטון, וודאי שעמדת בכללים, ושלחי.\n\n"
ASK_NTH_VIDEO = 'יש! קיבלתי! \nאין עליך.. ' \
                'זהו, אתה משוחרר!\nאלא אם אתה מעוניין לעזור עוד טיפ טיפה..' \
                ' מממ מה אתה אומר? תרצה לתרום משפט נוסף?'
ASK_NTH_VIDEO_FEMALE = 'יש! קיבלתי! \n\nאין עליך..' \
                       'זהו, את משוחררת!\n אלא אם את מעוניינת לעזור עוד טיפ טיפה..' \
                       'מממ מה את אומרת? תרצי לתרום משפט נוסף?'
GOODBYE_TEXT = "בסדר גמור. לגמרי תרמת את חלקך.\n" \
               "תודה על כך. אתה מדהים, באמת!\n\n" \
               "אם סיימנו פה, אגש לבדוק את הסרטונים.. \nאולי אכין לעופר משהו לאכול, " \
               "הוא בדיוק צריך להגיע.. \n\nאדוני, היה תענוג. מוזמן לקפוץ בכל שעה! \U0001F916"
GOODBYE_TEXT_FEMALE = "בסדר גמור. לגמרי תרמת את חלקך.\n" \
                      "תודה על כך. את מדהימה, באמת!\n\n" \
                      "אם סיימנו פה, אגש לבדוק את הסרטונים.. \nאולי אכין לעופר משהו לאכול, " \
                      "הוא בדיוק צריך להגיע.. \n\nגבירתי, היה תענוג. מוזמנת לקפוץ בכל שעה! \U0001F916"
WRONG_ACTION_TEXT = "לא השלב לשלוח את זה..." \
                    "בבקשה שימ/י לב להנחיות ותפעל/י בהתאם"
WHAT_TEXT = "היינו פה.."
WRONG_REPLY_TEXT = "מצטער, עליך להיות מעל גיל 16 כדי לתרום.. אולי בעתיד!"
FAIL_DOWNLOAD_TEXT = "לא הצלחתי להוריד את הסרטון ששלחת, תוכל/י לשלוח שוב?"
HELP = "כדי להתחיל את השיחה מחדש, שלח/י את המילה ״חדש״\n\n"