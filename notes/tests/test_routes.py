from http import HTTPStatus

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='Автор')
        cls.reader = User.objects.create_user(username='Читатель')
        cls.note = Note.objects.create(
            title='test',
            author=cls.author,
            text='test'
        )

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_users(self):
        self.client.force_login(self.author)
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_detail_delete_edit(self):
        self.client.force_login(self.author)
        users_statuses = (
            (self.reader, HTTPStatus.NOT_FOUND),
            (self.author, HTTPStatus.OK),
        )
        urls = (
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
        )
        for user, status in users_statuses:
            with self.subTest(user=user):
                self.client.force_login(user)
                for name, args in urls:
                    with self.subTest(name=name):
                        url = reverse(name, args=args)
                        response = self.client.get(url)
                        self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirected_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirected_url)
