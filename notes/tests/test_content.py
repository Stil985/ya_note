from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model( )

class TestNotesPages(TestCase):
    LIST_URL = reverse('notes:list')
    
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='test',
            text='test',
            author=cls.author)

    def test_notes_count(self):
        users = (
            (self.author, 1),
            (self.reader, 0),
        )
        for user, count in users:
            with self.subTest(user=user):
                self.client.force_login(user)
                response = self.client.get(self.LIST_URL)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.context['object_list']), count)       


    def test_authorized_client_has_form(self):
        urls = (
            reverse('notes:add'),
            reverse('notes:edit', args=(self.note.slug,)),
        )
        self.client.force_login(self.author)
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn('form', response.context)
                