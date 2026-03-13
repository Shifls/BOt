import json
import os
from datetime import datetime, date, timedelta

FILE_NAME = "events.json"


# -------------------- Робота з файлом --------------------
def load_events():
    """Завантажує події з JSON-файлу."""
    if not os.path.exists(FILE_NAME):
        return []

    try:
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_events(events):
    """Зберігає події у JSON-файл."""
    with open(FILE_NAME, "w", encoding="utf-8") as file:
        json.dump(events, file, ensure_ascii=False, indent=4)


# -------------------- Допоміжні функції --------------------
def parse_date(date_text):
    """Перетворює текст у дату формату YYYY-MM-DD."""
    try:
        return datetime.strptime(date_text, "%Y-%m-%d").date()
    except ValueError:
        return None


def parse_time(time_text):
    """Перетворює текст у час формату HH:MM."""
    try:
        return datetime.strptime(time_text, "%H:%M").time()
    except ValueError:
        return None


def event_start_datetime(event):
    """Повертає datetime початку події."""
    return datetime.strptime(
        event["date"] + " " + event["start_time"],
        "%Y-%m-%d %H:%M"
    )


def event_end_datetime(event):
    """Повертає datetime початку події."""
    return datetime.strptime(
        event["date"] + " " + event["end_time"],
        "%Y-%m-%d %H:%M"
    )


def sort_events(events):
    """Сортує події за датою та часом початку."""
    return sorted(events, key=lambda event: (event["date"], event["start_time"]))


def print_event(event, index=None):
    """Виводить одну подію у зручному форматі."""
    prefix = f"{index}. " if index is not None else ""

    print(
        f"{prefix}Назва: {event['title']} | "
        f"Дата: {event['date']} | "
        f"Початок: {event['start_time']} | "
        f"Кінець: {event['end_time']} | "
        f"Категорія: {event['category']}"
    )


def show_events(events):
    """Показує список подій."""
    if not events:
        print("Список подій порожній.")
        return

    sorted_list = sort_events(events)
    print("Список подій:")
    for i, event in enumerate(sorted_list, start=1):
        print_event(event, i)


def has_conflict(events, new_event, skip_original_event=None):
    """Перевіряє, чи перетинається подія з уже існуючими."""
    new_start = event_start_datetime(new_event)
    new_end = event_end_datetime(new_event)

    for event in events:
        if skip_original_event is not None and event is skip_original_event:
            continue

        if event["date"] != new_event["date"]:
            continue

        old_start = event_start_datetime(event)
        old_end = event_end_datetime(event)

        if new_start < old_end and new_end > old_start:
            return True, event

    return False, None


