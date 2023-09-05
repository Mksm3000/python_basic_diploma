import sqlite3 as sq


async def create_database():
    """
    The first initialization of the database
    """
    with sq.connect('user_requests.db') as db:
        db.execute('CREATE TABLE IF NOT EXISTS requests('
                   'user_id INTEGER PRIMARY KEY, '
                   'date TEXT, '
                   'command TEXT, '
                   'hotels_found BLOB)')
        db.commit()


async def add_row(user_id, time, command, matches):
    """
    Adds a new row into the database
    """
    with sq.connect('user_requests.db') as db:
        cursor = db.cursor()
        cursor.execute('INSERT INTO requests VALUES(?, ?, ?, ?)', (user_id, time, command, matches))
        db.commit()


async def show_tables(message):
    """
    Obtains the last 5 successful search results from the database.
    """
    with sq.connect('user_requests.db') as db:
        cursor = db.cursor()
        result = cursor.execute('SELECT * FROM requests WHERE user_id == ? ORDER BY date DESC LIMIT 5',
                                (message.from_user.id,)).fetchall()
    return result
