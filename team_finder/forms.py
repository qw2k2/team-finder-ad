from urllib.parse import urlparse

from django import forms


class GithubUrlMixin:
    def clean_github_url(self):
        url = (self.cleaned_data.get("github_url") or "").strip()
        if not url:
            return url

        host = urlparse(url).netloc.lower()
        if host not in ("github.com", "www.github.com"):
            raise forms.ValidationError("Ссылка должна вести на GitHub")
        return url
