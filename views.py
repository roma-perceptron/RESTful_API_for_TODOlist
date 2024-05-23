from models import task
from flask_restx import Resource
from setup_app import ns, app, api


@ns.route('/')
class Tasks(Resource):
    @ns.marshal_list_with(task)
    def get(self):
        """ Получить список всех задач """
        return app.db_manager.get()

    @ns.expect(task)
    @ns.marshal_with(task, code=201)
    def post(self):
        """ Добавить новую задачу """
        return app.db_manager.insert(**api.payload), 201


@ns.route('/<int:id>')
@ns.param('id', 'Идентификатор задачи')
class Task(Resource):
    @ns.marshal_with(task)
    def get(self, id):
        """ Получить задачу """
        task_item = app.db_manager.get(id)
        if task_item:
            return task_item
        api.abort(404, f'Задачи с id={id} не существует!')

    @ns.response(200, f'Задача с id={id} успешно удалена')
    def delete(self, id):
        """ Удалить задачу """
        result = app.db_manager.delete(id)
        if result:
            return f'Задача с id={id} успешно удалена', 200
        else:
            return f'Ошибка при удалении задачи с id={id}. Проверьте идентификатор', 400

    @ns.expect(task)
    @ns.marshal_with(task)
    def put(self, id):
        """ Изменить задачу """
        if not api.payload.get('title', False) and not api.payload.get('description', False):
            return api.abort(400, 'Должно быть указано хотя бы одно из полей title или description')
        #
        result = app.db_manager.put(id, **api.payload)
        if result:
            return result, 200
        else:
            return api.abort(404, f'Ошибка при изменении задачи с id={id}. Проверьте идентификатор')
