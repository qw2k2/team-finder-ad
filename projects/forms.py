from urllib.parse import urlparse

from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
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

    def clean_github_url(self):
        url = (self.cleaned_data.get("github_url") or "").strip()
        if not url:
            return url

        host = urlparse(url).netloc.lower()
        if host not in ("github.com", "www.github.com"):
            raise forms.ValidationError("Ссылка должна вести на GitHub")
        return url
