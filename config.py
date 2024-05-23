import os
import yaml
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    host: str = 'localhost'
    port: int = 3306
    user: str = 'user'
    password: str = 'password'
    database: str = 'database'

    def to_dict(self):
        return self.__dict__


@dataclass
class Config:
    database: DatabaseConfig


def get_configs(config_path: str = 'config.yml'):
    """
    Чтение и распарсинг yaml файла с данными конфига БД
    :param config_path: имя yaml файла
    :return: датакласс с данными
    """
    if os.getcwd().endswith('tests'):
        os.chdir('..')
    #
    with open(config_path, mode='r') as f:
        raw_config = yaml.safe_load(f)

    return Config(
        database=DatabaseConfig(
            host=raw_config['database']['host'],
            port=raw_config['database']['port'],
            user=raw_config['database']['user'],
            password=raw_config['database']['password'],
            database=raw_config['database']['database']
        )
    )
