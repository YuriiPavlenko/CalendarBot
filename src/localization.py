# -*- coding: utf-8 -*-

STRINGS = {
    # General greetings and menus
    "greeting": "Привет! Я бот для просмотра встреч из календаря. Сначала нужно настроить фильтр и уведомления.",
    "settings_done": "Настройки завершены. Список доступных команд см. в меню.",
    "menu_title": "Команды:",
    "menu_start": "/start - Начать настройку",
    "menu_settings_filter": "/settings_filter - Настройка фильтра",
    "menu_settings_notifications": "/settings_notifications - Настройка уведомлений",
    "menu_get_today": "/get_today - Встречи сегодня",
    "menu_get_tomorrow": "/get_tomorrow - Встречи завтра",
    "menu_get_rest_week": "/get_rest_week - Встречи до субботы",
    "menu_get_next_week": "/get_next_week - Встречи на следующей неделе",

    # Filter related
    "settings_filter_intro": "Выберите вариант фильтра:",
    "settings_filter_all": "Показывать все встречи",
    "settings_filter_mine": "Показывать только мои встречи",
    "settings_filter_saved": "Настройки фильтра сохранены.",
    "filter_saved_standalone": "Фильтр сохранен. Вы можете изменить его позже командой /settings_filter.",

    # Notifications related
    "settings_notifications_intro": "Выберите настройки уведомлений.",
    "settings_notifications_1h": "Уведомлять за 1 час до встречи?",
    "settings_notifications_15m": "Уведомлять за 15 минут до встречи?",
    "settings_notifications_5m": "Уведомлять за 5 минут до встречи?",
    "settings_notifications_new": "Уведомлять о новой встрече?",
    "settings_notifications_saved": "Настройки уведомлений сохранены.",

    # Yes/No buttons
    "yes_button": "Да",
    "no_button": "Нет",

    # No meetings
    "no_meetings": "Нет встреч по выбранному фильтру.",

    # Notifications text
    "notify_before_meeting": "Напоминание о встрече:\n{details}",
    "notify_new_meeting": "Добавлена новая встреча:\n{details}",

    # Meetings formatting
    "meetings_for_today": "ВСТРЕЧИ НА СЕГОДНЯ ({date}):",
    "meetings_for_tomorrow": "ВСТРЕЧИ НА ЗАВТРА ({date}):",
    "meetings_for_day_of_week": "ВСТРЕЧИ НА {weekday} ({date}):",
    "ukraine_time": "Украина: {start} - {end}",
    "thailand_time": "Таиланд: {start} - {end}",
    "location_label": "Место: {location}",
    "link_label": "Ссылка: {link}",
    "description_label": "Описание: {description}",

    # Weekdays (0=Monday)
    "weekdays": ["Понедельник","Вторник","Среда","Четверг","Пятница","Суббота","Воскресенье"],

    # Meeting details template
    "meeting_details": "Название: {title}\nНачало (Украина): {start_ua}\nНачало (Таиланд): {start_th}\nКонец (Украина): {end_ua}\nКонец (Таиланд): {end_th}\nУчастники: {attendants}\nМесто: {location}\nСсылка: {link}\nОписание: {desc}"
}
