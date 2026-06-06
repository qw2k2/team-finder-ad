from django import forms

from team_finder.forms import GithubUrlMixin
from .models import Project


class ProjectForm(GithubUrlMixin, forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "Ссылка на GitHub репозиторий",
            "status": "Статус",
        }
        widgets = {
            "description": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Опишите ваш проект..."}
            ),
        }
