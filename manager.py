import time
import utils
import datetime
import mysql.connector
from config import DatabaseConfig
from typing import Union, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from setup_app import MyFlaskApplication


class BaseManager:
    """ Базовый класс менеджера БД с общим функционалом для управления БД """
    def __init__(self, app: "MyFlaskApplication", db_config: DatabaseConfig):
        self.app = app
        self.config = db_config.to_dict()
        self.connection = None
        self.cursor = None
        self.table_names = None
        #
        # self.drop_tables()    # затирание данных, при необходимости
        self.connect()
        if self.connection:
            self.get_tables()
        else:
            for i in range(3):
                time.sleep(i * 1000)
                self.connect()
                if self.connection:
                    break

    def connect(self):
        """ Подключение к базе данных """
        try:
            self.connection = mysql.connector.connect(**self.config)
            self.cursor = self.connection.cursor()
            #
            if self.connection.is_connected():
                db_info = self.connection.get_server_info()
                print(f'Успешное подключение к серверу MySQL ({db_info}): {self.connection.database}')
        except mysql.connector.Error as exp:
            print(f'Ошибка при подключении к базе данных: {exp}')

    def disconnect(self):
        """ Закрытие соединения """
        bd_name = self.connection.database
        if self.connection.is_connected():
            self.connection.close()
            print(f'Соединение с базой данных {bd_name} закрыто')

    def check_connections(self):
        """ Проверка соединения - на этой бесплатной БД постоянно отваливается соединение """
        if not self.connection or not self.connection.is_connected():
            self.connect()

    def get_tables(self, silent=False):
        """
        Получение списка всех таблиц в базе данных
        :param silent: Отключение уведомлений в консоли
        :return: Список имен таблиц
        """
        self.check_connections()
        self.cursor.execute('SHOW TABLES')
        tables = self.cursor.fetchall()
        tables = [table[0] for table in tables]
        self.table_names = tables

        if not silent:
            if tables:
                print(f'В Базе Данных {self.connection.database} существуют следующие таблицы:')
                for table in tables:
                    print('\t', table)
            else:
                print(f'База Данных {self.connection.database} пуста, нет ни одной таблицы..')
                self.make_initial_table()
        #
        return tables

    def _drop_table(self, table_name):
        """
        Формирование SQL-запроса для удаления таблицы
        :param table_name: имя таблицы
        :return: Кортеж с флагом итога операции и выброшенным исключением (при возникновении)
        """
        try:
            query = f'DROP TABLE {table_name}'
            self.write_to_db(query)
            self.get_tables(silent=True)
            return True, None
        except Exception as exp:
            return False, exp

    def drop_tables(self):
        """ Удаление всех таблиц - очистка БД """
        self.check_connections()
        existing_tables = self.get_tables(silent=True)

        # удаляю в while цикле поочередно пробуя каждую таблицу (из-за связей и ограничений)
        # можно было просто в обратном порядке, но это не дает 100% гарантии
        while existing_tables:
            is_dropped, exp = self._drop_table(existing_tables[0])
            if is_dropped:
                existing_tables.pop(0)
            elif isinstance(exp, mysql.connector.errors.DatabaseError) and exp.errno == 3730:
                # это ошибка из-за неверной очереди удаления таблиц
                existing_tables.append(existing_tables.pop(0))
            else:
                # иная ошибка, пробрасываю наверх
                raise exp
            #
            self.connection.commit()

    def write_to_db__many(self, query: str, params: Union[None, list] = None):
        """
        Выполнение SQL для массовой записи строк
        :param query: Строка со SQL-запросом
        :param params: Параметры для массовой записи
        """
        self.check_connections()
        self.cursor.executemany(query, params)
        self.connection.commit()

    def write_to_db(self, query: str, params: Union[None, list, tuple] = None):
        """
        Выполнение SQL запроса и закрепление результата
        :param query: Строка со SQL-запросом
        :param params: Параметры (опционально)
        """
        self.check_connections()
        self.cursor.execute(query, params)
        new_id = self.cursor.lastrowid
        self.connection.commit()
        return new_id

    def read_from_db(self, query: str, params: Union[None, list, tuple] = None):
        """
        Выполнение SQL запроса на выборку и возврат этих значений
        :param query: Строка со SQL-запросом
        :param params: Параметры запроса (при наличии)
        :return: список словарей с полученными данными в формате column:value
        """
        self.check_connections()
        self.cursor.execute(query, params)
        columns = [column[0] for column in self.cursor.description]
        data = self.cursor.fetchall()
        if data:
            data = [{col: val for col, val in zip(columns, row)} for row in data]
        return data

    def make_initial_table(self):
        """ Наполнение БД первичными данными """
        self.check_connections()
        print('Создаю и наполняю таблицу')
        table, insert, data = utils.get_initial_table_sql()
        self.write_to_db(table)
        self.write_to_db__many(insert, data)
        self.get_tables()


class Manager(BaseManager):
    """ Класс с верхнеуровневым функционалом для внесения изменений в бд """
    def __init__(self, app: "MyFlaskApplication", db_config: DatabaseConfig):
        super().__init__(app, db_config)

    def get(self, task_id: Optional[int] = None):
        """ Выборка задачи / всех задач """
        if task_id:
            query = '''
                SELECT * FROM tasks
                WHERE id = %s
            '''
            data = self.read_from_db(query, (task_id,))
            if data:
                return data[0]
            else:
                return False
        else:
            query = 'SELECT * FROM tasks'
            data = self.read_from_db(query)
        return data

    def insert(self, title: str, description: str = None, created_at: datetime = None, **kwargs):
        """ Добавление новой задачи """
        query = '''
            INSERT INTO tasks (title, description, created_at, updated_at) VALUES (%s, %s, %s, %s)
        '''
        if not created_at:
            created_at = datetime.datetime.now()
        else:
            from dateutil import parser
            created_at = parser.parse(created_at)
        last_id = self.write_to_db(query, (title, description, created_at, created_at))
        #
        added = self.get(last_id)
        return added

    def delete(self, task_id: Optional[int] = None):
        """ Удаление существующей задачи """
        query = '''
            DELETE FROM tasks
            WHERE id = %s
        '''
        self.check_connections()
        self.cursor.execute(query, (task_id,))
        rowcount = self.cursor.rowcount
        self.connection.commit()
        if rowcount:
            return True
        else:
            return False

    def put(self, task_id: Optional[int] = None, title: str = None, description: str = None, **kwargs):
        """ Изменение title и/или description существующей задачи """
        if not title and not description:
            return False

        query = f'''
            UPDATE tasks 
            SET {'title = %s, ' if title else ''}{'description = %s, ' if description else ''} updated_at = %s
            WHERE id = %s
        '''
        params = [title] if title else []
        params += [description] if description else []
        params += [datetime.datetime.now(), task_id]
        self.check_connections()
        self.cursor.execute(query, params)
        rowcount = self.cursor.rowcount
        self.connection.commit()
        if rowcount:
            return self.get(task_id)
        else:
            return False
