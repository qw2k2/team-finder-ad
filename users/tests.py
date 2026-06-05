import json
import shutil
import tempfile

from django.test import TestCase, override_settings

from projects.models import Skill
from .forms import ProfileForm
from .models import User


TEST_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class UserTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def test_register_creates_user_and_redirects_to_login(self):
        response = self.client.post("/users/register/", {
            "name": "Иван",
            "surname": "Петров",
            "email": "ivan@example.com",
            "password": "password",
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/users/login/")
        self.assertTrue(User.objects.filter(email="ivan@example.com").exists())
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_by_email(self):
        User.objects.create_user(
            email="maria@example.com",
            password="password",
            name="Мария",
            surname="Иванова",
        )

        response = self.client.post("/users/login/", {
            "email": "maria@example.com",
            "password": "password",
        })

        self.assertEqual(response.status_code, 302)

    def test_user_list_orders_newest_first(self):
        first = User.objects.create_user(
            email="first@example.com",
            password="password",
            name="Первый",
            surname="Пользователь",
        )
        second = User.objects.create_user(
            email="second@example.com",
            password="password",
            name="Второй",
            surname="Пользователь",
        )

        response = self.client.get("/users/list/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["page_obj"].object_list), [second, first])

    def test_profile_phone_validation_normalizes_and_checks_duplicates(self):
        User.objects.create_user(
            email="first@example.com",
            password="password",
            name="Первый",
            surname="Пользователь",
            phone="+79000000001",
        )
        user = User.objects.create_user(
            email="second@example.com",
            password="password",
            name="Второй",
            surname="Пользователь",
        )

        form = ProfileForm(data={
            "name": "Второй",
            "surname": "Пользователь",
            "about": "",
            "phone": "89000000001",
            "github_url": "https://github.com/second",
        }, instance=user)

        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

    def test_profile_github_url_must_point_to_github(self):
        user = User.objects.create_user(
            email="github@example.com",
            password="password",
            name="Гит",
            surname="Хабов",
        )

        form = ProfileForm(data={
            "name": "Гит",
            "surname": "Хабов",
            "about": "",
            "phone": "+79000000002",
            "github_url": "https://gitlab.com/user",
        }, instance=user)

        self.assertFalse(form.is_valid())
        self.assertIn("github_url", form.errors)

    def test_owner_can_add_and_remove_profile_skill(self):
        user = User.objects.create_user(
            email="skill@example.com",
            password="password",
            name="Навык",
            surname="Пользователь",
        )
        self.client.login(username="skill@example.com", password="password")

        response = self.client.post(
            f"/users/{user.id}/skills/add/",
            data=json.dumps({"name": "Django"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["created"])
        self.assertTrue(data["added"])
        self.assertTrue(user.skills.filter(name="Django").exists())

        remove_response = self.client.post(
            f"/users/{user.id}/skills/{data['id']}/remove/"
        )

        self.assertEqual(remove_response.status_code, 200)
        self.assertFalse(user.skills.filter(name="Django").exists())

    def test_other_user_cannot_manage_profile_skills(self):
        owner = User.objects.create_user(
            email="owner-skill@example.com",
            password="password",
            name="Владелец",
            surname="Профиля",
        )
        other = User.objects.create_user(
            email="other-skill@example.com",
            password="password",
            name="Другой",
            surname="Пользователь",
        )
        skill = Skill.objects.create(name="Python")
        owner.skills.add(skill)
        self.client.login(username="other-skill@example.com", password="password")

        add_response = self.client.post(
            f"/users/{owner.id}/skills/add/",
            data=json.dumps({"name": "Django"}),
            content_type="application/json",
        )
        remove_response = self.client.post(f"/users/{owner.id}/skills/{skill.id}/remove/")

        self.assertEqual(add_response.status_code, 403)
        self.assertEqual(remove_response.status_code, 403)
        self.assertFalse(other.skills.filter(name="Django").exists())
