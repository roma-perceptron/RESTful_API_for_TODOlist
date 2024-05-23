from setup_app import api
from flask_restx import fields

# Модель для задачи
task = api.model('Task', {
    'id': fields.Integer(required=True, readonly=True, description='Уникальный идентификатор задачи'),
    'title': fields.String(description='Название задачи'),
    'description': fields.String(description='Описание задачи'),
    'created_at': fields.DateTime(description='Дата и время первичной постановки'),
    'updated_at': fields.DateTime(description='Дата и время последнего изменения'),
})
