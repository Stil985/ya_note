from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'Текст'
    SLUG = slugify(NOTE_TITLE)[:Note._meta.get_field('slug').max_length]

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.user = User.objects.create(username='Автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
        }

    def test_anonymous_client_cannot_create_note(self):
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        self.auth_client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_user_cant_create_notes_with_same_slug(self):
        Note.objects.create(
            title=self.NOTE_TITLE,
            text=self.NOTE_TEXT,
            author=self.user,
            slug=self.SLUG
        )
        self.auth_client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_new_note_slug_will_slugify(self):
        self.auth_client.post(self.url, data=self.form_data)
        note = Note.objects.get()
        self.assertEqual(note.slug, self.SLUG)


class TestNoteEditDelete(TestCase):
    NEW_NOTE_TEXT = 'Новый текст'
    NOTE_TEXT = 'Текст'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='test',
            text=cls.NOTE_TEXT,
            author=cls.author,
            slug='test',
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user_client = Client()
        cls.user_client.force_login(cls.reader)
        cls.form_data = {
            'title': cls.note.title,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.note.slug
        }
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_note_by_other_user(self):
        self.user_client.post(self.edit_url, data=self.form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)

    def test_user_cant_delete_note_by_other_user(self):
        self.user_client.delete(self.delete_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_delete_note(self):
        self.author_client.delete(self.delete_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)
