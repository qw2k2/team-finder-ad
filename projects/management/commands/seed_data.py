from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from projects.models import Project, Skill


class Command(BaseCommand):
    def handle(self, *args, **options):
        User = get_user_model()

        users_data = [
            {
                "email": "maria@yandex.ru",
                "password": "password",
                "name": "Мария",
                "surname": "Петрова",
                "phone": "+79000000001",
                "about": "UX/UI дизайнер, люблю понятные интерфейсы и pet-проекты.",
                "github_url": "https://github.com/mariapetrova",
            },
            {
                "email": "alex@example.com",
                "password": "password",
                "name": "Алексей",
                "surname": "Иванов",
                "phone": "+79000000002",
                "about": "Frontend разработчик с опытом работы в React и TypeScript.",
                "github_url": "https://github.com/alexivanov",
            },
            {
                "email": "dmitry@example.com",
                "password": "password",
                "name": "Дмитрий",
                "surname": "Сидоров",
                "phone": "+79000000003",
                "about": "Backend разработчик, специализируюсь на Python и Django.",
                "github_url": "https://github.com/dsid",
            },
            {
                "email": "olga@example.com",
                "password": "password",
                "name": "Ольга",
                "surname": "Васильева",
                "phone": "+79000000004",
                "about": "Product manager, помогаю командам доводить идеи до релиза.",
                "github_url": "https://github.com/olgav",
            },
        ]

        users = {}
        for item in users_data:
            password = item.pop("password")
            user, _ = User.objects.update_or_create(email=item["email"], defaults=item)
            user.set_password(password)
            if user.avatar and not user.avatar.storage.exists(user.avatar.name):
                user.avatar = ""
            user.save()
            users[user.email] = user
            item["password"] = password

        admin, _ = User.objects.update_or_create(
            email="admin@example.com",
            defaults={
                "name": "Admin",
                "surname": "TeamFinder",
                "phone": "+79000000009",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        admin.set_password("admin")
        if admin.avatar and not admin.avatar.storage.exists(admin.avatar.name):
            admin.avatar = ""
        admin.save()

        skills = {}
        for name in [
            "Django",
            "Python",
            "React",
            "TypeScript",
            "HTML",
            "CSS",
            "PostgreSQL",
            "UI/UX",
        ]:
            skills[name], _ = Skill.objects.get_or_create(name=name)

        users["maria@yandex.ru"].skills.set([
            skills["UI/UX"], skills["React"], skills["HTML"],
        ])
        users["alex@example.com"].skills.set([
            skills["React"], skills["TypeScript"], skills["CSS"],
        ])
        users["dmitry@example.com"].skills.set([
            skills["Python"], skills["Django"], skills["PostgreSQL"],
        ])
        users["olga@example.com"].skills.set([skills["UI/UX"], skills["Python"]])

        projects_data = [
            {
                "name": "Социальная сеть для программистов",
                "description": (
                    "Создаем платформу для общения разработчиков, обмена опытом "
                    "и поиска команды для проектов."
                ),
                "owner": users["alex@example.com"],
                "github_url": "https://github.com/alexivanov/dev-social",
                "status": Project.STATUS_OPEN,
                "skill_names": ["React", "TypeScript", "Django"],
                "participants": ["maria@yandex.ru", "dmitry@example.com"],
            },
            {
                "name": "Мобильное приложение для фитнеса",
                "description": (
                    "Разрабатываем приложение для отслеживания тренировок и питания. "
                    "Ищем мобильных разработчиков и дизайнера."
                ),
                "owner": users["maria@yandex.ru"],
                "github_url": "https://github.com/mariapetrova/fitness-app",
                "status": Project.STATUS_OPEN,
                "skill_names": ["UI/UX", "React"],
                "participants": ["alex@example.com"],
            },
            {
                "name": "Сервис для командных заметок",
                "description": (
                    "Нужны backend и frontend разработчики для сервиса "
                    "совместных заметок и задач."
                ),
                "owner": users["dmitry@example.com"],
                "github_url": "https://github.com/dsid/team-notes",
                "status": Project.STATUS_OPEN,
                "skill_names": ["Python", "Django", "PostgreSQL"],
                "participants": ["olga@example.com"],
            },
            {
                "name": "Приложение для инвестиций",
                "description": (
                    "Ищу UX/UI-дизайнера и backend-разработчика "
                    "для финансового pet-проекта."
                ),
                "owner": users["olga@example.com"],
                "github_url": "https://github.com/olgav/invest-app",
                "status": Project.STATUS_OPEN,
                "skill_names": ["UI/UX", "Python"],
                "participants": ["maria@yandex.ru"],
            },
        ]

        for item in projects_data:
            skill_names = item.pop("skill_names")
            participant_emails = item.pop("participants")
            project, _ = Project.objects.update_or_create(
                name=item["name"],
                owner=item["owner"],
                defaults=item,
            )
            project.participants.add(project.owner)
            for email in participant_emails:
                project.participants.add(users[email])
            project.skills.set([skills[name] for name in skill_names])
            item["skill_names"] = skill_names
            item["participants"] = participant_emails

        if options.get("verbosity", 1):
            self.stdout.write(self.style.SUCCESS("Demo data created"))
