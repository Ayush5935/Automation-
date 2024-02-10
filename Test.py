from django.test import TestCase, Client
from django.urls import reverse
from todo_list.models import TodoItem

class TodoListViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.todo_item = TodoItem.objects.create(title='Test Todo', completed=False)

    def test_todo_list_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Todo')

    def test_todo_item_creation(self):
        todo_item = TodoItem.objects.create(title='New Todo', completed=False)
        self.assertEqual(todo_item.title, 'New Todo')
        self.assertFalse(todo_item.completed)

    def test_todo_item_update(self):
        todo_item = TodoItem.objects.get(title='Test Todo')
        todo_item.title = 'Updated Todo'
        todo_item.save()
        updated_todo_item = TodoItem.objects.get(id=todo_item.id)
        self.assertEqual(updated_todo_item.title, 'Updated Todo')

    def test_todo_item_deletion(self):
        todo_item = TodoItem.objects.get(title='Test Todo')
        todo_item.delete()
        with self.assertRaises(TodoItem.DoesNotExist):
            TodoItem.objects.get(title='Test Todo')

    def test_completed_todo_list_view(self):
        response = self.client.get(reverse('completed_todos'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Test Todo')  # Assuming 'Test Todo' is completed

    def test_incomplete_todo_list_view(self):
        response = self.client.get(reverse('incomplete_todos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Todo')  # Assuming 'Test Todo' is incomplete

# Add more test cases as needed
