import json
import shutil
import tempfile

from django.core.management import call_command
from django.test import TestCase, override_settings

from projects.forms import ProjectForm
from projects.models import Project, Skill
from users.models import User


TEST_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ProjectTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="password",
            name="Олег",
            surname="Автор",
        )
        self.member = User.objects.create_user(
            email="member@example.com",
            password="password",
            name="Анна",
            surname="Участник",
        )
        self.skill = Skill.objects.create(name="Django")
        self.project = Project.objects.create(
            name="TeamFinder",
            description="Поиск команды для pet-проектов",
            owner=self.owner,
            github_url="https://github.com/example/teamfinder",
        )
        self.project.participants.add(self.owner)
        self.project.skills.add(self.skill)

    def test_project_list_filter_by_skill(self):
        response = self.client.get("/projects/list/?skill=Django")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TeamFinder")
        self.assertEqual(list(response.context["page_obj"].object_list), [self.project])

    def test_guest_does_not_see_create_project_button(self):
        response = self.client.get("/projects/list/")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "+ Создать проект")

    def test_staff_can_complete_any_project(self):
        admin = User.objects.create_user(
            email="admin@example.com",
            password="password",
            name="Админ",
            surname="Админов",
            is_staff=True,
        )
        self.client.login(username="admin@example.com", password="password")

        response = self.client.post(f"/projects/{self.project.id}/complete/")

        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.STATUS_CLOSED)

    def test_skill_search_returns_matching_skills(self):
        Skill.objects.create(name="React")

        response = self.client.get("/projects/skills/?q=Dj")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{"id": self.skill.id, "name": "Django"}])

    def test_owner_can_add_and_remove_project_skill(self):
        self.client.login(username="owner@example.com", password="password")

        response = self.client.post(
            f"/projects/{self.project.id}/skills/add/",
            data=json.dumps({"name": "Python"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["created"])
        self.assertTrue(data["added"])
        self.assertTrue(self.project.skills.filter(name="Python").exists())

        remove_response = self.client.post(
            f"/projects/{self.project.id}/skills/{data['id']}/remove/"
        )

        self.assertEqual(remove_response.status_code, 200)
        self.assertFalse(self.project.skills.filter(name="Python").exists())

    def test_project_skill_duplicate_returns_added_false(self):
        self.client.login(username="owner@example.com", password="password")

        response = self.client.post(
            f"/projects/{self.project.id}/skills/add/",
            data=json.dumps({"skill_id": self.skill.id}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["added"])

    def test_non_owner_cannot_manage_project_skills(self):
        self.client.login(username="member@example.com", password="password")

        add_response = self.client.post(
            f"/projects/{self.project.id}/skills/add/",
            data=json.dumps({"name": "Python"}),
            content_type="application/json",
        )
        remove_response = self.client.post(
            f"/projects/{self.project.id}/skills/{self.skill.id}/remove/"
        )

        self.assertEqual(add_response.status_code, 403)
        self.assertEqual(remove_response.status_code, 403)

    def test_user_can_toggle_participation(self):
        self.client.login(username="member@example.com", password="password")

        response = self.client.post(f"/projects/{self.project.id}/toggle-participate/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["participant"])
        self.assertTrue(self.project.participants.filter(pk=self.member.pk).exists())

    def test_project_form_accepts_only_github_url(self):
        form = ProjectForm(data={
            "name": "Project",
            "description": "",
            "github_url": "https://gitlab.com/example/project",
            "status": Project.STATUS_OPEN,
        })

        self.assertFalse(form.is_valid())
        self.assertIn("github_url", form.errors)

    def test_seed_data_creates_demo_users_projects_and_skills(self):
        call_command("seed_data", verbosity=0)

        self.assertTrue(User.objects.filter(email="maria@yandex.ru").exists())
        self.assertGreaterEqual(User.objects.count(), 5)
        self.assertGreaterEqual(Project.objects.count(), 4)
        self.assertGreaterEqual(Skill.objects.count(), 6)
        self.assertTrue(Project.objects.filter(skills__name="Django").exists())
