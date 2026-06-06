from django.conf import settings
from django.db import models
from django.urls import reverse

from team_finder.constants import PROJECT_NAME_MAX_LENGTH, PROJECT_STATUS_MAX_LENGTH
from team_finder.constants import SKILL_NAME_MAX_LENGTH


class Skill(models.Model):
    name = models.CharField("Название", max_length=SKILL_NAME_MAX_LENGTH, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"

    def __str__(self):
        return self.name


class Project(models.Model):
    STATUS_OPEN = "open"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = [
        (STATUS_OPEN, "Открыт"),
        (STATUS_CLOSED, "Закрыт"),
    ]

    name = models.CharField("Название", max_length=PROJECT_NAME_MAX_LENGTH)
    description = models.TextField("Описание", blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="owned_projects",
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    github_url = models.URLField("Ссылка на GitHub", blank=True)
    status = models.CharField(
        "Статус",
        max_length=PROJECT_STATUS_MAX_LENGTH,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="Участники",
        blank=True,
        related_name="participated_projects",
    )
    skills = models.ManyToManyField(
        Skill,
        verbose_name="Необходимые навыки",
        blank=True,
        related_name="projects",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("projects:detail", kwargs={"pk": self.pk})
