import datetime


def get_initial_table_sql():
    """
    Генерация SQL запросов для создания демо-таблиц
    :return: кортеж из строк с sql кодом и списком параметров для вставки
    """
    making = '''
        CREATE TABLE IF NOT EXISTS tasks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(128),
            description TEXT,
            created_at DATETIME,
            updated_at DATETIME
        )
    '''

    inserting = 'INSERT INTO tasks (title, description, created_at, updated_at) VALUES (%s, %s, %s, %s)'

    data = (
        (f'Задача номер {i}', f'Описание задачи #{i}', datetime.datetime.now(), datetime.datetime.now())
        for i in range(1, 11)
    )

    return making, inserting, data