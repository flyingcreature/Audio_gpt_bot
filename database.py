import sqlite3
from config import DB_TABLE
from utils import logging


def create_db():
    connection = sqlite3.connect(DB_TABLE)
    connection.close()


def create_table(db_name=DB_TABLE):
    """Функция создания таблицы"""
    try:
        with sqlite3.connect(db_name) as connection:
            cursor = connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                message TEXT,
                tts_symbols INTEGER)
            ''')
            connection.commit()
            logging.info("Таблица успешно создана")
            print("Таблица успешно создана")
    except Exception as e:
        logging.error(f"Ошибка при создании таблицы: {e}")





def execute_query(query: str, data: tuple | None = None, db_file: str = DB_TABLE):
    """
    Функция для выполнения запроса к базе данных.
    Принимает имя файла базы данных, SQL-запрос и опциональные данные для вставки.
    """
    try:
        connection = sqlite3.connect(db_file)
        cursor = connection.cursor()

        if data:
            cursor.execute(query, data)
            connection.commit()
        else:
            cursor.execute(query)

    except sqlite3.Error as e:
        print("Ошибка при выполнении запроса:", e)
        logging.error("Ошибка при выполнении запроса:", e)

    else:
        result = cursor.fetchall()
        connection.close()
        return result


def is_user_in_db(user_id: int) -> bool:
    """
    Проверка есть ли, пользователь в базе

    """
    query = (
        """
        SELECT user_id 
        FROM messages
        WHERE user_id = ?;
        """
    )
    return bool(execute_query(query, (user_id,)))


def add_user(user_id: int, message: str, tts_symbols: int):
    """
    Функция для добавления нового студента в базу данных.
    """
    if not is_user_in_db(user_id):
        #  SQL-запрос для вставки данных о новом пользователе в таблицу users
        query = '''
        INSERT INTO messages (user_id, message, tts_symbols)
        VALUES (?, ?, ?);
         '''
        data = (user_id, message, tts_symbols)

        execute_query(query, data)
        print(f"Новый пользователь успешно добавлен в таблицу.")
        logging.info(f"Новый пользователь успешно добавлен в таблицу.")
    else:
        print(f"Пользователь {user_id} уже существует.")
        logging.info(f"Пользователь {user_id} уже существует.")


def get_all_users_data() -> list[tuple[int, str, int]]:
    sql_query = (
        f"SELECT * "
        f"FROM messages;"
    )

    result = execute_query(sql_query)
    return result


def insert_row(user_id, message, tts_symbols, db_name=DB_TABLE):
    """Добавление значения в таблицу"""
    try:
        with sqlite3.connect(db_name) as connection:
            cursor = connection.cursor()

            cursor.execute('''
            INSERT INTO messages (user_id, message, tts_symbols)
            VALUES (?, ?, ?)
            ''',
                           (user_id, message, tts_symbols))
            connection.commit()
    except Exception as e:
        print(f"Error: {e}")
        logging.error(f"Ошибка при добавлении значения в таблицу: {e}")


def count_all_symbol(user_id, db_name=DB_TABLE):
    """Функция подсчёта символов"""
    try:
        with sqlite3.connect(db_name) as connection:
            cursor = connection.cursor()
            # Считаем, сколько символов использовал пользователь
            cursor.execute('''SELECT SUM(tts_symbols) FROM messages WHERE user_id=?''', (user_id,))
            data = cursor.fetchone()
            # Проверяем data на наличие хоть какого-то полученного результата запроса
            # И на то, что в результате запроса мы получили какое-то число в data[0]
            if data and data[0]:
                # Если результат есть и data[0] == какому-то числу, то
                return data[0]  # возвращаем это число - сумму всех потраченных символов
            else:
                # Результата нет, так как у нас ещё нет записей о потраченных символах
                return 0  # возвращаем 0
    except Exception as e:
        print(f"Error: {e}")
        logging.error(f"Ошибка при подсчёте символов: {e}")
