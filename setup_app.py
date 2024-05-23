import config, manager
from flask import Flask
from typing import Optional
from flask_restx import Api


class MyFlaskApplication(Flask):
    """ Переопределяю базовый класс чтобы хранить внутри объект-менеджер бд """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_manager: Optional[manager.Manager] = None


# Создание объекта Flask-Приложения и Flask-RESTx АПИ
app = MyFlaskApplication('TASK_MASTER')
api = Api(app, version='2024.05.23', title='Task API', description='API для управления списком задач',
          contact='Github',
          contact_url='https://github.com/roma-perceptron/RESTful_API_for_TODOlist'
          )

# формирование конфига для БД и создание менеджера БД
configs = config.get_configs()
app.db_manager = manager.Manager(app, configs.database)

# создаю пространство имен для апи
ns = api.namespace('tasks', description='Действия с задачами')