def input_event_data():
    """Запитує у користувача дані нової події."""
    title = input("Введіть назву події: ").strip()

    while True:
        date_text = input("Введіть дату (YYYY-MM-DD): ").strip()
        event_date = parse_date(date_text)
        if event_date:
            break
        print("Неправильний формат дати. Спробуйте ще раз.")

    while True:
        start_time = input("Введіть час початку (HH:MM): ").strip()
        if parse_time(start_time):
            break
        print("Неправильний формат часу. Спробуйте ще раз.")

    category = input("Введіть категорію або короткий опис: ").strip()

    print("Оберіть спосіб введення часу завершення:")
    print("1 - ввести час завершення")
    print("2 - ввести тривалість у хвилинах")
    choice = input("Ваш вибір: ").strip()

    if choice == "1":
        while True:
            end_time = input("Введіть час завершення (HH:MM): ").strip()
            end_obj = parse_time(end_time)
            if end_obj is None:
                print("Неправильний формат часу. Спробуйте ще раз.")
                continue

            start_dt = datetime.strptime(date_text + " " + start_time, "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(date_text + " " + end_time, "%Y-%m-%d %H:%M")

            if end_dt > start_dt:
                break

            print("Час завершення має бути пізніше за час початку.")
    else:
        while True:
            duration_text = input("Введіть тривалість у хвилинах: ").strip()
            if duration_text.isdigit() and int(duration_text) > 0:
                duration_minutes = int(duration_text)
                start_dt = datetime.strptime(date_text + " " + start_time, "%Y-%m-%d %H:%M")
                end_dt = start_dt + timedelta(minutes=duration_minutes)
                end_time = end_dt.strftime("%H:%M")
                break
            print("Тривалість має бути додатним цілим числом.")

    return {
        "title": title,
        "date": date_text,
        "start_time": start_time,
        "end_time": end_time,
        "category": category
    }


def choose_event(events, action_text):
    """Дає змогу вибрати подію зі списку."""
    if not events:
        print(f"Немає подій для команди '{action_text}'.")
        return None, None

    sorted_list = sort_events(events)
    show_events(sorted_list)

    number = input(f"Введіть номер події, яку потрібно {action_text}: ").strip()
    if not number.isdigit():
        print("Потрібно ввести число.")
        return None, None

    index = int(number) - 1
    if index < 0 or index >= len(sorted_list):
        print("Неправильний номер події.")
        return None, None

    selected_event = sorted_list[index]
    original_index = events.index(selected_event)
    return original_index, selected_event


# -------------------- Команди бота --------------------
def greeting():
    """Вітання користувача."""
    print("Вітаю! Я бот 'Організатор подій'.")
    print("Я допоможу вам додавати, переглядати та редагувати події.")
    print("Введіть 'допомога', щоб побачити список доступних команд.")


def help_command():
    """Виводить список команд."""
    print("Доступні команди:")
    print("- допомога")
    print("- додати подію")
    print("- показати події")
    print("- події на тиждень")
    print("- події на дату")
    print("- події за період")
    print("- події за категорією")
    print("- пошук")
    print("- редагувати подію")
    print("- видалити подію")
    print("- події на сьогодні")
    print("- події на завтра")
    print("- найближча подія")
    print("- вийти")


def add_event(events):
    """Додає нову подію."""
    new_event = input_event_data()

    conflict, conflict_event = has_conflict(events, new_event)
    if conflict:
        print("Увага! Є конфлікт з іншою подією:")
        print_event(conflict_event)

    events.append(new_event)
    save_events(events)
    print("Подію успішно додано.")


def events_this_week(events):
    """Показує події поточного тижня."""
    today = date.today()
    start_week = today - timedelta(days=today.weekday())
    end_week = start_week + timedelta(days=6)

    result = []
    for event in events:
        event_date = parse_date(event["date"])
        if event_date and start_week <= event_date <= end_week:
            result.append(event)

    print(f"Події на цей тиждень ({start_week} - {end_week}):")
    show_events(result)


def events_on_date(events):
    """Показує події на конкретну дату."""
    date_text = input("Введіть дату (YYYY-MM-DD): ").strip()
    if parse_date(date_text) is None:
        print("Неправильний формат дати.")
        return

    result = [event for event in events if event["date"] == date_text]
    print(f"Події на дату {date_text}:")
    show_events(result)


def events_by_period(events):
    """Показує події за період між двома датами."""
    start_text = input("Введіть початкову дату (YYYY-MM-DD): ").strip()
    end_text = input("Введіть кінцеву дату (YYYY-MM-DD): ").strip()

    start_date = parse_date(start_text)
    end_date = parse_date(end_text)

    if not start_date or not end_date:
        print("Неправильний формат дати.")
        return

    if start_date > end_date:
        print("Початкова дата не може бути пізніше кінцевої.")
        return

    result = []
    for event in events:
        event_date = parse_date(event["date"])
        if event_date and start_date <= event_date <= end_date:
            result.append(event)

    print(f"Події за період {start_text} - {end_text}:")
    show_events(result)


def events_by_category(events):
    """Показує події за категорією."""
    category = input("Введіть категорію: ").strip().lower()
    result = [event for event in events if event["category"].lower() == category]

    print(f"Події за категорією '{category}':")
    show_events(result)


def search_events(events):
    """Шукає події за словом у назві або описі."""
    keyword = input("Введіть слово для пошуку: ").strip().lower()
    result = []

    for event in events:
        if keyword in event["title"].lower() or keyword in event["category"].lower():
            result.append(event)

    print(f"Результати пошуку за словом '{keyword}':")
    show_events(result)


def edit_event(events):
    """Редагує подію."""
    index, original_event = choose_event(events, "редагувати")
    if original_event is None:
        return

    print("Введіть нові дані події.")
    updated_event = input_event_data()

    conflict, conflict_event = has_conflict(events, updated_event, skip_original_event=original_event)
    if conflict:
        print("Увага! Нова подія конфліктує з іншою:")
        print_event(conflict_event)

    events[index] = updated_event
    save_events(events)
    print("Подію успішно відредаговано.")


def delete_event(events):
    """Видаляє подію."""
    index, original_event = choose_event(events, "видалити")
    if original_event is None:
        return

    removed = events.pop(index)
    save_events(events)
    print("Подію видалено:")
    print_event(removed)


def events_today(events):
    """Показує події на сьогодні."""
    today_text = date.today().strftime("%Y-%m-%d")
    result = [event for event in events if event["date"] == today_text]

    print(f"Події на сьогодні ({today_text}):")
    show_events(result)


def events_tomorrow(events):
    """Показує події на завтра."""
    tomorrow_text = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    result = [event for event in events if event["date"] == tomorrow_text]

    print(f"Події на завтра ({tomorrow_text}):")
    show_events(result)


def nearest_event(events):
    """Показує найближчу майбутню подію."""
    now = datetime.now()
    future_events = []

    for event in events:
        start_dt = event_start_datetime(event)
        if start_dt >= now:
            future_events.append(event)

    if not future_events:
        print("Немає майбутніх подій.")
        return

    nearest = min(future_events, key=event_start_datetime)
    print("Найближча подія:")
    print_event(nearest)


# -------------------- Головна програма --------------------
def main():
    events = load_events()
    greeting()

    while True:
        print()
        command = input("Введіть команду: ").strip().lower()

        if command == "допомога":
            help_command()
        elif command == "додати подію":
            add_event(events)
            events = load_events()
        elif command == "показати події":
            show_events(events)
        elif command == "події на тиждень":
            events_this_week(events)
        elif command == "події на дату":
            events_on_date(events)
        elif command == "події за період":
            events_by_period(events)
        elif command == "події за категорією":
            events_by_category(events)
        elif command == "пошук":
            search_events(events)
        elif command == "редагувати подію":
            edit_event(events)
            events = load_events()
        elif command == "видалити подію":
            delete_event(events)
            events = load_events()
        elif command == "події на сьогодні":
            events_today(events)
        elif command == "події на завтра":
            events_tomorrow(events)
        elif command == "найближча подія":
            nearest_event(events)
        elif command == "вийти":
            print("Роботу завершено. До побачення!")
            break
        else:
            print("Невідома команда. Введіть 'допомога'.")


if __name__ == "__main__":
    main()
