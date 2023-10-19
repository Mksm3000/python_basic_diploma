import sqlite3 as sq


async def create_database():
    """
    Создание БД, если её ещё не существует
    """
    with sq.connect('user_requests.db') as db:
        db.execute(""" CREATE TABLE IF NOT EXISTS requests(
                    user_id INTEGER,
                    date TEXT,
                    command TEXT,
                    destination TEXT,
                    hotels_found TEXT)
                    """)
        db.commit()


async def add_row(user_id, date, command, destination, matches):
    """
    Добавление новой строки в БД
    """
    with sq.connect('user_requests.db') as db:
        cursor = db.cursor()
        cursor.execute('INSERT INTO requests VALUES(?, ?, ?, ?, ?)', (user_id, date, command, destination, matches))
        db.commit()


async def show_tables(user_id):
    """
    Получение последних 5 запросов из БД для юзера с 'user_id'
    return: List
    """
    with sq.connect('user_requests.db') as db:
        cursor = db.cursor()
        result = cursor.execute('SELECT rowid, date, command, destination FROM requests WHERE user_id == ? ORDER BY date DESC LIMIT 5',
                                (user_id,)).fetchall()
    return result


async def show_hotels_found(row_num):
    """
    Получение информации по отелям для указанного 'row_id'
    return: Tuple
    """
    with sq.connect('user_requests.db') as db:
        cursor = db.cursor()
        result = cursor.execute('SELECT command, hotels_found FROM requests WHERE rowid == ?',
                                (row_num,)).fetchone()
    return result
