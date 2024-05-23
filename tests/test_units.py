import pytest
from main import app


TASK_FOR_ADD = {
    "title": "Новая задача",
    "description": "Очень важная задача",
}


class Test_API:
    new_task = {}

    @pytest.fixture(scope="session")
    def client(self):
        with app.test_client() as client:
            yield client

    def test_tasks_GET(self, client):
        """ Проверка получения списка задач """
        response = client.get('tasks/')

        assert response.status_code == 200

        tasks = response.json
        assert isinstance(tasks, list)
        if tasks:
            assert all([isinstance(task, dict) for task in tasks])

    def test_tasks_POST(self, client):
        """ Проверка добавления новой задачи """
        response = client.post('/tasks/', json=TASK_FOR_ADD)
        assert response.status_code == 201

        task = response.json
        assert isinstance(task, dict)

        assert task['title'] == TASK_FOR_ADD['title']
        assert task['description'] == TASK_FOR_ADD['description']

        Test_API.new_task = task

    def test_task_GET(self, client):
        """ Проверка получения конкретной задачи """
        response = client.get(f'/tasks/{Test_API.new_task["id"]}')

        assert response.status_code == 200

        task = response.json
        assert isinstance(task, dict)

        assert task['title'] == TASK_FOR_ADD['title']
        assert task['description'] == TASK_FOR_ADD['description']

    def test_task_GET_wrong(self, client):
        """ Проверка получения не существующей задачи """
        response = client.get(f'/tasks/{Test_API.new_task["id"] + 1}')

        assert response.status_code == 404

    def test_task_PUT(self, client):
        """ Проверка изменения задачи """
        changes = {'title': 'Новый заголовок', 'description': 'Новое описание'}
        response = client.put(f'/tasks/{Test_API.new_task["id"]}', json=changes)
        assert response.status_code == 200

        task = response.json
        assert task['title'] == changes['title']
        assert task['description'] == changes['description']

        response = client.put(f'/tasks/{Test_API.new_task["id"]}', json={'title': 'Меняем только заголовок'})
        assert response.status_code == 200

        response = client.put(f'/tasks/{Test_API.new_task["id"]}', json={'description': 'Меняем только описание'})
        assert response.status_code == 200

    def test_task_PUT_wrong(self, client):
        """ Проверка попытки изменения задачи без указания обязательных полей """
        response = client.put(f'/tasks/{Test_API.new_task["id"]}', json={'other': 'Только бессмысленные параметры'})
        assert response.status_code == 400

        assert response.json == {'message': 'Должно быть указано хотя бы одно из полей title или description'}

    def test_task_PUT_notexist(self, client):
        """ Проверка попытки изменения задачи которой не существует """
        changes = {'title': 'Новый заголовок', 'description': 'Новое описание'}
        response = client.put(f'/tasks/{Test_API.new_task["id"] + 1}', json=changes)
        assert response.status_code == 404

    def test_tasks_DELETE(self, client):
        """ Проверка удаления задачи """
        response = client.delete(f'/tasks/{Test_API.new_task["id"]}')
        assert response.status_code == 200

        assert response.json == f'Задача с id={Test_API.new_task["id"]} успешно удалена'

    def test_tasks_DELETE_wrong(self, client):
        """ Проверка удаления задачи которой не существует """
        response = client.delete(f'/tasks/{Test_API.new_task["id"] + 1}')
        assert response.status_code == 400

        assert response.json == f'Ошибка при удалении задачи с id={Test_API.new_task["id"] + 1}. Проверьте идентификатор'
