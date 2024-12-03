def get_texts(language):
    texts = {
        'uk': {
            'no_meetings': "Немає зустрічей.",
            'meetings_today': "Зустрічі на сьогодні:\n",
            'meetings_tomorrow': "Зустрічі на завтра:\n",
            'meetings_next_week': "Зустрічі на наступний тиждень:\n",
            'meetings_this_week': "Зустрічі на цей тиждень:\n",
            'days_of_week': ['Понеділок', 'Вівторок', 'Середа', 'Четвер', "П'ятниця", 'Субота', 'Неділя'],
            'language_set': "Мова встановлена на Українська.",
            'choose_language': "Будь ласка, оберіть свою мову:",
            'time_thailand': "Час у Таїланді",
            'time_ukraine': "Час в Україні",
            'goal': "Мета",
            'attendants': "Учасники",
            'location': "Місце",
            'meet_link': "Посилання на зустріч",
            'command_descriptions': [
                ("start", "Почати взаємодію з ботом"),
                ("today", "Отримати зустрічі на сьогодні"),
                ("tomorrow", "Отримати зустрічі на завтра"),
                ("today_tomorrow", "Отримати зустрічі на сьогодні та завтра"),
                ("week", "Отримати зустрічі на цей тиждень"),
                ("next_week", "Отримати зустрічі на наступний тиждень")
            ]
        },
        'ru': {
            'no_meetings': "Нет встреч.",
            'meetings_today': "Встречи на сегодня:\n",
            'meetings_tomorrow': "Встречи на завтра:\n",
            'meetings_next_week': "Встречи на следующую неделю:\n",
            'meetings_this_week': "Встречи на эту неделю:\n",
            'days_of_week': ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'],
            'language_set': "Язык установлен на Русский.",
            'choose_language': "Пожалуйста, выберите ваш язык:",
            'time_thailand': "Время в Таиланде",
            'time_ukraine': "Время в Украине",
            'goal': "Цель",
            'attendants': "Участники",
            'location': "Место",
            'meet_link': "Ссылка на встречу",
            'command_descriptions': [
                ("start", "Начать взаимодействие с ботом"),
                ("today", "Получить встречи на сегодня"),
                ("tomorrow", "Получить встречи на завтра"),
                ("today_tomorrow", "Получить встречи на сегодня и завтра"),
                ("week", "Получить встречи на эту неделю"),
                ("next_week", "Получить встречи на следующую неделю")
            ]
        },
        'en': {
            'no_meetings': "No meetings.",
            'meetings_today': "Meetings for today:\n",
            'meetings_tomorrow': "Meetings for tomorrow:\n",
            'meetings_next_week': "Meetings for next week:\n",
            'meetings_this_week': "Meetings for this week:\n",
            'days_of_week': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            'language_set': "Language set to English.",
            'choose_language': "Please choose your language:",
            'time_thailand': "Time in Thailand",
            'time_ukraine': "Time in Ukraine",
            'goal': "Goal",
            'attendants': "Attendants",
            'location': "Location",
            'meet_link': "Meeting Link",
            'command_descriptions': [
                ("start", "Start interacting with the bot"),
                ("today", "Get today's meetings"),
                ("tomorrow", "Get tomorrow's meetings"),
                ("today_tomorrow", "Get today's and tomorrow's meetings"),
                ("week", "Get this week's meetings"),
                ("next_week", "Get next week's meetings")
            ]
        },
        'th': {
            'no_meetings': "ไม่พบการประชุม",
            'meetings_today': "การประชุมสำหรับวันนี้:\n",
            'meetings_tomorrow': "การประชุมสำหรับพรุ่งนี้:\n",
            'meetings_next_week': "การประชุมสำหรับสัปดาห์หน้า:\n",
            'meetings_this_week': "การประชุมสำหรับสัปดาห์นี้:\n",
            'days_of_week': ['วันจันทร์', 'วันอังคาร', 'วันพุธ', 'วันพฤหัสบดี', 'วันศุกร์', 'วันเสาร์', 'วันอาทิตย์'],
            'language_set': "ตั้งค่าภาษาเป็น ภาษาไทย.",
            'choose_language': "กรุณาเลือกภาษาของคุณ:",
            'time_thailand': "เวลาในประเทศไทย",
            'time_ukraine': "เวลาในยูเครน",
            'goal': "เป้าหมาย",
            'attendants': "ผู้เข้าร่วม",
            'location': "สถานที่",
            'meet_link': "ลิงก์การประชุม",
            'command_descriptions': [
                ("start", "เริ่มโต้ตอบกับบอท"),
                ("today", "รับการประชุมวันนี้"),
                ("tomorrow", "รับการประชุมพรุ่งนี้"),
                ("today_tomorrow", "รับการประชุมวันนี้และพรุ่งนี้"),
                ("week", "รับการประชุมสัปดาห์นี้"),
                ("next_week", "รับการประชุมสัปดาห์หน้า")
            ]
        }
    }
    return texts[language]