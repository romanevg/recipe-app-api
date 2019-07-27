from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@gmail.com',
            password='pass123'
        )
        # force_login - helper функция для автоматического залогинивания
        # пользователя (а не вручную из админки), чтобы протестировать его.
        # Это делает тесты гораздо проще.
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='test@gmail.com',
            password='qwer321',
            name='Test User'
        )

    def test_users_listed(self):
        """Test that users are listed on user page"""
        # reverse - функция для поиска URL по его имени с
        # передачей при необходимости args и kwargs
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """Test that the user edit page works"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        # url => /admin/core/user/13
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test that the create user page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
